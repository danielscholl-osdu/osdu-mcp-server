# ADR-009: Service URL Management

## Status
**Accepted** - 2025-05-16

## Context
OSDU services expose their APIs at different base URLs with varying version patterns. For example:
- Storage: `/api/storage/v2`
- Search: `/api/search/v2`
- Legal: `/api/legal/v1` (uses v1, not v2)
- Schema: `/api/schema-service/v1`

The health check and other tools need to know the correct endpoint paths for each service. Hardcoding these paths throughout the codebase would lead to maintenance issues.

## Decision
Implement a **centralized service URL configuration system** using an enum-based approach with a mapping of service identifiers to their base URLs.

## Rationale
1. **Central Management**: All service URLs in one place
2. **Type Safety**: Enum prevents typos in service names
3. **Flexibility**: Easy to add new services or update versions
4. **Discoverability**: Clear which services are supported
5. **Testability**: Easy to mock service endpoints

## Implementation
```python
class OSMCPService(Enum):
    """OSDU service identifiers."""
    STORAGE = "storage"
    SEARCH = "search"
    LEGAL = "legal"
    
SERVICE_BASE_URLS = {
    OSMCPService.STORAGE: "/api/storage/v2",
    OSMCPService.SEARCH: "/api/search/v2",
    OSMCPService.LEGAL: "/api/legal/v1",
}

def get_service_info_endpoint(service: OSMCPService) -> str:
    """Get the info endpoint for a service."""
    return f"{SERVICE_BASE_URLS[service]}/info"
```

## Alternatives Considered
1. **Configuration File**
   - **Pros**: Runtime configurable
   - **Cons**: Another config to manage, potential errors
   - **Decision**: Over-engineering for static endpoints

2. **Hardcoded in Each Tool**
   - **Pros**: Simple, no abstraction
   - **Cons**: Duplication, maintenance nightmare
   - **Decision**: Too error-prone

3. **Service Discovery**
   - **Pros**: Dynamic, always current
   - **Cons**: Complex, requires discovery endpoint
   - **Decision**: OSDU doesn't provide this

## Consequences
**Positive:**
- Service endpoints are consistently managed
- Easy to identify version mismatches
- New services can be added easily
- Clear documentation of supported services

**Negative:**
- Additional abstraction layer
- Must update when service versions change
- Assumes static endpoint patterns

## Updates
- Documented adding new services (Partition)

## Success Criteria
- All service endpoints defined in one location
- No hardcoded URLs in tools
- Easy to add new services
- Clear which version each service uses