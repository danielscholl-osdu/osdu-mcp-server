# ADR-012: Multi-Provider Authentication Architecture

## Status
**Accepted** - 2025-05-16

## Context
The OSDU MCP Server initially implemented only Azure authentication. As the project expands, we need to support multiple cloud providers (AWS, GCP) while maintaining backward compatibility and keeping the codebase simple.

The OSDU CLI implementation uses a simple switch-based authentication selection pattern that has proven effective. We should follow this pattern rather than over-engineering with abstract classes.

## Decision
Implement automatic authentication provider detection based on environment variables, with an optional override mechanism.

## Rationale
1. **Zero Configuration**: Authentication mode is automatically detected from provider-specific environment variables
2. **Convention over Configuration**: Uses standard environment variable patterns (AZURE_*, AWS_*, GOOGLE_*)
3. **Simplicity**: No need to set authentication mode explicitly in most cases
4. **Flexibility**: Optional OSDU_MCP_AUTH_MODE for edge cases requiring explicit control
5. **OSDU CLI Pattern**: Follows similar detection patterns used in OSDU CLI

## Implementation
```python
class AuthenticationMode(Enum):
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"

class AuthHandler:
    def __init__(self, config):
        self.mode = self._detect_authentication_mode()
        self._initialize_credential()
    
    def _detect_authentication_mode(self) -> AuthenticationMode:
        # Auto-detect based on provider-specific environment variables
        if os.environ.get("AZURE_CLIENT_ID") or os.environ.get("AZURE_TENANT_ID"):
            detected_mode = AuthenticationMode.AZURE
        elif os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_REGION"):
            detected_mode = AuthenticationMode.AWS
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
            detected_mode = AuthenticationMode.GCP
        else:
            detected_mode = None
            
        # Optional explicit override
        explicit_mode = os.environ.get("OSDU_MCP_AUTH_MODE")
        if explicit_mode:
            return AuthenticationMode(explicit_mode)
            
        # Use detected mode or raise error
        if detected_mode:
            return detected_mode
            
        raise OSMCPAuthError("Cannot detect authentication mode")
    
    def _initialize_credential(self):
        if self.mode == AuthenticationMode.AZURE:
            self._initialize_azure_credential()
        elif self.mode == AuthenticationMode.AWS:
            self._initialize_aws_credential()
        # etc.
```

## Alternatives Considered
1. **Abstract Base Classes**
   - **Pros**: Formal interface, enforced contracts
   - **Cons**: Over-engineered for current needs, complex
   - **Decision**: Too much abstraction for simple use case

2. **Plugin Architecture**
   - **Pros**: Dynamic loading, maximum flexibility
   - **Cons**: Complex implementation, runtime overhead
   - **Decision**: Unnecessary complexity

3. **Keep Azure-Only**
   - **Pros**: Simplest option
   - **Cons**: Limits future expansion
   - **Decision**: Need to prepare for multi-cloud support

## Consequences
**Positive:**
- Simple and maintainable code
- Easy to add new providers
- Follows established patterns
- Minimal breaking changes
- Clear error messages for unsupported providers

**Negative:**
- Some code duplication between providers
- No formal interface contract
- Must manually ensure consistency across providers

## Implementation Status
- Azure authentication continues to work
- AWS and GCP methods return NotImplementedError
- Mode detection works with explicit and auto-detection
- All existing tests pass
- New tests verify mode detection

## Success Criteria
- Azure authentication unchanged
- Clear path for adding AWS/GCP
- Mode detection works correctly