"""가드레일 시스템 - JWT 토큰 기반 접근 제어 (EndpointAccessType 중심)"""

from __future__ import annotations

# 감사 로깅 시스템
from .audit.logger import AuditLogger

# 통합된 권한 확인 시스템 (JWT 토큰 기반)
from .auth.dependencies import (
    EndpointAccessType,
    check_permission,
    check_platform_permission,
    create_permission_dependency,
    get_access_context,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_user,
    get_iam_client_instance,
    get_user_permissions,
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
    # 통합 권한 확인 시스템 (JWT 토큰 기반)
    "EndpointAccessType",
    "get_access_context",
    "check_platform_permission",
    "require_permission",
    "check_permission",
    "create_permission_dependency",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_verified_user",
    "get_user_permissions",
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
