"""RBAC 권한 확인 미들웨어 - 고급 권한 관리 전용"""

import json
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

if TYPE_CHECKING:
    CallNextType = Any
else:
    CallNextType = Any


from mysingle.auth.auth_utils import (
    get_auth_context,
)
from mysingle.exceptions import PermissionDeniedError, RBACError
from mysingle.iam.client import UnifiedIAMClient

# 순환 import 방지를 위해 직접 import
from mysingle.logging import get_logger

logger = get_logger(__name__)


class RBACMiddleware(BaseHTTPMiddleware):
    """고급 RBAC 권한 확인 미들웨어

    이 미들웨어는 복잡한 권한 관리가 필요한 경우에만 사용합니다:
    - 경로 기반 자동 권한 매핑
    - 테넌트별 권한 확인
    - 배치 권한 확인 최적화

    주의: AuthMiddleware와 함께 사용 시 AuthMiddleware가 먼저 적용되어야 합니다.
    """

    def __init__(
        self,
        app: Any,
        rbac_service_url: Optional[str] = None,
        protected_paths: Optional[Dict[str, Dict[str, str]]] = None,
        excluded_paths: Optional[Set[str]] = None,
        enable_path_based_check: bool = False,
        enable_batch_optimization: bool = True,
    ):
        """
        RBAC 미들웨어 초기화

        Args:
            app: ASGI 애플리케이션
            rbac_service_url: RBAC 서비스 URL (None이면 기본값 사용)
            protected_paths: 보호된 경로와 권한 매핑
            excluded_paths: 권한 확인에서 제외할 경로
            enable_path_based_check: 경로 기반 자동 권한 확인 활성화
            enable_batch_optimization: 배치 권한 확인 최적화 활성화
        """
        super().__init__(app)
        self.rbac_service_url = rbac_service_url
        self.protected_paths = protected_paths or {}
        self.excluded_paths = excluded_paths or set()
        self.enable_path_based_check = enable_path_based_check
        self.enable_batch_optimization = enable_batch_optimization

        # UnifiedIAMClient 초기화
        self.iam_client = UnifiedIAMClient()

        # HTTP 메서드와 액션 매핑
        self.method_action_mapping = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

    async def dispatch(
        self, request: Request, call_next: CallNextType
    ) -> Response:
        """미들웨어 메인 로직"""
        start_time = time.time()

        # 제외 경로 확인
        if self._is_excluded_path(request.url.path):
            response = await call_next(request)
            return response  # type: ignore[no-any-return]

        try:
            # 권한 확인이 필요한지 판단
            if not self._needs_permission_check(request):
                response = await call_next(request)
                return response  # type: ignore[no-any-return]

            # 사용자 인증 정보 추출
            user_info = await self._extract_user_info(request)
            if not user_info:
                return self._create_error_response(
                    401, "Authentication required"
                )

            # 권한 확인
            if self.enable_path_based_check:
                permission_result = await self._check_path_based_permission(
                    request, user_info
                )
                if not permission_result:
                    return self._create_error_response(
                        HTTP_403_FORBIDDEN,
                        "Insufficient privileges for this operation",
                    )

                # 권한 정보를 request.state에 저장
                request.state.rbac_info = permission_result
                request.state.user_info = user_info

            # 다음 미들웨어/핸들러로 요청 전달
            response = await call_next(request)

            # 응답 처리 후 감사 로그 기록
            await self._log_request(request, response, start_time)

            return response  # type: ignore[no-any-return]

        except PermissionDeniedError as e:
            logger.warning(
                f"Permission denied for {request.url.path}: {e.message}"
            )
            return self._create_error_response(HTTP_403_FORBIDDEN, e.message)

        except RBACError as e:
            logger.error(f"RBAC error for {request.url.path}: {e.message}")
            return self._create_error_response(
                HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal authorization error",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in RBAC middleware: {str(e)}",
                exc_info=True,
            )
            return self._create_error_response(
                HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error",
            )

    def _is_excluded_path(self, path: str) -> bool:
        """경로가 권한 확인에서 제외되는지 확인"""
        return any(
            path.startswith(excluded_path)
            for excluded_path in self.excluded_paths
        )

    def _needs_permission_check(self, request: Request) -> bool:
        """요청이 권한 확인이 필요한지 판단"""
        # 기본적으로 모든 요청은 권한 확인이 필요
        # 하위 클래스에서 오버라이드 가능
        return True

    async def _extract_user_info(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        """요청에서 사용자 정보 추출"""
        try:
            # AuthMiddleware에서 설정한 인증 정보 사용
            auth_context = get_auth_context(request)
            if auth_context:
                return {
                    "user_id": auth_context.payload.get("sub"),
                    "tenant_id": auth_context.payload.get("tenant_id"),
                    "roles": auth_context.payload.get("roles", []),
                    "permissions": auth_context.payload.get("permissions", []),
                }

            # fallback: request.state에서 직접 추출
            if hasattr(request.state, "user"):
                user = request.state.user
                return {
                    "user_id": user.get("sub"),
                    "tenant_id": user.get("tenant_id"),
                    "roles": user.get("roles", []),
                    "permissions": user.get("permissions", []),
                }

            return None

        except Exception as e:
            logger.error(f"Failed to extract user info: {str(e)}")
            return None

    async def _check_path_based_permission(
        self, request: Request, user_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """경로 기반 권한 확인"""
        path = request.url.path
        method = request.method

        # 보호된 경로에서 리소스와 액션 추출
        resource, action = self._extract_resource_action(path, method)
        if not resource or not action:
            # 매핑되지 않은 경로는 통과
            return {"allowed": True, "resource": None, "action": None}

        try:
            # UnifiedIAMClient를 통한 권한 확인
            result = await self.iam_client.check_permission(
                user_id=user_info["user_id"],
                tenant_id=user_info["tenant_id"],
                resource=resource,
                action=action,
            )

            return {
                "allowed": result,
                "resource": resource,
                "action": action,
                "user_id": user_info["user_id"],
                "tenant_id": user_info["tenant_id"],
            }

        except Exception as e:
            logger.error(
                f"Permission check failed for {resource}:{action}: {str(e)}"
            )
            # 권한 확인 실패 시 기본적으로 거부
            return None

    def _extract_resource_action(
        self, path: str, method: str
    ) -> tuple[Optional[str], Optional[str]]:
        """경로와 메서드에서 리소스와 액션 추출"""
        # 설정된 보호 경로에서 매핑 찾기
        for path_pattern, permissions in self.protected_paths.items():
            if path.startswith(path_pattern):
                resource = permissions.get("resource")
                action = permissions.get(method.lower()) or permissions.get(
                    "default"
                )
                if resource and action:
                    return resource, action

        # 기본 매핑 시도
        action = self.method_action_mapping.get(method)
        if action:
            # 경로에서 리소스 추출 시도 (예: /api/v1/users -> users)
            path_parts = [p for p in path.split("/") if p]
            if len(path_parts) >= 3:  # /api/v1/resource 형태
                resource = path_parts[2]
                return resource, action

        return None, None

    async def _log_request(
        self, request: Request, response: Response, start_time: float
    ) -> None:
        """요청 감사 로그 기록"""
        try:
            duration = time.time() - start_time

            # 기본 로그 정보
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "timestamp": time.time(),
            }

            # RBAC 정보 추가
            if hasattr(request.state, "rbac_info"):
                log_data["rbac_info"] = request.state.rbac_info

            # 사용자 정보 추가
            if hasattr(request.state, "user_info"):
                user_info = request.state.user_info
                log_data["user_id"] = user_info.get("user_id")
                log_data["tenant_id"] = user_info.get("tenant_id")

            logger.info(f"RBAC access log: {json.dumps(log_data)}")

        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")

    def _create_error_response(
        self, status_code: int, message: str
    ) -> Response:
        """에러 응답 생성"""
        content = json.dumps({"detail": message})
        return Response(
            content=content,
            status_code=status_code,
            media_type="application/json",
        )


class RBACMiddlewareConfig:
    """RBAC 미들웨어 설정 헬퍼"""

    @staticmethod
    def create_service_config(
        service_name: str, resources: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """서비스별 기본 보호 경로 설정 생성"""
        config = {}

        for resource in resources:
            # RESTful API 패턴에 따른 경로 매핑
            base_path = f"/api/v1/{resource}"

            config[base_path] = {
                "resource": f"{service_name}:{resource}",
                "get": "read",
                "post": "create",
                "put": "update",
                "patch": "update",
                "delete": "delete",
                "default": "read",
            }

            # 개별 리소스 경로 (/api/v1/resource/{id})
            item_path = f"{base_path}/"
            config[item_path] = {
                "resource": f"{service_name}:{resource}",
                "get": "read",
                "put": "update",
                "patch": "update",
                "delete": "delete",
                "default": "read",
            }

        return config

    @staticmethod
    def create_admin_config() -> Dict[str, Dict[str, str]]:
        """관리자용 보호 경로 설정"""
        return {
            "/admin": {
                "resource": "admin:panel",
                "default": "admin",
            },
            "/api/v1/admin": {
                "resource": "admin:api",
                "default": "admin",
            },
        }
