"""Tests for partition_get tool."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch, AsyncMock

from osdu_mcp_server.tools.partition.get import partition_get


@pytest.mark.asyncio
async def test_partition_get_success():
    """Test successful partition retrieval."""
    with aioresponses() as mocked:
        # Mock the partition get endpoint
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions/osdu",
            payload={
                "compliance-ruleset": {
                    "sensitive": False,
                    "value": "shared"
                },
                "storage-account-key": {
                    "sensitive": True,
                    "value": "secret-key"
                }
            },
        )
        
        with patch("osdu_mcp_server.tools.partition.get.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]
            
            with patch("osdu_mcp_server.tools.partition.get.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")
                mock_auth.return_value.get_user_info = AsyncMock(return_value="test-user")
                
                result = await partition_get("osdu")
                
                assert result["success"] is True
                assert result["exists"] is True
                assert result["partition_id"] == "osdu"
                assert result["sensitive_properties_count"] == 1
                # By default (include_sensitive=False), sensitive properties are excluded
                assert "storage-account-key" not in result["properties"]
                assert "compliance-ruleset" in result["properties"]


@pytest.mark.asyncio
async def test_partition_get_with_redacted_sensitive():
    """Test successful partition retrieval with sensitive values redacted."""
    with aioresponses() as mocked:
        # Mock the partition get endpoint
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions/osdu",
            payload={
                "compliance-ruleset": {
                    "sensitive": False,
                    "value": "shared"
                },
                "storage-account-key": {
                    "sensitive": True,
                    "value": "secret-key"
                }
            },
        )
        
        with patch("osdu_mcp_server.tools.partition.get.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]
            
            with patch("osdu_mcp_server.tools.partition.get.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")
                mock_auth.return_value.get_user_info = AsyncMock(return_value="test-user")
                
                # Request with sensitive included but redacted (default)
                result = await partition_get("osdu", include_sensitive=True)
                
                assert result["success"] is True
                assert result["exists"] is True
                assert result["partition_id"] == "osdu"
                assert result["sensitive_properties_count"] == 1
                # Sensitive values should be redacted
                assert result["properties"]["storage-account-key"]["value"] == "<REDACTED>"
                assert result["properties"]["compliance-ruleset"]["value"] == "shared"


@pytest.mark.asyncio
async def test_partition_get_not_found():
    """Test partition not found."""
    with aioresponses() as mocked:
        # Mock 404 response
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions/nonexistent",
            status=404,
            body="nonexistent partition not found",
        )
        
        with patch("osdu_mcp_server.tools.partition.get.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]
            
            with patch("osdu_mcp_server.tools.partition.get.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")
                mock_auth.return_value.get_user_info = AsyncMock(return_value="test-user")
                
                result = await partition_get("nonexistent")
                
                assert result["success"] is False
                assert result["exists"] is False
                assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_partition_get_with_sensitive_values():
    """Test partition retrieval with sensitive values exposed."""
    with aioresponses() as mocked:
        # Mock the partition get endpoint
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions/osdu",
            payload={
                "storage-account-key": {
                    "sensitive": True,
                    "value": "secret-key"
                }
            },
        )
        
        with patch("osdu_mcp_server.tools.partition.get.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]
            
            with patch("osdu_mcp_server.tools.partition.get.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")
                mock_auth.return_value.get_user_info = AsyncMock(return_value="test-user")
                
                # Request with sensitive values exposed
                result = await partition_get("osdu", include_sensitive=True, redact_sensitive_values=False)
                
                assert result["success"] is True
                assert result["properties"]["storage-account-key"]["value"] == "secret-key"


@pytest.mark.asyncio
async def test_partition_get_exclude_sensitive():
    """Test partition retrieval excluding sensitive properties."""
    with aioresponses() as mocked:
        # Mock the partition get endpoint
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions/osdu",
            payload={
                "compliance-ruleset": {
                    "sensitive": False,
                    "value": "shared"
                },
                "storage-account-key": {
                    "sensitive": True,
                    "value": "secret-key"
                }
            },
        )
        
        with patch("osdu_mcp_server.tools.partition.get.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]
            
            with patch("osdu_mcp_server.tools.partition.get.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")
                mock_auth.return_value.get_user_info = AsyncMock(return_value="test-user")
                
                # Request without sensitive properties
                result = await partition_get("osdu", include_sensitive=False)
                
                assert result["success"] is True
                assert len(result["properties"]) == 1
                assert "compliance-ruleset" in result["properties"]
                assert "storage-account-key" not in result["properties"]
