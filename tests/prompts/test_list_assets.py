"""
Tests for list_mcp_assets prompt.

Following ADR-010 Testing Philosophy: Test the data provider (prompt function),
not the data consumer (AI model). Focus on contract compliance and data structure.
"""

import pytest
from osdu_mcp_server.prompts.list_assets import list_mcp_assets


@pytest.mark.asyncio
async def test_list_mcp_assets_returns_message_list():
    """Test that list_mcp_assets returns a list of messages."""
    result = await list_mcp_assets()

    assert isinstance(result, list)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_list_mcp_assets_returns_proper_message_format():
    """Test that list_mcp_assets returns properly formatted MCP messages."""
    result = await list_mcp_assets()
    message = result[0]

    # Verify Message structure
    assert isinstance(message, dict)
    assert "role" in message
    assert "content" in message

    # Verify message content
    assert message["role"] == "user"
    assert isinstance(message["content"], str)
    assert len(message["content"]) > 0


@pytest.mark.asyncio
async def test_list_mcp_assets_content_has_required_sections():
    """Test that generated content includes all required sections."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify main sections are present
    assert "OSDU MCP Server Assets" in content
    assert "📊 Server Overview" in content
    assert "📝 Prompts" in content
    assert "🔧 Tools" in content
    assert "⚡ Configuration Quick Setup" in content
    assert "🎯 Quick Start Workflows" in content
    assert "💡 Pro Tips" in content


@pytest.mark.asyncio
async def test_list_mcp_assets_includes_all_service_tools():
    """Test that content includes tools from all implemented services."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify each service section is present
    assert "Foundation" in content
    assert "health_check" in content

    assert "Partition Service" in content
    assert "partition_list" in content
    assert "partition_get" in content

    assert "Entitlements Service" in content
    assert "entitlements_mine" in content

    assert "Legal Service" in content
    assert "legaltag_list" in content
    assert "legaltag_get" in content

    assert "Schema Service" in content
    assert "schema_list" in content
    assert "schema_get" in content

    assert "Storage Service" in content
    assert "storage_get_record" in content
    assert "storage_create_update_records" in content


@pytest.mark.asyncio
async def test_list_mcp_assets_includes_configuration_guidance():
    """Test that content includes configuration and setup guidance."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify configuration sections
    assert "OSDU_MCP_SERVER_URL" in content
    assert "AZURE_CLIENT_ID" in content
    assert "OSDU_MCP_ENABLE_WRITE_MODE" in content
    assert "OSDU_MCP_ENABLE_DELETE_MODE" in content

    # Verify authentication methods
    assert "Service Principal" in content
    assert "Managed Identity" in content
    assert "Azure CLI" in content


@pytest.mark.asyncio
async def test_list_mcp_assets_includes_workflow_examples():
    """Test that content includes workflow examples and quick start guidance."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify workflow sections
    assert "Quick Start Workflows" in content
    assert "Verify OSDU Connectivity" in content
    assert "Explore Available Data" in content
    assert "Query Existing Data" in content
    assert "Create New Data" in content


@pytest.mark.asyncio
async def test_list_mcp_assets_function_executes_without_errors():
    """Test that the prompt function executes without raising exceptions."""
    # This should complete without raising any exceptions
    result = await list_mcp_assets()

    # Basic sanity check that we got something
    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_list_mcp_assets_content_has_minimum_length():
    """Test that generated content has reasonable minimum length."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Content should be substantial (at least 1000 characters)
    assert len(content) >= 1000


@pytest.mark.asyncio
async def test_list_mcp_assets_includes_write_protection_information():
    """Test that content includes information about write protection."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify write protection information
    assert "write-protected" in content or "Write Mode Required" in content
    assert "delete-protected" in content or "delete mode" in content
    assert "disabled by default" in content


@pytest.mark.asyncio
async def test_list_mcp_assets_includes_helpful_footer():
    """Test that content includes helpful footer with next steps."""
    result = await list_mcp_assets()
    content = result[0]["content"]

    # Verify footer guidance
    assert "Ready to explore" in content or "Ready to get started" in content
    assert "health_check" in content  # Should recommend starting with health check
