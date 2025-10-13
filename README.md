# OSDU MCP Server

[![CI](https://github.com/danielscholl-osdu/osdu-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/danielscholl-osdu/osdu-mcp-server/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/danielscholl-osdu/osdu-mcp-server)](https://github.com/danielscholl-osdu/osdu-mcp-server/releases)
[![Python](https://img.shields.io/badge/python-3.12%20|%203.13-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green)](https://modelcontextprotocol.io)

A Model Context Protocol (MCP) server that provides AI assistants with access to OSDU platform capabilities.

## Purpose

This server enables AI assistants to interact with OSDU platform services including search, data management, and schema operations through the MCP protocol.

## AI-Driven Development

[![AI-Driven](https://img.shields.io/badge/AI--Driven-Development-blueviolet)](https://github.com/danielscholl-osdu/osdu-mcp-server/blob/main/case-study.md)
[![Copilot-Ready](https://img.shields.io/badge/GitHub%20Copilot-Ready-8A2BE2?logo=github)](https://github.com/danielscholl-osdu/osdu-mcp-server/blob/main/.github/copilot-instructions.md)

This project follows an AI-driven development workflow:
- 🤖 **Built with AI** - Developed using Claude Code and GitHub Copilot
- 📋 **AI Task Assignment** - Issues labeled with `copilot` are automatically assigned
- 📚 **AI-Friendly Documentation** - Comprehensive guides for AI agents in [CLAUDE.md](CLAUDE.md) and [.github/copilot-instructions.md](.github/copilot-instructions.md)
- 🔄 **Multi-Agent Orchestration** - Different AI agents handle different tasks based on their strengths

See our [Case Study](case-study.md) for insights on building quality code with AI agents.

## Documentation

- [Project Brief](docs/project-brief.md)
- [Project Requirements](docs/project-prd.md)
- [Architecture Overview](docs/project-architect.md)
- [Architecture Design Decisions](docs/adr/README.md)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd osdu-mcp-server

# Install using uv (recommended)
uv sync
uv pip install -e '.[dev]'
```

## Configuration

### Claude Code CLI

To add this MCP server using the Claude Code CLI:

```bash
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "AZURE_CLIENT_ID=your-client-id" \
  -e "AZURE_TENANT_ID=your-tenant-id"
```

### Direct Installation

To use this MCP server in your projects, add the following to your `.mcp.json` file:

```json
{
  "mcpServers": {
    "osdu-mcp-server": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main",
        "osdu-mcp-server"
      ],
      "env": {
        "OSDU_MCP_SERVER_URL": "https://your-osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "your-partition",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

### VS Code Quick Install

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22osdu-mcp-server%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fdanielscholl-osdu%2Fosdu-mcp-server%40main%22%2C%22osdu-mcp-server%22%5D%2C%22env%22%3A%7B%22OSDU_MCP_SERVER_URL%22%3A%22%24%7Binput%3Aosdu_url%7D%22%2C%22OSDU_MCP_SERVER_DATA_PARTITION%22%3A%22%24%7Binput%3Adata_partition%7D%22%2C%22AZURE_CLIENT_ID%22%3A%22%24%7Binput%3Aazure_client_id%7D%22%2C%22AZURE_TENANT_ID%22%3A%22%24%7Binput%3Aazure_tenant_id%7D%22%7D%2C%22inputs%22%3A%5B%7B%22id%22%3A%22osdu_url%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OSDU%20Server%20URL%20(e.g.%2C%20https%3A%2F%2Fyour-osdu.com)%22%7D%2C%7B%22id%22%3A%22data_partition%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OSDU%20Data%20Partition%20(e.g.%2C%20your-partition)%22%7D%2C%7B%22id%22%3A%22azure_client_id%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Client%20ID%22%7D%2C%7B%22id%22%3A%22azure_tenant_id%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Tenant%20ID%22%7D%2C%7B%22id%22%3A%22azure_client_secret%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Client%20Secret%20(optional%20for%20Service%20Principal%20auth)%22%2C%22password%22%3Atrue%7D%5D%7D)

### Local Development

For local development, you can also use the local installation method:

To use the OSDU MCP Server, configure it through your MCP client's configuration file:

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

### Domain Configuration

**Critical for ACL Format**: OSDU deployments use different data domain formats for Access Control Lists (ACL). Configure your data domain to avoid ACL format errors:

```json
"env": {
  "OSDU_MCP_SERVER_DOMAIN": "contoso.com"
}
```

**Data Domain Examples:**
- Standard OSDU: `contoso.com` (default)
- Microsoft OSDU: `dataservices.energy`
- Microsoft Internal: `msft-osdu-test.org`

**Data Domain Detection Methods:**
1. **Environment Variable** (Recommended): Set `OSDU_MCP_SERVER_DOMAIN`
2. **Use Entitlements Tool**: Run `entitlements_mine()` to see your group format
3. **Check with Administrator**: Ask your OSDU administrator for the correct data domain

**Important**: The data domain is the internal OSDU data system domain used in ACL group emails, not the FQDN from your server URL.

If not set, the server will attempt to extract the domain from your server URL. For more guidance, use the MCP resource: `ReadMcpResourceTool(server="osdu-mcp-server", uri="file://acl-format-examples.json")`.

### Authentication Methods

The server supports **multi-cloud authentication** with automatic provider detection:

#### Authentication Priority

The server automatically detects your authentication provider in this priority order:

1. **Manual Token** (highest priority) - `OSDU_MCP_USER_TOKEN`
2. **Azure** - `AZURE_CLIENT_ID` or `AZURE_TENANT_ID`
3. **AWS** (explicit) - `AWS_ACCESS_KEY_ID` or `AWS_PROFILE`
4. **GCP** (explicit) - `GOOGLE_APPLICATION_CREDENTIALS`
5. **AWS** (auto-discovery) - IAM roles, SSO
6. **GCP** (auto-discovery) - gcloud, metadata service

---

#### Azure Authentication

**Method 1: Azure CLI (Development)**
- **Setup**: Run `az login` before using the server
- **Environment Variables**:
  - `AZURE_CLIENT_ID`: Your OSDU application ID
  - `AZURE_TENANT_ID`: Your Azure tenant ID
  - No `AZURE_CLIENT_SECRET` needed

**Example:**
```bash
az login
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "AZURE_CLIENT_ID=your-osdu-app-id" \
  -e "AZURE_TENANT_ID=your-tenant-id"
```

**Method 2: Service Principal (Production)**
- **Setup**: Create or use an existing service principal
- **Environment Variables**:
  - `AZURE_CLIENT_ID`: Service principal ID
  - `AZURE_CLIENT_SECRET`: Service principal secret
  - `AZURE_TENANT_ID`: Your Azure tenant ID
  - `OSDU_MCP_AUTH_SCOPE`: (Optional) Custom OAuth scope for v1.0 token environments

**Example:**
```bash
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "AZURE_CLIENT_ID=your-service-principal-id" \
  -e "AZURE_CLIENT_SECRET=your-service-principal-secret" \
  -e "AZURE_TENANT_ID=your-tenant-id"
```

---

#### AWS Authentication

**Method 1: AWS SSO (Development)**
- **Setup**: Configure AWS SSO and log in
- **Environment Variables**:
  - `AWS_PROFILE`: Your AWS profile name
  - (Other OSDU config as usual)

**Example:**
```bash
aws sso login --profile dev-profile
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "AWS_PROFILE=dev-profile"
```

**Method 2: Access Keys (Production)**
- **Setup**: Obtain AWS access keys
- **Environment Variables**:
  - `AWS_ACCESS_KEY_ID`: Your AWS access key
  - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
  - `AWS_REGION`: AWS region (e.g., us-east-1)

**Example:**
```bash
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" \
  -e "AWS_SECRET_ACCESS_KEY=your-secret-key" \
  -e "AWS_REGION=us-east-1"
```

**Method 3: IAM Roles (EC2/ECS/Lambda)**
- **Setup**: Assign IAM role to your compute instance
- **Environment Variables**: None needed! Automatic credential discovery
- **Note**: Works on EC2, ECS/Fargate, Lambda with appropriate IAM roles

---

#### GCP Authentication

**Method 1: gcloud CLI (Development)**
- **Setup**: Run `gcloud auth application-default login`
- **Environment Variables**: None needed! Automatic credential discovery

**Example:**
```bash
gcloud auth application-default login
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition"
```

**Method 2: Service Account Key (Production)**
- **Setup**: Download service account JSON key
- **Environment Variables**:
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON key

**Example:**
```bash
claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"
```

**Method 3: Workload Identity (GKE)**
- **Setup**: Configure Workload Identity on GKE
- **Environment Variables**: None needed! Automatic credential discovery
- **Note**: Works on GKE with Workload Identity configured

---

#### Manual OAuth Token (Any Provider)

**Use Case**: Custom OAuth providers, testing, or unsupported clouds

- **Setup**: Obtain OAuth Bearer token from your provider
- **Environment Variables**:
  - `OSDU_MCP_USER_TOKEN`: Your OAuth Bearer token (JWT format)
  - **Priority**: This method ALWAYS takes precedence over all others

**Example:**
```bash
# Obtain token from your OAuth provider
TOKEN=$(your-oauth-command)

claude mcp add osdu-mcp-server uvx "git+https://github.com/danielscholl-osdu/osdu-mcp-server@main" \
  -e "OSDU_MCP_SERVER_URL=https://your-osdu.com" \
  -e "OSDU_MCP_SERVER_DATA_PARTITION=your-partition" \
  -e "OSDU_MCP_USER_TOKEN=$TOKEN"
```

**Token Requirements:**
- Valid JWT format (header.payload.signature)
- Not expired
- Server warns if token expires within 5 minutes

**Security Notes:**
- Tokens are validated for format and expiration
- Tokens are never logged
- Tokens must be refreshed manually when they expire

#### Authorization Setup

**When you need additional setup:**
- ✅ **Azure CLI auth**: Always requires authorization setup
- ✅ **External service principal**: Requires authorization setup  
- ❌ **OSDU app's own service principal**: No additional setup needed

**For Azure CLI or External Service Principal:**

1. **Navigate to your OSDU application** in **App registrations**
2. **Go to Expose an API** → **Authorized client applications**
3. **Click Add a client application**
4. **Enter the client ID**:
   - Azure CLI: `04b07795-8ddb-461a-bbee-02f9e1bf7b46`
   - External Service Principal: Your service principal's ID
5. **Select the `user_impersonation` scope**
6. **Click Add**

**Verify authentication:**
```bash
az account get-access-token --resource YOUR_AZURE_CLIENT_ID
```

**Common Issues:**
- **"Application not found"**: Azure CLI app doesn't exist in some tenants. Use service principal instead.
- **"Invalid resource"**: The client hasn't been authorized. Follow authorization setup above.
- **"Authentication failed"**: Verify your client ID matches your OSDU application or service principal.


### Write Operations

Write operations (create, update) for any service are disabled by default, you must explicitly enable them:

```json
"env": {
  "OSDU_MCP_ENABLE_WRITE_MODE": "true"
}
```

### Delete Operations

Delete and purge operations are separately controlled and disabled by default:

```json
"env": {
  "OSDU_MCP_ENABLE_DELETE_MODE": "true"
}
```

This dual protection allows you to enable data creation and updates while maintaining strict control over destructive operations.

### Complete Configuration Example

Here's a complete `.mcp.json` configuration example with all common environment variables:

```json
{
  "mcpServers": {
    "osdu-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "osdu-mcp-server"],
      "env": {
        "OSDU_MCP_SERVER_URL": "https://your-osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "opendes",
        "OSDU_MCP_SERVER_DOMAIN": "contoso.com",
        "OSDU_MCP_ENABLE_WRITE_MODE": "true",
        "OSDU_MCP_ENABLE_DELETE_MODE": "true",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Logging Configuration

The MCP server uses structured JSON logging that follows [ADR-016](docs/adr/016-structured-logging-and-observability-pattern.md). By default, logging is disabled due to verbosity. You can enable it by setting:

```json
"env": {
  "OSDU_MCP_LOGGING_ENABLED": "true",
  "OSDU_MCP_LOGGING_LEVEL": "INFO" 
}
```

Valid logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Usage

### Health Check

```
osdu:health_check
```

This returns the health status of your OSDU platform, checking authentication and the availability of all services (storage, search, legal, schema, file, workflow, entitlements, and dataset).

## Available Capabilities

### Prompts
- **list_mcp_assets**: Comprehensive overview of all server capabilities with usage examples and quick start guidance
- **guide_search_patterns**: Search pattern guidance for OSDU operations with Elasticsearch syntax examples

### Tools

#### Foundation
- **health_check**: Check OSDU platform connectivity and service health

#### Partition Service
- **partition_list**: List all accessible OSDU partitions
- **partition_get**: Retrieve configuration for a specific partition
- **partition_create**: Create a new partition (write-protected)
- **partition_update**: Update partition properties (write-protected)
- **partition_delete**: Delete a partition (write-protected)

#### Entitlements Service
- **entitlements_mine**: Get groups for the current authenticated user

#### Legal Service
- **legaltag_list**: List all legal tags
- **legaltag_get**: Get specific legal tag
- **legaltag_get_properties**: Get allowed property values
- **legaltag_search**: Search legal tags with filters
- **legaltag_batch_retrieve**: Get multiple tags at once
- **legaltag_create**: Create new legal tag (write-protected)
- **legaltag_update**: Update legal tag (write-protected)
- **legaltag_delete**: Delete legal tag (delete-protected)

#### Schema Service
- **schema_list**: List available schemas with optional filtering
- **schema_get**: Retrieve complete schema by ID
- **schema_search**: Advanced schema discovery with rich filtering and text search
- **schema_create**: Create a new schema (write-protected)
- **schema_update**: Update an existing schema (write-protected)

#### Search Service
- **search_query**: Execute search queries using Elasticsearch syntax
- **search_by_id**: Find specific records by ID
- **search_by_kind**: Find all records of specific type

#### Storage Service
- **storage_create_update_records**: Create or update records (write-protected)
- **storage_get_record**: Get latest version of a record by ID
- **storage_get_record_version**: Get specific version of a record
- **storage_list_record_versions**: List all versions of a record
- **storage_query_records_by_kind**: Get record IDs of a specific kind
- **storage_fetch_records**: Retrieve multiple records at once
- **storage_delete_record**: Logically delete a record (delete-protected)
- **storage_purge_record**: Permanently delete a record (delete-protected)



