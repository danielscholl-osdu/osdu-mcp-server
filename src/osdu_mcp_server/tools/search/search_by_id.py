"""Find specific records by ID."""

from typing import Dict, Any

from ...shared.clients import SearchClient
from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.exceptions import handle_osdu_exceptions


@handle_osdu_exceptions
async def search_by_id(id: str, limit: int = 10) -> Dict[str, Any]:
    """Find specific records by ID.

    Args:
        id: Record ID to search for
        limit: Maximum results (default: 10)

    Returns:
        Dictionary containing search results with the following structure:
        {
            "success": true,
            "results": [
                {
                    "id": str,
                    "kind": str,
                    "data": {...},
                    "createTime": str,
                    "version": int (optional)
                }
            ],
            "totalCount": int,
            "searchMeta": {
                "query_executed": str,
                "execution_time_ms": int
            },
            "partition": str
        }
    """
    # Validate parameters
    if not id:
        raise ValueError("ID parameter is required")

    config = ConfigManager()
    auth = AuthHandler(config)
    client = SearchClient(config, auth)

    try:
        result = await client.search_by_id(record_id=id, limit=limit)
        return result
    finally:
        await client.close()
