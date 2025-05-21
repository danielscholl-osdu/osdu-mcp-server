"""Tool for searching legal tags with filter conditions."""

from typing import Dict, Optional
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.exceptions import (
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_search(
    query: Optional[str] = None,
    valid_only: Optional[bool] = True,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict:
    """Search legal tags with filter conditions.
    
    Args:
        query: Filter condition (e.g., "properties.countryOfOrigin:US")
        valid_only: If true returns only valid tags, if false returns only invalid tags
        sort_by: Field to sort by
        sort_order: "ASC" or "DESC"
        limit: Maximum results
    
    Returns:
        Dictionary containing filtered legal tags with the following structure:
        {
            "success": true,
            "legalTags": [...],
            "count": 10,
            "partition": "opendes"
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Build query list
        query_list = []
        if query:
            query_list = [query]
        
        # Search legal tags
        if query_list or sort_by or sort_order or limit:
            # Use search endpoint
            response = await client.search_legal_tags(
                query=query_list,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit
            )
        else:
            # Use list endpoint with valid filter
            response = await client.list_legal_tags(valid=valid_only)
        
        # Process response
        legal_tags = response.get("legalTags", [])
        
        # Simplify tag names for AI-friendly display
        for tag in legal_tags:
            if "name" in tag:
                tag["simplifiedName"] = client.simplify_tag_name(tag["name"])
        
        # Build response
        result = {
            "success": True,
            "legalTags": legal_tags,
            "count": len(legal_tags),
            "partition": partition
        }
        
        logger.info(
            "Searched legal tags successfully",
            extra={
                "query": query,
                "count": len(legal_tags),
                "partition": partition
            }
        )
        
        return result
        
    finally:
        await client.close()
