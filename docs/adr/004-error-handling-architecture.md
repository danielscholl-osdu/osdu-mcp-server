# ADR-004: Error Handling Architecture

## Status
**Accepted** - 2025-05-15

## Context
The MCP server needs robust error handling that provides useful feedback to AI assistants while maintaining security and debuggability. Errors can originate from OSDU APIs, authentication, configuration, or internal logic.

## Decision
Implement a **structured error hierarchy** with decorator-based error handling for tools.

## Rationale
1. **Consistent Error Format**: All tools return errors in the same format
2. **Actionable Error Messages**: Errors include context for resolution
3. **Security Conscious**: No sensitive data in error messages
4. **CLI Pattern Adaptation**: Similar to OSDU CLI error handling but MCP-optimized
5. **Easy to Use**: Decorator pattern makes tool error handling automatic

## Alternatives Considered
1. **Basic Try-Catch in Each Tool**
   - **Pros**: Simple, direct control
   - **Cons**: Inconsistent error handling, code duplication
   - **Decision**: Rejected due to maintenance burden

2. **Middleware-Based Error Handling**
   - **Pros**: Centralized processing
   - **Cons**: Complex for MCP tools, harder to customize per tool
   - **Decision**: Doesn't fit FastMCP patterns

3. **Exception Propagation**
   - **Pros**: Python-native approach
   - **Cons**: Raw exceptions not suitable for AI consumption
   - **Decision**: Needs transformation layer

## Consequences
**Positive:**
- Consistent error experience across all tools
- Easy to add error handling to new tools
- Structured errors help AI assistants understand and retry
- Security-conscious by design

**Negative:**
- Some overhead for simple tools
- Requires discipline to use decorators consistently
- May need customization for special error cases

## Implementation Notes
```python
# Exception hierarchy
class OSMCPError(Exception):
    """Base exception for OSDU MCP operations."""
    pass

class OSMCPAuthError(OSMCPError):
    """Authentication failures."""
    pass

class OSMCPAPIError(OSMCPError):
    """OSDU API communication errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

# Decorator for automatic error handling
@handle_osdu_exceptions
async def health_check() -> dict:
    # Tool implementation
    pass
```

## Error Categories
1. **Authentication Errors**: Token issues, permission problems
2. **API Errors**: OSDU service communication failures
3. **Configuration Errors**: Missing or invalid configuration
4. **Validation Errors**: Invalid input parameters
5. **Internal Errors**: Unexpected system failures

## Updates
Added `OSMCPValidationError` for 400-level input validation errors

## Success Criteria
- All tools use consistent error format
- Error messages provide actionable guidance
- No sensitive information leaked in errors
- AI assistants can understand and act on error responses