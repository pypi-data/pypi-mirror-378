# py_common.rbac - 공용 권한 관리 데코레이터 (순환 import 방지)

# 공용 데코레이터들 (외부에서 자주 사용)
# 공용 예외들
from mysingle.exceptions import (
    PermissionDeniedError,
    RBACCacheError,
    RBACError,
    RBACServiceUnavailableError,
    RBACTimeoutError,
)

from .decorators import (
    audit_log,
    extract_tenant_from_request,
    rate_limit,
    require_permission,
    require_subscription_limit,
)
from .rbac_client import RBACClient, close_global_rbac_client, get_rbac_client

__all__ = [
    # 데코레이터
    "require_permission",
    "require_subscription_limit",
    "extract_tenant_from_request",
    "rate_limit",
    "audit_log",
    # 예외
    "RBACError",
    "PermissionDeniedError",
    "RBACServiceUnavailableError",
    "RBACCacheError",
    "RBACTimeoutError",
    # 클라이언트
    "RBACClient",
    "get_rbac_client",
    "close_global_rbac_client",
]
