from .app_factory import create_fastapi_app
from .base import BaseClient, BaseDoc, BaseResponseSchema
from .config import CommonSettings, settings
from .crud_factory import BaseCRUDService, create_crud_router
from .database import get_database_name, get_redis_url, init_mongo
from .iam.client import (
    UnifiedIAMClient,
    close_global_iam_client,
    get_iam_client,
)
from .logging import get_logger, setup_logging
from .rbac import audit_log, require_permission

__all__ = [
    # Core
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
    "get_iam_client",
    "close_global_iam_client",
    "setup_logging",
    "get_logger",
    # RBAC
    "audit_log",
    "require_permission",
]
