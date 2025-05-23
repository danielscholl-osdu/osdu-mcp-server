"""Tool for listing all versions of a record."""

from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_list_record_versions(id: str) -> dict:
    """List all versions of a record.

    Args:
        id: Required string - Record ID

    Returns:
        Dictionary containing version information with the structure:
        {
            "success": true,
            "recordId": str,
            "versions": [int, int, int, ...],
            "count": int,
            "partition": str
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)

    try:
        # Get record versions
        response = await client.list_record_versions(id)

        # Build response
        result = {
            "success": True,
            "recordId": response.get("recordId", id),
            "versions": response.get("versions", []),
            "count": len(response.get("versions", [])),
            "partition": config.get("server", "data_partition"),
        }

        logger.info(
            f"Listed {result['count']} versions for record {id}",
            extra={
                "record_id": id,
                "version_count": result["count"],
                "operation": "list_record_versions",
            },
        )

        return result

    finally:
        await client.close()
