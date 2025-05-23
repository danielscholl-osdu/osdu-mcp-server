"""Tool for deleting OSDU partitions."""

import json
import logging
from datetime import datetime, UTC
from typing import Any, Dict

from ...shared.auth_handler import AuthHandler
from ...shared.clients.partition_client import PartitionClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPError, handle_osdu_exceptions
from ...shared.utils import get_trace_id

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def partition_delete(
    partition_id: str,
    confirm: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Delete an OSDU partition.

    WARNING: This operation permanently deletes a partition and ALL of its data.
    This is an extremely destructive operation that cannot be undone.
    It requires write permissions to be enabled via OSDU_MCP_ENABLE_WRITE_MODE=true.
    Use with extreme caution and only after careful consideration.

    Args:
        partition_id: ID of the partition to delete
        confirm: Explicit confirmation required to proceed (default: False)
        dry_run: Whether to simulate the operation without actually deleting (default: False)

    Returns:
        Dictionary containing operation result with the following structure:
        {
            "success": bool,
            "deleted": bool,
            "partition_id": str,
            "write_enabled": bool,
            "confirmed": bool,
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
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": trace_id,
        "level": "INFO",
        "tool": "partition_delete",
        "action": "partition_delete_request",
        "partition_id": partition_id,
        "write_enabled": write_enabled,
        "confirmed": confirm,
        "dry_run": dry_run,
    }))

    # Check write permissions before proceeding
    if not write_enabled:
        error_msg = "Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable partition deletion."
        logger.warning(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "WARN",
            "tool": "partition_delete",
            "action": "write_operation_blocked",
            "partition_id": partition_id,
        }))

        return {
            "success": False,
            "deleted": False,
            "partition_id": partition_id,
            "write_enabled": False,
            "confirmed": confirm,
            "dry_run": dry_run,
            "error": error_msg,
        }

    # Check confirmation
    if not confirm and not dry_run:
        error_msg = "Deletion requires explicit confirmation. Set confirm=True to proceed with deletion."
        logger.warning(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "WARN",
            "tool": "partition_delete",
            "action": "delete_not_confirmed",
            "partition_id": partition_id,
        }))

        return {
            "success": False,
            "deleted": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "confirmed": False,
            "dry_run": dry_run,
            "error": error_msg,
        }

    if dry_run:
        # Simulate the operation
        logger.info(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "INFO",
            "tool": "partition_delete",
            "action": "partition_delete_dry_run",
            "partition_id": partition_id,
        }))

        return {
            "success": True,
            "deleted": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "confirmed": confirm,
            "dry_run": True,
            "message": "Dry run completed. Partition would be deleted if confirm=True was provided.",
        }

    try:
        # Initialize dependencies
        config = ConfigManager()
        auth_handler = AuthHandler(config)
        client = PartitionClient(config, auth_handler)

        # Delete the partition
        await client.delete_partition(partition_id)

        # Log successful deletion
        logger.warning(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "WARN",
            "tool": "partition_delete",
            "action": "partition_delete_success",
            "partition_id": partition_id,
            "user": await auth_handler.get_user_info() if hasattr(auth_handler, 'get_user_info') else "unknown",
        }))

        return {
            "success": True,
            "deleted": True,
            "partition_id": partition_id,
            "write_enabled": True,
            "confirmed": True,
            "dry_run": False,
        }

    except OSMCPError as e:
        # Log error
        logger.error(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "ERROR",
            "tool": "partition_delete",
            "action": "partition_delete_error",
            "partition_id": partition_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))

        return {
            "success": False,
            "deleted": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "confirmed": confirm,
            "dry_run": False,
            "error": str(e),
        }

    finally:
        # Clean up resources
        if 'client' in locals():
            await client.close()
