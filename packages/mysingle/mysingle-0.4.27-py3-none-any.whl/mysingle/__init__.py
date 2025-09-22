from .app_factory import create_fastapi_app
from .base import BaseClient, BaseDoc, BaseResponseSchema
from .config import CommonSettings, settings
from .crud_factory import BaseCRUDService, create_crud_router
from .database import get_database_name, get_redis_url, init_mongo
from .exceptions import (
    APIError,
    AppError,
    ConflictError,
    ErrorResponse,
    InternalServerError,
    NotFoundError,
    ValidationError,
    api_error_handler,
    general_exception_handler,
    http_exception_handler,
    register_exception_handlers,
)
from .iam.client import UnifiedIAMClient
from .logging import get_logger, setup_logging
from .rbac.decorators import audit_log, require_permission

__all__ = [
    "create_fastapi_app",
    "settings",
    "CommonSettings",
    "BaseDoc",
    "BaseClient",
    "BaseResponseSchema",
    "BaseCRUDService",
    "create_crud_router",
    "init_mongo",
    "get_database_name",
    "get_redis_url",
    "UnifiedIAMClient",
    "setup_logging",
    "get_logger",
    # RBAC
    "audit_log",
    "require_permission",
    # Exceptions
    "AppError",
    "APIError",
    "ValidationError",
    "NotFoundError",
    "ErrorResponse",
    "ConflictError",
    "InternalServerError",
    "http_exception_handler",
    "general_exception_handler",
    "register_exception_handlers",
    "api_error_handler",
]
