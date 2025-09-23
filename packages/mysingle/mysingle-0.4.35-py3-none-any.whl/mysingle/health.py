"""Common health check endpoints for all services.

🆕 2025.09.23 업데이트: JWT 기반 EndpointAccessType 시스템으로 전환
- 기존 get_tenant_id + require_permission → EndpointAccessType.TENANT_ONLY
- 인증된 헬스체크는 테넌트 전용 접근으로 제한
- 공개 헬스체크는 여전히 인증 없이 사용 가능
"""

from fastapi import APIRouter, Depends, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def _get_guardrails():
    """지연 import로 순환 import 방지"""
    from .guardrails.auth.dependencies import (
        EndpointAccessType,
        get_access_context,
    )

    return get_access_context, EndpointAccessType


def _create_access_dependency(access_type):
    """EndpointAccessType을 위한 의존성 팩토리"""
    get_access_context, EndpointAccessType = _get_guardrails()

    async def access_dependency(request: Request):
        return await get_access_context(
            request=request, access_type=access_type
        )

    return access_dependency


def create_health_routers(
    service_name: str,
    service_version: str = "0.1.0",
    enable_metrics: bool = True,
) -> tuple[APIRouter, APIRouter]:
    """Create authenticated and public health check routers.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        enable_metrics: Whether to include metrics endpoint

    Returns:
        Tuple of (authenticated_router, public_router)
    """
    # 지연 import로 순환 import 방지
    get_access_context, EndpointAccessType = _get_guardrails()

    # Router used for versioned API paths (e.g. ``/api/v1/health/``)
    # 테넌트 전용 접근으로 인증된 헬스체크 엔드포인트
    auth_dependency = _create_access_dependency(EndpointAccessType.TENANT_ONLY)

    authenticated_router = APIRouter(dependencies=[Depends(auth_dependency)])

    # Router for top-level service metadata endpoints (``/health`` and ``/version``)
    public_router = APIRouter()

    @authenticated_router.get("/")
    async def api_health() -> dict[str, str]:
        """Return service health status for API routes."""
        return {"status": "ok"}

    @public_router.get("/health")
    async def health() -> dict[str, str]:
        """Return basic service health information."""
        return {"status": "ok", "service": service_name}

    @public_router.get("/version")
    async def version() -> dict[str, str]:
        """Return service version information."""
        return {"service": service_name, "version": service_version}

    if enable_metrics:

        @public_router.get("/metrics")
        async def metrics() -> Response:
            """Return Prometheus metrics."""
            data = generate_latest()
            return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return authenticated_router, public_router


# Backward compatibility exports
def create_public_health_router(
    service_name: str,
    service_version: str = "0.1.0",
    enable_metrics: bool = True,
) -> APIRouter:
    """Create a public health router (backward compatibility)."""
    _, public_router = create_health_routers(
        service_name, service_version, enable_metrics
    )
    return public_router


def create_authenticated_health_router() -> APIRouter:
    """Create an authenticated health router (backward compatibility)."""
    authenticated_router, _ = create_health_routers("unknown")
    return authenticated_router
