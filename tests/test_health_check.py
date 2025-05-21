"""Tests for the health check tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from osdu_mcp_server.tools.health_check import health_check


@pytest.mark.asyncio
async def test_health_check_success():
    """Test successful health check with mocked dependencies."""
    with patch('osdu_mcp_server.tools.health_check.ConfigManager') as mock_config, \
         patch('osdu_mcp_server.tools.health_check.AuthHandler') as mock_auth, \
         patch('osdu_mcp_server.tools.health_check.OsduClient') as mock_client:
        
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_required.side_effect = lambda section, key: {
            ("server", "url"): "https://test-osdu.com",
            ("server", "data_partition"): "test-partition"
        }[(section, key)]
        mock_config.return_value = mock_config_instance
        
        mock_auth_instance = AsyncMock()
        mock_auth_instance.validate_token.return_value = True
        mock_auth.return_value = mock_auth_instance
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = {"version": "1.0.0"}
        mock_client.return_value = mock_client_instance
        
        # Execute test
        result = await health_check()
        
        # Verify results
        assert result["connectivity"] == "success"
        assert result["server_url"] == "https://test-osdu.com"
        assert result["data_partition"] == "test-partition"
        assert result["authentication"]["status"] == "valid"
        assert "services" in result
        assert "timestamp" in result


@pytest.mark.asyncio
async def test_health_check_auth_failure():
    """Test health check with authentication failure."""
    with patch('osdu_mcp_server.tools.health_check.ConfigManager') as mock_config, \
         patch('osdu_mcp_server.tools.health_check.AuthHandler') as mock_auth, \
         patch('osdu_mcp_server.tools.health_check.OsduClient') as mock_client:
        
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_required.return_value = "test-value"
        mock_config.return_value = mock_config_instance
        
        mock_auth_instance = AsyncMock()
        mock_auth_instance.validate_token.return_value = False
        mock_auth.return_value = mock_auth_instance
        
        mock_client.return_value = AsyncMock()
        
        # Execute test
        result = await health_check()
        
        # Verify authentication status
        assert result["authentication"]["status"] == "invalid"


@pytest.mark.asyncio
async def test_health_check_service_unhealthy():
    """Test health check with one unhealthy service."""
    with patch('osdu_mcp_server.tools.health_check.ConfigManager') as mock_config, \
         patch('osdu_mcp_server.tools.health_check.AuthHandler') as mock_auth, \
         patch('osdu_mcp_server.tools.health_check.OsduClient') as mock_client:
        
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_required.return_value = "test-value"
        mock_config.return_value = mock_config_instance
        
        mock_auth.return_value = AsyncMock()
        
        mock_client_instance = AsyncMock()
        # Storage service fails
        mock_client_instance.get.side_effect = [
            Exception("Service unavailable"),  # storage fails
            {"version": "1.0.0"},              # search succeeds
            {"version": "1.0.0"}               # legal succeeds
        ]
        mock_client.return_value = mock_client_instance
        
        # Execute test
        result = await health_check()
        
        # Verify results - health check includes error message for unhealthy services
        assert result["services"]["storage"] == "unhealthy: Service unavailable"
        assert result["services"]["search"] == "healthy"
        assert result["services"]["legal"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_without_services():
    """Test health check without checking services."""
    with patch('osdu_mcp_server.tools.health_check.ConfigManager') as mock_config, \
         patch('osdu_mcp_server.tools.health_check.AuthHandler') as mock_auth, \
         patch('osdu_mcp_server.tools.health_check.OsduClient') as mock_client:
        
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_required.return_value = "test-value"
        mock_config.return_value = mock_config_instance
        
        mock_auth.return_value = AsyncMock()
        mock_client.return_value = AsyncMock()
        
        # Execute test
        result = await health_check(include_services=False)
        
        # Verify services not included
        assert "services" not in result
        assert result["connectivity"] == "success"


@pytest.mark.asyncio
async def test_health_check_with_version_info():
    """Test health check with version information."""
    with patch('osdu_mcp_server.tools.health_check.ConfigManager') as mock_config, \
         patch('osdu_mcp_server.tools.health_check.AuthHandler') as mock_auth, \
         patch('osdu_mcp_server.tools.health_check.OsduClient') as mock_client:
        
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_required.return_value = "test-value"
        mock_config.return_value = mock_config_instance
        
        mock_auth.return_value = AsyncMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = {"version": "1.0.0"}
        mock_client.return_value = mock_client_instance
        
        # Execute test
        result = await health_check(include_version_info=True)
        
        # Verify version info included
        assert "services" in result
        assert "version_info" in result["services"]
