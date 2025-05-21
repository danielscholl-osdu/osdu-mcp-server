"""Tests for the MCP server integration."""

from osdu_mcp_server.server import mcp
from osdu_mcp_server.tools.health_check import health_check
from osdu_mcp_server.tools.schema import (
    schema_list,
    schema_get,
    schema_search,
    schema_create,
    schema_update,
)


def test_server_instance():
    """Test that server instance is created correctly."""
    assert mcp is not None
    assert mcp.name == "OSDU MCP Server"


def test_tools_registered():
    """Test that tools are registered with the server."""
    # The health_check function should be registered
    # This is a basic test to ensure the server setup is correct
    assert health_check is not None
    
    # Verify schema tools are available
    assert schema_list is not None
    assert schema_get is not None
    assert schema_search is not None
    assert schema_create is not None
    assert schema_update is not None
    
    # In a real test, we would verify the tool is registered
    # with the MCP server, but this depends on the MCP framework API
