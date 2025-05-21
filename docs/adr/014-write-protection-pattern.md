# ADR-014: Write Protection Pattern

## Status
**Accepted** - 2025-05-17

## Context
Destructive operations (CREATE, UPDATE, DELETE) need protection against accidental execution, especially in production environments.

## Decision
Implement environment variable-based write protection with `OSDU_MCP_PARTITION_ALLOW_WRITE` defaulting to `false`.

## Implementation
```python
def _is_write_allowed(self) -> bool:
    return os.environ.get("OSDU_MCP_PARTITION_ALLOW_WRITE", "false").lower() == "true"

# In tools
if not write_enabled:
    return {
        "success": False,
        "error": "Write operations are disabled. Set OSDU_MCP_PARTITION_ALLOW_WRITE=true to enable."
    }
```

## Rationale
1. **Safety First**: Destructive operations disabled by default
2. **Clear Intent**: Explicit environment variable for enabling writes
3. **Consistent Pattern**: Same mechanism across all write operations
4. **Audit Trail**: Clear logging of write attempts

## Consequences
**Positive:**
- Prevents accidental data loss
- Clear error messages
- Easy to enable/disable
- Supports dry-run testing

**Negative:**
- Additional configuration step
- May surprise users expecting write access