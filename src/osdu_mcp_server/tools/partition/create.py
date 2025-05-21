"""Tool for creating OSDU partitions."""

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
async def partition_create(
    partition_id: str,
    properties: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Create a new OSDU partition.

    WARNING: This operation creates a new partition and is a destructive operation.
    It requires write permissions to be enabled via OSDU_MCP_ENABLE_WRITE_MODE=true.
    Use with caution and only in controlled environments.

    Args:
        partition_id: ID for the new partition
        properties: Partition properties (key-value pairs). Each property will be
                   automatically formatted with value and sensitive fields.
        dry_run: Whether to simulate the operation without actually creating (default: False)

    Returns:
        Dictionary containing operation result with the following structure:
        {
            "success": bool,
            "created": bool,
            "partition_id": str,
            "write_enabled": bool,
            "dry_run": bool,
            "error": str (optional)
        }

    Raises:
        OSMCPError: For any errors during the operation
    """
    trace_id = get_trace_id()

    # Check write permissions first
    import os
    write_enabled = os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true"

    # Log the operation
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "level": "INFO",
        "tool": "partition_create",
        "action": "partition_create_request",
        "partition_id": partition_id,
        "write_enabled": write_enabled,
        "dry_run": dry_run,
        "property_count": len(properties),
    }))

    # Check write permissions before proceeding
    if not write_enabled:
        error_msg = "Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable partition creation."
        logger.warning(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "WARN",
            "tool": "partition_create",
            "action": "write_operation_blocked",
            "partition_id": partition_id,
        }))

        return {
            "success": False,
            "created": False,
            "partition_id": partition_id,
            "write_enabled": False,
            "dry_run": dry_run,
            "error": error_msg,
        }

    if dry_run:
        # Simulate the operation
        logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "INFO",
            "tool": "partition_create",
            "action": "partition_create_dry_run",
            "partition_id": partition_id,
        }))

        return {
            "success": True,
            "created": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": True,
            "message": "Dry run completed. Partition would be created with the provided properties.",
        }

    try:
        # Initialize dependencies
        config = ConfigManager()
        auth_handler = AuthHandler(config)
        client = PartitionClient(config, auth_handler)

        # Create the partition
        result = await client.create_partition(partition_id, properties)

        # Log successful creation
        logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "INFO",
            "tool": "partition_create",
            "action": "partition_create_success",
            "partition_id": partition_id,
        }))

        return {
            "success": True,
            "created": True,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": False,
        }

    except OSMCPError as e:
        # Log error
        logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "level": "ERROR",
            "tool": "partition_create",
            "action": "partition_create_error",
            "partition_id": partition_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))

        return {
            "success": False,
            "created": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": False,
            "error": str(e),
        }

    finally:
        # Clean up resources
        if 'client' in locals():
            await client.close()
