"""Tool for updating an existing schema."""

import os
from typing import Dict, Optional, Any
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.schema_client import SchemaClient
from ...shared.exceptions import (
    OSMCPError,
    OSMCPAPIError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def schema_update(
    id: str,
    schema: Dict[str, Any],
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing schema in DEVELOPMENT status.
    
    WARNING: This operation modifies schema definition and requires write permissions.
    It requires write permissions to be enabled via OSDU_MCP_ENABLE_WRITE_MODE=true.
    Only schemas in DEVELOPMENT status can be modified.
    Use with caution and only in controlled environments.
    
    Args:
        id: Schema ID to update (format: authority:source:entityType:majorVersion.minorVersion.patchVersion)
        schema: New schema definition
        status: New schema status (can transition from DEVELOPMENT to PUBLISHED)
    
    Returns:
        Dictionary containing operation result with the following structure:
        {
            "success": true,
            "updated": true,
            "id": "lab:test:testSchema:1.0.0",
            "status": "PUBLISHED",
            "write_enabled": true,
            "partition": "opendes"
        }
    
    Notes:
        - Only schemas in INTERNAL scope can be updated (custom schemas)
        - SHARED scope schemas are reserved for standard OSDU definitions
        - Only schemas in DEVELOPMENT status can be modified
        - Once a schema transitions from DEVELOPMENT to PUBLISHED, it cannot be modified
        - Status transitions follow a one-way path: DEVELOPMENT → PUBLISHED → OBSOLETE
        - These transitions are irreversible
    
    Example status transitions:
        - DEVELOPMENT to PUBLISHED: Allowed (schema becomes immutable)
        - DEVELOPMENT to OBSOLETE: Allowed (schema becomes deprecated)
        - PUBLISHED to OBSOLETE: Allowed (schema becomes deprecated)
        - Any status to DEVELOPMENT: Not allowed (once you leave DEVELOPMENT, you can't go back)
        - OBSOLETE to any status: Not allowed (terminal state)
    
    Raises:
        OSMCPAPIError: If write mode is disabled or schema update fails
    """
    # Check write protection
    if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Schema write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations",
            status_code=403
        )
    
    config = ConfigManager()
    auth = AuthHandler(config)
    client = SchemaClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Get the existing schema first to verify its current status and scope
        try:
            existing_schema = await client.get_schema(id)
            
            # Extract schema info from existing schema
            schema_info = existing_schema.get("schemaInfo", {})
            current_status = schema_info.get("status")
            current_scope = schema_info.get("scope")
            
            # Validate schema can be updated
            if current_scope == "SHARED":
                raise OSMCPAPIError(
                    f"Cannot update schema in SHARED scope: {id}. Only INTERNAL scope schemas can be modified.",
                    status_code=403
                )
                
            if current_status != "DEVELOPMENT" and status is None:
                raise OSMCPAPIError(
                    f"Cannot update schema with status {current_status}: {id}. Only schemas in DEVELOPMENT status can be modified.",
                    status_code=403
                )
                
            # Validate status transition
            if status is not None:
                if current_status == "PUBLISHED" and status != "OBSOLETE":
                    raise OSMCPAPIError(
                        f"Invalid status transition from {current_status} to {status}. PUBLISHED schemas can only transition to OBSOLETE.",
                        status_code=400
                    )
                    
                if current_status == "OBSOLETE":
                    raise OSMCPAPIError(
                        f"Cannot update schema with status OBSOLETE: {id}. OBSOLETE is a terminal state.",
                        status_code=403
                    )
                    
        except OSMCPAPIError as e:
            if e.status_code == 404:
                # Schema doesn't exist, no validation needed
                logger.warning(f"Schema {id} not found for update")
            else:
                # Re-raise any other errors
                raise
        
        # Update schema
        response = await client.update_schema(
            id=id,
            schema=schema,
            status=status
        )
        
        # Determine final status
        final_status = status
        if not final_status and 'current_status' in locals():
            # Use current status if known
            final_status = current_status
        elif not final_status:
            # Try to get it from the response or default to DEVELOPMENT
            final_status = response.get("status", "DEVELOPMENT")
        
        # Extract schema identity components if available
        components = id.split(":")
        authority = components[0] if len(components) > 0 else None
        source = components[1] if len(components) > 1 else None
        entity = components[2] if len(components) > 2 else None
        
        # Version components
        version = components[3] if len(components) > 3 else None
        
        # Build response
        result = {
            "success": True,
            "updated": True,
            "id": id,
            "status": final_status,
            "write_enabled": True,
            "partition": partition
        }
        
        # Include API response details if available
        if isinstance(response, dict) and response:
            # Add any useful fields from the API response
            if "schemaInfo" in response:
                schema_info = response["schemaInfo"]
                if "dateCreated" in schema_info:
                    result["dateCreated"] = schema_info["dateCreated"]
                if "createdBy" in schema_info:
                    result["createdBy"] = schema_info["createdBy"]
        
        logger.info(
            "Updated schema successfully",
            extra={
                "schema_id": id,
                "partition": partition,
                "status": final_status,
                "authority": authority,
                "source": source,
                "entity": entity,
                "version": version
            }
        )
        
        return result
        
    finally:
        await client.close()