# ADR-011: OAuth Scope Simplification

## Status
**Accepted** - 2025-05-16

## Context
During initial implementation, the OSDU MCP Server supported custom OAuth scopes via the `AZURE_TOKEN_SCOPE` environment variable. However, testing revealed that OSDU platform has strict requirements for JWT token audiences:

1. OSDU validates JWT tokens against specific audience values
2. Custom API audience identifiers (e.g., `api://your-osdu`) cause authentication failures
3. OSDU expects the JWT audience to match the `CLIENT_ID` exactly
4. The standard Azure pattern `{CLIENT_ID}/.default` works correctly with OSDU

This discovery led to unnecessary configuration complexity and user confusion.

## Decision
Remove OAuth scope customization and always use the standard pattern `{CLIENT_ID}/.default` for authentication.

## Rationale
1. **OSDU Compatibility**: OSDU requires JWT audience to match CLIENT_ID
2. **Eliminate Configuration Errors**: No more scope misconfiguration issues  
3. **Simplicity**: One less configuration parameter to manage
4. **Standard Pattern**: Follows Azure's standard OAuth scope pattern
5. **Security**: Prevents accidental exposure of incorrect scope values

## Implementation
```python
class AuthHandler:
    def __init__(self, config):
        # Always derive scope from AZURE_CLIENT_ID
        client_id = os.environ.get("AZURE_CLIENT_ID")
        if not client_id:
            raise AuthenticationError("AZURE_CLIENT_ID environment variable is required")
            
        # Use standard Azure OAuth pattern
        self._scopes = [f"{client_id}/.default"]
```

## Alternatives Considered
1. **Keep Configurable Scope**
   - **Pros**: Flexibility for future use cases
   - **Cons**: Adds complexity, causes user errors, doesn't work with OSDU
   - **Decision**: Rejected due to OSDU incompatibility

2. **Document Correct Scope Pattern**
   - **Pros**: Retains flexibility while providing guidance
   - **Cons**: Still allows misconfiguration, requires user understanding
   - **Decision**: Rejected in favor of eliminating the option entirely

3. **Auto-detect Scope from OSDU**
   - **Pros**: Dynamic configuration
   - **Cons**: OSDU doesn't provide scope discovery endpoint
   - **Decision**: Not feasible with current OSDU capabilities

## Consequences
**Positive:**
- Eliminates a common source of authentication errors
- Simplifies configuration for users
- Guarantees compatibility with OSDU platform
- Reduces documentation complexity
- Follows Azure best practices

**Negative:**
- Less flexibility if non-OSDU endpoints are needed in future
- Breaking change for any existing configurations using custom scopes
- Requires documentation updates

## Migration Path
1. Remove `AZURE_TOKEN_SCOPE` environment variable
2. Update documentation to reflect automatic scope derivation
3. Modify authentication handler to use fixed pattern
4. Update any existing configurations

## Success Criteria
- Authentication works without scope configuration
- No more JWT audience errors with OSDU
- Simplified user onboarding experience
- Clear documentation of the change