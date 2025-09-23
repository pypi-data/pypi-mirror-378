"""Common FastAPI application factory for all services."""

from typing import TYPE_CHECKING, Any, Optional

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from mysingle.config import settings
from mysingle.health import create_health_routers
from mysingle.middleware.auth_middleware import AuthMiddleware
from mysingle.middleware.metrics_middleware import PrometheusMiddleware

if TYPE_CHECKING:
    from typing import List


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for each route based on its tags and name."""
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


def create_fastapi_app(
    service_name: str,
    service_version: str = "0.1.0",
    title: Optional[str] = None,
    description: Optional[str] = None,
    enable_iam: bool = True,  # 통합 IAM 활성화
    enable_metrics: bool = True,
    public_paths: Optional["List[str]"] = None,
    cors_origins: Optional["List[str]"] = None,
    lifespan: Any = None,
) -> FastAPI:
    """Create a FastAPI application with common middleware and routes.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        title: Custom title for the API documentation
        description: Custom description for the API
        enable_iam: Whether to enable IAM (authentication + authorization) middleware
        enable_metrics: Whether to enable metrics collection
        public_paths: List of public paths that don't require authentication
        cors_origins: List of allowed CORS origins
        lifespan: Lifespan event handler

    Returns:
        Configured FastAPI application instance
    """
    # Generate application metadata
    app_title = title or f"MySingle {service_name.replace('_', ' ').title()}"
    app_description = description or f"{service_name} for MySingle platform"

    # Default public paths
    default_public_paths = [
        "/health",
        "/version",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    if enable_metrics:
        default_public_paths.append("/metrics")

    final_public_paths = public_paths or default_public_paths

    # Check if we're in development
    is_development = not hasattr(
        settings, "ENVIRONMENT"
    ) or settings.ENVIRONMENT in [
        "development",
        "local",
    ]

    # Create FastAPI app
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=service_version,
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=lifespan,
        docs_url="/docs" if is_development else None,
        redoc_url="/redoc" if is_development else None,
        openapi_url="/openapi.json" if is_development else None,
    )

    # Add CORS middleware
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add IAM middleware (authentication + authorization)
    if enable_iam and not is_development:
        app.add_middleware(
            AuthMiddleware,
            public_paths=final_public_paths,
        )

    # Add metrics middleware
    if enable_metrics:
        app.add_middleware(PrometheusMiddleware, service_name=service_name)

    # Add health routes
    _, public_health_router = create_health_routers(
        service_name, service_version, enable_metrics
    )
    app.include_router(public_health_router)

    return app
