# Minimal Specification for OSDU MCP Server (Phase 2: Entitlements Service - Single Tool)

> Minimal implementation focusing on one entitlements endpoint to debug and establish patterns.

## Overview

This minimal specification implements only the "myPermissions" endpoint - getting groups for the authenticated user. This single tool will establish the pattern for the full entitlements service implementation.

## Single Tool Specification

### Get My Groups Tool

**Purpose**: List groups that the current authenticated user belongs to

**API Endpoint**:
```http
GET /api/entitlements/v2/groups
Authorization: Bearer {token}
Accept: application/json
data-partition-id: {partition}
```

**Tool Name**: `get_my_groups`

**Parameters**: None (uses authenticated user from token)

**Response**:
```json
{
  "success": true,
  "groups": [
    {
      "name": "users",
      "email": "users@opendes.dataservices.energy",
      "description": "All users"
    },
    {
      "name": "users.datalake.viewers",
      "email": "users.datalake.viewers@opendes.dataservices.energy", 
      "description": "Data Lake read access"
    }
  ],
  "count": 2,
  "partition": "opendes"
}
```

## Implementation Requirements

### 1. Service URL Management

Update `shared/service_urls.py`:
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    ENTITLEMENTS = "entitlements"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.ENTITLEMENTS: "/api/entitlements/v2",
}
```

### 2. Create Minimal Entitlements Client

Create `shared/clients/entitlements_client.py`:
```python
"""Minimal OSDU Entitlements service client."""

from typing import Dict, Any

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError


class EntitlementsClient(OsduClient):
    """Minimal client for OSDU Entitlements service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize EntitlementsClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.ENTITLEMENTS)
    
    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override get to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().get(full_path, **kwargs)
    
    async def get_my_groups(self) -> Dict[str, Any]:
        """Get groups for the authenticated user."""
        return await self.get("/groups")
```

### 3. Create Single Tool

Create `tools/entitlements/get_my_groups.py`:
```python
"""Tool for getting current user's groups."""

from typing import Dict
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.entitlements_client import EntitlementsClient
from ...shared.exceptions import (
    OSMCPError,
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def get_my_groups() -> Dict:
    """Get groups for the current authenticated user.
    
    Returns:
        Dictionary containing group information with the following structure:
        {
            "success": bool,
            "groups": [
                {
                    "name": str,
                    "email": str,
                    "description": str
                }
            ],
            "count": int,
            "partition": str
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = EntitlementsClient(config, auth)
    
    try:
        # Get current partition
        partition = config.get("server", "data_partition")
        
        # Get user's groups
        response = await client.get_my_groups()
        
        # Process response
        groups = response.get("groups", [])
        
        # Build simplified response
        result = {
            "success": True,
            "groups": groups,
            "count": len(groups),
            "partition": partition
        }
        
        logger.info(
            "Retrieved user groups successfully",
            extra={
                "count": len(groups),
                "partition": partition
            }
        )
        
        return result
        
    finally:
        await client.close()
```

### 4. Tool Registration

Update `tools/entitlements/__init__.py`:
```python
"""OSDU Entitlements service tools - minimal version."""

from .get_my_groups import get_my_groups

__all__ = [
    "get_my_groups"
]
```

Update `server.py`:
```python
from .tools.entitlements import (
    get_my_groups
)

# Register entitlements tools
mcp.tool()(get_my_groups)
```

## Testing Approach

### 1. Direct API Test
First verify the API works directly:
```bash
curl -X GET "{{ENTITLEMENTS_HOST}}/groups" \
  -H "Authorization: Bearer {{access_token}}" \
  -H "Accept: application/json" \
  -H "data-partition-id: {{DATA_PARTITION}}"
```

### 2. Unit Test
Create `tests/tools/entitlements/test_get_my_groups.py`:
```python
"""Tests for get_my_groups tool."""

import pytest
from aioresponses import aioresponses

from osdu_mcp_server.tools.entitlements import get_my_groups


@pytest.mark.asyncio
async def test_get_my_groups_success():
    """Test successful retrieval of user groups."""
    mock_response = {
        "groups": [
            {
                "name": "users",
                "email": "users@opendes.dataservices.energy",
                "description": "All users"
            }
        ]
    }
    
    with aioresponses() as mocked:
        mocked.get(
            "https://test.osdu.com/api/entitlements/v2/groups",
            payload=mock_response
        )
        
        result = await get_my_groups()
        
        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["groups"]) == 1
        assert result["groups"][0]["name"] == "users"
```

## Implementation Steps

1. Create service URL entry
2. Create minimal entitlements client
3. Create get_my_groups tool
4. Register tool in server
5. Test with real API
6. Debug any issues
7. Build from this working foundation

## Success Criteria

This minimal implementation is successful when:
- [ ] Tool registers without "undefined" error
- [ ] API call succeeds with proper authentication
- [ ] Response is properly formatted
- [ ] Errors are handled gracefully
- [ ] Tests pass

## Next Steps

Once this single tool works:
1. Add group simplification helpers
2. Add member format detection
3. Implement remaining tools
4. Add write protection
5. Complete full specification

This minimal approach should help isolate and resolve the registration issues before building the complete service.