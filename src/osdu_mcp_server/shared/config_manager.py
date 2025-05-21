"""Configuration management for OSDU MCP Server.

This module implements environment-first configuration with YAML fallback
as defined in ADR-003.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .exceptions import OSMCPConfigError


class ConfigManager:
    """Environment-first configuration with YAML fallback."""

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_file: Path to YAML configuration file (default: config.yaml)
        """
        self.config_file = config_file or Path("config.yaml")
        self._file_config: Optional[Dict[str, Any]] = None
        self._load_file_config()

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable priority.

        Priority order:
        1. Environment variable (OSDU_MCP_{SECTION}_{KEY})
        2. YAML configuration file
        3. Default value

        Args:
            section: Configuration section (e.g., "server", "auth")
            key: Configuration key within the section
            default: Default value if not found

        Returns:
            Configuration value from highest priority source
        """
        # Build environment variable name
        env_var = f"OSDU_MCP_{section.upper()}_{key.upper()}"

        # Check environment variable first (highest priority)
        env_value = os.environ.get(env_var)
        if env_value is not None:
            return self._parse_env_value(env_value)

        # Check YAML configuration (second priority)
        if self._file_config:
            section_config = self._file_config.get(section, {})
            if key in section_config:
                return section_config[key]

        # Return default value (lowest priority)
        return default

    def get_required(self, section: str, key: str) -> Any:
        """Get required configuration value.

        Args:
            section: Configuration section
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            OSMCPConfigError: If configuration value is not found
        """
        value = self.get(section, key)
        if value is None:
            env_var = f"OSDU_MCP_{section.upper()}_{key.upper()}"
            raise OSMCPConfigError(
                f"Required configuration '{section}.{key}' not found. "
                f"Set environment variable {env_var} or add to config.yaml"
            )
        return value

    def _load_file_config(self) -> Optional[dict]:
        """Load configuration from YAML file if it exists.

        Returns:
            Loaded configuration dictionary or None
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._file_config = yaml.safe_load(f)
                    return self._file_config
            except Exception as e:
                raise OSMCPConfigError(f"Failed to load config file: {e}")
        return None

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type.

        Args:
            value: String value from environment

        Returns:
            Parsed value (bool, int, float, or string)
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # Try to parse as number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values for debugging/logging.

        Returns:
            Dictionary of all configuration values
        """
        # Start with file config as base
        all_config = self._file_config.copy() if self._file_config else {}

        # Override with any environment variables
        for key, value in os.environ.items():
            if key.startswith("OSDU_MCP_"):
                parts = key.split("_", 3)
                if len(parts) >= 4:
                    section = parts[2].lower()
                    config_key = parts[3].lower()
                    if section not in all_config:
                        all_config[section] = {}
                    all_config[section][config_key] = self._parse_env_value(value)

        return all_config