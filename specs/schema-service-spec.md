# Specification for OSDU MCP Server (Phase 3: Schema Service)

## Overview

This specification defines the Schema Service integration into the MCP Server, following patterns established by the Partition and Legal services. The Schema Service enables central management and governance of schemas in the OSDU platform, providing AI assistants with capabilities to discover and retrieve data structures.

## Service Scope

### Included Operations
- List available schemas
- Get specific schema
- Search schemas with filters
- Create schema (write-protected)
- Update schema (write-protected)

### Excluded Operations
- System schema management (admin-only function)
- Schema version comparison
- Client-side schema validation

## Service Context

The Schema Service manages JSON schemas that define data structures within the OSDU platform. Each schema has:

- **Schema Identity**: Uniquely identifies a schema with:
  - `authority`: Entity authority (e.g., "osdu")
  - `source`: Entity source (e.g., "wks")
  - `entityType`: Entity type (e.g., "wellbore")
  - `schemaVersionMajor`: Major version number
  - `schemaVersionMinor`: Minor version number
  - `schemaVersionPatch`: Patch version number
  - `id`: System-generated identifier (e.g., "osdu:wks:wellbore:1.0.0")

- **Schema Info**: Contains metadata about the schema:
  - Schema identity (as above)
  - `createdBy`: User who created the schema
  - `dateCreated`: Creation timestamp
  - `status`: Lifecycle status (DEVELOPMENT, PUBLISHED, OBSOLETE)
  - `scope`: Visibility (INTERNAL, SHARED)
  - `supersededBy`: Reference to newer schema (if obsolete)

- **Schema Content**: The actual JSON Schema definition

### Schema Lifecycle

Schemas follow a defined lifecycle:
1. **DEVELOPMENT**: Initial state, can be modified
2. **PUBLISHED**: Production-ready, immutable
3. **OBSOLETE**: Deprecated but maintained for backward compatibility

### Schema References

Schemas may reference other schemas through JSON Schema `$ref` properties. A self-contained schema has all references embedded within it, while others may require additional schema lookups to fully validate data.

## Tool Specifications

### 1. List Schemas Tool

**Purpose**: List available schemas with optional filtering

**Tool Name**: `schema_list`

**Parameters**:
- `authority`: Optional string - Filter by authority
- `source`: Optional string - Filter by source
- `entity`: Optional string - Filter by entity type
- `status`: Optional string - Schema status
- `scope`: Optional string - Schema scope
- `latest_version`: Optional boolean - Only return latest versions (default: false)
- `limit`: Optional integer - Maximum number of results (default: 10, max 100)
- `offset`: Optional integer - Pagination offset (default: 0)

**Implementation Note**: The actual implementation does not set default values for authority, source, entity, status, or scope parameters. When not provided, the API will return schemas based on user's access rights without filtering, which may include both SHARED and INTERNAL scopes.

**API Endpoint**:
```http
GET /api/schema-service/v1/schema?limit=100&authority=osdu&source=wks&entityType=wellbore
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "schemas": [
    {
      "schemaIdentity": {
        "id": "osdu:wks:wellbore:1.0.0",
        "authority": "osdu",
        "source": "wks",
        "entityType": "wellbore",
        "schemaVersionMajor": 1,
        "schemaVersionMinor": 0,
        "schemaVersionPatch": 0
      },
      "status": "PUBLISHED",
      "scope": "INTERNAL",
      "createdBy": "user@example.com",
      "dateCreated": "2025-01-15T10:30:00Z"
    }
  ],
  "count": 1,
  "totalCount": 15,
  "offset": 0,
  "partition": "opendes"
}
```

**Note**: The API response uses "schemaInfos" as the key for the array of schemas, but this is mapped to "schemas" in the tool's response for consistency.

### 2. Get Schema Tool

**Purpose**: Retrieve complete schema by ID

**Tool Name**: `schema_get`

**Parameters**:
- `id`: Required string - Schema ID (format: authority:source:entityType:majorVersion.minorVersion.patchVersion)

**API Endpoint**:
```http
GET /api/schema-service/v1/schema/{id}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "id": "osdu:wks:wellbore:1.0.0",
  "schemaInfo": {
    "schemaIdentity": {
      "authority": "osdu",
      "source": "wks",
      "entityType": "wellbore",
      "schemaVersionMajor": 1,
      "schemaVersionMinor": 0,
      "schemaVersionPatch": 0,
      "id": "osdu:wks:wellbore:1.0.0"
    },
    "createdBy": "user@example.com",
    "dateCreated": "2025-01-15T10:30:00Z",
    "status": "PUBLISHED",
    "scope": "INTERNAL"
  },
  "schema": {
    "$id": "https://schema.osdu.opengroup.org/json/wks/wellbore.1.0.0.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Wellbore",
    "description": "Wellbore schema definition",
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Wellbore name"
      }
    },
    "required": ["name"]
  },
  "partition": "opendes"
}
```

### 3. Enhanced Schema Search Tool

**Purpose**: Provide advanced schema discovery with rich filtering and text search capabilities

**Tool Name**: `schema_search`

**Parameters**:
- **Text Search Parameters**:
  - `text`: Optional string - Text to search for across schema content and metadata
  - `search_in`: Optional array of strings - Fields to search in (default: ["title", "description", "properties"])
  
- **Version Filtering**:
  - `version_pattern`: Optional string - Version pattern with wildcard support (e.g., "1.1.*")
  
- **Rich Filtering**:
  - `filter`: Optional object - Structured filter criteria
    - `authority`: Optional string or array - Filter by authorities
    - `source`: Optional string or array - Filter by sources
    - `entity`: Optional string or array - Filter by entity types
    - `status`: Optional string or array - Filter by statuses
    - `scope`: Optional string or array - Filter by scopes
  
- **Common Parameters**:
  - `latest_version`: Optional boolean - Only return latest versions (default: false)
  - `limit`: Optional integer - Maximum number of results (default: 100, max 1000)
  - `offset`: Optional integer - Pagination offset (default: 0)
  
- **Advanced Options**:
  - `include_content`: Optional boolean - Include full schema content (default: false)
  - `sort_by`: Optional string - Field to sort by (default: "dateCreated")
  - `sort_order`: Optional string - Sort order "ASC" or "DESC" (default: "DESC")

**Implementation**:
This tool uses GET /schema with server-side filtering for optimal performance, then applies client-side filtering for advanced capabilities not directly supported by the API:

1. Convert filters to API request parameters when possible
2. Perform GET request to /schema endpoint with applicable filters
3. Apply client-side text search across requested fields
4. Apply version pattern matching with wildcard support
5. Apply additional client-side filtering for complex criteria
6. Handle pagination and sorting intelligently

**Example Use Cases**:
- Find all schemas containing "pressure" in their description
- Get all wellbore-related schemas created in the last month
- Find all schemas with version 1.1.* across any authority
- Search for schemas that reference a specific schema ID
- Find all schemas with a specific property pattern

**Response**: Same format as schema_list with optional full schema content

### 4. Create Schema Tool (Write-Protected)

**Purpose**: Create a new schema

**Tool Name**: `schema_create`

**Parameters**:
- `authority`: Required string - Schema authority
- `source`: Required string - Schema source 
- `entity`: Required string - Schema entity type
- `major_version`: Required integer - Major version number
- `minor_version`: Required integer - Minor version number
- `patch_version`: Required integer - Patch version number
- `schema`: Required object - JSON Schema definition
- `status`: Optional string - Schema status (default: "DEVELOPMENT")
- `description`: Optional string - Schema description

**Safety**: Requires `OSDU_MCP_ENABLE_WRITE_MODE=true`

**API Endpoint**:
```http
POST /api/schema-service/v1/schema
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "schemaInfo": {
    "schemaIdentity": {
      "authority": "lab",
      "source": "test",
      "entityType": "testSchema",
      "schemaVersionMajor": 1,
      "schemaVersionMinor": 0,
      "schemaVersionPatch": 0,
      "id": "lab:test:testSchema:1.0.0"
    },
    "status": "DEVELOPMENT"
  },
  "schema": {
    "title": "Test Schema",
    "description": "Schema for testing",
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      }
    },
    "required": ["name"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "created": true,
  "id": "lab:test:testSchema:1.0.0",
  "status": "DEVELOPMENT",
  "write_enabled": true
}
```

### 5. Update Schema Tool (Write-Protected)

**Purpose**: Update an existing schema in DEVELOPMENT status

**Tool Name**: `schema_update`

**Parameters**:
- `id`: Required string - Schema ID to update
- `schema`: Required object - New schema definition
- `status`: Optional string - New schema status (can transition from DEVELOPMENT to PUBLISHED)

**Safety**: Requires `OSDU_MCP_ENABLE_WRITE_MODE=true`

**API Endpoint**:
```http
PUT /api/schema-service/v1/schema
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "schemaInfo": {
    "schemaIdentity": {
      "authority": "lab",
      "source": "test",
      "entityType": "testSchema",
      "schemaVersionMajor": 1,
      "schemaVersionMinor": 0,
      "schemaVersionPatch": 0,
      "id": "lab:test:testSchema:1.0.0"
    },
    "status": "PUBLISHED"
  },
  "schema": {
    "title": "Test Schema",
    "description": "Updated schema definition",
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "description": {
        "type": "string"
      }
    },
    "required": ["name"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "updated": true,
  "id": "lab:test:testSchema:1.0.0",
  "status": "PUBLISHED",
  "write_enabled": true
}
```

## Implementation Requirements

### 1. Service URL Configuration

Update `shared/service_urls.py`:
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    SCHEMA = "schema"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.SCHEMA: "/api/schema-service/v1",
}
```

### 2. Schema Client Implementation

Create `shared/clients/schema_client.py`:
```python
"""OSDU Schema service client."""

import os
from typing import Dict, Any, List, Optional

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError


class SchemaClient(OsduClient):
    """Client for OSDU Schema service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize SchemaClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.SCHEMA)
    
    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override get to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().get(full_path, **kwargs)
    
    async def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override post to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().post(full_path, **kwargs)
    
    async def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override put to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().put(full_path, **kwargs)
    
    async def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """Get schema by ID."""
        return await self.get(f"/schema/{schema_id}")
    
    def format_schema_id(self, authority: str, source: str, entity: str, 
                         major: int, minor: int, patch: int) -> str:
        """Format schema ID from components."""
        return f"{authority}:{source}:{entity}:{major}.{minor}.{patch}"

    async def list_schemas(self, 
                         authority: Optional[str] = None, 
                         source: Optional[str] = None, 
                         entity: Optional[str] = None,
                         status: str = "PUBLISHED",
                         limit: int = 100) -> Dict[str, Any]:
        """List schemas with optional filtering."""
        params = [f"limit={limit}", f"status={status}"]
        
        if authority:
            params.append(f"authority={authority}")
        if source:
            params.append(f"source={source}")
        if entity:
            params.append(f"entityType={entity}")
            
        query_string = "&".join(params)
        return await self.get(f"/schema?{query_string}")
```

### 3. Write Protection Pattern

All write operations (create, update) must follow the unified write protection pattern:

```python
if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
    raise OSMCPAPIError(
        "Schema write operations are disabled",
        status_code=403,
        details="Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations"
    )
```

### 4. Testing Requirements

#### Unit Tests
- Test schema listing with various filters
- Test schema retrieval by ID
- Test write protection for create/update
- Test schema ID formatting

#### Integration Tests
- Verify API compatibility
- Test schema search with complex filters
- Validate error handling
- Check schema lifecycle transitions

### 5. Documentation Requirements

Update README.md with:
- Schema service overview
- Available tools with examples
- Configuration for write operations
- Schema format guidelines

### 6. Security Considerations

1. **Write Protection**: Disabled by default via `OSDU_MCP_ENABLE_WRITE_MODE`
2. **Schema Status Protection**: Only DEVELOPMENT schemas can be modified
3. **Error Context**: Clear, actionable error messages
4. **Group Permissions**: 
   - `service.schema-service.viewers` group for read operations
   - `service.schema-service.editors` group for write operations

## Error Handling

All tools should handle:
- 401: Authentication failures
- 403: Authorization failures  
- 404: Schema not found
- 409: Schema already exists on create
- 400: Invalid schema definition

## Notes

1. Only schemas in DEVELOPMENT status can be modified
2. Transitioning a schema from DEVELOPMENT to PUBLISHED is irreversible
3. Each schema is identified by its unique ID: authority:source:entityType:version
4. Parameter naming follows CLI conventions for consistency
5. The API path structure for get operation uses `/schema/{id}` format

## Success Criteria

- [x] All read operations functional
- [x] Write protection properly enforced
- [x] Schema lifecycle transitions validated
- [x] Clear error messages
- [x] Basic test coverage in place
- [ ] Extended test coverage for all edge cases
- [x] Documentation updated

**Current Status**: Schema service is implemented and integrated with the MCP server. Basic functionality is working, but additional test coverage is needed for edge cases.