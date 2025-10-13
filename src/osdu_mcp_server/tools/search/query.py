"""Execute search queries using Elasticsearch syntax."""

from typing import Dict, Any

from ...shared.clients import SearchClient
from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.exceptions import handle_osdu_exceptions


@handle_osdu_exceptions
async def search_query(
    query: str,
    kind: str = "*:*:*:*",
    limit: int = 50,
    offset: int = 0,
    user_token: str | None = None,
) -> Dict[str, Any]:
    """Execute search queries using Elasticsearch syntax.

    Args:
        query: Elasticsearch query syntax
        kind: Kind pattern to search (default: "*:*:*:*")
        limit: Maximum results (default: 50, max: 1000)
        offset: Pagination offset (default: 0)
        user_token: Optional user-provided token to use for this request.

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
    if not query:
        raise ValueError("Query parameter is required")

    if limit > 1000:
        limit = 1000

    config = ConfigManager()
    auth = AuthHandler(config, user_token=user_token)
    client = SearchClient(config, auth)

    try:
        result = await client.search_query(
            query=query, kind=kind, limit=limit, offset=offset
        )
        return result
    finally:
        await client.close()
