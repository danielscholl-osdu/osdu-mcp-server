"""Tool for listing schemas."""

from typing import Dict, Optional
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.schema_client import SchemaClient
from ...shared.exceptions import (
    OSMCPError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def schema_list(
    authority: Optional[str] = None,
    source: Optional[str] = None,
    entity: Optional[str] = None,
    status: Optional[str] = None,
    scope: Optional[str] = None,
    latest_version: bool = False,
    limit: int = 10,
    offset: int = 0
) -> Dict:
    """List schemas with optional filtering.
    
    Args:
        authority (str, optional): Filter by authority. Examples: "osdu", "SchemaSanityTest"
        source (str, optional): Filter by source. Example: "wks"
        entity (str, optional): Filter by entity type. Example: "wellbore"
        status (str, optional): Schema status. Options: "DEVELOPMENT", "PUBLISHED", "OBSOLETE"
        scope (str, optional): Schema scope. Options: "INTERNAL" (custom schemas), "SHARED" (standard schemas)
        latest_version (bool, optional): Only return latest versions. Default: False
        limit (int, optional): Maximum results to return. Range: 1-100. Default: 10
        offset (int, optional): Pagination offset. Default: 0
    
    Returns:
        Dict: List results containing:
            - success (bool): Operation success status
            - schemas (List[Dict]): Matching schemas
            - count (int): Number of returned schemas
            - totalCount (int): Total schemas matching criteria
            - offset (int): Current pagination offset
            - partition (str): Current data partition
    
    Example Usage:
        # List standard OSDU schemas
        schema_list(scope="SHARED")
        
        # List wellbore-related schemas
        schema_list(entity="wellbore")
        
        # List OSDU schemas with pagination
        schema_list(authority="osdu", limit=20, offset=40)
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = SchemaClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Get schemas
        response = await client.list_schemas(
            authority=authority,
            source=source,
            entity=entity,
            status=status,
            scope=scope,
            latest_version=latest_version,
            limit=limit,
            offset=offset
        )
        
        # Process response - check for both "schemaInfos" and "schemas" field
        schemas = response.get("schemaInfos", [])
        if not schemas:
            schemas = response.get("schemas", [])
        
        total_count = response.get("totalCount", len(schemas))
        
        # Build response
        result = {
            "success": True,
            "schemas": schemas,
            "count": len(schemas),
            "totalCount": total_count,
            "offset": offset,
            "partition": partition
        }
        
        logger.info(
            "Retrieved schemas successfully",
            extra={
                "count": len(schemas),
                "totalCount": total_count,
                "partition": partition,
                "filters": {
                    "authority": authority,
                    "source": source,
                    "entity": entity,
                    "status": status,
                    "scope": scope,
                    "latest_version": latest_version
                }
            }
        )
        
        return result
        
    finally:
        await client.close()