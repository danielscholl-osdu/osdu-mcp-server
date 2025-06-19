# Specification for OSDU MCP Server (Phase 5: Search Service)

## Overview

This specification defines the Search Service integration into the MCP Server, following the proven patterns from the OSDU CLI while adding AI-optimized guidance through prompts. The Search Service provides access to OSDU's Elasticsearch-based search capabilities through simple, focused tools.

## Service Scope

### Included Operations
- General query search with Elasticsearch syntax
- ID-specific record searches  
- Kind-specific record discovery
- Search guidance and query examples

### Excluded Operations
- Index management operations
- Search template management
- Real-time search subscriptions
- Complex spatial queries (future enhancement)

## Design Approach

**CLI-Inspired with MCP Enhancements**

This service follows the proven CLI pattern with three core search commands, enhanced with AI-friendly guidance prompts. This approach:
- Leverages proven CLI patterns for reliability
- Provides direct access to Elasticsearch query capabilities
- Offers guidance for query construction without abstraction layers
- Maintains consistency with other OSDU MCP service specifications

## Prompt Specification

### Search Guide Prompt

**Purpose**: Provide query syntax guidance and search patterns

**Prompt Name**: `guide_search_patterns`

**Parameters**: None

**Response Content**:
```markdown
# OSDU Search Patterns Guide

## Available Search Tools

- **search_query**: General search with Elasticsearch syntax
- **search_by_id**: Find specific records by ID
- **search_by_kind**: Find all records of specific type

## Quick Start Examples

### Text Search
```python
search_query(query="well*")
search_query(query="(well AND log)")
```

### Field Search  
```python
search_query(query="data.UWI:\"8690\"")
search_query(query="data.Name:*test*")
search_query(query="data.SpudDate:[2020-01-01 TO 2023-12-31]")
```

### ID Search
```python
search_by_id(id="opendes:reference-data:12345")
```

### Kind Search
```python
search_by_kind(kind="*:osdu:well:*")
search_by_kind(kind="opendes:osdu:wellbore:1.0.0")
```

## Common Query Patterns

### Boolean Operators
- AND: `(data.A:"value1") AND (data.B:"value2")`
- OR: `data.Field:("value1" OR "value2")`
- NOT: `data.Field:* AND NOT data.Field:"excluded"`

### Wildcards
- Single character: `data.Code:?00`
- Multiple characters: `data.Name:well*`
- Partial match: `data.Description:*offshore*`

### Range Queries
- Numeric: `data.Depth:[1000 TO 5000]`
- Date: `data.SpudDate:[2020-01-01 TO 2023-12-31]`
- Exclusive: `data.Value:{100 TO 200}`

### Common Fields
- `data.UWI` - Unique Well Identifier
- `data.WellID` - Well reference
- `data.Name` - Record name
- `data.SpudDate` - Well spud date
- `id` - Record identifier

## Multi-Step Workflows

1. **Explore Data**: Start with `search_by_kind(kind="*:*:*:*", limit=5)` to see available types
2. **Focus Search**: Use discovered kinds in targeted searches
3. **Field Discovery**: Examine results to find searchable field paths
4. **Refine Query**: Build specific field queries using discovered paths
```

## Tool Specifications

### 1. General Query Tool

**Purpose**: Execute search queries using Elasticsearch syntax

**Tool Name**: `search_query`

**Parameters**:
- `query`: Required string - Elasticsearch query syntax
- `kind`: Optional string - Kind pattern to search (default: "*:*:*:*")
- `limit`: Optional integer - Maximum results (default: 50, max: 1000)
- `offset`: Optional integer - Pagination offset (default: 0)

**API Endpoint**:
```http
POST /api/search/v2/query
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
  "query": "data.ID:(\"qatest\")",
  "limit": 50,
  "offset": 0
}
```

**Request Schema**:
```json
{
  "kind": "string (required)",
  "query": "string (optional)",
  "limit": "integer (optional, default: 50)",
  "offset": "integer (optional, default: 0)",
  "returnedFields": "array of strings (optional)",
  "sort": {
    "field": ["string"],
    "order": ["ASC|DESC"]
  },
  "trackTotalCount": "boolean (optional)"
}
```

**Examples**:
```python
# Text search
search_query(query="well*")

# Field search
search_query(query="data.UWI:\"8690\"")

# Boolean query
search_query(query="(data.Type:\"well\") AND (data.Status:\"active\")")

# With specific kind
search_query(
    query="data.ID:(\"qatest\")",
    kind="osdu:wks:reference-data--ProcessingParameterType:1.0.0",
    limit=1
)
```

**OSDU API Response**:
```json
{
  "results": [
    {
      "id": "opendes:reference-data:12345",
      "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
      "version": 123456789,
      "acl": {
        "viewers": ["data.default.viewers@opendes.dataservices.energy"],
        "owners": ["data.default.owners@opendes.dataservices.energy"]
      },
      "legal": {
        "legaltags": ["opendes-Public-USA-EHC"],
        "otherRelevantDataCountries": ["US"]
      },
      "data": {
        "ID": "qatest",
        "Name": "QA Test Parameter",
        "Description": "Test processing parameter for QA"
      },
      "createTime": "2023-06-02T18:05:47.428Z",
      "createUser": "user@example.com",
      "modifyTime": "2023-06-02T18:05:47.428Z",
      "modifyUser": "user@example.com"
    }
  ],
  "totalCount": 1,
  "aggregations": []
}
```

**MCP Tool Response**:
```json
{
  "success": true,
  "results": [
    {
      "id": "opendes:reference-data:12345",
      "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
      "data": {
        "ID": "qatest",
        "Name": "QA Test Parameter",
        "Description": "Test processing parameter for QA"
      },
      "createTime": "2023-06-02T18:05:47.428Z"
    }
  ],
  "totalCount": 1,
  "searchMeta": {
    "query_executed": "data.ID:(\"qatest\")",
    "execution_time_ms": 125
  },
  "partition": "opendes"
}
```

### 2. Search by ID Tool

**Purpose**: Find specific records by ID

**Tool Name**: `search_by_id`

**Parameters**:
- `id`: Required string - Record ID to search for
- `limit`: Optional integer - Maximum results (default: 10)

**API Endpoint**:
```http
POST /api/search/v2/query
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "kind": "*:*:*:*",
  "query": "id:(\"opendes:reference-data:12345\")",
  "limit": 10
}
```

**Examples**:
```python
# Find specific record
search_by_id(id="opendes:reference-data:12345")

# Multiple possible matches
search_by_id(id="*:reference-data:12345", limit=5)
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "id": "opendes:reference-data:12345",
      "kind": "opendes:osdu:reference-data:1.0.0",
      "data": {
        "Name": "Test Record",
        "ID": "qatest"
      }
    }
  ],
  "totalCount": 1,
  "searchMeta": {
    "query_executed": "id:\"opendes:reference-data:12345\"",
    "execution_time_ms": 89
  },
  "partition": "opendes"
}
```

### 3. Search by Kind Tool

**Purpose**: Find all records of specific type

**Tool Name**: `search_by_kind`

**Parameters**:
- `kind`: Required string - Kind pattern (supports wildcards)
- `limit`: Optional integer - Maximum results (default: 100, max: 1000)
- `offset`: Optional integer - Pagination offset (default: 0)

**API Endpoint**:
```http
POST /api/search/v2/query
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "kind": "*:osdu:well:*",
  "query": "",
  "limit": 100,
  "offset": 0
}
```

**Examples**:
```python
# Find all wells
search_by_kind(kind="*:osdu:well:*")

# Find specific version
search_by_kind(kind="opendes:osdu:wellbore:1.0.0")

# Explore all data types
search_by_kind(kind="*:*:*:*", limit=10)
```

**Response**:
```json
{
  "success": true,
  "results": [...],
  "totalCount": 1543,
  "searchMeta": {
    "query_executed": "kind:*:osdu:well:*",
    "execution_time_ms": 89
  },
  "partition": "opendes"
}
```

## Implementation Requirements

### 1. Service URL Configuration

Update `shared/service_urls.py`:
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    SEARCH = "search"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.SEARCH: "/api/search/v2",
}
```

### 2. Search Client Implementation

Create `shared/clients/search_client.py`:

```python
"""OSDU Search service client."""

from typing import Dict, Any
from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..logging_manager import get_logger

logger = get_logger(__name__)

class SearchClient(OsduClient):
    """Client for OSDU Search service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize SearchClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.SEARCH)
    
    async def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override post to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().post(full_path, **kwargs)
    
    async def search_query(self, query: str, kind: str = "*:*:*:*",
                          limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Execute general search query."""
        payload = {
            "kind": kind,
            "query": query,
            "limit": limit,
            "offset": offset
        }
        
        logger.info(
            f"Executing search query: {query}",
            extra={
                "query": query,
                "kind": kind,
                "limit": limit,
                "operation": "search_query"
            }
        )
        
        response = await self.post("/query", json=payload)
        return self._standardize_response(response, query)
    
    async def search_by_id(self, record_id: str, limit: int = 10) -> Dict[str, Any]:
        """Execute ID-specific search."""
        query = f'id:("{record_id}")'
        payload = {
            "kind": "*:*:*:*",
            "query": query,
            "limit": limit
        }
        
        logger.info(
            f"Executing ID search: {record_id}",
            extra={
                "record_id": record_id,
                "operation": "search_by_id"
            }
        )
        
        response = await self.post("/query", json=payload)
        return self._standardize_response(response, query)
    
    async def search_by_kind(self, kind: str, limit: int = 100, 
                           offset: int = 0) -> Dict[str, Any]:
        """Execute kind-specific search."""
        payload = {
            "kind": kind,
            "query": "",
            "limit": limit,
            "offset": offset
        }
        
        logger.info(
            f"Executing kind search: {kind}",
            extra={
                "kind": kind,
                "limit": limit,
                "operation": "search_by_kind"
            }
        )
        
        response = await self.post("/query", json=payload)
        return self._standardize_response(response, f"kind:{kind}")
    
    def _standardize_response(self, osdu_response: Dict[str, Any], 
                            query: str) -> Dict[str, Any]:
        """Convert OSDU Search API response to MCP format."""
        # Filter OSDU response to include only essential fields for AI consumption
        simplified_results = []
        for result in osdu_response.get("results", []):
            simplified_result = {
                "id": result.get("id"),
                "kind": result.get("kind"),
                "data": result.get("data", {}),
                "createTime": result.get("createTime")
            }
            # Optionally include version for debugging
            if "version" in result:
                simplified_result["version"] = result["version"]
            simplified_results.append(simplified_result)
        
        return {
            "success": True,
            "results": simplified_results,
            "totalCount": osdu_response.get("totalCount", 0),
            "searchMeta": {
                "query_executed": query,
                "execution_time_ms": osdu_response.get("took", 0)
            },
            "partition": self.data_partition
        }
```

### 3. Prompt Implementation

Create `prompts/guide_search_patterns.py`:

```python
"""Search patterns guidance prompt."""

from typing import List
from mcp.types import Message
from ..shared.exceptions import handle_osdu_exceptions
from ..shared.logging_manager import get_logger

logger = get_logger(__name__)

@handle_osdu_exceptions
async def guide_search_patterns() -> List[Message]:
    """Provide search pattern guidance for OSDU operations.
    
    Returns:
        List[Message]: Search pattern guidance content
    """
    content = """# OSDU Search Patterns Guide

## Available Search Tools

- **search_query**: General search with Elasticsearch syntax
- **search_by_id**: Find specific records by ID
- **search_by_kind**: Find all records of specific type

## Quick Start Examples

### Text Search
```python
search_query(query="well*")
search_query(query="(well AND log)")
```

### Field Search  
```python
search_query(query="data.UWI:\\"8690\\"")
search_query(query="data.Name:*test*")
search_query(query="data.SpudDate:[2020-01-01 TO 2023-12-31]")
```

### ID Search
```python
search_by_id(id="opendes:reference-data:12345")
```

### Kind Search
```python
search_by_kind(kind="*:osdu:well:*")
search_by_kind(kind="opendes:osdu:wellbore:1.0.0")
```

## Common Query Patterns

### Boolean Operators
- AND: `(data.A:\\"value1\\") AND (data.B:\\"value2\\")`
- OR: `data.Field:(\\"value1\\" OR \\"value2\\")`
- NOT: `data.Field:* AND NOT data.Field:\\"excluded\\"`

### Wildcards
- Single character: `data.Code:?00`
- Multiple characters: `data.Name:well*`
- Partial match: `data.Description:*offshore*`

### Range Queries
- Numeric: `data.Depth:[1000 TO 5000]`
- Date: `data.SpudDate:[2020-01-01 TO 2023-12-31]`
- Exclusive: `data.Value:{100 TO 200}`

### Common Fields
- `data.UWI` - Unique Well Identifier
- `data.WellID` - Well reference
- `data.Name` - Record name
- `data.SpudDate` - Well spud date
- `id` - Record identifier

## Multi-Step Workflows

1. **Explore Data**: Start with `search_by_kind(kind="*:*:*:*", limit=5)` to see available types
2. **Focus Search**: Use discovered kinds in targeted searches
3. **Field Discovery**: Examine results to find searchable field paths
4. **Refine Query**: Build specific field queries using discovered paths
"""
    
    logger.info(
        "Generated search patterns guidance",
        extra={
            "operation": "guide_search_patterns"
        }
    )
    
    return [
        {
            "role": "user",
            "content": content
        }
    ]
```

## Testing Strategy

### Tool Testing (Following ADR-010)

```python
# tests/tools/search/test_search_query.py
import pytest
from aioresponses import aioresponses
import re

async def test_search_query_returns_expected_structure():
    """Test that search_query returns properly structured response."""
    with aioresponses() as mock:
        mock.post(
            url=re.compile(r".*/api/search/v2/query"),
            payload={
                "results": [
                    {
                        "id": "test:well:123",
                        "kind": "test:osdu:well:1.0.0",
                        "data": {"Name": "Test Well"}
                    }
                ],
                "totalCount": 1
            }
        )
        
        result = await search_query("data.Name:*test*")
        
        assert result["success"] is True
        assert "results" in result
        assert "totalCount" in result
        assert "searchMeta" in result
        assert result["searchMeta"]["query_executed"] == "data.Name:*test*"

async def test_search_by_id_constructs_correct_query():
    """Test that search_by_id constructs proper ID query."""
    with aioresponses() as mock:
        mock.post(
            url=re.compile(r".*/api/search/v2/query"),
            payload={"results": [], "totalCount": 0}
        )
        
        await search_by_id("test:record:123")
        
        # Verify the query was constructed correctly
        assert mock.requests[('POST', re.compile(r".*/api/search/v2/query"))][0].kwargs['json']['query'] == 'id:("test:record:123")'
```

### Prompt Testing

```python
# tests/prompts/test_guide_search_patterns.py
async def test_guide_search_patterns_returns_message_format():
    """Test that search patterns prompt returns correct Message format."""
    result = await guide_search_patterns()
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert isinstance(result[0]["content"], str)
    assert len(result[0]["content"]) > 0
    assert "search_query" in result[0]["content"]
```

## Error Handling

### Error Contract Mapping (ADR-004)

Map OSDU Search Service errors to standard MCP errors:

| OSDU Status | MCP Error Type | Search Context | Tool Response |
|-------------|----------------|----------------|---------------|
| 400 | OSMCPValidationError | Invalid query syntax | `{"error": "Invalid Elasticsearch query: {details}"}` |
| 404 | OSMCPAPIError | No search results | `{"success": true, "results": [], "totalCount": 0}` |
| 403 | OSMCPAuthError | Search not authorized | `{"error": "Insufficient permissions for search"}` |
| 401 | OSMCPAuthError | Authentication required | `{"error": "Authentication required"}` |
| 413 | OSMCPValidationError | Query too complex | `{"error": "Query exceeds complexity limits"}` |
| 503 | OSMCPAPIError | Elasticsearch unavailable | `{"error": "Search service temporarily unavailable"}` |
| 500 | OSMCPAPIError | Internal search error | `{"error": "Search service error"}` |

### Search-Specific Error Scenarios

Additional error handling for search operations:
- **Malformed queries**: Invalid Elasticsearch syntax or unsupported operators
- **Query timeouts**: Long-running or complex queries exceeding timeout limits
- **Index unavailable**: Elasticsearch index issues or maintenance mode
- **Result set too large**: Queries returning excessive results beyond system limits
- **Query injection**: Potentially unsafe query patterns or reserved characters
- **Kind pattern errors**: Invalid kind syntax or non-existent schema references

### Implementation Pattern

```python
@handle_osdu_exceptions
async def search_query(query: str, kind: str = "*:*:*:*", 
                      limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Execute search query using Elasticsearch syntax."""
    # Standard error handling via decorator
    # Search-specific validation before API call
    # Graceful handling of empty results (not an error)
```

## Performance Considerations

1. **Default Limits**: Reasonable defaults (50-100 records) to prevent large result sets
2. **Pagination**: Support offset-based pagination for large result sets  
3. **Query Validation**: Basic syntax validation before API calls
4. **Result Filtering**: Respect OSDU ACL permissions in results

## Success Criteria

- [ ] Search patterns guidance prompt implemented and functional
- [ ] Three core search tools implemented following CLI patterns
- [ ] Response standardization across all search operations
- [ ] Direct Elasticsearch query support working
- [ ] Error handling with standard patterns
- [ ] Test coverage meeting ADR standards
- [ ] Real use case (HTTP file example) working perfectly
- [ ] Documentation updated with CLI-inspired approach

## Future Enhancements

### Phase 5.1: Extended Search
- Spatial search capabilities (bounding box, distance, polygon)
- Aggregation search for statistics and counts
- Advanced query building helpers

### Phase 5.2: Search Optimization
- Query caching and optimization
- Search result ranking improvements
- Field discovery automation

## References

- [ADR-024: Prompt Implementation Pattern](../docs/adr/024-prompt-implementation-pattern.md)
- [ADR-025: Prompt Naming Convention](../docs/adr/025-prompt-naming-convention.md)
- [Search Service API Documentation](../ai-docs/search.yaml)
- [Search Query Examples](../ai-docs/search.http)
- [CLI Search Implementation](../cli-docs/osdu-cli.xml)
- [Architecture Decision Records](../docs/adr/README.md)