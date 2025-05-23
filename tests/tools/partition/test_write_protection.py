"""Tests for write operation protection."""

import os
from unittest.mock import patch

import pytest

from osdu_mcp_server.tools.partition.create import partition_create
from osdu_mcp_server.tools.partition.delete import partition_delete
from osdu_mcp_server.tools.partition.update import partition_update


@pytest.mark.asyncio
async def test_partition_create_blocked_by_default():
    """Test partition create is blocked when write is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove the env var if it exists
        os.environ.pop("OSDU_MCP_ENABLE_WRITE_MODE", None)

        with patch("osdu_mcp_server.tools.partition.create.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.create.AuthHandler"):
                result = await partition_create("test-partition", {"key": "value"})

                assert result["success"] is False
                assert result["write_enabled"] is False
                assert "Write operations are disabled" in result["error"]


@pytest.mark.asyncio
async def test_partition_update_blocked_by_default():
    """Test partition update is blocked when write is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("OSDU_MCP_ENABLE_WRITE_MODE", None)

        with patch("osdu_mcp_server.tools.partition.update.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.update.AuthHandler"):
                result = await partition_update("test-partition", {"key": "value"})

                assert result["success"] is False
                assert result["write_enabled"] is False
                assert "Write operations are disabled" in result["error"]


@pytest.mark.asyncio
async def test_partition_delete_blocked_by_default():
    """Test partition delete is blocked when write is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("OSDU_MCP_ENABLE_WRITE_MODE", None)

        with patch("osdu_mcp_server.tools.partition.delete.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.delete.AuthHandler"):
                result = await partition_delete("test-partition", confirm=True)

                assert result["success"] is False
                assert result["write_enabled"] is False
                assert "Write operations are disabled" in result["error"]


@pytest.mark.asyncio
async def test_partition_delete_requires_confirmation():
    """Test partition delete requires explicit confirmation."""
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_WRITE_MODE": "true"}):
        with patch("osdu_mcp_server.tools.partition.delete.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.delete.AuthHandler"):
                # Without confirmation
                result = await partition_delete("test-partition", confirm=False)

                assert result["success"] is False
                assert result["write_enabled"] is True
                assert result["confirmed"] is False
                assert "requires explicit confirmation" in result["error"]


@pytest.mark.asyncio
async def test_dry_run_operations():
    """Test dry run mode for write operations."""
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_WRITE_MODE": "true"}):
        with patch("osdu_mcp_server.tools.partition.create.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.create.AuthHandler"):
                # Test create dry run
                result = await partition_create(
                    "test-partition", {"key": "value"}, dry_run=True
                )

                assert result["success"] is True
                assert result["created"] is False
                assert result["dry_run"] is True
                assert "would be created" in result["message"]

        with patch("osdu_mcp_server.tools.partition.delete.ConfigManager"):
            with patch("osdu_mcp_server.tools.partition.delete.AuthHandler"):
                # Test delete dry run
                result = await partition_delete(
                    "test-partition", confirm=True, dry_run=True
                )

                assert result["success"] is True
                assert result["deleted"] is False
                assert result["dry_run"] is True
                assert "would be deleted" in result["message"]
