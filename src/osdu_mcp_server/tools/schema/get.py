"""Tool for retrieving a specific schema."""

from typing import Dict, Any
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.schema_client import SchemaClient
from ...shared.exceptions import (
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def schema_get(
    id: str
) -> Dict[str, Any]:
    """Retrieve complete schema by ID.
    
    Args:
        id: Schema ID (format: authority:source:entityType:majorVersion.minorVersion.patchVersion)
            Example standard schema: "osdu:wks:AbstractAccessControlList:1.0.0"
            Example custom schema: "SchemaSanityTest:testSource:testEntity:1.1.0"
    
    Returns:
        Dictionary containing schema details with the following structure:
        {
            "success": true,
            "$schema": "http://json-schema.org/draft-07/schema#",
            "x-osdu-schema-source": "osdu:wks:AbstractAccessControlList:1.0.0",
            "title": "Access Control List",
            "description": "The access control tags associated with this entity...",
            "type": "object",
            "properties": {
                "viewers": {
                    "title": "List of Viewers",
                    "description": "The list of viewers...",
                    "type": "array",
                    "items": {
                        "pattern": "...",
                        "type": "string"
                    }
                },
                "owners": {
                    "title": "List of Owners",
                    "description": "The list of owners...",
                    "type": "array",
                    "items": {
                        "pattern": "...",
                        "type": "string"
                    }
                }
            },
            "required": [
                "owners",
                "viewers"
            ],
            "additionalProperties": false,
            "partition": "opendes",
            "schemaInfo": {
                "schemaIdentity": {
                    "authority": "osdu",
                    "source": "wks",
                    "entityType": "AbstractAccessControlList",
                    "schemaVersionMajor": 1,
                    "schemaVersionMinor": 0,
                    "schemaVersionPatch": 0,
                    "id": "osdu:wks:AbstractAccessControlList:1.0.0"
                },
                "createdBy": "ServiceAdminUser",
                "dateCreated": "2023-01-01T00:00:00.000Z",
                "status": "PUBLISHED",
                "scope": "SHARED"
            }
        }
    
    Notes:
        - Both SHARED and INTERNAL scope schemas can be retrieved
        - Standard OSDU schemas use "osdu:" as the authority prefix
        - Custom schemas typically use other authorities (e.g., "SchemaSanityTest:")
        - The returned schema is in JSON Schema format (draft-07)
        - The response includes the full schema definition plus schema metadata in "schemaInfo"
        - Schema status can be "DEVELOPMENT", "PUBLISHED", or "OBSOLETE"
        - Only DEVELOPMENT status schemas can be modified
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = SchemaClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Get schema
        response = await client.get_schema(id)
        
        # Add success flag and partition info
        response["success"] = True
        response["partition"] = partition
        
        # Enhance response to provide more context about the schema
        if "schemaInfo" in response:
            schema_info = response["schemaInfo"]
            identity = schema_info.get("schemaIdentity", {})
            
            # Log status and scope for informational purposes
            status = schema_info.get("status", "UNKNOWN")
            scope = schema_info.get("scope", "UNKNOWN")
            
            logger.info(
                "Retrieved schema successfully",
                extra={
                    "schema_id": id,
                    "partition": partition,
                    "authority": identity.get("authority"),
                    "status": status,
                    "scope": scope
                }
            )
        else:
            logger.info(
                "Retrieved schema successfully",
                extra={
                    "schema_id": id,
                    "partition": partition
                }
            )
        
        return response
        
    finally:
        await client.close()
