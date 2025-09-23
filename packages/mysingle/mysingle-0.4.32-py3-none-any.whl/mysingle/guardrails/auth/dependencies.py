"""통합 FastAPI 권한 확인 의존성 - 가드레일 중심 통합"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN

from mysingle.auth.auth_utils import get_auth_context
from mysingle.config import settings
from mysingle.exceptions import (
    PermissionDeniedError,
    RBACServiceUnavailableError,
    RBACTimeoutError,
)
from mysingle.iam.client import UnifiedIAMClient, get_iam_client
from mysingle.iam.schemas import UserInfo
from mysingle.logging import get_logger
from mysingle.rbac.cache import RBACCache

logger = get_logger(__name__)

# OAuth2 스키마 (토큰 추출용)
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.IAM_SERVICE_PUBLIC_URL}/api/{settings.IAM_API_VERSION}/auth/login",
    auto_error=False,
)

# 전역 클라이언트 및 캐시
_iam_client: Optional[UnifiedIAMClient] = None
_rbac_cache: Optional[RBACCache] = None


async def get_iam_client_instance() -> UnifiedIAMClient:
    """IAM 클라이언트 인스턴스 반환 (싱글톤)"""
    global _iam_client
    if _iam_client is None:
        _iam_client = await get_iam_client()
    return _iam_client


async def get_rbac_cache_instance() -> RBACCache:
    """RBAC 캐시 인스턴스 반환 (싱글톤)"""
    global _rbac_cache
    if _rbac_cache is None:
        _rbac_cache = RBACCache()
        await _rbac_cache.initialize()
    return _rbac_cache


async def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    """테넌트 ID 추출 (기존 가드레일과 호환)"""
    if x_tenant_id is None:
        raise HTTPException(
            status_code=400, detail="X-Tenant-Id header missing"
        )
    return x_tenant_id


# async def get_auth_token(
#     authorization: str = Header(default=None),
# ) -> Optional[str]:
#     """Authorization 헤더에서 토큰 추출"""
#     if not authorization:
#         return None

#     if authorization.startswith("Bearer "):
#         return authorization[7:]  # "Bearer " 제거
#     return authorization


async def get_auth_token(
    token: str = Depends(oauth2_scheme),
) -> Optional[str]:
    """OAuth2 스키마에서 토큰 추출"""
    return token


async def get_current_user(
    request: Request,
    auth_token: str = Depends(get_auth_token),
) -> UserInfo:
    """현재 인증된 사용자 정보 반환"""
    if not auth_token:
        raise HTTPException(
            status_code=401, detail="Authentication token required"
        )

    try:
        client = await get_iam_client_instance()
        user_info = await client.get_current_user(auth_token)
        return user_info
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(
            status_code=401, detail="Invalid authentication token"
        )


async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User"
        )
    return current_user


async def get_current_active_verified_user(
    current_user=Depends(get_current_active_user),
):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unverified Email"
        )
    return current_user


async def get_user_permissions(
    user_id: str,
    tenant_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    auth_token: str = Depends(get_auth_token),
) -> List[Dict[str, Any]]:
    """사용자 권한 목록 조회"""
    if not auth_token:
        raise HTTPException(
            status_code=401, detail="Authentication token required"
        )

    try:
        client = await get_iam_client_instance()
        permissions = await client.get_user_permissions(
            user_id=user_id,
            tenant_id=tenant_id,
            resource_type=resource_type,
            auth_token=auth_token,
        )
        return permissions
    except Exception as e:
        logger.error(f"Failed to get user permissions: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve user permissions"
        )


def create_permission_dependency(
    resource: str,
    action: str,
    tenant_from_path: bool = True,
    user_id_from_token: bool = True,
    context_builder: Optional[Callable] = None,
    fail_open: bool = False,
) -> Callable[[Request], Awaitable[None]]:
    """
    통합된 권한 확인 의존성 팩토리

    가드레일과 RBAC 기능을 모두 지원하는 통합 의존성 생성기

    Args:
        resource: 리소스 명 (예: "ledger:journals")
        action: 액션 (create|read|update|delete)
        tenant_from_path: 경로/헤더에서 tenant_id 추출 여부
        user_id_from_token: JWT 토큰에서 user_id 추출 여부
        context_builder: 추가 컨텍스트 빌더 함수
        fail_open: 권한 확인 실패 시 접근 허용 여부 (개발용)

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

            # 캐시 키 생성
            cache = await get_rbac_cache_instance()
            cache_key = RBACCache.generate_cache_key(
                user_id=user_id,
                resource=resource,
                action=action,
                tenant_id=tenant_id,
                context=context if context else None,
            )

            # 캐시에서 권한 확인 결과 조회
            try:
                cached_result = await cache.get_permission(cache_key)
                if cached_result is not None:
                    logger.debug(
                        f"Using cached permission result for {cache_key}"
                    )
                    if not cached_result.get("allowed", False):
                        if fail_open:
                            logger.warning("Cached denial, but fail_open=True")
                            return
                        raise PermissionDeniedError(
                            user_id=user_id,
                            resource=resource,
                            action=action,
                            reason="Insufficient permissions (cached)",
                        )
                    else:
                        logger.debug(
                            f"Cached permission granted: user={user_id}, resource={resource}"
                        )
                        return
            except Exception as cache_error:
                logger.warning(
                    f"Cache lookup failed for {cache_key}: {cache_error}"
                )
                # 캐시 실패 시 계속 진행 (fallback to IAM service)

            # 캐시 미스 또는 캐시 오류 - UnifiedIAMClient로 권한 확인
            try:
                client = await get_iam_client_instance()
                permission_result = await client.check_permission(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    tenant_id=tenant_id,
                )
            except TimeoutError as e:
                logger.error(f"IAM service timeout: {e}")
                if fail_open:
                    logger.warning("IAM timeout, but fail_open=True")
                    return
                raise RBACTimeoutError(
                    timeout_seconds=30.0, operation="check_permission"
                )
            except Exception as e:
                logger.error(f"IAM service error: {e}")
                if fail_open:
                    logger.warning(f"IAM error, but fail_open=True: {e}")
                    return
                raise RBACServiceUnavailableError("IAM service unavailable")

            # 결과를 캐시에 저장 (실패해도 계속 진행)
            try:
                cache_data = {
                    "allowed": permission_result.allowed,
                    "user_id": user_id,
                    "resource": resource,
                    "action": action,
                    "tenant_id": tenant_id,
                }
                await cache.set_permission(cache_key, cache_data)
            except Exception as cache_error:
                logger.warning(
                    f"Failed to cache permission result: {cache_error}"
                )

            if not permission_result.allowed:
                logger.warning(
                    f"Permission denied: user={user_id}, resource={resource}, "
                    f"action={action}, tenant_id={tenant_id}"
                )

                if fail_open:
                    logger.warning(
                        "fail_open=True, allowing access despite denial"
                    )
                    return

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
        except RBACTimeoutError as e:
            logger.error(f"RBAC timeout: {e}")
            raise HTTPException(
                status_code=503, detail="권한 확인 서비스가 응답하지 않습니다"
            )
        except RBACServiceUnavailableError as e:
            logger.error(f"RBAC service unavailable: {e}")
            raise HTTPException(
                status_code=503, detail="권한 확인 서비스를 사용할 수 없습니다"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in permission check: {e}")
            if fail_open:
                logger.warning(f"Unexpected error, but fail_open=True: {e}")
                return
            raise HTTPException(
                status_code=500, detail="권한 확인 중 오류가 발생했습니다"
            )

    return permission_dependency


async def check_permission(
    resource: str,
    action: str,
    request: Request,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """권한 확인 의존성 (가드레일 호환)"""
    try:
        auth_context = get_auth_context(request)
        if not auth_context:
            raise HTTPException(
                status_code=401, detail="Authentication context not found"
            )

        client = await get_iam_client_instance()
        permission_result = await client.check_permission(
            user_id=auth_context.user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id,
        )

        if not permission_result.allowed:
            raise HTTPException(status_code=403, detail="Permission denied")

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="Authorization system error"
        )


def require_permission(
    resource: str,
    action: str,
    tenant_from_path: bool = True,
    user_id_from_token: bool = True,
    context_builder: Optional[Callable] = None,
    fail_open: bool = False,
) -> Any:
    """
    통합된 권한 확인 의존성

    Usage:
        # FastAPI Dependencies 방식 (권장)
        _auth: None = Depends(require_permission("ledger:journals", "create"))

        # 가드레일 방식 (하위 호환)
        _auth: None = require_permission("ledger:journals", "create")
    """
    return Depends(
        create_permission_dependency(
            resource=resource,
            action=action,
            tenant_from_path=tenant_from_path,
            user_id_from_token=user_id_from_token,
            context_builder=context_builder,
            fail_open=fail_open,
        )
    )


# 편의 의존성 함수들
def get_user_dependency(user_id: str) -> Any:
    """특정 사용자 정보 조회 의존성"""

    async def _get_user(auth_token: str = Depends(get_auth_token)) -> UserInfo:
        if not auth_token:
            raise HTTPException(
                status_code=401, detail="Authentication token required"
            )

        try:
            client = await get_iam_client_instance()
            return await client.get_user(user_id, auth_token)
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise HTTPException(status_code=404, detail="User not found")

    return Depends(_get_user)


def get_user_permissions_dependency(
    user_id: str,
    tenant_id: Optional[str] = None,
    resource_type: Optional[str] = None,
) -> Any:
    """사용자 권한 목록 조회 의존성"""

    async def _get_permissions(
        auth_token: str = Depends(get_auth_token),
    ) -> List[Dict[str, Any]]:
        return await get_user_permissions(
            user_id=user_id,
            tenant_id=tenant_id,
            resource_type=resource_type,
            auth_token=auth_token,
        )

    return Depends(_get_permissions)


# 캐시 관리 함수들
async def invalidate_user_cache(
    user_id: str, tenant_id: Optional[str] = None
) -> None:
    """사용자 권한 캐시 무효화 헬퍼"""
    cache = await get_rbac_cache_instance()
    await cache.invalidate_user_permissions(user_id, tenant_id)


async def get_cache_stats() -> Dict[str, Any]:
    """캐시 통계 조회"""
    cache = await get_rbac_cache_instance()
    return cache.get_cache_stats()


async def clear_all_cache() -> None:
    """모든 캐시 지우기 (개발/테스트용)"""
    cache = await get_rbac_cache_instance()
    await cache.clear_all_cache()
