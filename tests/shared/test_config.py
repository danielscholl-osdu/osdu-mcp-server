"""Tests for the ConfigManager class."""

import os
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch

from osdu_mcp_server.shared.config_manager import ConfigManager
from osdu_mcp_server.shared.exceptions import OSMCPConfigError


def test_config_manager_env_priority():
    """Test that environment variables have highest priority."""
    with patch.dict(os.environ, {"OSDU_MCP_SERVER_URL": "https://env-osdu.com"}):
        config = ConfigManager()
        assert config.get("server", "url") == "https://env-osdu.com"


def test_config_manager_yaml_fallback():
    """Test that YAML configuration is used when env var not set."""
    yaml_content = """
server:
    url: https://yaml-osdu.com
    data_partition: yaml-partition
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)), \
         patch("pathlib.Path.exists", return_value=True):
        config = ConfigManager()
        assert config.get("server", "url") == "https://yaml-osdu.com"


def test_config_manager_default_fallback():
    """Test that default value is used when neither env nor yaml provide value."""
    with patch("pathlib.Path.exists", return_value=False):
        config = ConfigManager()
        assert config.get("server", "unknown_key", "default") == "default"


def test_config_manager_required_missing():
    """Test that get_required raises error for missing values."""
    with patch("pathlib.Path.exists", return_value=False):
        config = ConfigManager()
        with pytest.raises(OSMCPConfigError) as exc_info:
            config.get_required("server", "url")
        assert "Required configuration" in str(exc_info.value)


def test_config_manager_parse_boolean():
    """Test parsing of boolean environment values."""
    test_cases = [
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("1", True),
        ("false", False),
        ("FALSE", False),
        ("no", False),
        ("0", False),
    ]
    
    for env_value, expected in test_cases:
        with patch.dict(os.environ, {"OSDU_MCP_AUTH_ALLOW_CLI": env_value}):
            config = ConfigManager()
            assert config.get("auth", "allow_cli") == expected


def test_config_manager_parse_numbers():
    """Test parsing of numeric environment values."""
    test_cases = [
        ("42", 42),
        ("3.14", 3.14),
        ("0", 0),
        ("-1", -1),
    ]
    
    for env_value, expected in test_cases:
        with patch.dict(os.environ, {"OSDU_MCP_SERVER_TIMEOUT": env_value}):
            config = ConfigManager()
            assert config.get("server", "timeout") == expected


def test_config_manager_yaml_error():
    """Test that YAML errors are properly reported."""
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")), \
         patch("pathlib.Path.exists", return_value=True):
        with pytest.raises(OSMCPConfigError) as exc_info:
            ConfigManager()
        assert "Failed to load config file" in str(exc_info.value)


def test_config_manager_get_all_config():
    """Test getting all configuration values."""
    yaml_content = """
server:
    url: https://yaml-osdu.com
auth:
    scope: yaml-scope
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)), \
         patch("pathlib.Path.exists", return_value=True), \
         patch.dict(os.environ, {"OSDU_MCP_SERVER_TIMEOUT": "30"}):
        
        config = ConfigManager()
        all_config = config.get_all_config()
        
        assert all_config["server"]["url"] == "https://yaml-osdu.com"
        assert all_config["server"]["timeout"] == 30
        assert all_config["auth"]["scope"] == "yaml-scope"


def test_config_manager_custom_file():
    """Test using custom configuration file."""
    custom_path = Path("/custom/config.yaml")
    yaml_content = """
server:
    url: https://custom-osdu.com
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)), \
         patch("pathlib.Path.exists", return_value=True):
        
        config = ConfigManager(config_file=custom_path)
        assert config.get("server", "url") == "https://custom-osdu.com"
