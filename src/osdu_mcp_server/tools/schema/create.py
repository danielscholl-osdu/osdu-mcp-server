"""Tool for creating a new schema."""

import logging
import os
from typing import Any

from ...shared.auth_handler import AuthHandler
from ...shared.clients.schema_client import SchemaClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPAPIError, handle_osdu_exceptions

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def schema_create(
    authority: str,
    source: str,
    entity: str,
    major_version: int,
    minor_version: int,
    patch_version: int,
    schema: dict[str, Any],
    status: str = "DEVELOPMENT",
    description: str | None = None,
    user_token: str | None = None,
) -> dict[str, Any]:
    """Create a new schema.

    WARNING: This operation creates a new schema and requires write permissions.
    It requires write permissions to be enabled via OSDU_MCP_ENABLE_WRITE_MODE=true.
    Use with caution and only in controlled environments.

    Args:
        authority: Schema authority (e.g., "mycompany")
        source: Schema source (e.g., "app")
        entity: Schema entity type (e.g., "customtype")
        major_version: Major version number
        minor_version: Minor version number
        patch_version: Patch version number
        schema: JSON Schema definition
        status: Schema status (default: DEVELOPMENT)
        description: Schema description
        user_token: Optional user-provided token to use for this request.

    Returns:
        Dictionary containing operation result with the following structure:
        {
            "success": true,
            "created": true,
            "id": "lab:test:testSchema:1.0.0",
            "status": "DEVELOPMENT",
            "write_enabled": true,
            "partition": "opendes"
        }

    Notes:
        - New schemas are created in INTERNAL scope
        - SHARED scope is reserved for standard OSDU schemas
        - Only schemas in DEVELOPMENT status can be modified
        - Schemas in PUBLISHED or OBSOLETE status are immutable
        - Schema lifecycle: DEVELOPMENT → PUBLISHED → OBSOLETE
        - These transitions are irreversible
        - Basic JSON Schema validation is performed by the API
        - Minimum schema requirements: $schema (draft-07), type, properties

    Example schema structure:
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "My Custom Type",
            "description": "Description of my custom type",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object"
                },
                "value": {
                    "type": "number",
                    "description": "Value of the object"
                }
            },
            "required": ["name"]
        }

    Raises:
        OSMCPAPIError: If write mode is disabled or schema creation fails
    """
    # Check write protection
    if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Schema write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations",
            status_code=403,
        )

    config = ConfigManager()
    auth = AuthHandler(config, user_token=user_token)
    client = SchemaClient(config, auth)

    try:
        # Get current partition
        partition = config.get("server", "data_partition")

        # Format schema ID for logging and response
        schema_id = client.format_schema_id(
            authority, source, entity, major_version, minor_version, patch_version
        )

        # Ensure schema has the minimum required elements
        if "$schema" not in schema:
            schema["$schema"] = "http://json-schema.org/draft-07/schema#"

        if "type" not in schema:
            schema["type"] = "object"

        if "properties" not in schema and schema["type"] == "object":
            schema["properties"] = {}

        # Set title and description if provided and not already in schema
        if description and "description" not in schema:
            schema["description"] = description

        if description and "title" not in schema:
            schema["title"] = (
                description.split(".")[0] if "." in description else description
            )

        # Create schema
        response = await client.create_schema(
            authority=authority,
            source=source,
            entity=entity,
            major_version=major_version,
            minor_version=minor_version,
            patch_version=patch_version,
            schema=schema,
            status=status,
            description=description,
        )

        # Build response
        result = {
            "success": True,
            "created": True,
            "id": schema_id,
            "status": status,
            "write_enabled": True,
            "partition": partition,
        }

        # Include API response details if available
        if isinstance(response, dict) and response:
            # Include relevant fields from the API response
            if "id" in response:
                result["schema_id"] = response["id"]
            if "status" in response:
                result["api_status"] = response["status"]

        logger.info(
            "Created schema successfully",
            extra={
                "schema_id": schema_id,
                "partition": partition,
                "authority": authority,
                "source": source,
                "entity": entity,
                "version": f"{major_version}.{minor_version}.{patch_version}",
                "status": status,
            },
        )

        return result

    finally:
        await client.close()
