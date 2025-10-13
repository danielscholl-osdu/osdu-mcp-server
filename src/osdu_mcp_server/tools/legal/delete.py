"""Tool for deleting legal tags (write-protected)."""

import logging

from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPAPIError, handle_osdu_exceptions

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_delete(name: str, confirm: bool, user_token: str | None = None) -> dict:
    """Delete a legal tag.

    CAUTION: Deleting a legal tag will make all associated data invalid.

    Args:
        name: Legal tag name
        confirm: Explicit confirmation required
        user_token: Optional user-provided token to use for this request.

    Returns:
        Dictionary containing deletion confirmation

    Note: Requires OSDU_MCP_ENABLE_DELETE_MODE=true
    """

    # Check confirmation
    if not confirm:
        raise OSMCPAPIError(
            "Deletion not confirmed. Set confirm=true to delete the legal tag. WARNING: This will invalidate all associated data.",
            status_code=400,
        )

    config = ConfigManager()
    auth = AuthHandler(config, user_token=user_token)
    client = LegalClient(config, auth)

    try:
        # Get current partition
        partition = config.get("server", "data_partition")

        # Delete legal tag
        await client.delete_legal_tag(name)

        # Build response
        result = {
            "success": True,
            "deleted": True,
            "name": client.ensure_full_tag_name(name),
            "delete_enabled": True,
            "partition": partition,
            "warning": "Associated data is now invalid",
        }

        logger.warning(
            "Legal tag deleted - associated data is now invalid",
            extra={
                "operation": "delete_legal_tag",
                "tag_name": name,
                "partition": partition,
                "destructive": True,
                "permanent": False,
                "warning": "Associated data is now invalid",
            },
        )

        return result

    finally:
        await client.close()
