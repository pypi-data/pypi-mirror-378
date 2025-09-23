"""Authentication middleware handling JWT validation and basic endpoint permissions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    pass

from mysingle.auth.auth_utils import (
    AuthenticationError,
    extract_auth_context,
    is_public_path,
    set_auth_context,
)
from mysingle.iam.client import UnifiedIAMClient


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT validation and basic endpoint permission checks.

    This middleware handles:
    1. JWT token validation and user context extraction
    2. Basic endpoint permission checks via IAM service
    3. Caching of permission results in Redis

    Note: Complex RBAC logic should use RBACMiddleware instead.
    """

    def __init__(
        self,
        app,
        redis: Redis | None = None,  # 호환성을 위해 유지하지만 사용하지 않음
        public_paths: list[str] | None = None,
        cache_ttl: int = 30,
    ) -> None:
        super().__init__(app)

        # UnifiedIAMClient 초기화
        self.iam_client = UnifiedIAMClient()

        default_public_paths = [
            "/health",
            "/version",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.public_paths = public_paths or default_public_paths

    async def dispatch(
        self,
        request: Request,
        call_next: Any,  # Simplified type for Pydantic compatibility
    ) -> Response:
        # Skip authentication for public paths
        if is_public_path(request.url.path, self.public_paths):
            return await call_next(request)

        try:
            # Extract authentication context (shared JWT processing)
            auth_context = await extract_auth_context(request)
            if auth_context is None:
                return JSONResponse(
                    {"detail": "Authentication failed"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            set_auth_context(request, auth_context)

            # For backward compatibility, set user in request.state
            request.state.user = auth_context.payload

        except AuthenticationError as e:
            return JSONResponse(
                {"detail": e.message},
                status_code=e.status_code,
            )

        # Check endpoint-specific permissions (simple endpoint-based check)
        endpoint = None
        for route in request.app.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", [])
            if path == request.url.path and request.method in methods:
                endpoint = getattr(route, "endpoint", None)
                break

        required_perm = getattr(endpoint, "required_permission", None)
        if required_perm and auth_context.token:
            if not await self._check_permission(auth_context, required_perm):
                return JSONResponse(
                    {"detail": "Permission denied"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        return await call_next(request)

    async def _check_permission(self, auth_context, permission: str) -> bool:
        """권한 확인 (UnifiedIAMClient 사용)"""
        try:
            result = await self.iam_client.check_permission(
                user_id=auth_context.user_id,
                tenant_id=auth_context.tenant_id,
                resource=permission.split(":")[0]
                if ":" in permission
                else permission,
                action=permission.split(":")[-1]
                if ":" in permission
                else "access",
            )
            return result.allowed
        except Exception:
            # 권한 확인 실패 시 기본적으로 거부
            return False
