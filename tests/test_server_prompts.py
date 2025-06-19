"""
Integration tests for server prompt registration.

Tests that prompts are properly registered with the MCP server.
"""

import pytest


def test_prompt_available_in_main_package():
    """Test that list_mcp_assets is available in main package exports."""
    from osdu_mcp_server import list_mcp_assets

    assert list_mcp_assets is not None
    assert callable(list_mcp_assets)


@pytest.mark.asyncio
async def test_prompt_execution_via_main_import():
    """Test that prompt can be executed via main package import."""
    from osdu_mcp_server import list_mcp_assets

    result = await list_mcp_assets()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert len(result[0]["content"]) > 1000