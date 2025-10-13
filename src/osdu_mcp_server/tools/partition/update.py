"""Tool for updating OSDU partitions."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from ...shared.auth_handler import AuthHandler
from ...shared.clients.partition_client import PartitionClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPError, handle_osdu_exceptions
from ...shared.utils import get_trace_id

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def partition_update(
    partition_id: str,
    properties: dict[str, Any],
    dry_run: bool = False,
    user_token: str | None = None,
) -> dict[str, Any]:
    """Update properties of an existing OSDU partition.

    WARNING: This operation modifies partition configuration and is a destructive operation.
    It requires write permissions to be enabled via OSDU_MCP_ENABLE_WRITE_MODE=true.
    Use with caution and only in controlled environments.

    Args:
        partition_id: ID of the partition to update
        properties: Updated properties (key-value pairs). Each property will be
                   automatically formatted with value and sensitive fields.
        dry_run: Whether to simulate the operation without actually updating (default: False)
        user_token: Optional user-provided token to use for this request.

    Returns:
        Dictionary containing operation result with the following structure:
        {
            "success": bool,
            "updated": bool,
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

    write_enabled = (
        os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true"
    )

    # Log the operation
    logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": trace_id,
                "level": "INFO",
                "tool": "partition_update",
                "action": "partition_update_request",
                "partition_id": partition_id,
                "write_enabled": write_enabled,
                "dry_run": dry_run,
                "property_count": len(properties),
            }
        )
    )

    # Check write permissions before proceeding
    if not write_enabled:
        error_msg = "Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable partition updates."
        logger.warning(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "trace_id": trace_id,
                    "level": "WARN",
                    "tool": "partition_update",
                    "action": "write_operation_blocked",
                    "partition_id": partition_id,
                }
            )
        )

        return {
            "success": False,
            "updated": False,
            "partition_id": partition_id,
            "write_enabled": False,
            "dry_run": dry_run,
            "error": error_msg,
        }

    if dry_run:
        # Simulate the operation
        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "trace_id": trace_id,
                    "level": "INFO",
                    "tool": "partition_update",
                    "action": "partition_update_dry_run",
                    "partition_id": partition_id,
                }
            )
        )

        return {
            "success": True,
            "updated": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": True,
            "message": "Dry run completed. Partition would be updated with the provided properties.",
        }

    try:
        # Initialize dependencies
        config = ConfigManager()
        auth_handler = AuthHandler(config, user_token=user_token)
        client = PartitionClient(config, auth_handler)

        # Update the partition
        result = await client.update_partition(partition_id, properties)

        # Log successful update
        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "trace_id": trace_id,
                    "level": "INFO",
                    "tool": "partition_update",
                    "action": "partition_update_success",
                    "partition_id": partition_id,
                }
            )
        )

        return {
            "success": True,
            "updated": True,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": False,
        }

    except OSMCPError as e:
        # Log error
        logger.error(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "trace_id": trace_id,
                    "level": "ERROR",
                    "tool": "partition_update",
                    "action": "partition_update_error",
                    "partition_id": partition_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
        )

        return {
            "success": False,
            "updated": False,
            "partition_id": partition_id,
            "write_enabled": True,
            "dry_run": False,
            "error": str(e),
        }

    finally:
        # Clean up resources
        if "client" in locals():
            await client.close()
