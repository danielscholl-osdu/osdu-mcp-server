"""Tests for partition_list tool."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch, AsyncMock

from osdu_mcp_server.tools.partition.list import partition_list


@pytest.mark.asyncio
async def test_partition_list_success():
    """Test successful partition listing."""
    with aioresponses() as mocked:
        # Mock the partition list endpoint
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions",
            payload=["osdu", "tenant-a", "tenant-b"],
        )

        with patch("osdu_mcp_server.tools.partition.list.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]

            with patch("osdu_mcp_server.tools.partition.list.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")

                result = await partition_list()

                assert result["success"] is True
                assert result["partitions"] == ["osdu", "tenant-a", "tenant-b"]
                assert result["count"] == 3


@pytest.mark.asyncio
async def test_partition_list_empty():
    """Test partition listing with no results."""
    with aioresponses() as mocked:
        # Mock empty partition list
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions",
            payload=[],
        )

        with patch("osdu_mcp_server.tools.partition.list.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]

            with patch("osdu_mcp_server.tools.partition.list.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")

                result = await partition_list()

                assert result["success"] is True
                assert result["partitions"] == []
                assert result["count"] == 0


@pytest.mark.asyncio
async def test_partition_list_forbidden():
    """Test partition listing with insufficient permissions."""
    with aioresponses() as mocked:
        # Mock forbidden response
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions",
            status=403,
            body="Access denied",
        )

        with patch("osdu_mcp_server.tools.partition.list.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]

            with patch("osdu_mcp_server.tools.partition.list.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")

                result = await partition_list()

                assert result["success"] is False
                assert result["partitions"] == []
                assert "Insufficient permissions" in result["error"]


@pytest.mark.asyncio
async def test_partition_list_with_detailed_metadata():
    """Test partition listing with detailed metadata."""
    with aioresponses() as mocked:
        # Mock partition list
        mocked.get(
            "https://test.osdu.com/api/partition/v1/partitions",
            payload=["osdu", "tenant-a"],
        )

        with patch("osdu_mcp_server.tools.partition.list.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = "https://test.osdu.com"
            mock_config.return_value.get_required.side_effect = lambda section, key: {
                ("server", "url"): "https://test.osdu.com",
                ("server", "data_partition"): "osdu",
            }[(section, key)]

            with patch("osdu_mcp_server.tools.partition.list.AuthHandler") as mock_auth:
                mock_auth.return_value.get_access_token = AsyncMock(return_value="test-token")

                result = await partition_list(detailed=True)

                assert result["success"] is True
                assert result["partitions"] == ["osdu", "tenant-a"]
                assert result["count"] == 2
                assert "metadata" in result
                assert result["metadata"]["server_url"] == "https://test.osdu.com"
