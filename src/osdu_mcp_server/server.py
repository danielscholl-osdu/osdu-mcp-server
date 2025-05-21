"""MCP server instance for OSDU platform integration."""

from mcp.server.fastmcp import FastMCP

from .tools.health_check import health_check
from .tools.partition import (
    partition_list,
    partition_get,
    partition_create,
    partition_update,
    partition_delete,
)
from .tools.entitlements import (
    entitlements_mine,
)
from .tools.legal import (
    legaltag_list,
    legaltag_get,
    legaltag_get_properties,
    legaltag_search,
    legaltag_batch_retrieve,
    legaltag_create,
    legaltag_update,
    legaltag_delete,
)
from .tools.schema import (
    schema_list,
    schema_get,
    schema_search,
    schema_create,
    schema_update,
)
from .tools.storage import (
    storage_create_update_records,
    storage_get_record,
    storage_get_record_version,
    storage_list_record_versions,
    storage_query_records_by_kind,
    storage_fetch_records,
    storage_delete_record,
    storage_purge_record,
)

# Create FastMCP server instance
mcp = FastMCP("OSDU MCP Server")

# Register tools
mcp.tool()(health_check)

# Register partition tools
mcp.tool()(partition_list)
mcp.tool()(partition_get)
mcp.tool()(partition_create)
mcp.tool()(partition_update)
mcp.tool()(partition_delete)

# Register entitlements tools
mcp.tool()(entitlements_mine)

# Register legal tools
mcp.tool()(legaltag_list)
mcp.tool()(legaltag_get)
mcp.tool()(legaltag_get_properties)
mcp.tool()(legaltag_search)
mcp.tool()(legaltag_batch_retrieve)
mcp.tool()(legaltag_create)
mcp.tool()(legaltag_update)
mcp.tool()(legaltag_delete)

# Register schema tools
mcp.tool()(schema_list)
mcp.tool()(schema_get)
mcp.tool()(schema_search)
mcp.tool()(schema_create)
mcp.tool()(schema_update)

# Register storage tools
mcp.tool()(storage_create_update_records)
mcp.tool()(storage_get_record)
mcp.tool()(storage_get_record_version)
mcp.tool()(storage_list_record_versions)
mcp.tool()(storage_query_records_by_kind)
mcp.tool()(storage_fetch_records)
mcp.tool()(storage_delete_record)
mcp.tool()(storage_purge_record)

# This module can be imported by the main entry point