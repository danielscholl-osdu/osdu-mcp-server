# ADR-013: Service Client Architecture Pattern

## Status
**Accepted** - 2025-05-17

## Context
The Partition Service implementation established patterns for service-specific clients that will be reused across all OSDU service integrations.

## Decision
Implement service-specific clients that inherit from the base `OsduClient` class, adding service-specific logic while reusing common functionality.

## Pattern Details
```python
class PartitionClient(OsduClient):
    def __init__(self, config: ConfigManager, auth_handler: AuthHandler):
        super().__init__(config, auth_handler)
        self._base_path = get_service_base_url(OSMCPService.PARTITION)
    
    async def service_specific_method(self, ...):
        # Custom headers per request
        headers = {"data-partition-id": partition_id}
        # Service-specific error handling
        # Response format validation
```

## Rationale
1. **Code Reuse**: Common HTTP, auth, and error handling in base class
2. **Service Isolation**: Service-specific logic contained in dedicated clients
3. **Flexibility**: Per-request header customization
4. **Maintainability**: Clear separation of concerns

## Consequences
**Positive:**
- Consistent client behavior across services
- Easy to add new service clients
- Reduced code duplication

**Negative:**
- Additional abstraction layer
- Must maintain inheritance hierarchy