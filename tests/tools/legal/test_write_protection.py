"""Tests for write protection on legal tools."""

import pytest
from unittest.mock import patch
import os

from mcp.shared.exceptions import McpError

from osdu_mcp_server.tools.legal import (
    legaltag_create,
    legaltag_update,
    legaltag_delete
)


@pytest.mark.asyncio
async def test_legaltag_create_write_disabled():
    """Test that legaltag_create fails when write is disabled."""
    test_env = {
        'OSDU_MCP_ENABLE_WRITE_MODE': 'false'
    }
    
    with patch.dict(os.environ, test_env):
        with pytest.raises(McpError) as exc_info:
            await legaltag_create(
                name="Test-Tag",
                description="Test description",
                country_of_origin=["US"],
                contract_id="TEST123",
                security_classification="Private",
                personal_data="No Personal Data",
                export_classification="EAR99",
                data_type="First Party Data"
            )
        
        assert exc_info.value.error.code == 403
        assert "Legal tag write operations are disabled" in exc_info.value.error.message
        assert "OSDU_MCP_ENABLE_WRITE_MODE=true" in exc_info.value.error.message


@pytest.mark.asyncio
async def test_legaltag_update_write_disabled():
    """Test that legaltag_update fails when write is disabled."""
    test_env = {
        'OSDU_MCP_ENABLE_WRITE_MODE': 'false'
    }
    
    with patch.dict(os.environ, test_env):
        with pytest.raises(McpError) as exc_info:
            await legaltag_update(
                name="Test-Tag",
                description="Updated description"
            )
        
        assert exc_info.value.error.code == 403
        assert "Legal tag write operations are disabled" in exc_info.value.error.message


@pytest.mark.asyncio
async def test_legaltag_delete_disabled():
    """Test that legaltag_delete fails when delete is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove the env var if it exists
        os.environ.pop("OSDU_MCP_ENABLE_DELETE_MODE", None)
        
        with patch("osdu_mcp_server.tools.legal.delete.ConfigManager"):
            with patch("osdu_mcp_server.tools.legal.delete.AuthHandler"):
                with pytest.raises(McpError) as exc_info:
                    await legaltag_delete(
                        name="Test-Tag",
                        confirm=True
                    )
                
                assert exc_info.value.error.code == 403
                assert "Delete operations are disabled" in exc_info.value.error.message
                assert "OSDU_MCP_ENABLE_DELETE_MODE=true" in exc_info.value.error.message


@pytest.mark.asyncio
async def test_legaltag_delete_no_confirmation():
    """Test that legaltag_delete fails without confirmation."""
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_DELETE_MODE": "true"}, clear=False):
        with patch("osdu_mcp_server.tools.legal.delete.ConfigManager"):
            with patch("osdu_mcp_server.tools.legal.delete.AuthHandler"):
                with pytest.raises(McpError) as exc_info:
                    await legaltag_delete(
                        name="Test-Tag",
                        confirm=False
                    )
                
                assert exc_info.value.error.code == 400
                assert "Deletion not confirmed" in exc_info.value.error.message
                assert "WARNING: This will invalidate all associated data" in exc_info.value.error.message
