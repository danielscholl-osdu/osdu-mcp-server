# Specification for OSDU MCP Server (Phase 2: Legal Service)

## Overview

The Legal Service integration provides tools for managing legal tags in the OSDU platform. Legal tags are critical for data governance, defining legal and compliance attributes for data records. This service follows the write protection pattern established by the Partition Service.

## Service Scope

### Included Operations
- List all legal tags
- Get specific legal tag
- Get allowed property values
- Batch retrieve legal tags
- Search legal tags
- Create legal tag (write-protected)
- Update legal tag (write-protected)
- Delete legal tag (delete-protected)

### Excluded Operations
- Validation endpoints (can be added later if needed)
- Job status endpoints (administrative feature)

## Tool Specifications

### 1. List Legal Tags Tool

**Purpose**: List all legal tags in the current partition

**Tool Name**: `list_legal_tags`

**Parameters**:
- `valid_only`: Optional boolean (default: true) - If true returns only valid tags, if false returns only invalid tags

**API Endpoint**:
```http
GET /api/legal/v1/legaltags
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "legalTags": [
    {
      "name": "opendes-Private-USA-EHC",
      "description": "Private data for USA with EHC compliance",
      "properties": {
        "countryOfOrigin": ["US"],
        "contractId": "A1234",
        "expirationDate": "2028-12-31",
        "securityClassification": "Private",
        "personalData": "No Personal Data",
        "exportClassification": "EAR99"
      }
    }
  ],
  "count": 15,
  "partition": "opendes"
}
```

### 2. Get Legal Tag Tool

**Purpose**: Retrieve a specific legal tag by name

**Tool Name**: `get_legal_tag`

**Parameters**:
- `name`: Required string - Name of the legal tag (can include partition prefix or not)

**API Endpoint**:
```http
GET /api/legal/v1/legaltags/{name}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "legalTag": {
    "name": "opendes-Private-USA-EHC",
    "description": "Private data for USA with EHC compliance",
    "properties": {
      "countryOfOrigin": ["US"],
      "contractId": "A1234",
      "expirationDate": "2028-12-31",
      "securityClassification": "Private",
      "personalData": "No Personal Data",
      "exportClassification": "EAR99"
    }
  },
  "fullName": "opendes-Private-USA-EHC",
  "partition": "opendes"
}
```

### 3. Get Legal Tag Properties Tool

**Purpose**: Get allowed values for legal tag properties

**Tool Name**: `get_legal_tag_properties`

**Parameters**: None

**API Endpoint**:
```http
GET /api/legal/v1/legaltags:properties
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "properties": {
    "countriesOfOrigin": {
      "US": "United States",
      "GB": "United Kingdom",
      "CA": "Canada"
    },
    "securityClassifications": [
      "Public",
      "Private",
      "Confidential",
      "Restricted"
    ],
    "personalDataTypes": [
      "No Personal Data",
      "Personal Data",
      "Sensitive Personal Data"
    ],
    "exportClassifications": [
      "EAR99",
      "5D002",
      "No Export Control"
    ],
    "dataTypes": [
      "Seismic",
      "Well Log",
      "Production Data",
      "Interpreted Data"
    ]
  }
}
```

### 4. Search Legal Tags Tool

**Purpose**: Search legal tags with filter conditions

**Tool Name**: `search_legal_tags`

**Parameters**:
- `query`: Optional string - Filter condition (e.g., "properties.countryOfOrigin:US")
- `valid_only`: Optional boolean (default: true)
- `sort_by`: Optional string - Field to sort by
- `sort_order`: Optional string - "ASC" or "DESC"
- `limit`: Optional integer - Maximum results

**API Endpoint**:
```http
POST /api/legal/v1/legaltags:query
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "queryList": ["properties.countryOfOrigin:US"],
  "operatorList": [],
  "sortBy": "name",
  "sortOrder": "ASC",
  "limit": 100
}
```

**Response**: Same format as list_legal_tags

### 5. Batch Retrieve Legal Tags Tool

**Purpose**: Retrieve multiple legal tags by name

**Tool Name**: `batch_retrieve_legal_tags`

**Parameters**:
- `names`: Required array of strings - Legal tag names (max 25)

**API Endpoint**:
```http
POST /api/legal/v1/legaltags:batchRetrieve
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "names": ["opendes-Private-USA-EHC", "opendes-Public-US-Data"]
}
```

**Response**: Same format as list_legal_tags

### 6. Create Legal Tag Tool (Write-Protected)

**Purpose**: Create a new legal tag

**Tool Name**: `create_legal_tag`

**Parameters**:
- `name`: Required string - Legal tag name (without partition prefix)
- `description`: Required string - Tag description
- `country_of_origin`: Required array of strings - ISO country codes
- `contract_id`: Required string - Associated contract ID
- `expiration_date`: Optional string - YYYY-MM-DD format
- `security_classification`: Required string - Security level
- `personal_data`: Required string - Personal data indicator
- `export_classification`: Required string - Export control classification
- `data_type`: Required string - Type of data
- `extension_properties`: Optional object - Custom properties

**Safety**: Requires `OSDU_MCP_ENABLE_WRITE_MODE=true`

**API Endpoint**:
```http
POST /api/legal/v1/legaltags
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "name": "Private-US-NewData",
  "description": "New private data for US market",
  "properties": {
    "countryOfOrigin": ["US"],
    "contractId": "B5678",
    "expirationDate": "2030-12-31",
    "securityClassification": "Private",
    "personalData": "No Personal Data",
    "exportClassification": "EAR99",
    "dataType": "First Party Data"
  }
}
```

**Response**:
```json
{
  "success": true,
  "legalTag": {
    "name": "opendes-Private-US-NewData",
    "description": "New private data for US market",
    "properties": {
      "countryOfOrigin": ["US"],
      "contractId": "B5678",
      "expirationDate": "2030-12-31",
      "securityClassification": "Private",
      "personalData": "No Personal Data",
      "exportClassification": "EAR99",
      "dataType": "Seismic"
    }
  },
  "created": true,
  "write_enabled": true
}
```

### 7. Update Legal Tag Tool (Write-Protected)

**Purpose**: Update an existing legal tag

**Tool Name**: `update_legal_tag`

**Parameters**:
- `name`: Required string - Legal tag name (with or without partition prefix)
- `description`: Optional string - New description
- `contract_id`: Optional string - New contract ID
- `expiration_date`: Optional string - New expiration date
- `extension_properties`: Optional object - New custom properties

**Safety**: Requires `OSDU_MCP_ENABLE_WRITE_MODE=true`

**API Endpoint**:
```http
PUT /api/legal/v1/legaltags
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "name": "opendes-Private-US-NewData",
  "description": "Updated description",
  "contractId": "B5678-Rev1",
  "expirationDate": "2032-12-31"
}
```

**Response**:
```json
{
  "success": true,
  "legalTag": {
    "name": "opendes-Private-US-NewData",
    "description": "Updated description",
    "properties": {
      "contractId": "B5678-Rev1",
      "expirationDate": "2032-12-31"
    }
  },
  "updated": true,
  "write_enabled": true
}
```

### 8. Delete Legal Tag Tool (Delete-Protected)

**Purpose**: Delete a legal tag (makes associated data invalid)

**Tool Name**: `delete_legal_tag`

**Parameters**:
- `name`: Required string - Legal tag name
- `confirm`: Required boolean - Explicit confirmation

**Safety**: Requires `OSDU_MCP_ENABLE_DELETE_MODE=true`

**API Endpoint**:
```http
DELETE /api/legal/v1/legaltags/{name}
Authorization: Bearer {token}
data-partition-id: {partition}
```

**Response**:
```json
{
  "success": true,
  "deleted": true,
  "name": "opendes-Private-US-OldData",
  "delete_enabled": true,
  "warning": "Associated data is now invalid"
}
```

## Implementation Requirements

### 1. Service URL Configuration

Update `shared/service_urls.py`:
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    LEGAL = "legal"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.LEGAL: "/api/legal/v1",  # Note: v1 for legal service
}
```

### 2. Legal Client Implementation

Create `shared/clients/legal_client.py`:
```python
"""OSDU Legal service client."""

import os
import re
from typing import Dict, Any, List, Optional

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError


class LegalClient(OsduClient):
    """Client for OSDU Legal service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize LegalClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.LEGAL)
    
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
    
    def ensure_full_tag_name(self, name: str) -> str:
        """Ensure legal tag name includes partition prefix."""
        if "@" in name or "-" not in name or name.startswith(self.data_partition):
            return name
        return f"{self.data_partition}-{name}"
    
    def simplify_tag_name(self, name: str) -> str:
        """Remove partition prefix from legal tag name if present."""
        pattern = f"^{self.data_partition}-"
        return re.sub(pattern, "", name)
```

### 3. Dual Protection Pattern

The Legal Service implements dual protection controls for different operation types:

#### Write Operations (Create, Update)
- **Control**: `OSDU_MCP_ENABLE_WRITE_MODE=true`
- **Operations**: create_legal_tag, update_legal_tag
- **Purpose**: Enable data creation and modification

```python
if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
    raise OSMCPAPIError(
        "Legal tag write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations",
        status_code=403
    )
```

#### Delete Operations
- **Control**: `OSDU_MCP_ENABLE_DELETE_MODE=true`
- **Operations**: delete_legal_tag
- **Purpose**: Separate control for destructive operations

```python
if not os.environ.get("OSDU_MCP_ENABLE_DELETE_MODE", "false").lower() == "true":
    raise OSMCPAPIError(
        "Delete operations are disabled. Set OSDU_MCP_ENABLE_DELETE_MODE=true to enable legal tag deletion",
        status_code=403
    )
```

This dual protection allows environments to enable data creation/updates while maintaining strict control over destructive operations.

### 4. Testing Requirements

#### Unit Tests
- Test all read operations with mocked responses
- Test write protection for create/update operations
- Test delete protection for delete operations
- Test dual permission independence (write vs delete controls)
- Test tag name normalization
- Test property validation
- Test batch operations limits

#### Integration Tests  
- Verify API compatibility
- Test write operations when enabled
- Test delete operations when enabled
- Validate error handling for both permission types
- Check response formats

### 5. Documentation Requirements

Update README.md with:
- Legal service overview
- Available tools
- Configuration for write operations
- Legal tag property guidelines
- Warning about data invalidation on delete

### 6. Security Considerations

1. **Audit Logging**: All write operations must be logged
2. **Write Protection**: Disabled by default
3. **Tag Validation**: Ensure required properties are provided
4. **Data Impact**: Clear warnings about tag deletion effects

## Error Handling

All tools should handle:
- 401: Authentication failures
- 403: Authorization failures  
- 404: Tag not found
- 409: Duplicate tag on create
- 400: Invalid tag properties

## Notes

1. Legal tags use v1 API (not v2 like other services)
2. Tag names are automatically prefixed with partition
3. Deleting a tag invalidates all associated data
4. Property values should match allowed values from properties endpoint
5. Write operations are irreversible and affect data governance
6. API property names differ from properties endpoint:
   - Properties endpoint returns `personalDataTypes` but API uses `personalData`
   - Properties endpoint returns `exportClassificationControlNumbers` but API uses `exportClassification`
   - Valid values must still match those from the properties endpoint

## Success Criteria

- [ ] All read operations functional
- [ ] Write protection properly enforced
- [ ] Tag name handling (prefix/simplification) works correctly
- [ ] Batch operations respect limits
- [ ] Clear error messages for invalid operations
- [ ] Comprehensive test coverage
- [ ] Documentation complete