# OSDU MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with access to OSDU platform capabilities.

## Purpose

This server enables AI assistants to interact with OSDU platform services including search, data management, and schema operations through the MCP protocol.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd osdu-mcp-server

# Install using uv (recommended)
uv sync
uv pip install -e .
```

## Configuration

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
  "OSDU_MCP_LOGGING_LEVEL": "INFO"  // Optional, defaults to INFO
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

#### Advanced Schema Search

The `schema_search` tool provides powerful capabilities for discovering schemas:

```python
# Find all schemas containing "pressure" in their description
schema_search(text="pressure", search_in=["description"])

# Get all schemas with version 1.1.* across any authority
schema_search(version_pattern="1.1.*")

# Search for schemas with specific combinations of properties
schema_search(
    filter={
        "authority": ["osdu", "lab"],
        "status": ["PUBLISHED"],
        "scope": "SHARED"
    }
)

# Include full schema content in results
schema_search(include_content=True)
```

### Storage Service
- **storage_create_update_records**: Create or update records (write-protected)
- **storage_get_record**: Get latest version of a record by ID
- **storage_get_record_version**: Get specific version of a record
- **storage_list_record_versions**: List all versions of a record
- **storage_query_records_by_kind**: Get record IDs of a specific kind
- **storage_fetch_records**: Retrieve multiple records at once
- **storage_delete_record**: Logically delete a record (delete-protected)
- **storage_purge_record**: Permanently delete a record (delete-protected)

#### Storage Operations and Protection

The Storage Service implements two levels of protection for different types of operations:

- **Write Operations** (create, update): Controlled by `OSDU_MCP_ENABLE_WRITE_MODE=true`
- **Delete Operations** (delete, purge): Controlled by `OSDU_MCP_ENABLE_DELETE_MODE=true`

This provides granular control over data lifecycle operations, allowing environments to permit data creation while preventing deletion.

### High Level Roadmap
- Phase 2 (completed): Partition, Legal, and Entitlements services
- Phase 3 (completed): Schema Service and advanced search functionality
- Phase 4 (completed): Storage service and data validation
- Phase 5 (future): Advanced features and integrations

## Documentation

- [Project Brief](docs/project-brief.md)
- [Project Requirements](docs/project-prd.md)
- [Architecture Overview](docs/project-architect.md)
- [Architecture Design Decisions](docs/adr/README.md)
- [Foundation Spec](specs/foundation-spec.md)

## Project Development

This is an AI-developed project, built using AI coding tools to accelerate development while striving to maintain high quality standards.  Read the [case-study](case-study.md) to dive into what was found to work.