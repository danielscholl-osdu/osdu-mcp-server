# ADR-022: Confirmation Requirement Pattern

## Status
**Accepted** - 2025-05-20

## Context
Some operations are extremely destructive and irreversible, such as permanently purging records from the OSDU platform. These operations pose significant risk to data integrity and business continuity if executed accidentally.

Standard permission checks (like `OSDU_MCP_ENABLE_DELETE_MODE`) provide broad operational control but don't protect against accidental execution of specific destructive operations within an authorized context.

## Decision
Implement explicit confirmation requirements for highly destructive operations using a boolean confirmation parameter that must be explicitly set to `true`.

## Implementation

### Confirmation Parameter Pattern
```python
async def storage_purge_record(
    id: str,
    confirm: bool
) -> Dict:
    """Physically delete a record permanently (cannot be restored).
    
    Args:
        id: Required string - Record ID to purge
        confirm: Required boolean - Explicit confirmation (must be true)
    
    Note: Requires OSDU_MCP_ENABLE_DELETE_MODE=true
    """
    # ... tool implementation
```

### Client-Side Validation
```python
async def purge_record(self, id: str, confirm: bool = False) -> Dict[str, Any]:
    """Physically delete a record permanently.
    
    Args:
        id: Record ID to purge
        confirm: Explicit confirmation (must be True)
        
    Raises:
        OSMCPValidationError: If confirmation is not provided
    """
    if not confirm:
        raise OSMCPValidationError(
            "Purge operation requires explicit confirmation. Set confirm=True to proceed with permanent deletion"
        )
    
    # Check delete permission for purge operations
    self.check_delete_permission()
    
    # Proceed with operation
    return await self.delete(f"/records/{id}")
```

### Legal Tag Deletion Example
```python
async def legaltag_delete(
    name: str,
    confirm: bool
) -> Dict:
    """Delete a legal tag.
    
    CAUTION: Deleting a legal tag will make all associated data invalid.
    
    Args:
        name: Legal tag name
        confirm: Explicit confirmation required
    """
    # Check confirmation BEFORE permission checks
    if not confirm:
        raise OSMCPAPIError(
            "Deletion not confirmed. Set confirm=true to delete the legal tag. WARNING: This will invalidate all associated data.",
            status_code=400
        )
    
    # Proceed with delete operation
    # ...
```

## Criteria for Confirmation Requirements

### Operations Requiring Confirmation
1. **Permanent Data Loss**: Operations that permanently destroy data (purge, physical delete)
2. **Cascading Effects**: Operations that affect multiple related records (legal tag deletion)
3. **Irreversible Changes**: Operations that cannot be undone through the API
4. **High Business Impact**: Operations with significant business or compliance implications

### Operations NOT Requiring Confirmation
1. **Logical Operations**: Soft deletes that can be restored
2. **Reversible Changes**: Operations that can be undone (create, update with restore capability)
3. **Low Impact**: Operations with minimal business risk
4. **Frequent Operations**: Operations used in normal workflows

## Error Message Pattern

### Validation Error Format
```
"{Operation} requires explicit confirmation. Set confirm=True to proceed with {consequence}"
```

Examples:
- "Purge operation requires explicit confirmation. Set confirm=True to proceed with permanent deletion"
- "Deletion not confirmed. Set confirm=true to delete the legal tag. WARNING: This will invalidate all associated data."

### Key Elements
1. **Clear Action Required**: Explicitly state what parameter needs to be set
2. **Consequence Warning**: Clearly state what will happen if operation proceeds
3. **Actionable Guidance**: Provide exact parameter to set
4. **Severity Indication**: Use appropriate language (WARNING, CAUTION) for impact level

## Rationale
1. **Accident Prevention**: Prevents accidental execution of destructive operations
2. **Explicit Intent**: Forces users to explicitly acknowledge destructive consequences
3. **Audit Trail**: Clear record of intentional destructive actions
4. **User Education**: Error messages educate users about operation consequences
5. **Compliance Support**: Supports governance and compliance requirements
6. **Defense in Depth**: Additional safety layer beyond permission controls

## Implementation Guidelines

### Parameter Design
- **Type**: Always use `bool` type for confirmation parameters
- **Name**: Use `confirm` as the standard parameter name
- **Default**: Always default to `False` to require explicit setting
- **Position**: Place confirmation parameter after required operational parameters

### Validation Order
1. **Confirmation Check**: Validate confirmation FIRST, before other checks
2. **Permission Check**: Validate permissions after confirmation
3. **Business Logic**: Proceed with operation only after all validations pass

### Error Codes
- **Confirmation Error**: Use HTTP 400 (Bad Request) for missing confirmation
- **Permission Error**: Use HTTP 403 (Forbidden) for permission failures

## Testing Requirements

### Unit Tests
- Test operation rejection when `confirm=False`
- Test operation success when `confirm=True` and permissions enabled
- Test error message content and format
- Test validation order (confirmation before permissions)

### Integration Tests
- Test end-to-end operation flow with confirmation
- Test combination with permission controls
- Verify actual destructive behavior when confirmed

## Consequences

**Positive:**
- Prevents accidental execution of destructive operations
- Clear audit trail of intentional destructive actions
- Educational error messages improve user understanding
- Supports compliance and governance requirements
- Minimal performance impact on validation
- Compatible with existing permission control systems

**Negative:**
- Additional parameter complexity for destructive operations
- Potential user friction for legitimate operations
- Requires consistent implementation across all applicable operations
- Documentation overhead to explain confirmation requirements

## Related ADRs
- ADR-020: Unified Write Protection with Dual Permission Model (permission controls)
- ADR-021: Record Validation Pattern (client-side validation patterns)
- ADR-004: Error Handling Architecture (error message structure)

## Future Considerations
- **Multi-step Confirmation**: For extremely critical operations, consider multi-step confirmation
- **Confirmation Tokens**: For programmatic access, consider time-limited confirmation tokens
- **Confirmation Logging**: Enhanced audit logging for confirmation-required operations
- **User Interface**: Consider confirmation dialogs in user interfaces