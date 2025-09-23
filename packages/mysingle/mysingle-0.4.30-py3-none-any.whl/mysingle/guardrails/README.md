# MySingle 가드레일 시스템 상세 가이드

MySingle 가드레일 시스템은 FastAPI 애플리케이션을 위한 포괄적인 보안 및 제어 메커니즘을 제공합니다.

## 📦 주요 컴포넌트

### 🔐 권한 확인 (Authentication & Authorization)
- `require_permission()` - FastAPI 의존성 주입 기반 권한 확인
- `check_permission()` - 직접적인 권한 확인
- `get_tenant_id()` - JWT에서 테넌트 ID 추출
- `get_current_user()` - 현재 사용자 정보 조회

### 🚦 Rate Limiting
- `RateLimiter` - 사용자/테넌트별 요청 빈도 제한
- 메모리 기반 및 Redis 지원
- 유연한 설정 (테넌트별 다른 제한)

### 🛡️ PII 보호 (Privacy Protection)
- `PIIMasker` - 개인정보 자동 감지 및 마스킹
- `mask_pii_quick()` - 빠른 PII 마스킹
- 다양한 감지 레벨 (Basic, Advanced, AI)

### 📋 감사 로깅 (Audit Logging)
- `AuditLogger` - 포괄적인 감사 추적
- 접근 로그, Rate limit 로그, PII 감지 로그
- 규정 준수 및 보안 모니터링

## 🚀 빠른 시작

### 기본 설정

```python
from mysingle.guardrails import GuardrailConfig, PIIDetectionLevel

# 모든 가드레일 기능을 위한 통합 설정
config = GuardrailConfig(
    # 권한 확인
    enable_cache=True,
    cache_ttl=300,

    # Rate Limiting
    enable_rate_limiting=True,
    default_rate_limit=1000,  # 시간당 1000회

    # PII 보호
    enable_pii_masking=True,
    pii_detection_level=PIIDetectionLevel.ADVANCED,

    # 감사 로깅
    enable_audit_logging=True,
    audit_sensitive_operations=True,

    # 에러 처리
    fail_open=False,
    timeout_seconds=5.0
)
```

### FastAPI 앱에서 사용

```python
from fastapi import FastAPI, Depends
from mysingle import create_fastapi_app
from mysingle.guardrails import require_permission, get_tenant_id

# 가드레일이 통합된 FastAPI 앱 생성
app = create_fastapi_app(
    title="My Service",
    enable_auth=True,
    public_paths=["/health", "/docs"]
)

@app.post("/protected-resource")
async def create_resource(
    data: dict,
    # 권한 확인 가드레일
    _auth: None = Depends(require_permission("resources", "create")),
    # 테넌트 ID 추출
    tenant_id: str = Depends(get_tenant_id)
):
    return await service.create_resource(data, tenant_id)
```

## 📚 상세 사용법

### 1. 권한 확인 시스템

#### FastAPI 의존성 기반 사용

```python
from mysingle.guardrails import (
    require_permission,
    get_tenant_id,
    get_current_user,
    get_auth_token,
    check_permission
)

@router.post("/journals")
async def create_journal(
    data: JournalCreate,
    # 권한 확인 + 자동 캐싱
    _auth: None = Depends(require_permission("ledger:journals", "create")),
    # 테넌트 ID 추출
    tenant_id: str = Depends(get_tenant_id),
    # 현재 사용자 정보
    current_user = Depends(get_current_user)
):
    return await journal_service.create(data, tenant_id, current_user.id)

@router.get("/admin/reports")
async def get_admin_reports(
    # 관리자 권한 확인
    _auth: None = Depends(require_permission("admin:reports", "read")),
    auth_token: str = Depends(get_auth_token)
):
    # JWT 토큰을 다른 서비스로 전달
    return await external_service.get_reports(auth_token)
```

#### 직접 권한 확인

```python
from mysingle.guardrails import check_permission

async def business_logic(user_id: str, tenant_id: str, action: str):
    # 조건부 권한 확인
    if action == "delete":
        has_permission = await check_permission(
            user_id=user_id,
            resource="sensitive:data",
            action="delete",
            tenant_id=tenant_id
        )
        if not has_permission:
            raise HTTPException(403, "삭제 권한이 없습니다")

    # 비즈니스 로직 실행
    return await perform_action(action)
```

### 2. Rate Limiting 시스템

#### 기본 Rate Limiting

```python
from mysingle.guardrails import RateLimiter, GuardrailConfig

# Rate Limiter 설정
config = GuardrailConfig(
    enable_rate_limiting=True,
    default_rate_limit=1000,  # 기본: 시간당 1000회
    tenant_rate_limit={
        "premium_tenant": 5000,  # 프리미엄: 시간당 5000회
        "basic_tenant": 500,     # 기본: 시간당 500회
        "trial_tenant": 100      # 평가판: 시간당 100회
    }
)

limiter = RateLimiter(config)

# FastAPI 의존성으로 사용
async def rate_limit_dependency(request: Request):
    auth_context = get_auth_context(request)  # 인증 컨텍스트 추출

    allowed = await limiter.check_rate_limit(
        user_id=auth_context.user_id,
        tenant_id=auth_context.tenant_id,
        endpoint=str(request.url.path)
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

@router.post("/api/expensive-operation")
async def expensive_operation(
    data: dict,
    _rate_limit: None = Depends(rate_limit_dependency)
):
    return await perform_expensive_operation(data)
```

#### Rate Limit 모니터링

```python
# Rate limit 정보 조회
@router.get("/api/rate-limit-status")
async def get_rate_limit_status(
    request: Request,
    current_user = Depends(get_current_user)
):
    rate_info = await limiter.get_rate_info(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        endpoint="/api/expensive-operation"
    )

    return {
        "current_usage": rate_info["current_count"],
        "limit": rate_info["limit"],
        "remaining": rate_info["remaining"],
        "reset_time": rate_info["window_start"] + 3600  # 1시간 후 리셋
    }

# 관리자 기능: Rate limit 리셋
@router.post("/admin/reset-rate-limit")
async def reset_user_rate_limit(
    user_id: str,
    tenant_id: str,
    endpoint: str,
    _auth: None = Depends(require_permission("admin:rate-limits", "manage"))
):
    await limiter.reset_rate_limit(user_id, tenant_id, endpoint)
    return {"message": f"Rate limit reset for user {user_id}"}
```

### 3. PII 보호 시스템

#### 빠른 PII 마스킹

```python
from mysingle.guardrails import mask_pii_quick

def process_user_input(text: str) -> str:
    """사용자 입력에서 PII 자동 마스킹"""
    return mask_pii_quick(text, level="advanced")

# 사용 예시
original = "홍길동의 이메일은 hong@example.com이고 전화번호는 010-1234-5678입니다"
masked = mask_pii_quick(original)
print(masked)
# 출력: "홍길동의 이메일은 [EMAIL]이고 전화번호는 [PHONE_KR]입니다"

# 주민번호, 카드번호 등도 자동 감지
sensitive_data = "주민번호: 123456-1234567, 카드번호: 1234-5678-9012-3456"
safe_data = mask_pii_quick(sensitive_data)
print(safe_data)
# 출력: "주민번호: [SSN_KR], 카드번호: [CREDIT_CARD]"
```

#### 고급 PII 마스킹

```python
from mysingle.guardrails import PIIMasker, GuardrailConfig, PIIDetectionLevel

# 세밀한 제어를 위한 PII 마스커 설정
config = GuardrailConfig(
    enable_pii_masking=True,
    pii_detection_level=PIIDetectionLevel.ADVANCED
)

masker = PIIMasker(config)

# 전체 PII 마스킹
text = "고객 정보: 이름 김철수, 이메일 kim@example.com, 전화 010-9876-5432"
masked = masker.mask_pii(text)
print(masked)
# 출력: "고객 정보: 이름 김철수, 이메일 [EMAIL], 전화 [PHONE_KR]"

# 특정 PII 타입만 마스킹
email_only = masker.mask_specific_pii(
    "연락처: hong@test.com, 010-1111-2222",
    pattern_names=["email"]
)
print(email_only)
# 출력: "연락처: [EMAIL], 010-1111-2222"

# PII 감지 (마스킹 없이 타입만 확인)
detected = masker.detect_pii_types("test@example.com 010-1234-5678")
print(detected)
# 출력: ['email', 'phone_kr']

# 지원되는 PII 패턴 확인
patterns = masker.get_supported_patterns()
print(patterns)
# 출력: ['email', 'phone_kr', 'ssn_kr', 'credit_card', 'ip_address', ...]
```

#### 실시간 PII 보호 미들웨어

```python
from fastapi import Request, Response
from mysingle.guardrails import get_pii_masker

async def pii_protection_middleware(request: Request, call_next):
    """응답에서 PII 자동 마스킹"""
    response = await call_next(request)

    # 민감한 엔드포인트에서만 PII 마스킹 적용
    sensitive_paths = ["/api/users", "/api/customers", "/api/reports"]

    if any(path in str(request.url.path) for path in sensitive_paths):
        if hasattr(response, 'body') and response.body:
            try:
                # JSON 응답 파싱
                import json
                data = json.loads(response.body.decode())

                # 텍스트 필드에서 PII 마스킹
                masked_data = mask_json_pii(data)

                # 마스킹된 데이터로 응답 업데이트
                masked_body = json.dumps(masked_data).encode()
                response.body = masked_body
                response.headers["content-length"] = str(len(masked_body))

            except (json.JSONDecodeError, UnicodeDecodeError):
                # JSON이 아닌 경우 텍스트로 처리
                text_data = response.body.decode()
                masked_text = mask_pii_quick(text_data)
                response.body = masked_text.encode()

    return response

def mask_json_pii(data):
    """JSON 데이터에서 PII 마스킹"""
    if isinstance(data, dict):
        return {k: mask_json_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_json_pii(item) for item in data]
    elif isinstance(data, str):
        return mask_pii_quick(data)
    return data

# FastAPI 앱에 미들웨어 추가
app.middleware("http")(pii_protection_middleware)
```

### 4. 감사 로깅 시스템

#### 기본 감사 로깅

```python
from mysingle.guardrails import AuditLogger, GuardrailConfig

config = GuardrailConfig(
    enable_audit_logging=True,
    audit_sensitive_operations=True
)

audit_logger = AuditLogger(config)

# 접근 로그 기록
async def log_api_access(request: Request, allowed: bool, user_id: str, resource: str, action: str):
    await audit_logger.log_access(
        user_id=user_id,
        resource=resource,
        action=action,
        allowed=allowed,
        tenant_id=get_tenant_from_request(request),
        reason="Permission check completed",
        context={
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        }
    )

# Rate limit 이벤트 로그
async def log_rate_limit_event(user_id: str, tenant_id: str, endpoint: str, exceeded: bool):
    rate_info = await limiter.get_rate_info(user_id, tenant_id, endpoint)

    await audit_logger.log_rate_limit(
        user_id=user_id,
        tenant_id=tenant_id,
        endpoint=endpoint,
        limit_exceeded=exceeded,
        current_count=rate_info["current_count"],
        limit=rate_info["limit"]
    )

# PII 감지 로그
async def log_pii_detection(user_id: str, tenant_id: str, text: str, detected_types: list):
    await audit_logger.log_pii_detection(
        user_id=user_id,
        tenant_id=tenant_id,
        detected_types=detected_types,
        text_length=len(text),
        masked_length=len(mask_pii_quick(text)),
        context={
            "detection_level": "advanced",
            "patterns_found": len(detected_types)
        }
    )
```

#### 통합 감사 미들웨어

```python
async def comprehensive_audit_middleware(request: Request, call_next):
    """포괄적인 감사 로깅 미들웨어"""
    start_time = time.time()

    # 요청 정보 추출
    user_id = None
    tenant_id = None

    try:
        auth_context = get_auth_context(request)
        user_id = auth_context.user_id
        tenant_id = auth_context.tenant_id
    except:
        pass  # 인증되지 않은 요청

    # 응답 처리
    response = await call_next(request)

    # 응답 시간 계산
    process_time = time.time() - start_time

    # 감사 로그 기록
    if user_id:  # 인증된 요청만 로깅
        await audit_logger.log_access(
            user_id=user_id,
            resource=f"{request.method}:{request.url.path}",
            action="api_call",
            allowed=response.status_code < 400,
            tenant_id=tenant_id,
            reason=f"HTTP {response.status_code}",
            context={
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "response_time_ms": process_time * 1000,
                "status_code": response.status_code,
                "content_length": response.headers.get("content-length", 0)
            }
        )

    return response

# FastAPI 앱에 감사 미들웨어 추가
app.middleware("http")(comprehensive_audit_middleware)
```

## 🔧 고급 설정

### 커스텀 가드레일 설정

```python
from mysingle.guardrails import GuardrailConfig, PIIDetectionLevel

# 프로덕션 환경용 설정
production_config = GuardrailConfig(
    # 보안 중심 설정
    enable_cache=True,
    cache_ttl=600,  # 10분 캐시

    # 엄격한 Rate Limiting
    enable_rate_limiting=True,
    default_rate_limit=500,  # 보수적인 제한
    tenant_rate_limit={
        "enterprise": 10000,
        "professional": 2000,
        "basic": 500,
        "trial": 50
    },

    # 고급 PII 보호
    enable_pii_masking=True,
    pii_detection_level=PIIDetectionLevel.ADVANCED,

    # 포괄적인 감사 로깅
    enable_audit_logging=True,
    audit_sensitive_operations=True,

    # 보안 우선 에러 처리
    fail_open=False,  # 권한 확인 실패 시 접근 거부
    timeout_seconds=3.0  # 빠른 타임아웃
)

# 개발 환경용 설정
development_config = GuardrailConfig(
    # 개발 편의성 중심
    enable_cache=True,
    cache_ttl=60,  # 1분 캐시

    # 관대한 Rate Limiting
    enable_rate_limiting=False,  # 개발 중에는 비활성화
    default_rate_limit=10000,

    # 기본 PII 보호
    enable_pii_masking=True,
    pii_detection_level=PIIDetectionLevel.BASIC,

    # 최소한의 감사 로깅
    enable_audit_logging=True,
    audit_sensitive_operations=False,

    # 개발 친화적 에러 처리
    fail_open=True,  # 권한 확인 실패 시에도 접근 허용
    timeout_seconds=10.0  # 여유로운 타임아웃
)
```

### 환경별 가드레일 초기화

```python
import os
from mysingle.guardrails import GuardrailConfig

def get_guardrail_config() -> GuardrailConfig:
    """환경에 따른 가드레일 설정 반환"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return GuardrailConfig(
            enable_rate_limiting=True,
            default_rate_limit=int(os.getenv("DEFAULT_RATE_LIMIT", "1000")),
            enable_pii_masking=True,
            pii_detection_level=os.getenv("PII_DETECTION_LEVEL", "advanced"),
            enable_audit_logging=True,
            fail_open=False
        )
    elif env == "staging":
        return GuardrailConfig(
            enable_rate_limiting=True,
            default_rate_limit=5000,
            enable_pii_masking=True,
            pii_detection_level="advanced",
            enable_audit_logging=True,
            fail_open=False
        )
    else:  # development
        return GuardrailConfig(
            enable_rate_limiting=False,
            enable_pii_masking=True,
            pii_detection_level="basic",
            enable_audit_logging=False,
            fail_open=True
        )

# 환경별 설정으로 컴포넌트 초기화
config = get_guardrail_config()
rate_limiter = RateLimiter(config)
pii_masker = PIIMasker(config)
audit_logger = AuditLogger(config)
```

## 🧪 테스트

### 가드레일 테스트 예제

```python
import pytest
from fastapi.testclient import TestClient
from mysingle.guardrails import require_permission, mask_pii_quick, RateLimiter

def test_permission_dependency():
    """권한 확인 의존성 테스트"""

    @app.post("/test-endpoint")
    async def test_endpoint(
        _auth: None = Depends(require_permission("test:resource", "read"))
    ):
        return {"message": "success"}

    client = TestClient(app)

    # 유효한 토큰으로 테스트
    headers = {"Authorization": "Bearer valid_token"}
    response = client.post("/test-endpoint", headers=headers)
    assert response.status_code == 200

    # 무효한 토큰으로 테스트
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/test-endpoint", headers=headers)
    assert response.status_code == 403

def test_pii_masking():
    """PII 마스킹 테스트"""

    # 이메일 마스킹 테스트
    text = "연락처: hong@example.com"
    masked = mask_pii_quick(text)
    assert "[EMAIL]" in masked
    assert "hong@example.com" not in masked

    # 전화번호 마스킹 테스트
    text = "전화번호: 010-1234-5678"
    masked = mask_pii_quick(text)
    assert "[PHONE_KR]" in masked
    assert "010-1234-5678" not in masked

@pytest.mark.asyncio
async def test_rate_limiting():
    """Rate Limiting 테스트"""
    from mysingle.guardrails import GuardrailConfig

    config = GuardrailConfig(
        enable_rate_limiting=True,
        default_rate_limit=2  # 테스트용 낮은 제한
    )

    limiter = RateLimiter(config)

    # 첫 번째 요청 - 허용
    allowed = await limiter.check_rate_limit("test_user", "test_tenant", "test_endpoint")
    assert allowed is True

    # 두 번째 요청 - 허용
    allowed = await limiter.check_rate_limit("test_user", "test_tenant", "test_endpoint")
    assert allowed is True

    # 세 번째 요청 - 차단
    allowed = await limiter.check_rate_limit("test_user", "test_tenant", "test_endpoint")
    assert allowed is False
```

## 🔍 모니터링 및 관리

### 가드레일 상태 모니터링

```python
@router.get("/admin/guardrails/status")
async def get_guardrails_status(
    _auth: None = Depends(require_permission("admin:monitoring", "read"))
):
    """가드레일 시스템 상태 조회"""

    # Rate Limiter 통계
    rate_stats = limiter.get_store_stats()

    # PII 마스커 통계
    pii_patterns = masker.get_supported_patterns()

    # 감사 로그 통계 (구현 필요)
    # audit_stats = audit_logger.get_stats()

    return {
        "rate_limiting": {
            "enabled": config.enable_rate_limiting,
            "active_users": rate_stats.get("active_users", 0),
            "total_requests": rate_stats.get("total_requests", 0),
            "blocked_requests": rate_stats.get("blocked_requests", 0)
        },
        "pii_protection": {
            "enabled": config.enable_pii_masking,
            "detection_level": config.pii_detection_level,
            "supported_patterns": len(pii_patterns),
            "pattern_types": pii_patterns
        },
        "audit_logging": {
            "enabled": config.enable_audit_logging,
            "sensitive_operations": config.audit_sensitive_operations
        }
    }

@router.post("/admin/guardrails/cleanup")
async def cleanup_guardrails(
    _auth: None = Depends(require_permission("admin:maintenance", "execute"))
):
    """가드레일 시스템 정리"""

    # 만료된 Rate Limit 정보 정리
    limiter.cleanup_expired()

    # 기타 정리 작업...

    return {"message": "Guardrails cleanup completed"}
```

## 📝 모범 사례

### 1. 레이어드 보안 접근
```python
# 여러 가드레일을 조합하여 다층 보안 구현
@router.post("/sensitive-operation")
async def sensitive_operation(
    data: SensitiveData,
    # 1차: 인증 및 권한 확인
    _auth: None = Depends(require_permission("sensitive:ops", "execute")),
    # 2차: 테넌트 격리
    tenant_id: str = Depends(get_tenant_id),
    # 3차: Rate Limiting
    _rate: None = Depends(rate_limit_dependency),
    # 4차: 현재 사용자 검증
    current_user = Depends(get_current_user)
):
    # 5차: 입력 데이터 PII 보호
    safe_data = mask_pii_quick(str(data))

    # 6차: 추가 비즈니스 로직 검증
    if not await additional_security_check(current_user, data):
        raise HTTPException(403, "Additional security check failed")

    return await perform_sensitive_operation(safe_data, tenant_id)
```

### 2. 성능 고려사항
```python
# 캐싱을 활용한 성능 최적화
config = GuardrailConfig(
    enable_cache=True,
    cache_ttl=300,  # 5분 캐시
    timeout_seconds=3.0  # 빠른 타임아웃
)

# 무거운 작업은 비동기로 처리
async def log_audit_async(audit_data):
    """감사 로그를 비동기로 처리"""
    # 메인 요청을 차단하지 않고 백그라운드에서 로깅
    asyncio.create_task(audit_logger.log_access(**audit_data))
```

### 3. 오류 처리 전략
```python
from mysingle.exceptions import PermissionDeniedError, RBACTimeoutError

async def robust_permission_check(user_id: str, resource: str, action: str):
    """견고한 권한 확인 구현"""
    try:
        return await check_permission(user_id, resource, action)
    except RBACTimeoutError:
        # 타임아웃 시 캐시된 결과 사용 또는 안전한 기본값
        logger.warning(f"Permission check timeout for {user_id}, falling back to cache")
        return await get_cached_permission(user_id, resource, action)
    except Exception as e:
        # 예상치 못한 오류 시 안전한 기본 동작
        logger.error(f"Permission check error: {e}")
        if config.fail_open:
            return True  # 개발 환경에서는 허용
        else:
            return False  # 프로덕션에서는 거부
```

이 가이드는 MySingle 가드레일 시스템의 모든 기능을 다루며, 실제 프로덕션 환경에서 활용할 수 있는 구체적인 예제들을 제공합니다.
