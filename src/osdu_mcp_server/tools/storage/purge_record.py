"""Tool for permanently purging a record."""

from typing import Dict

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_purge_record(
    id: str,
    confirm: bool
) -> Dict:
    """Physically delete a record permanently (cannot be restored).
    
    Args:
        id: Required string - Record ID to purge
        confirm: Required boolean - Explicit confirmation (must be true)
    
    Returns:
        Dictionary containing purge confirmation with the structure:
        {
            "success": true,
            "purged": true,
            "id": str,
            "delete_enabled": bool,
            "warning": str,
            "partition": str
        }
    
    Note: Requires OSDU_MCP_ENABLE_DELETE_MODE=true
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)
    
    try:
        # Purge the record
        await client.purge_record(id, confirm)
        
        # Build response - purge endpoint may return 204 No Content
        result = {
            "success": True,
            "purged": True,
            "id": id,
            "delete_enabled": True,
            "warning": "Record has been permanently deleted and cannot be recovered",
            "partition": config.get("server", "data_partition")
        }
        
        logger.error(
            f"Successfully purged record {id} permanently",
            extra={
                "record_id": id,
                "operation": "purge_record",
                "destructive": True,
                "permanent": True
            }
        )
        
        return result
        
    finally:
        await client.close()
