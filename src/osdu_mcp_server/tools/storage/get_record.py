"""Tool for getting a record by ID."""

from typing import Dict, List, Optional

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_get_record(
    id: str,
    attributes: Optional[List[str]] = None
) -> Dict:
    """Get the latest version of a record by ID.
    
    Args:
        id: Required string - Record ID
        attributes: Optional array of strings - Specific data fields to return
    
    Returns:
        Dictionary containing record information with the structure:
        {
            "success": true,
            "record": {
                "id": str,
                "kind": str,
                "version": int,
                "acl": {...},
                "legal": {...},
                "data": {...},
                "createTime": str,
                "createUser": str,
                ...
            },
            "partition": str
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)
    
    try:
        # Get the record
        record = await client.get_record(id, attributes)
        
        # Build response
        result = {
            "success": True,
            "record": record,
            "partition": config.get("server", "data_partition")
        }
        
        logger.info(
            f"Retrieved record {id}",
            extra={
                "record_id": id,
                "operation": "get_record",
                "has_attributes": bool(attributes)
            }
        )
        
        return result
        
    finally:
        await client.close()