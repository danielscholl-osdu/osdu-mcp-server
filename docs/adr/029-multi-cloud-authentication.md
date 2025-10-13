# ADR-029: Multi-Cloud Authentication Architecture

**Status**: Accepted
**Date**: 2025-01-13
**Updated**: 2025-01-13

## Context

The OSDU MCP Server initially supported only Azure authentication via DefaultAzureCredential. This limited adoption to Azure-based OSDU deployments, excluding AWS and GCP users. Additionally, there was no fallback mechanism for custom OAuth providers or testing scenarios with pre-obtained tokens.

**Problem Statement:**
- AWS and GCP users cannot use OSDU MCP Server
- No support for custom OAuth providers (IBM Cloud, Oracle Cloud, etc.)
- Testing and debugging require specific token handling
- Inconsistent developer experience across cloud providers

**User Needs:**
1. AWS developers need first-class authentication support equivalent to Azure
2. GCP developers need Application Default Credentials support
3. Developers need ability to use manual OAuth tokens for testing
4. All users expect automatic credential discovery and token refresh

## Decision

Implement native multi-cloud authentication with automatic provider detection following a simple priority order:

### Authentication Modes

```python
class AuthenticationMode(Enum):
    USER_TOKEN = "user_token"  # Manual Bearer token from environment
    AZURE = "azure"            # Azure DefaultAzureCredential
    AWS = "aws"                # AWS boto3 SDK credentials
    GCP = "gcp"                # GCP Application Default Credentials
```

### Priority Order (Automatic Detection)

1. **USER_TOKEN** (highest priority) - `OSDU_MCP_USER_TOKEN`
2. **Azure** - `AZURE_CLIENT_ID` or `AZURE_TENANT_ID`
3. **AWS** (explicit) - `AWS_ACCESS_KEY_ID` or `AWS_PROFILE`
4. **GCP** (explicit) - `GOOGLE_APPLICATION_CREDENTIALS`
5. **AWS** (auto-discovery) - IAM roles, SSO
6. **GCP** (auto-discovery) - gcloud, metadata service
7. **Error** - No credentials found

### Implementation Strategy

1. **Native SDK Integration**: Use each cloud provider's official SDK for authentication
   - Azure: `azure-identity` library (existing)
   - AWS: `boto3` library (new)
   - GCP: `google-auth` library (new)

2. **Token Validation**: Validate JWT format and expiration for manual tokens using `PyJWT`

3. **Zero Tool Changes**: Authentication fully encapsulated in `AuthHandler`, no changes to any of the 31 MCP tools

4. **Environment Variable Strategy**:
   - **Cloud Provider Variables** (no prefix): Use native variable names (e.g., `AWS_ACCESS_KEY_ID`, `GOOGLE_APPLICATION_CREDENTIALS`)
   - **OSDU Variables** (prefixed): Use `OSDU_MCP_` prefix for application-specific variables

## Rationale

### Why This Approach?

1. **Native SDKs**:
   - ✅ Automatic credential chain discovery
   - ✅ Built-in token refresh
   - ✅ Production-tested and maintained
   - ✅ Future-proof for new credential types
   - ❌ Alternative: Custom credential chains would be fragile and incomplete

2. **Priority-Based Detection**:
   - ✅ Simple and predictable behavior
   - ✅ Manual token overrides everything (highest priority for testing)
   - ✅ No configuration needed in most cases
   - ❌ Alternative: Explicit mode selection would require extra configuration

3. **Manual Token Support**:
   - ✅ Supports any OAuth provider
   - ✅ Enables testing with known tokens
   - ✅ Debugging aid for authentication issues
   - ❌ Alternative: Token parameters on tools would pollute API and violate security best practices

### Alternatives Considered

**Alternative 1: Token Parameters on Tools**
- ❌ Security risk (tokens in parameters)
- ❌ API pollution (31 tools × parameter change)
- ❌ No auto-refresh
- ❌ Poor user experience (manual every call)

**Alternative 2: Single Generic OAuth Client**
- ❌ No auto-refresh
- ❌ No credential chain discovery
- ❌ Manual configuration for every scenario
- ❌ Poor developer experience

**Alternative 3: Cloud-Specific Servers**
- ❌ Code duplication (3 separate implementations)
- ❌ Inconsistent features across clouds
- ❌ Higher maintenance burden

## Implementation Details

### Dependencies Added

```toml
dependencies = [
    "azure-identity==1.25.1",    # Azure (existing)
    "azure-core==1.35.1",        # Azure (existing)
    "boto3>=1.35.0",             # AWS SDK (new)
    "google-auth>=2.35.0",       # GCP ADC (new)
    "PyJWT>=2.10.1",             # JWT validation (new)
]
```

### Core Changes

1. **AuthHandler Enhancement**:
   - Added `AuthenticationMode` enum with 4 modes
   - Implemented `_detect_authentication_mode()` with priority order
   - Added AWS boto3 session initialization
   - Added GCP Application Default Credentials initialization
   - Implemented JWT validation for manual tokens
   - Implemented token retrieval for each provider
   - Enhanced `close()` to handle all credential types

2. **Environment Variables**:
   - **Native Cloud Provider Variables** (no prefix): `AWS_ACCESS_KEY_ID`, `AWS_PROFILE`, `GOOGLE_APPLICATION_CREDENTIALS`
   - **OSDU Application Variables** (prefixed): `OSDU_MCP_USER_TOKEN`, `OSDU_MCP_AUTH_SCOPE`

3. **Zero Tool Impact**: All 31 MCP tools continue to work without any changes

### Token Acquisition Flow

```
Tool → AuthHandler.get_access_token() → Detect Mode →
    ├─ USER_TOKEN → Read from env + validate JWT
    ├─ AZURE → DefaultAzureCredential.get_token()
    ├─ AWS → boto3 STS get_session_token()
    └─ GCP → Credentials.refresh() + return token
```

## Consequences

### Positive

1. **Enhanced Adoption**: AWS and GCP users can now use the server
2. **Developer Experience**: Same seamless experience across all cloud providers
3. **Testing Flexibility**: Manual tokens enable debugging and testing scenarios
4. **Zero Breaking Changes**: Existing Azure users unaffected
5. **Future-Proof**: Easy to add more cloud providers
6. **Security**: Credentials managed by official SDKs with best practices

### Negative

1. **Dependency Growth**: Added 3 new dependencies (~10MB total)
2. **Testing Complexity**: Must test authentication across 4 modes
3. **Support Burden**: Must support AWS/GCP authentication issues
4. **Documentation**: More comprehensive authentication documentation needed

### Neutral

1. **Provider-Specific Quirks**: Each cloud has unique authentication characteristics:
   - AWS: STS token for Bearer token scenarios
   - GCP: Auto-refresh built into credentials
   - Azure: Cached tokens with expiration buffer
   - Manual: No refresh, requires user management

## Validation

### Success Criteria

- ✅ AWS boto3 SDK credentials supported
- ✅ Auto-detects AWS credentials (access keys, profiles, IAM roles)
- ✅ GCP Application Default Credentials supported
- ✅ Auto-detects GCP credentials (GOOGLE_APPLICATION_CREDENTIALS or gcloud)
- ✅ GCP tokens auto-refresh when expired
- ✅ Manual token mode via OSDU_MCP_USER_TOKEN
- ✅ Token validation (format, expiration) for manual tokens
- ✅ Clear error messages for each authentication method
- ✅ Mode detection follows documented priority order
- ✅ Backward compatible with existing Azure deployments
- ✅ Zero changes to any tool signatures
- ✅ Comprehensive test coverage for all modes

### Testing Coverage

- Unit tests for mode detection priority
- Unit tests for AWS credential discovery
- Unit tests for GCP token retrieval with refresh
- Unit tests for user token validation (format, expiration)
- Integration tests for each authentication mode
- Error message validation for each provider

## Migration Path

### Existing Users (Azure)

**No changes required!** Existing configurations continue to work:

```bash
export AZURE_CLIENT_ID=...
export AZURE_TENANT_ID=...
osdu-mcp-server  # Still works!
```

### New Users (AWS)

```bash
# AWS SSO
aws sso login --profile dev
export AWS_PROFILE=dev
osdu-mcp-server  # Just works!

# Or AWS Access Keys
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
osdu-mcp-server
```

### New Users (GCP)

```bash
# gcloud CLI
gcloud auth application-default login
osdu-mcp-server  # Just works!

# Or Service Account Key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
osdu-mcp-server
```

### Testing/Debugging

```bash
# Manual token for any provider
export OSDU_MCP_USER_TOKEN="$(get-token-from-anywhere)"
osdu-mcp-server
```

## Security Considerations

### Token Handling

**Never:**
- ❌ Log tokens in plaintext
- ❌ Include tokens in error messages
- ❌ Pass tokens as function parameters (except internal)
- ❌ Store tokens in files without encryption

**Always:**
- ✅ Validate token format (JWT structure)
- ✅ Check token expiration
- ✅ Use secure credential storage (provider SDKs)
- ✅ Sanitize logs to remove token patterns
- ✅ Warn when tokens expire soon (< 5 minutes)

### Manual Token Validation

```python
def _validate_jwt_token(self, token: str) -> None:
    """Validate JWT token format and expiration.

    Security checks:
    1. Valid JWT format (header.payload.signature)
    2. Not expired (if exp claim present)
    3. Warning if expires soon (< 5 minutes)

    Does NOT validate:
    - Signature (already validated by OAuth provider)
    - Audience (OSDU platform validates)
    - Issuer (OSDU platform validates)
    """
```

## Future Enhancements

### HTTP Transport Compatibility

The design supports future HTTP transport by separating "get token" from "validate token":

```python
class AuthHandler:
    # STDIO mode - GET tokens
    async def get_access_token(self) -> str:
        """Get token from environment/SDK (STDIO transport)."""
        ...

    # HTTP mode - VALIDATE tokens (future)
    async def validate_token(self, token: str, required_audience: str) -> dict:
        """Validate OAuth token from HTTP header (HTTP transport)."""
        ...
```

### Additional Cloud Providers

The pattern easily extends to other providers:
- Oracle Cloud Infrastructure (OCI)
- IBM Cloud
- Alibaba Cloud
- Custom corporate OAuth

## References

- [Azure DefaultAzureCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [AWS boto3 Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [GCP Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [MCP STDIO Guidance](https://modelcontextprotocol.io/docs/concepts/transports#stdio)
- [ADR-002: Authentication Strategy](002-authentication-strategy.md)
- [Specification](../../specs/multi-cloud-auth-spec.md)

## Approval

**Approved by**: AI Agent Development Team
**Date**: 2025-01-13

This ADR represents a significant architectural enhancement that maintains backward compatibility while substantially expanding the user base and use cases for OSDU MCP Server.
