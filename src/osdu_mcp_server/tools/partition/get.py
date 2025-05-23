"""Tool for retrieving OSDU partition details."""

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
async def partition_get(
    partition_id: str,
    include_sensitive: bool = False,
    redact_sensitive_values: bool = True,
) -> Dict[str, Any]:
    """Retrieve configuration for a specific OSDU partition.

    This tool fetches the properties and configuration for a specific partition.
    Properties may be marked as sensitive (e.g., credentials, connection strings).
    By default, sensitive properties are included but with redacted values for security.

    Args:
        partition_id: ID of the partition to retrieve
        include_sensitive: Whether to include sensitive properties (default: False)
        redact_sensitive_values: Whether to redact values of sensitive properties (default: True)

    Returns:
        Dictionary containing partition information with the following structure:
        {
            "success": bool,
            "exists": bool,
            "partition_id": str,
            "properties": dict,
            "sensitive_properties_count": int,
            "error": str (optional)
        }

    Raises:
        OSMCPError: For any errors during the operation
    """
    trace_id = get_trace_id()

    # Log the operation
    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": trace_id,
        "level": "INFO",
        "tool": "partition_get",
        "action": "partition_get_request",
        "partition_id": partition_id,
        "include_sensitive": include_sensitive,
        "redact_sensitive_values": redact_sensitive_values,
    }))

    try:
        # Initialize dependencies
        config = ConfigManager()
        auth_handler = AuthHandler(config)
        client = PartitionClient(config, auth_handler)

        # Get partition properties
        properties = await client.get_partition(partition_id)

        # Process properties based on sensitivity settings
        processed_properties = {}
        sensitive_count = 0
        sensitive_accessed = []

        for key, prop in properties.items():
            is_sensitive = prop.get("sensitive", False)

            if is_sensitive:
                sensitive_count += 1

                if not include_sensitive:
                    # Skip sensitive properties entirely
                    continue

                if redact_sensitive_values:
                    # Include property but redact value
                    processed_properties[key] = {
                        "sensitive": True,
                        "value": "<REDACTED>",
                    }
                else:
                    # Include full property (for authorized operations)
                    processed_properties[key] = prop
                    sensitive_accessed.append(key)
            else:
                # Non-sensitive property, include as-is
                processed_properties[key] = prop

        # Log sensitive data access if any
        if sensitive_accessed:
            logger.warning(json.dumps({
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": trace_id,
                "level": "WARN",
                "tool": "partition_get",
                "action": "sensitive_data_access",
                "partition_id": partition_id,
                "properties_accessed": sensitive_accessed,
                "user": await auth_handler.get_user_info() if hasattr(auth_handler, 'get_user_info') else "unknown",
                "result": "provided",
            }))

        response = {
            "success": True,
            "exists": True,
            "partition_id": partition_id,
            "properties": processed_properties,
            "sensitive_properties_count": sensitive_count,
        }

        # Log successful response
        logger.info(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "INFO",
            "tool": "partition_get",
            "action": "partition_get_success",
            "partition_id": partition_id,
            "property_count": len(processed_properties),
            "sensitive_count": sensitive_count,
        }))

        return response

    except OSMCPError as e:
        # Log error
        logger.error(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "level": "ERROR",
            "tool": "partition_get",
            "action": "partition_get_error",
            "partition_id": partition_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))

        # Check if it's a not found error
        exists = "not found" not in str(e).lower()

        return {
            "success": False,
            "exists": exists,
            "partition_id": partition_id,
            "properties": {},
            "error": str(e),
        }

    finally:
        # Clean up resources
        if 'client' in locals():
            await client.close()
