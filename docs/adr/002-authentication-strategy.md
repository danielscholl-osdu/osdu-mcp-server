# ADR-002: Authentication Strategy

## Status
**Accepted** - 2025-05-15

## Context
The MCP server needs to authenticate with OSDU services across various deployment scenarios:
- Local development (developer machines)
- Azure-hosted environments (App Service, AKS, VM)
- CI/CD pipelines
- On-premises deployments with Azure AD integration

## Decision
Use **Azure DefaultAzureCredential** with configurable credential type exclusions.

## Rationale
1. **Universal Coverage**: Supports all Azure deployment scenarios automatically
2. **Zero Secrets in Code**: Credentials managed by Azure platform or environment
3. **Fallback Chain**: Gracefully handles different authentication contexts
4. **Future-Proof**: New credential types added automatically by Microsoft
5. **CLI Pattern Consistency**: Mirrors successful OSDU CLI approach

## Alternatives Considered
1. **Static Token Authentication**
   - **Pros**: Simple implementation, works everywhere
   - **Cons**: Security risk, manual rotation, not production-ready
   - **Decision**: Suitable only for development/testing

2. **Custom Authentication Chain**
   - **Pros**: Full control over credential sources
   - **Cons**: Maintenance burden, reimplementing Microsoft's work
   - **Decision**: Unnecessary complexity

3. **Single Authentication Method**
   - **Pros**: Simpler implementation
   - **Cons**: Doesn't support multiple deployment scenarios
   - **Decision**: Too limiting for real-world use

## Consequences
**Positive:**
- Works in all Azure deployment scenarios without code changes
- No credential management in application code
- Automatic token refresh and caching
- Consistent with enterprise security best practices

**Negative:**
- Azure-specific (though OSDU is typically Azure-deployed)
- Requires understanding of credential fallback order
- Some credentials (like Interactive) must be explicitly disabled in production

## Implementation Notes
```python
from azure.identity.aio import DefaultAzureCredential
import os

class AuthHandler:
    def __init__(self, config):
        # Derive scope from AZURE_CLIENT_ID environment variable
        client_id = os.environ.get("AZURE_CLIENT_ID")
        if not client_id:
            raise AuthenticationError("AZURE_CLIENT_ID environment variable is required")
            
        self._scopes = [f"{client_id}/.default"]  # Standard Azure OAuth pattern
        
        # Auto-detect authentication method based on available credentials
        has_client_secret = os.environ.get("AZURE_CLIENT_SECRET") is not None
        
        if has_client_secret:
            # Service Principal authentication - only allow SP credential
            self._cred = DefaultAzureCredential(
                exclude_azure_cli_credential=True,
                exclude_powershell_credential=True,
                exclude_interactive_browser_credential=True,
                exclude_visual_studio_code_credential=True
            )
        else:
            # Development authentication - allow CLI and PowerShell
            self._cred = DefaultAzureCredential(
                exclude_interactive_browser_credential=True,  # Always disabled
                exclude_visual_studio_code_credential=True    # Not relevant for server
            )
```

## Configuration Options
- `AZURE_CLIENT_ID`: Azure service principal or application ID (required)
- `AZURE_TENANT_ID`: Azure tenant ID (required)
- `AZURE_CLIENT_SECRET`: Service principal secret (optional, presence determines auth method)
- OAuth scope is automatically derived from `AZURE_CLIENT_ID` as `{client_id}/.default`

## Authentication Behavior
- **Service Principal Mode**: When `AZURE_CLIENT_SECRET` is present
  - Only Service Principal authentication is allowed
  - Azure CLI and PowerShell credentials are disabled for security
- **Development Mode**: When `AZURE_CLIENT_SECRET` is absent  
  - Azure CLI and PowerShell credentials are enabled
  - Useful for local development without secrets
- **Interactive Authentication**: Always disabled for security reasons

## Success Criteria
- Authentication works in all planned deployment scenarios
- No credentials stored in application configuration
- Token refresh happens automatically without server restart