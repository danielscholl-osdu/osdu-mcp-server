"""Tool for advanced schema discovery with rich filtering and text search."""

import fnmatch
from typing import Dict, Optional, List, Union

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.schema_client import SchemaClient
from ...shared.logging_manager import get_logger
from ...shared.exceptions import (
    handle_osdu_exceptions
)

# Get a logger with feature flag support
logger = get_logger(__name__)


@handle_osdu_exceptions
async def schema_search(
    # Text search parameters
    text: Optional[str] = None,
    search_in: List[str] = None,
    
    # Version filtering
    version_pattern: Optional[str] = None,
    
    # Rich filtering
    filter: Optional[Dict[str, Union[str, List[str]]]] = None,
    
    # Common parameters
    latest_version: bool = False,
    limit: int = 100,
    offset: int = 0,
    
    # Advanced options
    include_content: bool = False,
    sort_by: str = "dateCreated",
    sort_order: str = "DESC"
) -> Dict:
    """Advanced schema discovery with rich filtering and text search.

    Args:
        text (str, optional): Text to search across schema content. Example: "pressure"
        search_in (List[str], optional): Fields to search in. Default: ["title", "description", "properties"]
        version_pattern (str, optional): Version with wildcard support. Examples: "1.1.0", "1.*.*"
        filter (Dict, optional): Key-value filter criteria. Keys include:
            - authority: Schema authority (str or List[str]). Example: "osdu" or ["osdu", "lab"]
            - source: Schema source (str or List[str]). Example: "wks"
            - entity: Entity type (str or List[str]). Example: "wellbore"
            - status: Schema status (str or List[str]). Example: "PUBLISHED" or ["PUBLISHED", "DEVELOPMENT"]
            - scope: Schema scope (str or List[str]). Example: "SHARED" or "INTERNAL"
        latest_version (bool, optional): Only return latest versions. Default: False
        limit (int, optional): Maximum results to return. Range: 1-1000. Default: 100
        offset (int, optional): Pagination offset. Default: 0
        include_content (bool, optional): Include full schema content. Default: False
        sort_by (str, optional): Field to sort by. Options: "dateCreated", "authority", "source", "entityType", "status", "scope", "id". Default: "dateCreated"
        sort_order (str, optional): Sort direction. Options: "ASC", "DESC". Default: "DESC"

    Returns:
        Dict: Search results containing:
            - success (bool): Operation success status
            - schemas (List[Dict]): Matching schemas
            - count (int): Number of returned schemas
            - totalCount (int): Total schemas in repository
            - offset (int): Current pagination offset
            - partition (str): Current data partition
            - filteredCount (int): Number of schemas after filtering
            - query (str): Original text query if provided

    Example Usage:
        # Find schemas with version 1.1.0
        schema_search(version_pattern="1.1.0")
        
        # Find schemas about pressure in SHARED scope
        schema_search(
            text="pressure",
            filter={"scope": "SHARED"}
        )
        
        # Find schemas from multiple authorities
        schema_search(
            filter={
                "authority": ["osdu", "lab"],
                "status": "PUBLISHED"
            }
        )
        
        # Find schemas with 1.1.* versions across all scopes
        schema_search(
            version_pattern="1.1.*",
            filter={"scope": ["SHARED", "INTERNAL"]},
            limit=200
        )
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = SchemaClient(config, auth)
    
    # Default search fields if not provided
    if search_in is None:
        search_in = ["title", "description", "properties"]
    
    # Initialize filter if not provided
    filter = filter or {}
    
    # Analyze what can be server-side filtered
    server_filters = {}
    client_filters = {}
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Process server-side filtering
        # These are filters that can be directly passed to the API
        if isinstance(filter.get("authority"), str):
            server_filters["authority"] = filter["authority"]
        if isinstance(filter.get("source"), str):
            server_filters["source"] = filter["source"]
        if isinstance(filter.get("entity"), str):
            server_filters["entityType"] = filter["entity"]
        if isinstance(filter.get("status"), str):
            server_filters["status"] = filter["status"]
        if isinstance(filter.get("scope"), str):
            server_filters["scope"] = filter["scope"]
            
        # Collect filters that need client-side processing
        # These include array filters and other advanced criteria
        for key, value in filter.items():
            if key in ["authority", "source", "entity", "status", "scope"] and isinstance(value, list):
                client_filters[key] = value
            elif key not in ["authority", "source", "entity", "status", "scope"]:
                client_filters[key] = value
        
        # Apply server-side filtering through the API
        logger.info(f"Executing schema list with server filters: {server_filters}")
        api_limit = min(1000, limit * 2)  # Request more to account for client filtering
        
        try:
            # Make API request with server-side filters using search_schemas which internally redirects
            # to list_schemas with the appropriate parameters - this ensures forward compatibility
            # if a dedicated search endpoint is added in the future
            response = await client.search_schemas(
                filter_criteria=server_filters,
                latest_version=latest_version,
                limit=api_limit,
                offset=offset
            )
            
            # Extract schemas from response - API returns "schemaInfos" but we map to "schemas" for consistency
            schemas = response.get("schemaInfos", [])
            if not schemas:
                # Fallback - though schemaInfos is the expected field name from the API
                schemas = response.get("schemas", [])
                
            logger.info(f"Retrieved {len(schemas)} schemas from API response")
            
        except Exception as e:
            logger.error(f"Error during schema search: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve schemas: {str(e)}",
                "partition": partition
            }
        
        total_count = response.get("totalCount", len(schemas))
        
        logger.info(f"Retrieved {len(schemas)} schemas from server, applying client-side filtering")
        
        # Apply client-side filtering
        filtered_schemas = []
        for schema in schemas:
            if _matches_client_filters(schema, client_filters, version_pattern):
                # If text search is enabled, check if schema matches
                if text:
                    matches = await _matches_text_search(schema, text, search_in, include_content, client)
                    if not matches:
                        continue
                
                # Add schema to filtered results
                filtered_schemas.append(schema)
                
                # Fetch full schema content if requested
                if include_content and "id" in schema.get("schemaIdentity", {}):
                    schema_id = schema["schemaIdentity"]["id"]
                    try:
                        schema_content = await client.get_schema(schema_id)
                        schema["schemaContent"] = schema_content.get("schema", {})
                    except Exception as e:
                        logger.warning(f"Failed to fetch schema content for {schema_id}: {e}")
        
        # Apply sorting if needed
        if sort_by:
            filtered_schemas = _sort_schemas(filtered_schemas, sort_by, sort_order)
        
        # Apply pagination
        start_idx = 0
        end_idx = min(limit, len(filtered_schemas))
        paginated_schemas = filtered_schemas[start_idx:end_idx]
        
        # Build response
        result = {
            "success": True,
            "schemas": paginated_schemas,
            "count": len(paginated_schemas),
            "totalCount": total_count,  # Note: This is approximate due to client filtering
            "offset": offset,
            "partition": partition,
            "filteredCount": len(filtered_schemas),  # Additional info for transparency
            "query": text if text else None  # Include search query for reference
        }
        
        logger.info(
            "Schema search completed successfully",
            extra={
                "requested": api_limit,
                "retrieved": len(schemas),
                "filtered": len(filtered_schemas),
                "returned": len(paginated_schemas)
            }
        )
        
        return result
        
    finally:
        await client.close()


def _matches_client_filters(schema: Dict, filters: Dict, version_pattern: Optional[str]) -> bool:
    """Apply client-side filters to a schema."""
    # Extract schema identity for easier access
    schema_identity = schema.get("schemaIdentity", {})
    
    # Check array-based filters
    for key, values in filters.items():
        if not isinstance(values, list):
            continue
            
        if key == "authority" and schema_identity.get("authority") not in values:
            return False
        elif key == "source" and schema_identity.get("source") not in values:
            return False
        elif key == "entity" and schema_identity.get("entityType") not in values:
            return False
        elif key == "status" and schema.get("status") not in values:
            return False
        elif key == "scope" and schema.get("scope") not in values:
            return False
    
    # Check version pattern if provided
    if version_pattern:
        major = schema_identity.get("schemaVersionMajor", 0)
        minor = schema_identity.get("schemaVersionMinor", 0)
        patch = schema_identity.get("schemaVersionPatch", 0)
        version_str = f"{major}.{minor}.{patch}"
        
        if not fnmatch.fnmatch(version_str, version_pattern):
            return False
    
    return True


async def _matches_text_search(
    schema: Dict, 
    text: str, 
    search_fields: List[str],
    include_content: bool,
    client: SchemaClient
) -> bool:
    """Check if schema matches text search criteria."""
    # Convert to lowercase for case-insensitive search
    text_lower = text.lower()
    
    # Search in schema metadata
    schema_identity = schema.get("schemaIdentity", {})
    
    # Check in identity fields
    if "id" in search_fields and schema_identity.get("id", "").lower().find(text_lower) != -1:
        return True
    if "authority" in search_fields and schema_identity.get("authority", "").lower().find(text_lower) != -1:
        return True
    if "source" in search_fields and schema_identity.get("source", "").lower().find(text_lower) != -1:
        return True
    if "entityType" in search_fields and schema_identity.get("entityType", "").lower().find(text_lower) != -1:
        return True
    
    # Need to fetch full schema if searching in content
    if any(field in search_fields for field in ["title", "description", "properties", "content"]):
        if include_content and "schemaContent" in schema:
            schema_content = schema["schemaContent"]
        else:
            try:
                schema_id = schema_identity.get("id")
                if not schema_id:
                    return False
                    
                schema_data = await client.get_schema(schema_id)
                schema_content = schema_data.get("schema", {})
            except Exception:
                return False
        
        # Search in schema content fields
        if "title" in search_fields and schema_content.get("title", "").lower().find(text_lower) != -1:
            return True
        if "description" in search_fields and schema_content.get("description", "").lower().find(text_lower) != -1:
            return True
        
        # Search in properties (recursively)
        if "properties" in search_fields:
            properties = schema_content.get("properties", {})
            if _search_in_object(properties, text_lower):
                return True
    
    return False


def _search_in_object(obj: Dict, text: str) -> bool:
    """Recursively search for text in a nested object."""
    if not isinstance(obj, dict):
        return False
        
    # Search in current object
    for key, value in obj.items():
        # Check if text is in key
        if text in key.lower():
            return True
            
        # Check if text is in string value
        if isinstance(value, str) and text in value.lower():
            return True
            
        # Recursively check nested objects
        elif isinstance(value, dict):
            if _search_in_object(value, text):
                return True
                
        # Check in list elements
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and _search_in_object(item, text):
                    return True
                elif isinstance(item, str) and text in item.lower():
                    return True
    
    return False


def _sort_schemas(schemas: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
    """Sort schemas by the specified field."""
    # Map sort_by values to actual schema keys
    sort_field_mapping = {
        "dateCreated": "dateCreated",
        "authority": ["schemaIdentity", "authority"],
        "source": ["schemaIdentity", "source"],
        "entityType": ["schemaIdentity", "entityType"],
        "status": "status",
        "scope": "scope",
        "id": ["schemaIdentity", "id"],
        "version": ["schemaIdentity", "schemaVersionMajor", "schemaVersionMinor", "schemaVersionPatch"]
    }
    
    # Get actual field(s) to sort by
    sort_fields = sort_field_mapping.get(sort_by, sort_by)
    
    # Sort schemas
    def _get_sort_key(schema):
        if isinstance(sort_fields, list):
            # For nested fields, navigate through the object
            value = schema
            for field in sort_fields:
                if isinstance(value, dict) and field in value:
                    value = value[field]
                else:
                    # If field doesn't exist, use a default value
                    value = None
                    break
            return value
        else:
            # For direct fields
            return schema.get(sort_fields)
    
    # Sort with None values last
    sorted_schemas = sorted(
        schemas,
        key=lambda s: (_get_sort_key(s) is None, _get_sort_key(s)),
        reverse=(sort_order.upper() == "DESC")
    )
    
    return sorted_schemas
