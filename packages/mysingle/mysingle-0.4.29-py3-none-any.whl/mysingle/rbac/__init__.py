# RBAC 모듈 - 핵심 컴포넌트

"""
RBAC (Role-Based Access Control) 모듈

개발자가 실제 사용할 핵심 데코레이터만 제공:
- require_permission: 함수 레벨 권한 확인 데코레이터
- audit_log: 감사 로깅 데코레이터

예외 처리는 from mysingle.exceptions import PermissionDeniedError 사용
캐싱은 내부적으로 자동 처리됨
"""

# 개발자가 실제 사용할 데코레이터만 노출
from .decorators import audit_log, require_permission

# 공개 API - 실제 개발에서 사용하는 것만
__all__ = [
    "audit_log",
    "require_permission",
]
