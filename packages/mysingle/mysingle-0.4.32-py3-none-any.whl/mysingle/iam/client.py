"""통합 IAM 클라이언트 - MySingle IAM 서비스와의 통합 인터페이스"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from mysingle.config import settings
from mysingle.exceptions import APIError, InternalServerError
from mysingle.logging import get_logger

from .schemas import (
    AuthResponse,
    PermissionCheckRequest,
    PermissionResult,
    SessionInfo,
    UserInfo,
    UserLogin,
    UserUpdate,
)

logger = get_logger(__name__)


class UnifiedIAMClient:
    """통합 IAM 서비스 클라이언트

    MySingle 통합 IAM 서비스와의 모든 상호작용을 담당합니다.
    인증, 권한 확인, 사용자 관리, 세션 관리를 통합 제공합니다.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.base_url = base_url or settings.IAM_SERVICE_INTERNAL_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 반환 (지연 초기화)"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """HTTP 요청 실행 (재시도 로직 포함)"""
        client = await self._get_client()

        request_headers = headers or {}
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"

        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    headers=request_headers,
                )

                if response.status_code >= 400:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("detail", error_detail)
                    except Exception as e:
                        logger.debug(
                            f"Failed to parse error response as JSON: {e}"
                        )

                    if response.status_code >= 500:
                        raise InternalServerError(
                            message=f"IAM service error: {error_detail}"
                        )
                    else:
                        raise APIError(
                            status_code=response.status_code,
                            error="IAM_REQUEST_FAILED",
                            message=f"IAM request failed: {error_detail}",
                        )

                return response.json()

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"IAM request failed (attempt {attempt + 1}): {e}. Retrying..."
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                break

        raise InternalServerError(
            message=f"IAM service unavailable after {self.max_retries} retries: {last_exception}"
        )

    # ============================================================================
    # 인증 관련 메서드들
    # ============================================================================

    async def login(self, login_data: UserLogin) -> AuthResponse:
        """사용자 로그인"""
        response_data = await self._make_request(
            "POST",
            f"/api/{settings.IAM_API_VERSION}/auth/login",
            data=login_data.model_dump(),
        )
        return AuthResponse(**response_data)

    async def logout(self, token: str) -> bool:
        """사용자 로그아웃"""
        try:
            await self._make_request(
                "POST",
                f"/api/{settings.IAM_API_VERSION}/auth/logout",
                auth_token=token,
            )
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False

    async def verify_token(self, token: str) -> UserInfo:
        """JWT 토큰 검증"""
        response_data = await self._make_request(
            "POST",
            f"/api/{settings.IAM_API_VERSION}/auth/verify",
            data={"token": token},
        )
        return UserInfo(**response_data)

    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """토큰 갱신"""
        response_data = await self._make_request(
            "POST",
            f"/api/{settings.IAM_API_VERSION}/auth/refresh",
            data={"refresh_token": refresh_token},
        )
        return AuthResponse(**response_data)

    # ============================================================================
    # 권한 확인 관련 메서드들
    # ============================================================================

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> PermissionResult:
        """단일 권한 확인"""
        request_data = PermissionCheckRequest(
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id,
            context=context or {},
        )

        response_data = await self._make_request(
            "POST",
            f"/api/{settings.IAM_API_VERSION}/rbac/decisions/check",
            data=request_data.model_dump(),
            auth_token=auth_token,
        )
        return PermissionResult(**response_data)

    async def batch_check_permissions(
        self,
        user_id: str,
        permissions: List[Dict[str, str]],
        tenant_id: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> List[PermissionResult]:
        """배치 권한 확인"""
        request_data = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "permissions": permissions,
        }

        response_data = await self._make_request(
            "POST",
            f"/api/{settings.IAM_API_VERSION}/rbac/decisions/batch-check",
            data=request_data,
            auth_token=auth_token,
        )

        return [
            PermissionResult(**result)
            for result in response_data.get("results", [])
        ]

    async def get_user_permissions(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """사용자 권한 목록 조회"""
        params = {"tenant_id": tenant_id, "resource_type": resource_type}
        params = {k: v for k, v in params.items() if v is not None}

        # URL 쿼리 파라미터 구성
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/api/{settings.IAM_API_VERSION}/rbac/decisions/user-permissions/{user_id}"
        if query_string:
            endpoint += f"?{query_string}"

        response_data = await self._make_request(
            "GET", endpoint, auth_token=auth_token
        )
        return response_data.get("permissions", [])

    # ============================================================================
    # 사용자 관리 관련 메서드들
    # ============================================================================

    async def get_user(self, user_id: str, auth_token: str) -> UserInfo:
        """사용자 정보 조회"""
        response_data = await self._make_request(
            "GET",
            f"/api/{settings.IAM_API_VERSION}/users/{user_id}",
            auth_token=auth_token,
        )
        return UserInfo(**response_data)

    async def get_current_user(self, auth_token: str) -> UserInfo:
        """현재 로그인 사용자 정보 조회"""
        response_data = await self._make_request(
            "GET",
            f"/api/{settings.IAM_API_VERSION}/users/me",
            auth_token=auth_token,
        )
        return UserInfo(**response_data)

    async def update_user(
        self, user_id: str, update_data: UserUpdate, auth_token: str
    ) -> UserInfo:
        """사용자 정보 수정"""
        response_data = await self._make_request(
            "PUT",
            f"/api/{settings.IAM_API_VERSION}/users/{user_id}",
            data=update_data.model_dump(exclude_unset=True),
            auth_token=auth_token,
        )
        return UserInfo(**response_data)

    async def change_password(
        self,
        current_password: str,
        new_password: str,
        auth_token: str,
    ) -> bool:
        """비밀번호 변경"""
        try:
            await self._make_request(
                "POST",
                f"/api/{settings.IAM_API_VERSION}/users/change-password",
                data={
                    "current_password": current_password,
                    "new_password": new_password,
                },
                auth_token=auth_token,
            )
            return True
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return False

    # ============================================================================
    # 세션 관리 관련 메서드들
    # ============================================================================

    async def get_user_sessions(
        self,
        page: int = 1,
        size: int = 10,
        auth_token: Optional[str] = None,
    ) -> List[SessionInfo]:
        """사용자 세션 목록 조회"""
        response_data = await self._make_request(
            "GET",
            f"/api/{settings.IAM_API_VERSION}/sessions?page={page}&size={size}",
            auth_token=auth_token,
        )
        return [
            SessionInfo(**session)
            for session in response_data.get("items", [])
        ]

    async def get_current_session(self, auth_token: str) -> SessionInfo:
        """현재 세션 정보 조회"""
        response_data = await self._make_request(
            "GET",
            f"/api/{settings.IAM_API_VERSION}/sessions/current",
            auth_token=auth_token,
        )
        return SessionInfo(**response_data)

    async def deactivate_session(
        self, session_id: str, auth_token: str
    ) -> bool:
        """특정 세션 비활성화"""
        try:
            await self._make_request(
                "POST",
                f"/api/{settings.IAM_API_VERSION}/sessions/{session_id}/deactivate",
                auth_token=auth_token,
            )
            return True
        except Exception as e:
            logger.error(f"Session deactivation failed: {e}")
            return False

    async def deactivate_all_sessions(self, auth_token: str) -> bool:
        """모든 다른 세션 비활성화"""
        try:
            await self._make_request(
                "POST",
                f"/api/{settings.IAM_API_VERSION}/sessions/deactivate-all",
                auth_token=auth_token,
            )
            return True
        except Exception as e:
            logger.error(f"All sessions deactivation failed: {e}")
            return False

    # ============================================================================
    # 리소스 관리
    # ============================================================================

    async def close(self) -> None:
        """클라이언트 리소스 정리"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============================================================================
# 글로벌 클라이언트 관리
# ============================================================================

_global_iam_client: Optional[UnifiedIAMClient] = None


async def get_iam_client(
    base_url: Optional[str] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> UnifiedIAMClient:
    """글로벌 IAM 클라이언트 반환 (싱글톤 패턴)"""
    global _global_iam_client

    if _global_iam_client is None:
        _global_iam_client = UnifiedIAMClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    return _global_iam_client


async def close_global_iam_client() -> None:
    """글로벌 IAM 클라이언트 정리"""
    global _global_iam_client

    if _global_iam_client:
        await _global_iam_client.close()
        _global_iam_client = None
