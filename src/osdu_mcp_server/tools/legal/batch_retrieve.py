"""Tool for batch retrieving legal tags."""

from typing import Dict, List
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.exceptions import (
    OSMCPError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_batch_retrieve(
    names: List[str]
) -> Dict:
    """Retrieve multiple legal tags by name.
    
    Args:
        names: List of legal tag names (max 25)
    
    Returns:
        Dictionary containing legal tags with the following structure:
        {
            "success": true,
            "legalTags": [...],
            "count": 2,
            "partition": "opendes"
        }
    """
    if not names:
        raise OSMCPError("No legal tag names provided")
        
    if len(names) > 25:
        raise OSMCPError("Maximum 25 legal tags can be retrieved at once")
    
    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Batch retrieve legal tags
        response = await client.batch_retrieve_legal_tags(names)
        
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
            "Batch retrieved legal tags successfully",
            extra={
                "requested": len(names),
                "retrieved": len(legal_tags),
                "partition": partition
            }
        )
        
        return result
        
    finally:
        await client.close()