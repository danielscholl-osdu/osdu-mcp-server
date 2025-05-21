"""Tool for listing OSDU partitions."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from ...shared.auth_handler import AuthHandler
from ...shared.clients.partition_client import PartitionClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPError, handle_osdu_exceptions
from ...shared.utils import get_trace_id

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def partition_list(
    include_count: bool = True,
    detailed: bool = False,
) -> Dict[str, Any]:
    """List all accessible OSDU partitions.

    This tool retrieves a list of all partitions that the current user has access to.
    Partitions are logical data isolation boundaries in OSDU.

    Args:
        include_count: Whether to include the total count of partitions (default: True)
        detailed: Whether to include additional metadata (default: False)

    Returns:
        Dictionary containing partition information with the following structure:
        {
            "success": bool,
            "partitions": [str],
            "count": int (optional),
            "metadata": dict (optional),
            "error": str (optional)
        }

    Raises:
        OSMCPError: For any errors during the operation
    """
    trace_id = get_trace_id()
    
    # Log the operation
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "level": "INFO",
        "tool": "partition_list",
        "action": "partition_list_request",
        "include_count": include_count,
        "detailed": detailed,
    }))
    
    try:
        # Initialize dependencies
        config = ConfigManager()
        auth_handler = AuthHandler(config)
        client = PartitionClient(config, auth_handler)
        
        # Get partitions
        partitions = await client.list_partitions()
        
        # Build response
        response = {
            "success": True,
            "partitions": partitions,
        }
        
        if include_count:
            response["count"] = len(partitions)
            
        if detailed:
            response["metadata"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "server_url": config.get("server", "url"),
            }
        
        # Log successful response
        logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "INFO",
            "tool": "partition_list",
            "action": "partition_list_success",
            "partition_count": len(partitions),
        }))
        
        return response
        
    except OSMCPError as e:
        # Log error
        logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "ERROR",
            "tool": "partition_list",
            "action": "partition_list_error",
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))
        
        return {
            "success": False,
            "partitions": [],
            "error": str(e),
        }
        
    finally:
        # Clean up resources
        if 'client' in locals():
            await client.close()
