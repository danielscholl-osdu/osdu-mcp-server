# OSDU MCP Server: Architecture Document

## 1. Introduction

### 1.1. Purpose
This document outlines the architecture for the OSDU MCP Server, a Model Context Protocol server that provides AI assistants with access to the OSDU platform. The architecture leverages proven patterns from the OSDU CLI as a development accelerator while building an independent, MCP-optimized implementation.

### 1.2. Architectural Philosophy
**CLI-Informed, MCP-Optimized**: Learn from CLI success, build for MCP excellence.

- **Study CLI Patterns**: Authentication, configuration, error handling, and API design patterns
- **Build Independent Tools**: Native MCP tools optimized for AI workflows
- **Incremental Development**: Phased approach with validated deliverables
- **Simplicity First**: Right-size complexity for MCP use case

### 1.3. Scope
This document covers:
- Overall system architecture and design principles
- Phase 1 (Foundation) detailed implementation
- Future phases architectural evolution
- Integration patterns and development guidelines

## 2. Architectural Principles

### 2.1. Core Principles
- **MCP-First Design**: Built specifically for Model Context Protocol
- **AI-Optimized Interfaces**: Tools designed for natural language interaction
- **Pattern Reuse**: Apply proven CLI patterns where beneficial
- **Incremental Complexity**: Add sophistication only when needed
- **Developer Experience**: Easy to extend and maintain

### 2.2. CLI Pattern Adoption Strategy
**Study & Adapt Approach:**
1. Analyze CLI implementations for proven patterns
2. Extract architectural concepts and best practices
3. Adapt patterns for MCP context and constraints (headless, long-running service)
4. Implement independently with MCP optimizations

### 2.3. MCP Context Considerations
**Critical Differences from CLI:**
- **Headless Operation**: No user interaction during runtime
- **Long-Running Service**: Continuous operation vs. session-based CLI
- **Autonomous Management**: Self-sufficient credential and error handling
- **Container-Ready**: Designed for containerized deployment scenarios

## 3. System Architecture Overview

### 3.1. High-Level Architecture

```
┌─────────────────────────────────────────┐
│             MCP Client                  │
│         (Claude, GPT, etc.)             │
└─────────────┬───────────────────────────┘
              │ MCP Protocol
              │ (JSON-RPC over stdio)
              ▼
┌─────────────────────────────────────────┐
│         OSDU MCP Server                 │
│  ┌─────────────────────────────────┐    │
│  │        FastMCP Framework        │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │         Tool Registry           │    │
│  │   • Health Check               │    │
│  │   • Storage Tools (Phase 6)    │    │
│  │   • Search Tools (Phase 5) ✅  │    │
│  │   • Schema Tools (Phase 4)     │    │
│  │   • Legal Tools (Phase 3)      │    │
│  │   • Partition Tools (Phase 2)  │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │        Prompt Registry          │    │
│  │   • Asset Discovery            │    │
│  │   • Search Guidance            │    │
│  │   • Record Lifecycle Workflow  │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │       Resource Registry         │    │
│  │   • Working Templates          │    │
│  │   • Reference Examples         │    │
│  │   • Format Patterns            │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │      Shared Infrastructure      │    │
│  │   • Configuration              │    │
│  │   • Authentication             │    │
│  │   • OSDU API Client            │    │
│  │   • Error Handling             │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │ HTTPS/REST
              ▼
┌─────────────────────────────────────────┐
│            OSDU Platform                │
│   • Storage Service                     │
│   • Search Service                      │
│   • Schema Service                      │
│   • Legal Service                       │
└─────────────────────────────────────────┘
```

### 3.2. Phased Evolution Strategy

#### Phase 1: Foundation (Current)
**Goal**: Basic connectivity and health monitoring
**Scope**: Health check tool + core infrastructure

#### Phase 2: Partition & Entitlements Service
**Goal**: Platform administration capabilities  
**Scope**: Partition management + user entitlements

#### Phase 3: Legal Service
**Goal**: Compliance and legal tag management
**Scope**: Legal tag CRUD operations + validation

#### Phase 4: Schema Service  
**Goal**: Data schema management
**Scope**: Schema discovery + validation + CRUD

#### Phase 5: Search Service (✅ Complete)
**Goal**: OSDU data discovery and query capabilities
**Scope**: Elasticsearch-powered search + guidance prompts

#### Phase 6: Storage Service
**Goal**: OSDU record storage operations
**Scope**: Record CRUD + versioning + validation

## 4. MCP Capabilities Architecture

### 4.1. Prompts Implementation (ADR-024, ADR-025)
**Design Principle**: Self-documenting capabilities via guidance prompts

The server implements MCP prompts to provide AI assistants with rich guidance content:

```python
# Prompt implementation pattern
async def guide_record_lifecycle() -> List[Message]:
    """Provide comprehensive guidance for executing the complete OSDU record
    lifecycle workflow with validation at each step."""
    
    generator = AssetsGenerator()
    content = generator.generate_workflow_guide()
    
    return [{"role": "user", "content": content}]
```

**Current Prompts:**
- **list_mcp_assets**: Discover server capabilities and available tools
- **guide_search_patterns**: Elasticsearch query patterns and best practices  
- **guide_record_lifecycle**: Complete workflow from legal setup to cleanup

### 4.2. Resources Implementation (ADR-027, ADR-028)
**Design Principle**: Template-driven workflows eliminate format-guessing errors

The server provides working templates and reference examples via MCP Resources:

```
src/osdu_mcp_server/resources/
├── templates/           # Working templates for direct use
│   ├── legal-tag-template.json
│   └── processing-parameter-record.json
└── references/          # Reference examples and patterns
    ├── acl-format-examples.json
    └── search-query-patterns.json
```

**Resource Registration:**
```python
def get_workflow_resources() -> List[Resource]:
    """Discover and register all workflow resources."""
    resources = []
    base_path = Path(__file__).parent / "resources"
    
    # Auto-discover templates and references
    for category in ["templates", "references"]:
        category_path = base_path / category
        if category_path.exists():
            for json_file in category_path.glob("*.json"):
                resources.append(Resource(
                    uri=f"{category}://{json_file.stem}",
                    name=f"{category.title()}: {json_file.stem.replace('-', ' ').title()}",
                    description=f"Working {category[:-1]} for {json_file.stem.replace('-', ' ')}",
                    mimeType="application/json"
                ))
    
    return resources
```

### 4.3. Data Domain Configuration (ADR-028)
**Design Principle**: Environment-specific configuration for ACL accuracy

OSDU ACLs require deployment-specific data domains:

```python
# Configuration integration
class ConfigManager:
    def get_data_domain(self) -> str:
        """Get the OSDU data domain for ACL formatting."""
        return self.get("server", "domain", "contoso.com")

# Template domain injection
def get_acl_template(domain: str = None) -> dict:
    """Generate ACL template with appropriate domain."""
    if domain is None:
        config = ConfigManager()
        domain = config.get_data_domain()
    
    return {
        "viewers": [f"data.default.viewers@{domain}"],
        "owners": [f"data.default.owners@{domain}"]
    }
```

**Domain Mapping:**
- **Standard OSDU**: `contoso.com` (default)
- **Microsoft Energy Data Services**: `dataservices.energy`
- **Test Environments**: `msft-osdu-test.org`

## 5. Phase 1: Foundation Architecture

### 5.1. Component Structure

```
osdu_mcp_server/
├── main.py                    # Application entry point
├── server.py                  # FastMCP server configuration
├── shared/                    # Core infrastructure
│   ├── config_manager.py      # Configuration management
│   ├── auth_handler.py        # Authentication
│   ├── osdu_client.py         # OSDU API client
│   ├── data_types.py          # Standard response models
│   ├── exceptions.py          # Error handling
│   ├── assets_generator.py    # Content generation for prompts
│   └── clients/               # Service-specific clients
├── tools/                     # MCP tool implementations
│   ├── health_check.py        # Health check tool
│   ├── partition/             # Partition service tools
│   ├── legal/                 # Legal service tools
│   ├── schema/                # Schema service tools
│   ├── search/                # Search service tools
│   └── storage/               # Storage service tools
├── prompts/                   # MCP prompt implementations
│   ├── list_mcp_assets.py     # Asset discovery prompt
│   ├── guide_search_patterns.py # Search guidance prompt
│   └── guide_record_lifecycle.py # Workflow guidance prompt
├── resources/                 # MCP resources (JSON templates)
│   ├── templates/             # Working templates for direct use
│   │   ├── legal-tag-template.json
│   │   └── processing-parameter-record.json
│   └── references/            # Reference examples and patterns
│       ├── acl-format-examples.json
│       └── search-query-patterns.json
└── tests/                     # Test suite (mirrors source structure)
    ├── tools/
    ├── prompts/
    ├── resources/
    └── shared/
```

### 5.2. Configuration Architecture

**Design Principle**: Environment-first with simple fallback

```python
class ConfigManager:
    """
    Configuration priority:
    1. Environment variables (OSDU_MCP_*)
    2. YAML config file
    3. Default values
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        self.env_prefix = "OSDU_MCP_"
        self.config_file = config_file
        self._file_config = self._load_file_config()
    
    def get(self, section: str, key: str, default=None):
        # Check environment first (CLI pattern)
        env_key = f"{self.env_prefix}{section.upper()}_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # Check config file
        if self._file_config and section in self._file_config:
            return self._file_config[section].get(key, default)
        
        return default
```

**Configuration Sources:**
1. **Environment Variables**: `OSDU_MCP_SERVER_URL`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`
2. **YAML File**: Simple key-value structure
3. **Defaults**: Sensible defaults where possible

### 5.3. Authentication Architecture

#### Design Principle  
Use Azure's **DefaultAzureCredential** (or the async `aio` variant) with *selective exclusions* to cover every MCP-server deployment surface—laptop, CI/CD pipeline, or managed hosting—while avoiding hand-rolled chains.

---

#### Credential Strategy  

| Order (fixed by SDK) | Credential Source | When It's Enabled in MCP |
|----------------------|-------------------|--------------------------|
| 1 | **EnvironmentCredential** | Always (for service-principal secret/cert or Workload ID) |
| 2 | **ManagedIdentityCredential / WorkloadIdentityCredential** | Enabled automatically in AKS, VMSS, App Service, Container Apps |
| 3 | **AzureDeveloperCliCredential** | Enabled unless explicitly excluded |
| 4 | **AzureCliCredential** | Dev machines when `allowAzureCLI = true` |
| 5 | **VisualStudioCodeCredential / VisualStudioCredential** | On dev boxes; excluded in CI |
| 6 | **AzurePowerShellCredential** | When `allowAzPowerShell = true` |
| 7 | **InteractiveBrowserCredential** | Only when `allowInteractive = true` (local dev) |

> **Why not craft a custom chain?**  
> DefaultAzureCredential already bundles maintenance, telemetry, future credential types, and sync/async parity. We simply disable the links we don't want.

---

#### Configuration Switches  

```yaml
auth:
  # dev toggles
  allowAzureCLI:      true      # disable in CI or prod
  allowAzPowerShell:  false     # rarely needed
  allowInteractive:   false     # true only for local testing
  
# Note: OAuth scope is automatically derived from AZURE_CLIENT_ID
```

#### Minimal Async Implementation

```python
from azure.identity.aio import DefaultAzureCredential

class AuthHandler:
    """Non-blocking auth helper for MCP requests."""
    
    def __init__(self, cfg):
        self._scopes = [cfg["auth"]["scope"]]
        self._cred = DefaultAzureCredential(
            exclude_azure_cli_credential=not cfg["auth"]["allowAzureCLI"],
            exclude_azure_powershell_credential=not cfg["auth"]["allowAzPowerShell"],
            exclude_interactive_browser_credential=not cfg["auth"]["allowInteractive"],
        )
    
    async def get_token(self) -> str:
        token = await self._cred.get_token(*self._scopes)
        return token.token
```

*Sync version*: replace the `aio` import and drop `await`.

#### Deployment Modes

| Scenario | What to Provision | Flags |
|----------|------------------|-------|
| **Production (AKS / VM / App Service)** | System- or user-assigned **Managed Identity** | `allow*` flags **false** |
| **CI/CD Pipeline** | **Service Principal** secret or federated creds in pipeline env-vars | `allow*` flags **false** |
| **Developer Laptop** | `az login` or `azd login` | `allowAzureCLI: true` (others optional) |
| **Debug/POC** | Interactive browser fallback | `allowInteractive: true` |

#### Benefits Recap

* **Zero secrets in code** – MI and federated SP creds live in Azure or pipeline secure-vars.
* **Future-proof** – new Azure credential types arrive automatically.
* **Observability & Retry** – built-in; no custom caching required.
* **Async ready** – keeps event loop unblocked for high-throughput MCP requests.

### 5.4. OSDU Client Architecture

**Design Principle**: Simple HTTP client with CLI-inspired patterns, optimized for headless operation

```python
class OsduClient:
    """
    Lightweight OSDU API client inspired by CLI patterns.
    Optimized for long-running MCP server context.
    """
    
    def __init__(self, config: ConfigManager, auth: AuthHandler):
        self.base_url = config.get("server", "url").rstrip('/')
        self.data_partition = config.get("server", "data_partition")
        self.auth = auth
        self.timeout = config.get("server", "timeout", 30)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total pool size
                limit_per_host=30,  # Per-host pool size
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def get(self, path: str, **kwargs) -> dict:
        """GET request with CLI-inspired error handling."""
        return await self._request("GET", path, **kwargs)
    
    async def _request(self, method: str, path: str, **kwargs):
        """Base request method with retry logic."""
        session = await self._get_session()
        headers = await self._get_headers()
        
        # CLI-inspired retry and error handling
        for attempt in range(3):
            try:
                async with session.request(
                    method, f"{self.base_url}{path}",
                    headers=headers, **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt == 2:  # Last attempt
                    raise OSMCPAPIError(f"Request failed: {e}", status_code=getattr(response, 'status', None))
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with DefaultAzureCredential authentication."""
        headers = {
            "Content-Type": "application/json",
            "data-partition-id": self.data_partition
        }
        
        try:
            token = await self.auth.get_access_token()
            headers["Authorization"] = f"Bearer {token}"
        except OSMCPAuthError as e:
            raise OSMCPAPIError(f"Authentication failed: {e}")
        
        return headers
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
```

### 5.5. Tool Implementation Pattern

**Design Principle**: Consistent, FastMCP-optimized tools

```python
# Standard tool pattern for all phases
@handle_osdu_exceptions
async def health_check(
    include_services: bool = True,
    include_auth: bool = True,
    include_version_info: bool = False
) -> dict:
    """
    Check OSDU platform connectivity and service health.
    
    Args:
        include_services: Test individual service availability
        include_auth: Validate authentication
        include_version_info: Include service version information
    
    Returns:
        Comprehensive health status
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = OsduClient(config, auth)
    
    try:
        result = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "server_url": client.base_url,
            "data_partition": client.data_partition
        }
        
        if include_auth:
            result["authentication"] = await _test_authentication(auth)
        
        if include_services:
            result["services"] = await _test_services(client)
        
        if include_version_info:
            result["version_info"] = await _get_version_info(client)
        
        return result
        
    finally:
        await client.close()

async def _test_authentication(auth: AuthHandler) -> dict:
    """Test authentication validity."""
    try:
        valid = await auth.validate_token()
        return {"status": "valid" if valid else "invalid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_services(client: OsduClient) -> dict:
    """Test OSDU service connectivity."""
    # Note: OSDU services use different API versions
    # Legal uses v1 while most others use v2
    services = {
        "storage": "/api/storage/v2/info",
        "search": "/api/search/v2/info",
        "legal": "/api/legal/v1/info"  # Legal API uses v1
    }
    
    results = {}
    for service_name, endpoint in services.items():
        try:
            await client.get(endpoint)
            results[service_name] = "healthy"
        except Exception as e:
            results[service_name] = f"unhealthy: {str(e)}"
    
    return results
```

### 5.6. Error Handling Architecture

**Design Principle**: CLI-inspired structured errors optimized for AI

```python
# Exception hierarchy
class OSMCPError(Exception):
    """Base exception for OSDU MCP operations."""
    pass

class OSMCPAuthError(OSMCPError):
    """Authentication failures."""
    def __init__(self, message: str, auth_method: str = None):
        super().__init__(message)
        self.auth_method = auth_method

class OSMCPAPIError(OSMCPError):
    """OSDU API communication errors."""
    def __init__(self, message: str, status_code: int = None, endpoint: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint

# Error handling decorator
def handle_osdu_exceptions(func):
    """Convert OSDU errors to MCP-compatible tool errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except OSMCPAuthError as e:
            # Provide actionable error messages for AI assistants
            if e.auth_method == "environment":
                raise ToolError(f"Authentication failed: {e}. Check AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables.")
            elif "managed identity" in str(e).lower():
                raise ToolError(f"Managed Identity authentication failed: {e}. Ensure the server is running in Azure with managed identity enabled.")
            else:
                raise ToolError(f"Authentication failed: {e}")
        except OSMCPAPIError as e:
            if e.status_code == 401:
                raise ToolError(f"OSDU API unauthorized (401): Token may be expired or invalid. Endpoint: {e.endpoint}")
            elif e.status_code == 403:
                raise ToolError(f"OSDU API forbidden (403): Insufficient permissions for {e.endpoint}")
            elif e.status_code == 404:
                raise ToolError(f"OSDU API endpoint not found (404): {e.endpoint}")
            else:
                raise ToolError(f"OSDU API error: {e}")
        except Exception as e:
            logger.exception("Unexpected error in tool")
            raise ToolError(f"Internal error: {str(e)}")
    return wrapper
```

## 6. Future Phases Architecture Evolution

### 6.1. Phase 2: Core Tools Addition

**New Components:**
```python
# tools/storage/
├── get_record.py
├── create_record.py  
├── update_record.py
└── delete_record.py

# tools/search/
├── query_records.py
└── search_by_kind.py

# shared/clients/
├── storage_client.py
└── search_client.py
```

**Architectural Changes:**
- Add service-specific clients
- Implement batch operation support
- Enhanced error context for tool operations

### 6.2. Phase 3: Data Management

**New Components:**
```python
# tools/schema/
├── validate_record.py
├── get_schema.py
└── list_schemas.py

# tools/legal/
├── create_tag.py
├── validate_compliance.py
└── list_tags.py

# shared/validation/
├── schema_validator.py
└── legal_validator.py
```

**Architectural Changes:**
- Add validation framework
- Implement schema caching
- Enhanced compliance checking

### 6.3. Phase 4: AI Enhancement

**New Components:**
```python
# tools/ai/
├── natural_language_query.py
├── summarize_records.py
└── data_discovery.py

# shared/ai/
├── query_translator.py
├── content_summarizer.py
└── insight_generator.py
```

**Architectural Changes:**
- Add AI processing pipeline
- Implement response optimization
- Advanced batch processing

## 7. Integration Patterns

### 7.1. Tool Registration Pattern

```python
# server.py - Central tool registration
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OSDU MCP Server")

# Phase 1 tools
from .tools.health_check import health_check
mcp.register_tool()(health_check)

# Future phases - conditional registration
if FEATURE_FLAGS.get("storage_tools"):
    from .tools.storage import get_record, create_record
    mcp.register_tool()(get_record)
    mcp.register_tool()(create_record)
```

### 7.2. Client Factory Pattern

```python
# Centralized client management
class ClientFactory:
    """Factory for creating OSDU service clients."""
    
    def __init__(self, config: ConfigManager, auth: AuthHandler):
        self.config = config
        self.auth = auth
        self._clients = {}
    
    def get_storage_client(self) -> StorageClient:
        if "storage" not in self._clients:
            self._clients["storage"] = StorageClient(
                self.config, self.auth
            )
        return self._clients["storage"]
```

### 7.3. Testing Architecture

Following ADR-010 (Testing Philosophy), we use behavior-driven testing:

```python
# Behavior-focused testing patterns
import pytest
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_health_check_reports_service_unavailable():
    """Test that health check correctly reports when services are down."""
    
    with aioresponses() as mocked:
        # Mock external service behavior - not internal implementation
        mocked.get("https://osdu.com/api/storage/v2/info", status=503)
        mocked.get("https://osdu.com/api/search/v2/info", 
                  payload={"status": "healthy", "version": "1.0.0"})
        
        result = await health_check(include_services=True)
        
        # Verify behavior - what the user sees
        assert result["connectivity"] == "success"
        assert result["services"]["storage"] == "unhealthy: Service unavailable"
        assert result["services"]["search"] == "healthy"
```

#### Testing Principles (ADR-010)

1. **Test Boundaries**: Mock at service boundaries (HTTP, auth providers) only
2. **Behavior Focus**: Test observable outcomes, not implementation details
3. **Appropriate Tools**: Use `aioresponses` for HTTP mocking, `patch.dict` for environment
4. **Readable Tests**: Each test should be self-documenting

See [ADR-010: Testing Philosophy and Strategy](../docs/adr.md#adr-010-testing-philosophy-and-strategy) for complete guidelines.

## 8. Development Guidelines

### 8.1. Adding New Tools

1. **Create tool module** in appropriate phase directory
2. **Implement using standard pattern** with `@handle_osdu_exceptions` decorator
3. **Add error handling** with context-rich error messages
4. **Write behavior-driven tests** following ADR-010 guidelines
5. **Update documentation** with usage examples

### 8.2. Extending Authentication

1. **Follow DefaultAzureCredential pattern** - add new credentials to chain
2. **Test in multiple deployment scenarios** (local dev, Azure, containers)
3. **Maintain backward compatibility** with existing configurations
4. **Document new environment variables** and configuration options

### 8.3. Quality Gates

- **Code Review**: All changes reviewed
- **Test Coverage**: >90% for new components
- **Testing Philosophy**: Behavior-driven tests per ADR-010
- **Performance**: Tool responses <5s
- **Documentation**: All public APIs documented
- **Integration Testing**: Verify with real OSDU instances

## 9. Deployment Architecture

### 9.1. MCP Client Integration

```json
// .mcp.json configuration
{
  "mcpServers": {
    "osdu-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "osdu-mcp-server"],
      "env": {
        "OSDU_MCP_SERVER_URL": "https://your-osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "your-partition",
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### 9.2. Container Deployment

```dockerfile
FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ /app/src/
WORKDIR /app

# Set up environment for managed identity
ENV OSDU_MCP_AUTH_ALLOW_AZURE_CLI=false
ENV OSDU_MCP_AUTH_ALLOW_AZURE_POWERSHELL=false
ENV OSDU_MCP_AUTH_ALLOW_INTERACTIVE=false

# Run the server
CMD ["python", "-m", "osdu_mcp_server"]
```

### 9.3. Environment Setup

```bash
# Installation
uv sync
uv pip install -e .

# Configuration
export OSDU_MCP_SERVER_URL=https://your-osdu.com
export OSDU_MCP_SERVER_DATA_PARTITION=your-partition

# Authentication (choose one method)
# Method 1: Service Principal
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret

# Method 2: Developer login (local development)
az login

# Execution
osdu-mcp-server
```

## 10. Validation Strategy

### 10.1. Architecture Validation

- **Phase 1 Completion Criteria**:
  - Health check tool operational with DefaultAzureCredential
  - Configuration system functional with environment priority
  - Authentication validated across deployment scenarios
  - Error handling comprehensive with context-rich messages
  - Integration tests passing with real OSDU instances

### 10.2. Evolution Validation

- **Inter-phase validation**: Each phase builds on validated previous phases
- **Pattern consistency**: CLI-inspired patterns maintained across phases
- **Performance benchmarks**: Response time targets met
- **Integration testing**: MCP protocol compliance verified
- **Security validation**: Authentication chain tested in all scenarios

## 11. Conclusion

This architecture provides a solid foundation for the OSDU MCP Server while maintaining the flexibility to evolve through planned phases. By learning from CLI patterns while building MCP-optimized tools, the architecture balances proven reliability with innovation for AI workflows.

The authentication system using DefaultAzureCredential provides production-ready security with developer-friendly fallbacks, ensuring the server can operate across different deployment scenarios without compromising security or usability.

**Key Success Factors:**
- CLI pattern inspiration without dependency
- MCP-first design decisions optimized for headless operation
- DefaultAzureCredential for robust, deployment-flexible authentication
- Incremental complexity introduction with clear phase boundaries
- Comprehensive validation at each phase
- Clear development and extension guidelines

The phased approach ensures incremental value delivery while maintaining architectural coherence. Each phase introduces complexity only when validated and needed, resulting in a robust, maintainable system optimized for its specific MCP use case.

## References

- [Project Brief](project-brief.md)
- [Project Brief](project-prd.md)