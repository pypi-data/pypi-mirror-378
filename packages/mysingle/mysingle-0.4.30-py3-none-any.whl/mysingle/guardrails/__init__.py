"""가드레일 시스템 - 모듈형 아키텍처 (통합 RBAC 중심)"""

from __future__ import annotations

# 감사 로깅 시스템
from .audit.logger import AuditLogger

# 통합된 권한 확인 시스템 (가드레일 중심)
from .auth.dependencies import (
    check_permission,
    create_permission_dependency,
    get_auth_token,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_user,
    get_iam_client_instance,
    get_tenant_id,
    get_user_dependency,
    get_user_permissions,
    get_user_permissions_dependency,
    require_permission,
)
from .core.base import BaseGuardrail

# Core 구성 요소만 자동 노출 (순환 참조 없음)
from .core.config import GuardrailConfig, GuardrailMode, PIIDetectionLevel

# PII 보호 시스템
from .privacy.pii_masker import PIIMasker, get_pii_masker, mask_pii_quick

# Rate Limiting 시스템
from .rate_limiting.limiter import RateLimiter

__all__ = [
    # Core (순환 참조 없음)
    "GuardrailConfig",
    "PIIDetectionLevel",
    "GuardrailMode",
    "BaseGuardrail",
    # 통합 권한 확인 시스템 (가드레일 중심)
    "require_permission",
    "check_permission",
    "create_permission_dependency",
    "get_tenant_id",
    "get_auth_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_verified_user",
    "get_user_permissions",
    "get_user_dependency",
    "get_user_permissions_dependency",
    "get_iam_client_instance",
    # PII 보호
    "PIIMasker",
    "get_pii_masker",
    "mask_pii_quick",
    # Rate Limiting
    "RateLimiter",
    # 감사 로깅
    "AuditLogger",
]
