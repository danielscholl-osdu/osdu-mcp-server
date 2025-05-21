"""Tool for logically deleting a record."""

from typing import Dict

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_delete_record(id: str) -> Dict:
    """Logically delete a record (can be restored).
    
    Args:
        id: Required string - Record ID to delete
    
    Returns:
        Dictionary containing deletion confirmation with the structure:
        {
            "success": true,
            "deleted": true,
            "id": str,
            "delete_enabled": bool,
            "partition": str
        }
    
    Note: Requires OSDU_MCP_ENABLE_DELETE_MODE=true
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)
    
    try:
        # Delete the record
        await client.delete_record(id)
        
        # Build response - delete endpoint may return 204 No Content
        result = {
            "success": True,
            "deleted": True,
            "id": id,
            "delete_enabled": True,
            "partition": config.get("server", "data_partition")
        }
        
        logger.warning(
            f"Successfully deleted record {id}",
            extra={
                "record_id": id,
                "operation": "delete_record",
                "destructive": True
            }
        )
        
        return result
        
    finally:
        await client.close()