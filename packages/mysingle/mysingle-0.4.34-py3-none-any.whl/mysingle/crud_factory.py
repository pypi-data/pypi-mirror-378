"""
CRUD Factory 모듈 - 재사용 가능한 CRUD 작업을 위한 팩토리 클래스

이 모듈은 다음 기능을 제공합니다:
1. 공통 CRUD 패턴 추상화
2. RBAC 권한 확인 자동화
3. EndpointAccessType 기반 접근 제어 (JWT 토큰 기반)
4. 에러 처리 표준화

주요 특징 (2025.09.23 개선):
- JWT 토큰 기반 접근 제어
- EndpointAccessType을 통한 엔드포인트별 접근 유형 지정
- 플랫폼 사용자와 테넌트 사용자 통합 지원
- 기존 헤더 방식 완전 제거
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from mysingle.base import BaseDoc, BaseResponseSchema
from mysingle.guardrails.auth.dependencies import (
    EndpointAccessType,
    get_access_context,
    require_permission,
)
from mysingle.iam.client import UnifiedIAMClient
from mysingle.logging import get_logger
from mysingle.rbac.decorators import audit_log

logger = get_logger(__name__)


def get_effective_tenant_id(
    tenant_id: Optional[str], is_platform: bool
) -> str:
    """플랫폼 사용자와 테넌트 사용자에 따라 effective tenant_id 반환"""
    if is_platform:
        return "platform"
    elif tenant_id:
        return tenant_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required for non-platform users",
        )


class BaseCRUDService:
    """기본 CRUD 서비스 클래스"""

    def __init__(
        self,
        model: Type[BaseDoc],
        resource_name: str,
        service_prefix: str = "ledger",
        iam_client: Optional[UnifiedIAMClient] = None,
    ):
        self.model = model
        self.resource_name = resource_name
        self.service_prefix = service_prefix
        self.iam_client = iam_client or UnifiedIAMClient()

    async def create(
        self,
        data: Dict[str, Any],
        tenant_id: Optional[str],
        user_id: Optional[str] = None,
        is_platform: bool = False,
    ) -> BaseDoc:
        """리소스 생성"""
        try:
            # effective tenant_id 결정
            effective_tenant_id = get_effective_tenant_id(
                tenant_id, is_platform
            )

            # 권한 확인
            if user_id:
                # 플랫폼 사용자의 경우 platform 도메인, 일반 사용자는 tenant 도메인
                domain = "platform" if is_platform else effective_tenant_id
                result = await self.iam_client.check_permission(
                    user_id=user_id,
                    tenant_id=domain,
                    resource=self.resource_name,
                    action="create",
                )
                if not result.allowed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied for creating {self.resource_name}",
                    )

            # 기본 메타데이터 추가
            # 플랫폼 사용자가 아닌 경우에만 tenant_id 설정
            if not is_platform:
                data["tenant_id"] = effective_tenant_id
            data["created_at"] = datetime.now(timezone.utc)
            data["updated_at"] = None
            data["idempotency_key"] = None

            # 모델 생성 및 저장
            instance = self.model(**data)
            await instance.insert()

            # 로깅
            logger.info(
                f"Created {self.resource_name}: {instance.id} for domain: {effective_tenant_id}"
            )

            return instance

        except Exception as e:
            logger.error(f"Failed to create {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create {self.resource_name}",
            )

    async def list(
        self,
        tenant_id: Optional[str],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0,
        is_platform: bool = False,
    ) -> List[BaseDoc]:
        """리소스 목록 조회"""
        try:
            # 기본 쿼리 구성
            query = {}

            # 플랫폼 사용자가 아닌 경우에만 tenant_id 필터링
            if not is_platform and tenant_id:
                query["tenant_id"] = tenant_id
            elif not is_platform:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant ID is required for non-platform users",
                )

            if filters:
                query.update(filters)

            # 데이터 조회
            items = (
                await self.model.find(query).skip(skip).limit(limit).to_list()
            )
            return items

        except Exception as e:
            logger.error(f"Failed to list {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list {self.resource_name}",
            )

    async def get(
        self,
        item_id: str,
        tenant_id: Optional[str],
        is_platform: bool = False,
    ) -> BaseDoc:
        """리소스 단건 조회"""
        try:
            item = await self.model.get(item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 플랫폼 사용자가 아닌 경우에만 tenant_id 확인
            if (
                not is_platform
                and hasattr(item, "tenant_id")
                and item.tenant_id != tenant_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            return item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get {self.resource_name}",
            )

    async def update(
        self,
        item_id: str,
        data: Dict[str, Any],
        tenant_id: Optional[str],
        user_id: Optional[str] = None,
        is_platform: bool = False,
    ) -> BaseDoc:
        """리소스 업데이트"""
        try:
            # 기존 항목 조회
            item = await self.model.get(item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 플랫폼 사용자가 아닌 경우에만 tenant_id 확인
            if (
                not is_platform
                and hasattr(item, "tenant_id")
                and item.tenant_id != tenant_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 업데이트 데이터 준비
            data["updated_at"] = datetime.now(timezone.utc)

            # 업데이트 실행
            await item.set(data)
            await item.save()

            # 로깅
            effective_tenant_id = get_effective_tenant_id(
                tenant_id, is_platform
            )
            logger.info(
                f"Updated {self.resource_name}: {item_id} for domain: {effective_tenant_id}"
            )

            return item

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update {self.resource_name}",
            )

    async def delete(
        self,
        item_id: str,
        tenant_id: Optional[str],
        user_id: Optional[str] = None,
        is_platform: bool = False,
    ) -> None:
        """리소스 삭제"""
        try:
            # 기존 항목 조회
            item = await self.model.get(item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 플랫폼 사용자가 아닌 경우에만 tenant_id 확인
            if (
                not is_platform
                and hasattr(item, "tenant_id")
                and item.tenant_id != tenant_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.resource_name} not found",
                )

            # 삭제 실행
            await item.delete()

            # 로깅
            effective_tenant_id = get_effective_tenant_id(
                tenant_id, is_platform
            )
            logger.info(
                f"Deleted {self.resource_name}: {item_id} for domain: {effective_tenant_id}"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete {self.resource_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete {self.resource_name}",
            )


def create_crud_router(
    service: BaseCRUDService,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    response_schema: Type[BaseResponseSchema],
    prefix: str = "",
    include_operations: Optional[List[str]] = None,
    access_type: EndpointAccessType = EndpointAccessType.TENANT_ONLY,
) -> APIRouter:
    """
    CRUD 라우터 생성 함수 (EndpointAccessType 기반)

    Args:
        service: CRUD 서비스 인스턴스
        create_schema: 생성 스키마 클래스
        update_schema: 업데이트 스키마 클래스
        response_schema: 응답 스키마 클래스
        prefix: 라우터 URL 접두사
        include_operations: 포함할 작업 목록 (기본: 모든 작업)
        access_type: 엔드포인트 접근 유형 (TENANT_ONLY, PLATFORM_ADMIN, HYBRID 등)

    Returns:
        구성된 APIRouter 인스턴스
    """
    router = APIRouter(prefix=prefix)

    operations = include_operations or [
        "create",
        "list",
        "get",
        "update",
        "delete",
    ]

    # 접근 컨텍스트를 가져오는 의존성 함수 생성
    async def get_crud_access_context(request: Request) -> Dict[str, Any]:
        """CRUD 작업을 위한 접근 컨텍스트 의존성"""
        return await get_access_context(
            request=request,
            access_type=access_type,
            required_resource=f"{service.service_prefix}:{service.resource_name}",
        )

    # CREATE 엔드포인트
    if "create" in operations:

        @router.post(
            "",
            status_code=status.HTTP_201_CREATED,
            response_model=response_schema,
        )
        @audit_log("create", service.resource_name)
        async def create_item(
            data: create_schema,  # type: ignore
            access_ctx: Dict[str, Any] = Depends(get_crud_access_context),
            _auth: None = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "create",
                )
            ),
        ):
            # JWT 토큰 기반 접근 컨텍스트 사용
            result = await service.create(
                data.model_dump(),  # type: ignore
                tenant_id=access_ctx.get("tenant_id"),
                user_id=access_ctx["user_id"],
                is_platform=access_ctx["is_platform_user"],
            )
            return response_schema.model_validate(result, from_attributes=True)

    # LIST 엔드포인트
    if "list" in operations:

        @router.get(
            "",
            response_model=List[response_schema],  # type: ignore
        )
        @audit_log("list", service.resource_name)
        async def list_items(
            limit: int = 100,
            skip: int = 0,
            access_ctx: Dict[str, Any] = Depends(get_crud_access_context),
            _auth: None = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}", "read"
                )
            ),
        ):
            # JWT 토큰 기반 접근 컨텍스트 사용
            results = await service.list(
                tenant_id=access_ctx.get("tenant_id"),
                limit=limit,
                skip=skip,
                is_platform=access_ctx["is_platform_user"],
            )
            return [
                response_schema.model_validate(item, from_attributes=True)
                for item in results
            ]

    # GET 엔드포인트
    if "get" in operations:

        @router.get(
            "/{item_id}",
            response_model=response_schema,
        )
        @audit_log("get", service.resource_name)
        async def get_item(
            item_id: str,
            access_ctx: Dict[str, Any] = Depends(get_crud_access_context),
            _auth: None = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}", "read"
                )
            ),
        ):
            # JWT 토큰 기반 접근 컨텍스트 사용
            result = await service.get(
                item_id,
                tenant_id=access_ctx.get("tenant_id"),
                is_platform=access_ctx["is_platform_user"],
            )
            return response_schema.model_validate(result, from_attributes=True)

    # UPDATE 엔드포인트
    if "update" in operations:

        @router.put(
            "/{item_id}",
            response_model=response_schema,
        )
        @audit_log("update", service.resource_name)
        async def update_item(
            item_id: str,
            data: update_schema,  # type: ignore
            access_ctx: Dict[str, Any] = Depends(get_crud_access_context),
            _auth: None = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "update",
                )
            ),
        ):
            # JWT 토큰 기반 접근 컨텍스트 사용
            result = await service.update(
                item_id,
                data.model_dump(exclude_unset=True),  # type: ignore
                tenant_id=access_ctx.get("tenant_id"),
                user_id=access_ctx["user_id"],
                is_platform=access_ctx["is_platform_user"],
            )
            return response_schema.model_validate(result, from_attributes=True)

    # DELETE 엔드포인트
    if "delete" in operations:

        @router.delete(
            "/{item_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        @audit_log("delete", service.resource_name)
        async def delete_item(
            item_id: str,
            access_ctx: Dict[str, Any] = Depends(get_crud_access_context),
            _auth: None = Depends(
                require_permission(
                    f"{service.service_prefix}:{service.resource_name}",
                    "delete",
                )
            ),
        ):
            # JWT 토큰 기반 접근 컨텍스트 사용
            await service.delete(
                item_id,
                tenant_id=access_ctx.get("tenant_id"),
                user_id=access_ctx["user_id"],
                is_platform=access_ctx["is_platform_user"],
            )

    return router


# 사용 예시:
"""
# 테넌트 전용 CRUD 라우터 (기본)
journal_service = BaseCRUDService(Journal, "journals", "ledger")
journal_router = create_crud_router(
    service=journal_service,
    create_schema=JournalCreate,
    update_schema=JournalUpdate,
    response_schema=JournalResponse,
    prefix="/journals",
    access_type=EndpointAccessType.TENANT_ONLY  # 테넌트 사용자만 접근
)

# 플랫폼 관리자 전용 라우터
admin_router = create_crud_router(
    service=journal_service,
    create_schema=JournalCreate,
    update_schema=JournalUpdate,
    response_schema=JournalResponse,
    prefix="/admin/journals",
    access_type=EndpointAccessType.PLATFORM_ADMIN  # 플랫폼 관리자만 접근
)

# 하이브리드 접근 라우터 (테넌트와 플랫폼 모두 접근 가능)
hybrid_router = create_crud_router(
    service=journal_service,
    create_schema=JournalCreate,
    update_schema=JournalUpdate,
    response_schema=JournalResponse,
    prefix="/hybrid/journals",
    access_type=EndpointAccessType.HYBRID,  # 두 타입 모두 접근 가능
    include_operations=["list", "get"]  # 읽기 전용으로 제한
)

# 사용법:
# 1. Authorization Bearer 헤더로 JWT 토큰 전달 (필수)
# 2. 토큰에 user_id, tenant_id, is_platform_user 정보 포함
# 3. EndpointAccessType에 따른 자동 접근 제어
# 4. 권한 확인 자동 수행
# 5. 테넌트 격리 자동 적용
"""
