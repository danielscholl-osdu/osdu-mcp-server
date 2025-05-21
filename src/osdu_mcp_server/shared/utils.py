"""Utility functions for OSDU MCP Server."""

import uuid
from datetime import datetime
from typing import Any, Dict


def get_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        Current timestamp as ISO 8601 string
    """
    return datetime.utcnow().isoformat() + "Z"


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def get_trace_id() -> str:
    """Generate a unique trace ID for request correlation.
    
    Returns:
        A UUID string for request tracing
    """
    return str(uuid.uuid4())
