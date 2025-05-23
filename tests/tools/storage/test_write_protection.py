"""Tests for storage write and delete operation protection."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from osdu_mcp_server.tools.storage.create_update_records import (
    storage_create_update_records,
)
from osdu_mcp_server.tools.storage.delete_record import storage_delete_record
from osdu_mcp_server.tools.storage.purge_record import storage_purge_record


@pytest.mark.asyncio
async def test_storage_create_blocked_by_default():
    """Test storage create is blocked when write is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove the env var if it exists
        os.environ.pop("OSDU_MCP_ENABLE_WRITE_MODE", None)

        with patch("osdu_mcp_server.tools.storage.create_update_records.ConfigManager"):
            with patch(
                "osdu_mcp_server.tools.storage.create_update_records.AuthHandler"
            ):
                test_record = {
                    "kind": "test:test:test:1.0.0",
                    "acl": {"viewers": ["test"], "owners": ["test"]},
                    "legal": {
                        "legaltags": ["test"],
                        "otherRelevantDataCountries": ["US"],
                    },
                    "data": {"test": "data"},
                }

                try:
                    await storage_create_update_records([test_record])
                    assert False, "Expected exception was not raised"
                except Exception as e:
                    # Should fail with write protection error
                    assert "Write operations are disabled" in str(e)


@pytest.mark.asyncio
async def test_storage_delete_blocked_by_default():
    """Test storage delete is blocked when delete mode is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove the env var if it exists
        os.environ.pop("OSDU_MCP_ENABLE_DELETE_MODE", None)

        with patch("osdu_mcp_server.tools.storage.delete_record.ConfigManager"):
            with patch("osdu_mcp_server.tools.storage.delete_record.AuthHandler"):
                try:
                    await storage_delete_record("test:record:123")
                    assert False, "Expected exception was not raised"
                except Exception as e:
                    # Should fail with delete protection error
                    assert "Delete operations are disabled" in str(e)


@pytest.mark.asyncio
async def test_storage_purge_blocked_by_default():
    """Test storage purge is blocked when delete mode is disabled."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove the env var if it exists
        os.environ.pop("OSDU_MCP_ENABLE_DELETE_MODE", None)

        with patch("osdu_mcp_server.tools.storage.purge_record.ConfigManager"):
            with patch("osdu_mcp_server.tools.storage.purge_record.AuthHandler"):
                try:
                    await storage_purge_record("test:record:123", confirm=True)
                    assert False, "Expected exception was not raised"
                except Exception as e:
                    # Should fail with delete protection error
                    assert "Delete operations are disabled" in str(e)


@pytest.mark.asyncio
async def test_storage_purge_requires_confirmation():
    """Test storage purge requires explicit confirmation."""
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_DELETE_MODE": "true"}):
        with patch("osdu_mcp_server.tools.storage.purge_record.ConfigManager"):
            with patch("osdu_mcp_server.tools.storage.purge_record.AuthHandler"):
                try:
                    # Without confirmation
                    await storage_purge_record("test:record:123", confirm=False)
                    assert False, "Expected exception was not raised"
                except Exception as e:
                    # Should fail with confirmation requirement
                    assert "requires explicit confirmation" in str(e)


@pytest.mark.asyncio
async def test_dual_protection_independence():
    """Test that write and delete protections are independent."""
    test_record = {
        "kind": "test:test:test:1.0.0",
        "acl": {"viewers": ["test"], "owners": ["test"]},
        "legal": {"legaltags": ["test"], "otherRelevantDataCountries": ["US"]},
        "data": {"test": "data"},
    }

    # Test write enabled but delete disabled
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_WRITE_MODE": "true"}, clear=False):
        os.environ.pop("OSDU_MCP_ENABLE_DELETE_MODE", None)

        with patch("osdu_mcp_server.tools.storage.create_update_records.ConfigManager"):
            with patch(
                "osdu_mcp_server.tools.storage.create_update_records.AuthHandler"
            ):
                with patch(
                    "osdu_mcp_server.tools.storage.create_update_records.StorageClient"
                ) as mock_client:
                    # Mock successful creation
                    mock_instance = mock_client.return_value
                    mock_instance.create_update_records = AsyncMock(
                        return_value={
                            "recordCount": 1,
                            "recordIds": ["test:record:123"],
                            "recordIdVersions": ["1234567890"],
                        }
                    )
                    mock_instance.close = AsyncMock()

                    # Create should work
                    result = await storage_create_update_records([test_record])
                    assert result["success"] is True
                    assert result["write_enabled"] is True

        # But delete should still fail
        with patch("osdu_mcp_server.tools.storage.delete_record.ConfigManager"):
            with patch("osdu_mcp_server.tools.storage.delete_record.AuthHandler"):
                try:
                    await storage_delete_record("test:record:123")
                    assert False, "Expected exception was not raised"
                except Exception as e:
                    assert "Delete operations are disabled" in str(e)


@pytest.mark.asyncio
async def test_record_validation():
    """Test record validation for required fields."""
    with patch.dict(os.environ, {"OSDU_MCP_ENABLE_WRITE_MODE": "true"}):
        with patch("osdu_mcp_server.tools.storage.create_update_records.ConfigManager"):
            with patch(
                "osdu_mcp_server.tools.storage.create_update_records.AuthHandler"
            ):

                # Test missing required field
                invalid_record = {
                    "kind": "test:test:test:1.0.0",
                    "acl": {"viewers": ["test"], "owners": ["test"]},
                    # Missing legal and data fields
                }

                try:
                    await storage_create_update_records([invalid_record])
                    assert False, "Expected validation exception was not raised"
                except Exception as e:
                    assert "Missing required field" in str(e)

                # Test invalid ACL
                invalid_acl_record = {
                    "kind": "test:test:test:1.0.0",
                    "acl": {"viewers": ["test"]},  # Missing owners
                    "legal": {
                        "legaltags": ["test"],
                        "otherRelevantDataCountries": ["US"],
                    },
                    "data": {"test": "data"},
                }

                try:
                    await storage_create_update_records([invalid_acl_record])
                    assert False, "Expected validation exception was not raised"
                except Exception as e:
                    assert "ACL must contain both 'viewers' and 'owners'" in str(e)
