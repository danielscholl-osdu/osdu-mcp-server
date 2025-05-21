# Specification for OSDU MCP Server (Phase 1: Foundation)

> A lightweight MCP server implementation for OSDU platform integration with AI-powered tooling.

## Overview

This specification defines Phase 1 implementation of an OSDU (Open Subsurface Data Universe) MCP (Model Context Protocol) server that provides AI assistants with secure access to OSDU platform capabilities. The server exposes OSDU operations as MCP tools, enabling natural language interaction with subsurface data through a health check tool and foundational infrastructure.

The implementation follows architectural patterns established in our [Architecture Decision Records (ADR)](../docs/adr.md), which document the rationale behind key technical choices.

## Server Identity

- **Server Name**: `osdu-mcp-server`
- **Package Name**: `osdu_mcp_server` (Python package naming convention)
- **Description**: MCP server for OSDU platform integration
- **Protocol**: Model Context Protocol (MCP) v1.0+

## Architecture Overview

See [ADR-001: MCP Framework Selection](../docs/adr.md#adr-001-mcp-framework-selection) for the decision to use FastMCP.

### Key Architectural Decisions

The implementation follows these core architectural decisions:

- **[ADR-001](../docs/adr.md#adr-001-mcp-framework-selection)**: FastMCP for rapid development and protocol compliance
- **[ADR-002](../docs/adr.md#adr-002-authentication-strategy)**: Azure DefaultAzureCredential for universal deployment support
- **[ADR-003](../docs/adr.md#adr-003-configuration-management-approach)**: Environment-first configuration with YAML fallback
- **[ADR-008](../docs/adr.md#adr-008-async-first-design)**: Async/await throughout for optimal I/O performance
- **[ADR-010](../docs/adr.md#adr-010-testing-philosophy-and-strategy)**: Behavior-driven testing for maintainability

## Project Structure

Following [ADR-006: Project Structure and Packaging](../docs/adr.md#adr-006-project-structure-and-packaging):

```
osdu_mcp_server/
├── src/
│   └── osdu_mcp_server/
│       ├── __init__.py
│       ├── main.py                      # Entry point script
│       ├── server.py                    # FastMCP server instance
│       ├── shared/                      # Core infrastructure
│       │   ├── __init__.py
│       │   ├── config_manager.py        # Configuration (ADR-003)
│       │   ├── auth_handler.py          # Authentication (ADR-002)
│       │   ├── osdu_client.py           # HTTP client (ADR-005)
│       │   ├── exceptions.py            # Error handling (ADR-004)
│       │   └── utils.py                 # Helper functions
│       └── tools/                       # MCP tool implementations
│           ├── __init__.py
│           └── health_check.py          # Health check tool (ADR-007)
├── tests/                               # Test suite
│   ├── __init__.py
│   ├── test_health_check.py
│   └── shared/
│       ├── __init__.py
│       ├── test_config.py
│       └── test_auth.py
├── pyproject.toml
└── README.md
```

## Dependencies

The following Python libraries and versions are required for this project:

| Library           | Version      | Purpose                                 |
|-------------------|-------------|-----------------------------------------|
| mcp               | ≥1.8.1      | MCP protocol server framework           |
| aiohttp           | ≥3.11.18    | Async HTTP client                       |
| pyyaml            | ≥6.0.2      | YAML configuration parsing              |
| pydantic          | ≥2.11.4     | Data validation and settings management |
| azure-identity    | 1.23.0      | Azure authentication                    |
| azure-core        | 1.34.0      | Azure SDK core utilities                |
| aioresponses      | ≥0.7.8      | HTTP mocking for aiohttp in tests       |

All dependencies are defined in `pyproject.toml`.
Python version required: **≥3.12**

## Core Infrastructure Implementation

### Configuration Manager

Implementation pattern per [ADR-003: Configuration Management Approach](../docs/adr.md#adr-003-configuration-management-approach):

#### Interface Contract

```python
class ConfigManager:
    """Environment-first configuration with YAML fallback."""
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable priority."""
        pass
    
    def _load_file_config(self) -> Optional[dict]:
        """Load configuration from YAML file if it exists."""
        pass
```

#### Configuration Precedence

1. **Environment Variables** (highest priority) - `OSDU_MCP_{SECTION}_{KEY}`
2. **YAML Configuration File** - `config.yaml`
3. **Default Values** (lowest priority)

#### Required Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `OSDU_MCP_SERVER_URL` | OSDU platform URL | `https://your-osdu.com` |
| `OSDU_MCP_SERVER_DATA_PARTITION` | Data partition ID | `your-partition` |
| `AZURE_CLIENT_ID` | Azure service principal or application ID | `your-client-id` |
| `AZURE_TENANT_ID` | Azure tenant ID | `your-tenant-id` |

Note: OAuth scope is automatically derived from `AZURE_CLIENT_ID` as `{client_id}/.default`

### Authentication Handler

Implementation pattern per [ADR-002: Authentication Strategy](../docs/adr.md#adr-002-authentication-strategy):

#### Interface Contract

```python
class AuthHandler:
    """Authentication using Azure DefaultAzureCredential with configurable exclusions."""
    
    async def get_access_token(self) -> str:
        """Get valid access token with automatic refresh."""
        pass
    
    async def validate_token(self) -> bool:
        """Validate current token against OSDU."""
        pass
```

#### Authentication Methods

Authentication is automatically determined based on available credentials:

| Scenario | Credentials Present | Authentication Method |
|----------|-------------------|---------------------|
| Service Principal | `AZURE_CLIENT_SECRET` | Service Principal only |
| Development | No `AZURE_CLIENT_SECRET` | Azure CLI + PowerShell |

#### Deployment Scenarios

See [ADR-002](../docs/adr.md#adr-002-authentication-strategy) for detailed deployment guidance:

- **Production**: Service Principal via environment variables
- **CI/CD**: Service Principal via environment variables  
- **Development**: Azure CLI/PowerShell (when no client secret present)

### HTTP Client

Implementation pattern per [ADR-005: HTTP Client Implementation](../docs/adr.md#adr-005-http-client-implementation):

#### Interface Contract

```python
class OsduClient:
    """Async HTTP client for OSDU APIs with connection pooling and retries."""
    
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET request with retry logic."""
        pass
    
    async def post(self, path: str, data: Any, **kwargs) -> Dict[str, Any]:
        """POST request with retry logic."""
        pass
    
    async def close(self):
        """Clean up HTTP session."""
        pass
```

#### Key Features

- Connection pooling for efficiency
- Exponential backoff retry logic
- Proper timeout handling
- Automatic session cleanup

### Error Handling

Implementation pattern per [ADR-004: Error Handling Architecture](../docs/adr.md#adr-004-error-handling-architecture):

#### Exception Hierarchy

```python
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
```

#### Error Handling Decorator

```python
@handle_osdu_exceptions
async def tool_function() -> dict:
    """Tool implementation with automatic error handling."""
    pass
```

## Tool Implementation

### Health Check Tool

Implementation pattern per [ADR-007: Tool Implementation Pattern](../docs/adr.md#adr-007-tool-implementation-pattern):

#### Function Signature

```python
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
        Health status of OSDU connection and services
    """
    pass
```

#### Expected Response Format

```json
{
  "connectivity": "success",
  "server_url": "https://your-osdu.com",
  "data_partition": "your-partition",
  "timestamp": "2025-01-15T10:30:00Z",
  "authentication": {
    "status": "valid"
  },
  "services": {
    "storage": "healthy",
    "search": "healthy",
    "legal": "healthy"
  },
  "version_info": {
    "storage_service": "1.0.0"
  }
}
```

#### Implementation Guidelines

1. **Resource Management**: Always clean up HTTP clients in `finally` blocks
2. **Error Granularity**: Test each component independently when possible
3. **Timeout Handling**: Use reasonable timeouts for each service check
4. **Optional Features**: Make expensive checks optional via parameters

### Server Registration

Following [ADR-001: MCP Framework Selection](../docs/adr.md#adr-001-mcp-framework-selection):

```python
# server.py
from mcp.server.fastmcp import FastMCP
from .tools.health_check import health_check

# Create FastMCP server instance
mcp = FastMCP("OSDU MCP Server")

# Register tools
mcp.register_tool()(health_check)

# Entry point
if __name__ == "__main__":
    mcp.run()
```

## Environment Configuration

### Required Environment Variables

```bash
# Core OSDU Configuration
export OSDU_MCP_SERVER_URL="https://your-osdu.com"
export OSDU_MCP_SERVER_DATA_PARTITION="your-partition"

# Required Authentication Variables (all methods)
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant"

# Authentication Method (choose one)
# Method 1: Service Principal
export AZURE_CLIENT_SECRET="your-secret"

# Method 2: Managed Identity (production)
# No additional variables needed beyond AZURE_CLIENT_ID and AZURE_TENANT_ID

# Method 3: Azure CLI (development)
export OSDU_MCP_AUTH_ALLOW_AZURE_CLI="true"
# Run: az login
```

### Optional Configuration File

```yaml
# config.yaml
server:
  url: "https://your-osdu.com"
  data_partition: "your-partition"
  timeout: 30

auth:
  allowAzureCLI: false
  allowAzPowerShell: false
  allowInteractive: false

logging:
  level: "INFO"
```

## Testing Strategy

Following [ADR-010: Testing Philosophy and Strategy](../docs/adr.md#adr-010-testing-philosophy-and-strategy), we adopt a behavior-driven testing approach.

### Test Structure

Tests mirror the source structure per [ADR-006](../docs/adr.md#adr-006-project-structure-and-packaging):

```python
# tests/test_health_check.py
import pytest
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_health_check_reports_service_unavailable():
    """Test that health check correctly reports when services are down."""
    with aioresponses() as mocked:
        # Mock service returning error
        mocked.get("https://osdu.com/api/storage/v2/info", status=503)
        
        result = await health_check(include_services=True)
        
        assert result["services"]["storage"] == "unhealthy: Service unavailable"
```

### Testing Philosophy

1. **Behavior-Driven**: Test what code does, not how it does it
2. **Boundary Testing**: Mock at service boundaries (HTTP, auth) only
3. **Appropriate Tools**: Use `aioresponses` for HTTP mocking
4. **Readable Tests**: Each test should be understandable in isolation

### Test Categories

1. **Unit Tests**: Test individual components in isolation
   - Mock external dependencies only
   - Focus on single behavior per test
   - Fast execution (< 100ms per test)

2. **Integration Tests**: Test component interactions
   - Use real implementations where possible
   - Mock only external services (OSDU APIs)
   - Verify end-to-end workflows

3. **Contract Tests**: Verify API contracts
   - Test MCP protocol compliance
   - Validate response formats
   - Ensure backward compatibility

### Testing Guidelines

- Write descriptive test names that describe behavior
- Minimize test setup complexity
- Use factory functions for test objects
- Prefer simple test data over complex fixtures
- Each test should verify one specific behavior

### Dependencies

Test-specific dependencies:
- `pytest` and `pytest-asyncio` for async testing
- `aioresponses` for HTTP mocking
- `pytest-cov` for coverage reporting

## Deployment Options

### Container Deployment

```dockerfile
FROM python:3.12-slim

# Install dependencies
COPY pyproject.toml .
RUN pip install uv && uv sync

# Copy application
COPY src/ /app/src/
WORKDIR /app

# Set up environment for Managed Identity
ENV OSDU_MCP_AUTH_ALLOW_AZURE_CLI=false

# Run the server
CMD ["uv", "run", "osdu-mcp-server"]
```

### MCP Client Integration

```json
{
  "mcpServers": {
    "osdu-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "osdu-mcp-server"],
      "env": {
        "OSDU_MCP_SERVER_URL": "https://your-osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "your-partition",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_TENANT_ID": "your-tenant"
      }
    }
  }
}
```

## Development Environment

### Prerequisites

- Python ≥ 3.12
- uv package manager
- Azure CLI (for development authentication)

### Setup Instructions

```bash
# Clone and setup project
cd osdu_mcp_server
uv sync
uv pip install -e .

# Configure environment
export OSDU_MCP_SERVER_URL="https://your-osdu.com"
export OSDU_MCP_SERVER_DATA_PARTITION="your-partition"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant"
export OSDU_MCP_AUTH_ALLOW_AZURE_CLI="true"

# Authenticate with Azure
az login

# Run the server
uv run osdu-mcp-server
```

## Validation (Phase 1 Completion Criteria)

**Implementation is only complete when ALL validation steps pass successfully.**

### 1. Installation and Dependencies

```bash
# Verify installation
uv sync && uv pip install -e .
```

### 2. Configuration Validation

Test configuration precedence and loading:

```bash
# Test environment variable precedence
OSDU_MCP_SERVER_URL="https://test.com" \
uv run python -c "
from osdu_mcp_server.shared.config_manager import ConfigManager
config = ConfigManager()
assert config.get('server', 'url') == 'https://test.com'
print('✅ Configuration precedence working')
"
```

### 3. Authentication Testing

Verify authentication across scenarios:

```bash
# Test authentication initialization
uv run python -c "
import asyncio
from osdu_mcp_server.shared.config_manager import ConfigManager
from osdu_mcp_server.shared.auth_handler import AuthHandler

async def test_auth():
    config = ConfigManager()
    auth = AuthHandler(config)
    token = await auth.get_access_token()
    assert token, 'Token should be available'
    print('✅ Authentication working')

asyncio.run(test_auth())
"
```

### 4. Health Check Tool Validation

Test tool implementation:

```bash
# Test health check execution
uv run python -c "
import asyncio
from osdu_mcp_server.tools.health_check import health_check

async def test_health():
    result = await health_check()
    assert result['connectivity'] == 'success'
    print('✅ Health check tool working')

asyncio.run(test_health())
"
```

### 5. MCP Protocol Integration

Verify MCP server functionality:

```bash
# Test tool discovery
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
uv run osdu-mcp-server

# Test health check via MCP
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"health_check","arguments":{}}}' | \
uv run osdu-mcp-server
```

### 6. Test Suite Execution

Run comprehensive test suite:

```bash
# Execute all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=osdu_mcp_server --cov-report=html

# Verify coverage > 80%
uv run pytest --cov=osdu_mcp_server --cov-fail-under=80
```

### 7. Integration with MCP Client

Final validation with actual MCP client:

- [ ] Server appears in MCP client tool list
- [ ] Health check tool executes via MCP protocol
- [ ] Response format is correctly parsed by client
- [ ] Error handling works as expected

## Success Criteria Checklist

**✅ Phase 1 Complete When:**

- [ ] All architectural decisions documented in ADRs
- [ ] Installation completes without errors
- [ ] Configuration loads correctly with proper precedence
- [ ] Authentication works across all deployment scenarios
- [ ] Health check tool executes successfully
- [ ] OSDU connectivity confirmed
- [ ] All unit tests pass with >80% coverage
- [ ] MCP protocol compliance verified
- [ ] Error handling scenarios tested
- [ ] Integration with MCP client confirmed

## Future Phases

This specification establishes the foundation for future phases:

- **Phase 2**: Storage operations (CRUD operations)
- **Phase 3**: Search functionality and schema validation
- **Phase 4**: Legal tag management and advanced features

Each future phase will follow the same architectural patterns established in the ADRs, ensuring consistency and maintainability across the entire system.

## References

- [Project Brief](../docs/project-brief.md)
- [Project Brief](../docs/project-prd.md)
- [Architect Design](../docs/project-architect.md)
- [Architecture Decision Records](../docs/adr.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/pydantic/FastMCP)
- [Azure DefaultAzureCredential](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)