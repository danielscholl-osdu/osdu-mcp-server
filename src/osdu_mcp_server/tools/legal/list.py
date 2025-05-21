"""Tool for listing legal tags."""

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
async def legaltag_list(
    valid_only: Optional[bool] = True
) -> Dict:
    """List all legal tags in the current partition.
    
    Args:
        valid_only: If true returns only valid tags, if false returns only invalid tags
    
    Returns:
        Dictionary containing legal tags with the following structure:
        {
            "success": true,
            "legalTags": [
                {
                    "name": "opendes-Private-USA-EHC",
                    "description": "Private data for USA with EHC compliance",
                    "properties": {...}
                }
            ],
            "count": 15,
            "partition": "opendes"
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Get legal tags
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
            "Retrieved legal tags successfully",
            extra={
                "count": len(legal_tags),
                "partition": partition,
                "valid_only": valid_only
            }
        )
        
        return result
        
    finally:
        await client.close()