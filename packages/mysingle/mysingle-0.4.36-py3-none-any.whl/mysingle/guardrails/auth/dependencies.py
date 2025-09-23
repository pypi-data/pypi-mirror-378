"""통합 FastAPI 권한 확인 의존성 - JWT 토큰 기반 접근 제어"""

from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN

from mysingle.auth.auth_utils import get_auth_context
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


class EndpointAccessType(str, Enum):
    """엔드포인트 접근 유형 정의"""

    TENANT_ONLY = "tenant_only"  # 테넌트 사용자만 접근 가능
    PLATFORM_ADMIN = "platform_admin"  # 플랫폼 관리자만 접근 가능
    HYBRID = "hybrid"  # 테넌트와 플랫폼 모두 접근 가능
    TENANT_WITH_APPROVAL = (
        "tenant_with_approval"  # 테넌트 소유자 승인 필요 (미래)
    )


# JWT 토큰 추출용 Bearer 스키마
security = HTTPBearer(auto_error=False)

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


async def get_access_context(
    request: Request,
    access_type: EndpointAccessType,
    required_resource: Optional[str] = None,
    required_action: Optional[str] = None,
) -> Dict[str, Any]:
    """
    JWT 토큰을 기반으로 엔드포인트별 접근 컨텍스트를 제공하는 핵심 함수

    Args:
        request: FastAPI Request 객체
        access_type: 엔드포인트 접근 유형 (TENANT_ONLY, PLATFORM_ADMIN, etc.)
        required_resource: 권한 확인이 필요한 경우 리소스명
        required_action: 권한 확인이 필요한 경우 액션명

    Returns:
        Dict containing user_id, tenant_id, is_platform_user, access_type

    Raises:
        HTTPException: 인증 실패, 권한 부족, 접근 불가 등
    """
    # JWT 토큰에서 인증 컨텍스트 추출
    auth_context = get_auth_context(request)
    if not auth_context:
        raise HTTPException(
            status_code=401, detail="JWT token required for authentication"
        )

    user_id = auth_context.user_id
    tenant_id = getattr(auth_context, "tenant_id", None)
    is_platform_user = getattr(auth_context, "is_platform_user", False)

    # 접근 유형별 로직 처리
    if access_type == EndpointAccessType.TENANT_ONLY:
        # 테넌트 사용자만 접근 가능
        if is_platform_user:
            raise HTTPException(
                status_code=403,
                detail="Platform users cannot access tenant-only endpoints",
            )
        if not tenant_id:
            raise HTTPException(
                status_code=400,
                detail="Tenant ID required for tenant-only access",
            )

    elif access_type == EndpointAccessType.PLATFORM_ADMIN:
        # 플랫폼 관리자만 접근 가능
        if not is_platform_user:
            raise HTTPException(
                status_code=403, detail="Platform admin access required"
            )
        # 플랫폼 사용자의 권한 확인
        if required_resource and required_action:
            has_permission = await check_platform_permission(
                user_id=user_id,
                resource=required_resource,
                action=required_action,
            )
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient platform permissions for {required_resource}:{required_action}",
                )

    elif access_type == EndpointAccessType.HYBRID:
        # 테넌트와 플랫폼 모두 접근 가능
        if is_platform_user:
            # 플랫폼 사용자는 추가 권한 확인
            if required_resource and required_action:
                has_permission = await check_platform_permission(
                    user_id=user_id,
                    resource=required_resource,
                    action=required_action,
                )
                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient platform permissions for {required_resource}:{required_action}",
                    )
        else:
            # 테넌트 사용자는 기본 테넌트 권한 확인
            if not tenant_id:
                raise HTTPException(
                    status_code=400,
                    detail="Tenant ID required for tenant user access",
                )

    elif access_type == EndpointAccessType.TENANT_WITH_APPROVAL:
        # TODO: 테넌트 소유자 승인 기반 접근 (미래 구현)
        return await _handle_approval_based_access(
            user_id, tenant_id, is_platform_user
        )

    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "is_platform_user": is_platform_user,
        "access_type": access_type.value,
    }


async def check_platform_permission(
    user_id: str,
    resource: str,
    action: str,
) -> bool:
    """
    플랫폼 사용자의 리소스별 권한을 확인하는 함수

    Args:
        user_id: 플랫폼 사용자 ID
        resource: 접근하려는 리소스 (예: "tenant:management", "ledger:global_view")
        action: 수행하려는 액션 (create, read, update, delete)

    Returns:
        bool: 권한이 있으면 True, 없으면 False
    """
    try:
        client = await get_iam_client_instance()
        permission_result = await client.check_permission(
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=None,  # 플랫폼 레벨 권한은 tenant_id 없음
        )
        return permission_result.allowed
    except Exception as e:
        logger.error(
            f"Platform permission check failed for user {user_id}: {e}"
        )
        return False


async def _handle_approval_based_access(
    user_id: str, tenant_id: Optional[str], is_platform_user: bool
) -> Dict[str, Any]:
    """
    승인 기반 접근 처리 (미래 구현용 스켈레톤)

    TODO: 테넌트 소유자의 승인을 받은 플랫폼 사용자만 접근할 수 있는 로직 구현
    - 승인 요청 생성
    - 승인 상태 확인
    - 승인된 권한 범위 확인
    """
    raise HTTPException(
        status_code=501, detail="Approval-based access not yet implemented"
    )


async def get_current_user(
    request: Request,
) -> UserInfo:
    """현재 인증된 사용자 정보 반환 (JWT 토큰 기반)"""
    auth_context = get_auth_context(request)
    if not auth_context:
        raise HTTPException(
            status_code=401, detail="JWT authentication token required"
        )

    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    auth_token = auth_header.split(" ")[1]

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
    request: Request,
    user_id: str,
    tenant_id: Optional[str] = None,
    resource_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """사용자 권한 목록 조회 (JWT 토큰 기반)"""
    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    auth_token = auth_header.split(" ")[1]

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
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """권한 확인 의존성 (JWT 토큰 기반)"""
    try:
        auth_context = get_auth_context(request)
        if not auth_context:
            raise HTTPException(
                status_code=401, detail="JWT authentication context not found"
            )

        # 테넌트 ID는 JWT 토큰에서 추출
        tenant_id = getattr(auth_context, "tenant_id", None)

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
