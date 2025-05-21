# ADR-020: Unified Write Protection with Dual Permission Model

## Status
**Accepted** - 2025-05-19
**Updated** - 2025-05-20

## Context
The initial implementation used service-specific environment variables for write protection:
- `OSDU_MCP_PARTITION_ALLOW_WRITE` for partition operations
- `OSDU_MCP_LEGAL_ALLOW_WRITE` for legal tag operations
- Future services would require additional variables

This approach led to complexity in configuration and documentation.

With the Storage Service implementation, we identified the need for more granular control over destructive operations, distinguishing between data modification (write) and data destruction (delete).

## Decision
Implement a dual permission model using two unified environment variables:
1. `OSDU_MCP_ENABLE_WRITE_MODE` - Controls write operations (create/update) across all services
2. `OSDU_MCP_ENABLE_DELETE_MODE` - Controls delete operations (delete/purge) across all services

## Implementation

### Write Operations (Create/Update)
```python
def check_write_permission(self) -> None:
    """Check if write operations are enabled."""
    if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable record creation and updates",
            status_code=403
        )

# Usage in create/update operations
self.check_write_permission()
```

### Delete Operations
```python
def check_delete_permission(self) -> None:
    """Check if delete operations are enabled."""
    if not os.environ.get("OSDU_MCP_ENABLE_DELETE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Delete operations are disabled. Set OSDU_MCP_ENABLE_DELETE_MODE=true to enable record deletion",
            status_code=403
        )

# Usage in delete/purge operations
self.check_delete_permission()
```

## Rationale
1. **Operational Safety**: Separate controls for data modification vs. data destruction
2. **Granular Control**: Enable data creation/updates while preventing deletion
3. **Security Enhancement**: Principle of least privilege for destructive operations
4. **Simplified Configuration**: Two unified variables instead of per-service variables
5. **Clear Intent**: Explicit separation of write vs. delete operations
6. **Audit-Friendly**: Clear distinction for compliance and governance

## Use Cases
- **Development Environment**: Enable both write and delete modes for testing
- **Production Environment**: Enable write mode only, disable delete mode
- **Data Migration**: Enable write mode for ingestion, disable delete for safety
- **Read-Only Mode**: Disable both modes for maintenance or investigation

## Migration from ADR-014
This decision supersedes service-specific write protection variables introduced in ADR-014. The migration involves:
1. Updating all write operations to use `OSDU_MCP_ENABLE_WRITE_MODE`
2. Updating all delete operations to use `OSDU_MCP_ENABLE_DELETE_MODE`
3. Updating documentation and specifications
4. Maintaining backward compatibility during transition if needed

## Consequences
**Positive:**
- Enhanced operational safety with granular control
- Clear separation of concerns (write vs. delete)
- Simplified configuration (2 variables vs. N services)
- Consistent behavior across all services
- Better audit trail and governance
- Supports defense-in-depth security model

**Negative:**
- Additional configuration complexity (2 variables instead of 1)
- Less granular service-level control
- Breaking change for existing deployments using service-specific variables
- Requires understanding of dual permission model

## Notes
During implementation, consider supporting both old and new variables temporarily for smooth migration.