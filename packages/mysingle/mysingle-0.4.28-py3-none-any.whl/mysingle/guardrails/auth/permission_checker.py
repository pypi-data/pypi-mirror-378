"""권한 확인 로직"""

from typing import Any, Dict, Optional

from mysingle.iam.client import UnifiedIAMClient
from mysingle.logging import get_logger

from ..core.base import IPermissionChecker
from ..core.config import GuardrailConfig

logger = get_logger(__name__)


class PermissionChecker(IPermissionChecker):
    """통합 권한 확인 클래스"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self._iam_client: Optional[UnifiedIAMClient] = None

    async def initialize(self) -> None:
        """권한 확인 클라이언트 초기화"""
        self._iam_client = UnifiedIAMClient()
        logger.info("Permission checker initialized with UnifiedIAMClient")

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """권한 확인"""
        if not self._iam_client:
            await self.initialize()

        try:
            if not self._iam_client:
                await self.initialize()

            # 타입 체크를 위한 assert 추가
            assert (
                self._iam_client is not None
            ), "IAM client initialization failed"

            result = await self._iam_client.check_permission(
                user_id=user_id,
                tenant_id=tenant_id,
                resource=resource,
                action=action,
            )

            logger.debug(
                f"Permission check: user={user_id}, resource={resource}, "
                f"action={action}, tenant={tenant_id}, allowed={result.allowed}"
            )

            return result.allowed

        except Exception as e:
            logger.error(f"Permission check failed: {e}")

            if self.config.fail_open:
                logger.warning(
                    "Permission check failed, but fail_open=True, allowing access"
                )
                return True

            return False

    async def cleanup(self) -> None:
        """권한 확인 클라이언트 정리"""
        if self._iam_client:
            # UnifiedIAMClient cleanup if needed
            pass
