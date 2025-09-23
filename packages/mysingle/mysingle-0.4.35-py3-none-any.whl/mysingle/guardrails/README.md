# MySingle 가드레일 시스템 - JWT 기반 접근 제어

MySingle 가드레일 시스템은 **JWT 토큰 기반 EndpointAccessType 패턴**을 통해 FastAPI 애플리케이션에 엔터프라이즈급 보안 및 접근 제어를 제공합니다.

## 🆕 2025.09.23 주요 업데이트

- ✅ **JWT 토큰 기반 시스템으로 완전 전환** (헤더 기반 제거)
- ✅ **EndpointAccessType 도입** - 정교한 접근 제어 패턴
- ✅ **플랫폼 사용자 지원** - 멀티테넌트 환경에서 관리자 접근
- ✅ **통합된 접근 컨텍스트** - 하나의 함수로 모든 접근 제어

## 🎯 EndpointAccessType 패턴

### 접근 제어 타입

```python
from mysingle.guardrails import EndpointAccessType

# 1. 테넌트 전용 접근 (가장 일반적)
EndpointAccessType.TENANT_ONLY

# 2. 플랫폼 관리자 전용
EndpointAccessType.PLATFORM_ADMIN

# 3. 하이브리드 접근 (테넌트 + 플랫폼 관리자)
EndpointAccessType.HYBRID

# 4. 승인 기반 접근 (향후 확장)
EndpointAccessType.TENANT_WITH_APPROVAL
```

### 핵심 함수: `get_access_context`

모든 접근 제어 로직이 통합된 단일 함수:

```python
from mysingle.guardrails import get_access_context, EndpointAccessType
from fastapi import Depends

async def my_endpoint(
    context = Depends(get_access_context(EndpointAccessType.TENANT_ONLY))
):
    # context.user_id: 사용자 ID (항상 존재)
    # context.tenant_id: 테넌트 ID (TENANT_ONLY에서는 항상 존재)
    # context.is_platform_user: 플랫폼 사용자 여부

    return {"user": context.user_id, "tenant": context.tenant_id}
```

## � 실제 사용 예제

### 1. 테넌트 전용 엔드포인트 (가장 일반적)

```python
from fastapi import APIRouter, Depends
from mysingle.guardrails import get_access_context, EndpointAccessType

router = APIRouter()

@router.get("/journals")
async def list_journals(
    context = Depends(get_access_context(EndpointAccessType.TENANT_ONLY))
):
    """테넌트의 분개 목록 조회 - 테넌트 사용자만 접근 가능"""
    return await get_tenant_journals(context.tenant_id)

@router.post("/journals")
async def create_journal(
    journal_data: JournalCreate,
    context = Depends(get_access_context(EndpointAccessType.TENANT_ONLY))
):
    """분개 생성 - 테넌트 격리 보장"""
    return await create_journal_for_tenant(
        context.tenant_id,
        context.user_id,
        journal_data
    )
```

### 2. 플랫폼 관리자 전용 엔드포인트

```python
@router.get("/admin/tenants")
async def list_all_tenants(
    context = Depends(get_access_context(EndpointAccessType.PLATFORM_ADMIN))
):
    """모든 테넌트 조회 - 플랫폼 관리자만 접근"""
    # context.is_platform_user == True 보장
    return await get_all_tenants()

@router.delete("/admin/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    context = Depends(get_access_context(EndpointAccessType.PLATFORM_ADMIN))
):
    """테넌트 삭제 - 플랫폼 관리자 권한 필요"""
    return await delete_tenant_by_id(tenant_id)
```

### 3. 하이브리드 접근 엔드포인트

```python
@router.get("/reports/analytics")
async def get_analytics(
    tenant_id: str = None,  # 플랫폼 관리자는 특정 테넌트 지정 가능
    context = Depends(get_access_context(EndpointAccessType.HYBRID))
):
    """분석 보고서 조회 - 테넌트 사용자는 자신만, 플랫폼 관리자는 모든 테넌트"""

    if context.is_platform_user:
        # 플랫폼 관리자: tenant_id 매개변수로 지정 가능
        target_tenant = tenant_id or "all"
    else:
        # 테넌트 사용자: 자신의 테넌트만
        target_tenant = context.tenant_id

    return await get_analytics_report(target_tenant)
```

## 🏭 CRUD Factory 통합

CRUD Factory도 EndpointAccessType을 지원합니다:

```python
from mysingle import create_crud_router
from mysingle.guardrails import EndpointAccessType

# 테넌트 전용 CRUD (가장 일반적)
user_router = create_crud_router(
    service=user_service,
    access_type=EndpointAccessType.TENANT_ONLY
)

# 플랫폼 관리자 전용 CRUD
admin_router = create_crud_router(
    service=admin_service,
    access_type=EndpointAccessType.PLATFORM_ADMIN
)

# 하이브리드 CRUD
report_router = create_crud_router(
    service=report_service,
    access_type=EndpointAccessType.HYBRID
)
```

## � 개별 함수 사용

### 플랫폼 권한 확인

```python
from mysingle.guardrails import check_platform_permission

# 플랫폼 사용자의 특정 테넌트 접근 권한 확인
can_access = await check_platform_permission(
    user_id="platform_admin_123",
    tenant_id="tenant_456"
)
```

### 직접 권한 확인

```python
from mysingle.guardrails import check_permission

# 사용자의 특정 리소스 접근 권한 확인
has_permission = await check_permission(
    user_id="user123",
    resource="journals",
    action="read",
    tenant_id="tenant456"
)
```

### 권한 의존성 생성

```python
from mysingle.guardrails import create_permission_dependency

# 특정 권한이 필요한 의존성 생성
require_journal_write = create_permission_dependency(
    resource="journals",
    action="write"
)

@router.post("/journals")
async def create_journal(
    data: JournalCreate,
    context = Depends(require_journal_write)
):
    # 'journals:write' 권한이 있는 사용자만 접근 가능
    pass
```

## 🔒 기존 RBAC 데코레이터 호환성

기존 함수 레벨 권한 확인도 JWT 기반으로 업데이트되었습니다:

```python
from mysingle.rbac import require_permission, audit_log

@require_permission("journals", "create")
@audit_log("create", "journals")
async def create_journal_logic(request: Request, data: JournalCreate):
    """일반 함수에서 권한 확인 (FastAPI 엔드포인트가 아닌 경우)"""
    # JWT 토큰에서 자동으로 사용자/테넌트 정보 추출
    # 권한 확인 후 감사 로그 자동 기록
    pass
```

## 🛡️ 보안 기능

### 1. PII 보호

```python
from mysingle.guardrails import mask_pii_quick

# 민감한 정보 자동 마스킹
safe_data = mask_pii_quick("홍길동의 전화번호는 010-1234-5678입니다")
# 결과: "홍길동의 전화번호는 ***-****-****입니다"
```

### 2. Rate Limiting

```python
from mysingle.guardrails import RateLimiter

rate_limiter = RateLimiter(
    default_limit=100,  # 분당 요청 수
    tenant_limits={"premium_tenant": 1000}
)

@router.get("/api/data")
async def get_data(
    context = Depends(get_access_context(EndpointAccessType.TENANT_ONLY))
):
    # Rate limit 확인
    if not await rate_limiter.check_rate_limit(
        user_id=context.user_id,
        tenant_id=context.tenant_id
    ):
        raise HTTPException(429, "Rate limit exceeded")

    return {"data": "..."}
```

### 3. 감사 로깅

```python
from mysingle.guardrails import AuditLogger

audit_logger = AuditLogger(config)

# 접근 로그 기록
await audit_logger.log_access(
    user_id="user123",
    resource="journals",
    action="read",
    allowed=True,
    tenant_id="tenant456"
