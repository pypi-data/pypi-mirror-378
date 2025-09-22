"""RBAC FastAPI 의존성 함수들"""

from typing import Any, Awaitable, Callable, Optional

from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN

from mysingle.auth.auth_utils import get_auth_context
from mysingle.exceptions import PermissionDeniedError
from mysingle.logging import get_logger

logger = get_logger(__name__)


async def _get_rbac_client():
    """지연 import로 순환 import 방지"""
    from .rbac_client import get_rbac_client

    return await get_rbac_client()


def create_permission_dependency(
    resource: str,
    action: str,
    tenant_from_path: bool = True,
    tenant_param: str = "tenant_id",
    user_id_from_token: bool = True,
    user_id_param: str = "user_id",
    context_builder: Optional[Callable] = None,
    rbac_client=None,
) -> Callable[[Request], Awaitable[None]]:
    """
    권한 확인 의존성 함수를 생성하는 팩토리 함수

    Args:
        resource: 리소스 명 (예: "ledger:journals")
        action: 액션 (create|read|update|delete)
        tenant_from_path: 경로에서 tenant_id 추출 여부
        tenant_param: tenant_id 매개변수명
        user_id_from_token: JWT 토큰에서 user_id 추출 여부
        user_id_param: user_id 매개변수명
        context_builder: 추가 컨텍스트 빌더 함수
        rbac_client: 사용할 RBAC 클라이언트

    Returns:
        FastAPI 의존성 함수
    """

    async def permission_dependency(request: Request) -> None:
        """실제 권한 확인을 수행하는 의존성 함수"""
        try:
            # 사용자 ID 추출 (통합 인증 유틸리티 사용)
            user_id = None
            tenant_id = None

            if user_id_from_token:
                # 이미 미들웨어에서 처리된 인증 컨텍스트 확인
                auth_context = get_auth_context(request)
                if auth_context:
                    user_id = auth_context.user_id
                    tenant_id = auth_context.tenant_id

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication context not found",
                )

            # 테넌트 ID 추출 (헤더에서 우선)
            if tenant_from_path and not tenant_id:
                tenant_id = request.headers.get("x-tenant-id")
                if not tenant_id:
                    raise HTTPException(
                        status_code=400,
                        detail="X-Tenant-Id header required",
                    )

            # 추가 컨텍스트 빌드
            context = {}
            if context_builder:
                additional_context = context_builder(request)
                context.update(additional_context)

            # RBAC 클라이언트로 권한 확인
            client = rbac_client or await _get_rbac_client()
            permission_result = await client.check_permission(
                user_id=user_id,
                resource=resource,
                action=action,
                tenant_id=tenant_id,
            )

            if not permission_result.allowed:
                logger.warning(
                    f"Permission denied: user={user_id}, resource={resource}, "
                    f"action={action}, tenant_id={tenant_id}"
                )
                raise PermissionDeniedError(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    reason="Insufficient permissions",
                )

            logger.debug(
                f"Permission granted: user={user_id}, resource={resource}, "
                f"action={action}"
            )

        except PermissionDeniedError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="권한이 없습니다"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"RBAC check failed: {e}")
            raise HTTPException(
                status_code=500, detail="권한 확인 중 오류가 발생했습니다"
            )

    return permission_dependency


def require_permission(
    resource: str,
    action: str,
    tenant_from_path: bool = True,
    tenant_param: str = "tenant_id",
    user_id_from_token: bool = True,
    user_id_param: str = "user_id",
    context_builder: Optional[Callable] = None,
    rbac_client=None,
) -> Any:
    """
    권한 확인 의존성을 반환하는 함수

    Usage:
        _auth: None = Depends(require_permission("ledger:journals", "create"))
    """
    return create_permission_dependency(
        resource=resource,
        action=action,
        tenant_from_path=tenant_from_path,
        tenant_param=tenant_param,
        user_id_from_token=user_id_from_token,
        user_id_param=user_id_param,
        context_builder=context_builder,
        rbac_client=rbac_client,
    )
