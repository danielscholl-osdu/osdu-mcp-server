# OSDU MCP Server

[![CI](https://github.com/danielscholl-osdu/osdu-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/danielscholl-osdu/osdu-mcp-server/actions/workflows/ci.yml)
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

To utilize this MCP server directly in other projects either use the buttons to install in VSCode, edit the `.mcp.json` file directory.

> Clients tend to have slightly different configurations

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22osdu-mcp-server%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fdanielscholl-osdu%2Fosdu-mcp-server%40main%22%2C%22osdu-mcp-server%22%5D%2C%22env%22%3A%7B%22OSDU_MCP_SERVER_URL%22%3A%22%24%7Binput%3Aosdu_url%7D%22%2C%22OSDU_MCP_SERVER_DATA_PARTITION%22%3A%22%24%7Binput%3Adata_partition%7D%22%2C%22AZURE_CLIENT_ID%22%3A%22%24%7Binput%3Aazure_client_id%7D%22%2C%22AZURE_TENANT_ID%22%3A%22%24%7Binput%3Aazure_tenant_id%7D%22%7D%2C%22inputs%22%3A%5B%7B%22id%22%3A%22osdu_url%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OSDU%20Server%20URL%20(e.g.%2C%20https%3A%2F%2Fyour-osdu.com)%22%7D%2C%7B%22id%22%3A%22data_partition%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OSDU%20Data%20Partition%20(e.g.%2C%20your-partition)%22%7D%2C%7B%22id%22%3A%22azure_client_id%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Client%20ID%22%7D%2C%7B%22id%22%3A%22azure_tenant_id%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Tenant%20ID%22%7D%2C%7B%22id%22%3A%22azure_client_secret%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Azure%20Client%20Secret%20(optional%20for%20Service%20Principal%20auth)%22%2C%22password%22%3Atrue%7D%5D%7D)

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

### Authentication Methods

Authentication is handled via the Azure CLI by default. You must be logged in using `az login` before running the server:

To enable Service Principal authentication, add the optional `AZURE_CLIENT_SECRET` environment variable:.


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

## Available Tools

### Foundation
- **health_check**: Check OSDU platform connectivity and service health

### Partition Service
- **partition_list**: List all accessible OSDU partitions
- **partition_get**: Retrieve configuration for a specific partition
- **partition_create**: Create a new partition (write-protected)
- **partition_update**: Update partition properties (write-protected)
- **partition_delete**: Delete a partition (write-protected)

### Entitlements Service
- **entitlements_mine**: Get groups for the current authenticated user

### Legal Service
- **legaltag_list**: List all legal tags
- **legaltag_get**: Get specific legal tag
- **legaltag_get_properties**: Get allowed property values
- **legaltag_search**: Search legal tags with filters
- **legaltag_batch_retrieve**: Get multiple tags at once
- **legaltag_create**: Create new legal tag (write-protected)
- **legaltag_update**: Update legal tag (write-protected)
- **legaltag_delete**: Delete legal tag (delete-protected)

### Schema Service
- **schema_list**: List available schemas with optional filtering
- **schema_get**: Retrieve complete schema by ID
- **schema_search**: Advanced schema discovery with rich filtering and text search
- **schema_create**: Create a new schema (write-protected)
- **schema_update**: Update an existing schema (write-protected)

### Storage Service
- **storage_create_update_records**: Create or update records (write-protected)
- **storage_get_record**: Get latest version of a record by ID
- **storage_get_record_version**: Get specific version of a record
- **storage_list_record_versions**: List all versions of a record
- **storage_query_records_by_kind**: Get record IDs of a specific kind
- **storage_fetch_records**: Retrieve multiple records at once
- **storage_delete_record**: Logically delete a record (delete-protected)
- **storage_purge_record**: Permanently delete a record (delete-protected)



