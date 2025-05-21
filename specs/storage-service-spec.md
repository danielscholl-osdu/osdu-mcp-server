# Specification for OSDU MCP Server (Phase 4: Storage Service)

## Overview

This specification defines the Storage Service integration into the MCP Server, building on patterns established in previous phases with Partition, Legal, Entitlements, and Schema services. The Storage Service is a core component of the OSDU platform that manages record metadata lifecycle, providing AI assistants with capabilities to create, read, update, and delete data records.

## Service Scope

### Included Operations
- Create/update records (requires OSDU_MCP_ENABLE_WRITE_MODE=true)
- Get record by ID (latest version)
- Get record by specific version
- Get record versions
- Query records by kind
- Fetch multiple records
- Delete record (logical deletion, requires OSDU_MCP_ENABLE_DELETE_MODE=true)
- Purge record (physical deletion, requires OSDU_MCP_ENABLE_DELETE_MODE=true)

### Excluded Operations
- Record locking operations
- File association (implemented separately)
- Bulk data import/export
- Schema validation (handled by Schema Service)
- Replay operations (administrative function)

## Service Context

The Storage Service provides the central repository for metadata in the OSDU platform. Each record has:

- **Record Identity**: Uniquely identifies a record with:
  - `id`: Unique identifier following `{data-partition-id}:{object-type}:{uuid}` pattern
  - `kind`: Type of data following `{schema-authority}:{dataset-name}:{record-type}:{version}` pattern
  - `version`: System-generated version number

- **Record Metadata**:
  - `acl`: Access control lists defining viewers and owners
  - `legal`: Legal tags and compliance information
  - `ancestry`: References to parent records
  - `meta`: Additional metadata
  - `tags`: User-defined tags

- **Record Data**: The actual payload containing domain data

- **System Metadata**:
  - `createUser`: User who created the record
  - `createTime`: Creation timestamp
  - `modifyUser`: User who last modified the record
  - `modifyTime`: Last modification timestamp

### Record Lifecycle

Records follow a defined lifecycle:
1. **Creation**: Initial creation with required metadata
2. **Updates**: Create new versions when data changes
3. **Logical Deletion**: Mark as deleted but retain for audit
4. **Physical Deletion**: Permanently remove (destructive)

### Schema Relationship

Records require a schema matching their `kind` value. The schema defines data types and validation rules for the record's `data` property. This relationship connects the Storage and Schema services.

## Tool Specifications

### 1. Create/Update Records Tool

**Purpose**: Create new records or update existing ones

**Tool Name**: `storage_create_update_records`

**Parameters**:
- `records`: Required array of objects - Records to create or update
  - Each record must contain:
    - `kind`: Required string - Kind of data 
    - `acl`: Required object - Access control lists
      - `viewers`: Required array - Groups with read access
      - `owners`: Required array - Groups with write access
    - `legal`: Required object - Legal information
      - `legaltags`: Required array - Legal tag names
      - `otherRelevantDataCountries`: Required array - Relevant countries
    - `data`: Required object - Record payload
  - Optional fields include:
    - `id`: Optional string - Record ID (generated if not provided)
    - `ancestry`: Optional object - Parent record references
    - `meta`: Optional array - Additional metadata
    - `tags`: Optional object - User-defined tags
- `skip_dupes`: Optional boolean - Skip duplicates when updating (default: false)

**Safety**: Requires `OSDU_MCP_ENABLE_WRITE_MODE=true` for record creation and updates

**API Endpoint**:
```http
PUT /api/storage/v2/records
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

[
  {
    "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
    "acl": {
      "viewers": ["data.default.viewers@{partition}.contoso.com"],
      "owners": ["data.default.owners@{partition}.contoso.com"]
    },
    "legal": {
      "legaltags": ["{partition}-test-tag"],
      "otherRelevantDataCountries": ["US"],
      "status": "compliant"
    },
    "data": {
      "Name": "Test Record",
      "Description": "Record for testing"
    }
  }
]
```

**Response**:
```json
{
  "success": true,
  "recordCount": 1,
  "records": [
    {
      "id": "{partition}:reference-data--ProcessingParameterType:12345678",
      "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
      "version": 1622654747428
    }
  ],
  "created": true,
  "write_enabled": true,
  "partition": "{partition}"
}
```

### 2. Get Record Tool

**Purpose**: Retrieve latest version of a record

**Tool Name**: `storage_get_record`

**Parameters**:
- `id`: Required string - Record ID
- `attributes`: Optional array of strings - Specific data fields to return

**API Endpoint**:
```http
GET /api/storage/v2/records/{id}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "record": {
    "id": "{partition}:reference-data--ProcessingParameterType:12345678",
    "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
    "version": 1622654747428,
    "acl": {
      "viewers": ["data.default.viewers@{partition}.contoso.com"],
      "owners": ["data.default.owners@{partition}.contoso.com"]
    },
    "legal": {
      "legaltags": ["{partition}-test-tag"],
      "otherRelevantDataCountries": ["US"],
      "status": "compliant"
    },
    "data": {
      "Name": "Test Record",
      "Description": "Record for testing"
    },
    "createTime": "2023-06-02T18:05:47.428Z",
    "createUser": "user@example.com"
  },
  "partition": "{partition}"
}
```

### 3. Get Record Version Tool

**Purpose**: Retrieve specific version of a record

**Tool Name**: `storage_get_record_version`

**Parameters**:
- `id`: Required string - Record ID
- `version`: Required integer - Record version
- `attributes`: Optional array of strings - Specific data fields to return

**API Endpoint**:
```http
GET /api/storage/v2/records/{id}/{version}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**: Same format as get_record

### 4. List Record Versions Tool

**Purpose**: List all versions of a record

**Tool Name**: `storage_list_record_versions`

**Parameters**:
- `id`: Required string - Record ID

**API Endpoint**:
```http
GET /api/storage/v2/records/versions/{id}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "recordId": "{partition}:reference-data--ProcessingParameterType:12345678",
  "versions": [1622654747428, 1622654802543, 1622654982112],
  "count": 3,
  "partition": "{partition}"
}
```

### 5. Query Records By Kind Tool

**Purpose**: Get record IDs of a specific kind

**Tool Name**: `storage_query_records_by_kind`

**Parameters**:
- `kind`: Required string - Kind to query for
- `limit`: Optional integer - Maximum number of results (default: 10)
- `cursor`: Optional string - Cursor for pagination

**API Endpoint**:
```http
GET /api/storage/v2/query/records?kind={kind}&limit={limit}&cursor={cursor}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "cursor": "cursor-token-for-next-page",
  "results": [
    "{partition}:reference-data--ProcessingParameterType:12345678",
    "{partition}:reference-data--ProcessingParameterType:23456789"
  ],
  "count": 2,
  "partition": "{partition}"
}
```

### 6. Fetch Multiple Records Tool

**Purpose**: Retrieve multiple records at once

**Tool Name**: `storage_fetch_records`

**Parameters**:
- `records`: Required array of strings - Record IDs
- `attributes`: Optional array of strings - Specific data fields to return

**API Endpoint**:
```http
POST /api/storage/v2/query/records
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "records": [
    "{partition}:reference-data--ProcessingParameterType:12345678",
    "{partition}:reference-data--ProcessingParameterType:23456789"
  ],
  "attributes": ["data.Name"]
}
```

**Response**:
```json
{
  "success": true,
  "records": [
    {
      "id": "{partition}:reference-data--ProcessingParameterType:12345678",
      "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
      "version": 1622654747428,
      "data": {
        "Name": "Test Record"
      }
    },
    {
      "id": "{partition}:reference-data--ProcessingParameterType:23456789",
      "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
      "version": 1622654747428,
      "data": {
        "Name": "Another Test Record"
      }
    }
  ],
  "count": 2,
  "invalidRecords": [],
  "partition": "{partition}"
}
```

### 7. Delete Record Tool (Write-Protected)

**Purpose**: Logically delete a record

**Tool Name**: `storage_delete_record`

**Parameters**:
- `id`: Required string - Record ID to delete

**Safety**: Requires `OSDU_MCP_ENABLE_DELETE_MODE=true`

**API Endpoint**:
```http
POST /api/storage/v2/records/{id}:delete
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "deleted": true,
  "id": "{partition}:reference-data--ProcessingParameterType:12345678",
  "write_enabled": true,
  "partition": "{partition}"
}
```

### 8. Purge Record Tool (Write-Protected)

**Purpose**: Physically delete a record

**Tool Name**: `storage_purge_record`

**Parameters**:
- `id`: Required string - Record ID to purge
- `confirm`: Required boolean - Explicit confirmation (must be true)

**Safety**: Requires `OSDU_MCP_ENABLE_DELETE_MODE=true`

**API Endpoint**:
```http
DELETE /api/storage/v2/records/{id}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "purged": true,
  "id": "{partition}:reference-data--ProcessingParameterType:12345678",
  "write_enabled": true,
  "warning": "Record has been permanently deleted",
  "partition": "{partition}"
}
```

## Implementation Requirements

### 1. Service URL Configuration

Update `shared/service_urls.py`:
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    STORAGE = "storage"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.STORAGE: "/api/storage/v2",
}
```

### 2. Storage Client Implementation

Create `shared/clients/storage_client.py`:
```python
"""OSDU Storage service client."""

import os
from typing import Dict, Any, List, Optional, Union

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError, OSMCPValidationError
from ..logging_manager import get_logger

logger = get_logger(__name__)

class StorageClient(OsduClient):
    """Client for OSDU Storage service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize StorageClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.STORAGE)
    
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
    
    async def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override delete to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().delete(full_path, **kwargs)
    
    def validate_record(self, record: Dict[str, Any]) -> None:
        """Validate basic record structure."""
        required_fields = ["kind", "acl", "legal", "data"]
        for field in required_fields:
            if field not in record:
                raise OSMCPValidationError(
                    f"Missing required field '{field}' in record",
                    details=f"Records must contain: {', '.join(required_fields)}"
                )
        
        # Validate ACL
        if "acl" in record:
            if "viewers" not in record["acl"] or "owners" not in record["acl"]:
                raise OSMCPValidationError(
                    "ACL must contain both 'viewers' and 'owners' arrays",
                    details="Access control lists define who can read and modify the record"
                )
        
        # Validate Legal
        if "legal" in record:
            if "legaltags" not in record["legal"] or "otherRelevantDataCountries" not in record["legal"]:
                raise OSMCPValidationError(
                    "Legal must contain both 'legaltags' and 'otherRelevantDataCountries' arrays",
                    details="Legal information is required for compliance"
                )
    
    def check_write_permission(self) -> None:
        """Check if write operations are enabled."""
        if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
            raise OSMCPAPIError(
                "Write operations are disabled",
                status_code=403,
                details="Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable record creation and updates"
            )
            
    def check_delete_permission(self) -> None:
        """Check if delete operations are enabled."""
        if not os.environ.get("OSDU_MCP_ENABLE_DELETE_MODE", "false").lower() == "true":
            raise OSMCPAPIError(
                "Delete operations are disabled",
                status_code=403,
                details="Set OSDU_MCP_ENABLE_DELETE_MODE=true to enable record deletion"
            )
    
    async def create_update_records(self, records: List[Dict[str, Any]], 
                                    skip_dupes: bool = False) -> Dict[str, Any]:
        """Create or update records."""
        # Validate records
        for record in records:
            self.validate_record(record)
        
        # Check write permission for create/update operations
        self.check_write_permission()
        
        params = {}
        if skip_dupes:
            params["skipdupes"] = "true"
        
        logger.info(
            f"Creating/updating {len(records)} records",
            extra={
                "record_count": len(records),
                "operation": "create_update_records",
                "has_ids": bool(record_ids)
            }
        )
        
        return await self.put("/records", json=records, params=params)
```

### 3. Protection Patterns

#### Write Protection Pattern
Create and update operations must follow the write protection pattern:

```python
# For create and update operations
if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
    raise OSMCPAPIError(
        "Write operations are disabled",
        status_code=403,
        details="Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable record creation and updates"
    )
```

#### Delete Protection Pattern
Destructive operations (delete, purge) must follow the delete protection pattern, which is separate from the write protection:

```python
# For delete and purge operations
if not os.environ.get("OSDU_MCP_ENABLE_DELETE_MODE", "false").lower() == "true":
    raise OSMCPAPIError(
        "Destructive operations are disabled",
        status_code=403,
        details="Set OSDU_MCP_ENABLE_DELETE_MODE=true to enable record deletion"
    )
```

### 4. Tool Implementations

Implement tools in `tools/storage/` directory following the established pattern:

```python
# Example: tools/storage/get_record.py
"""Tool for getting a record by ID."""

from typing import Dict, List, Optional
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import (
    OSMCPError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)

@handle_osdu_exceptions
async def storage_get_record(id: str, attributes: Optional[List[str]] = None) -> Dict:
    """Get the latest version of a record by ID.
    
    Args:
        id: Record ID
        attributes: Optional data fields to return
        
    Returns:
        Dictionary containing record information
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)
    
    try:
        # Prepare query parameters
        params = {}
        if attributes:
            params["attribute"] = attributes
        
        # Get the record
        response = await client.get(f"/records/{id}", params=params)
        
        # Build response
        result = {
            "success": True,
            "record": response,
            "partition": config.get("server", "data_partition")
        }
        
        logger.info(
            f"Retrieved record {id}",
            extra={
                "record_id": id,
                "operation": "get_record"
            }
        )
        
        return result
        
    finally:
        await client.close()
```

### 5. Testing Requirements

#### Unit Tests
- Test record validation logic
- Test write permission checking
- Test record operations with mocked responses
- Test error handling scenarios

#### Security Tests
- Verify write protection works
- Test ACL enforcement  
- Test permission boundaries

### 6. Error Handling

All tools should handle:
- 401: Authentication failures
- 403: Authorization failures
- 404: Record not found
- 400: Invalid record format
- 409: Record conflicts

For Storage Service specific errors:
- Record schema validation failures
- Legal tag compliance issues
- ACL group validation errors
- Record lifecycle conflicts

## Response Design

### AI-Optimized Structures

```json
// Get Record Response
{
  "success": true,
  "record": {
    "id": "opendes:well:12345",
    "kind": "osdu:wks:well:1.0.0",
    "version": 1622654747428,
    "data": {
      "Name": "Test Well",
      "Description": "Well for testing"
    },
    // Other record fields...
  },
  "partition": "opendes"
}

// Create Records Response
{
  "success": true,
  "recordCount": 2,
  "records": [
    {
      "id": "opendes:well:12345",
      "kind": "osdu:wks:well:1.0.0",
      "version": 1622654747428
    },
    {
      "id": "opendes:well:67890",
      "kind": "osdu:wks:well:1.0.0",
      "version": 1622654747430
    }
  ],
  "created": true,
  "write_enabled": true, 
  "partition": "opendes"
}

// Error Response 
{
  "success": false,
  "error": "Write operations disabled",
  "details": "Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable",
  "operation": "create_update_records"
}
```

## Special Considerations for the Storage Service

### Separate Controls for Write and Delete Operations
- Create/update operations are controlled by OSDU_MCP_ENABLE_WRITE_MODE=true
- Delete/purge operations are controlled by a separate OSDU_MCP_ENABLE_DELETE_MODE=true flag
- This provides more granular control over data lifecycle operations
- Environments can be configured to allow creation but prevent deletion
- Both flags are false by default, requiring explicit enablement

### Schema Validation
- Records must comply with schemas registered in the Schema Service
- The Storage Service performs schema validation on create/update
- Tools should provide helpful messages for schema validation failures

### Legal Compliance
- All records must have valid legal tags
- Tools should check for legal tag compliance

### Access Control
- ACL validation ensures all groups exist
- Tool error messages for non-existent groups

### Performance Considerations
- Batch operations for multiple records
- Pagination for large result sets
- Attribute filtering to reduce payload size

### Integration with Other Services
- Legal Service for tag validation
- Schema Service for validation rules
- Entitlements Service for ACL enforcement

## Success Criteria

- [ ] Service URL added to central management
- [ ] StorageClient implementation complete
- [ ] All read operations functional
- [ ] Create/update operations require OSDU_MCP_ENABLE_WRITE_MODE=true
- [ ] Delete/purge operations require OSDU_MCP_ENABLE_DELETE_MODE=true
- [ ] Record validation working correctly
- [ ] Clear error messages differentiating between write and delete permissions
- [ ] Documentation updated with new environment variables
- [ ] Basic test coverage in place
- [ ] Extended test coverage for edge cases

## References

- [Architecture Decision Records](../docs/adr.md)
- [Storage Service API Documentation](../ai-docs/storage.yaml)
- [Storage Service Concepts](../ai-docs/storage.md)
- [Storage Service API Usage Sample](../ai-docs/storage.http)
- [Schema Service Specification](schema-service-spec.md)
- [Legal Service Specification](legal-service-spec.md)