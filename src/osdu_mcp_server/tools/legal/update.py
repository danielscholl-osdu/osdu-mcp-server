"""Tool for updating legal tags (write-protected)."""

import os
from typing import Dict, Optional, Any
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.exceptions import (
    OSMCPAPIError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_update(
    name: str,
    description: Optional[str] = None,
    contract_id: Optional[str] = None,
    expiration_date: Optional[str] = None,
    extension_properties: Optional[Dict[str, Any]] = None
) -> Dict:
    """Update an existing legal tag.
    
    Args:
        name: Legal tag name (with or without partition prefix)
        description: New description
        contract_id: New contract ID
        expiration_date: New expiration date (YYYY-MM-DD format)
        extension_properties: New custom properties
    
    Returns:
        Dictionary containing updated legal tag
    
    Note: Requires OSDU_MCP_ENABLE_WRITE_MODE=true
    """
    # Check write protection
    if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Legal tag write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations",
            status_code=403
        )
    
    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Update legal tag
        response = await client.update_legal_tag(
            name=name,
            description=description,
            contract_id=contract_id,
            expiration_date=expiration_date,
            extension_properties=extension_properties
        )
        
        # Extract tag data
        tag = response
        
        # Build response
        result = {
            "success": True,
            "legalTag": tag,
            "updated": True,
            "write_enabled": True,
            "partition": partition
        }
        
        logger.info(
            "Updated legal tag successfully",
            extra={
                "name": name,
                "partition": partition
            }
        )
        
        # Audit log for write operation
        logger.audit(
            "Legal tag updated",
            extra={
                "operation": "update_legal_tag",
                "tag_name": name,
                "partition": partition,
                "user": "authenticated_user"  # Should be extracted from auth context
            }
        )
        
        return result
        
    finally:
        await client.close()