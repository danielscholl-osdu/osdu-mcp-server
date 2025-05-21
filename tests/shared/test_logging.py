"""Tests for logging manager."""

import json
import logging
import unittest
from unittest.mock import patch, MagicMock

from osdu_mcp_server.shared.logging_manager import (
    LoggingManager,
    JSONFormatter,
    configure_logging,
    get_logger
)


class TestLoggingManager(unittest.TestCase):
    """Tests for the LoggingManager class."""

    def setUp(self):
        """Set up test environment."""
        # Save and reset test logger state before each test
        self.test_logger = logging.getLogger("osdu_mcp_test")
        self.test_handlers = self.test_logger.handlers.copy()
        self.test_level = self.test_logger.level
        self.test_logger.handlers = []

    def tearDown(self):
        """Clean up test environment."""
        # Restore test logger state after each test
        self.test_logger.handlers = self.test_handlers
        self.test_logger.setLevel(self.test_level)

    @patch("osdu_mcp_server.shared.logging_manager.ConfigManager")
    def test_logging_disabled(self, mock_config):
        """Test that logging is disabled by default."""
        # Mock config to return logging disabled
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = False
        mock_config.return_value = mock_config_instance

        # Create logging manager and configure
        manager = LoggingManager(mock_config_instance)
        manager.configure()

        # Verify the osdu_mcp_test logger is set to ERROR level
        self.assertEqual(logging.getLogger("osdu_mcp_test").level, logging.ERROR)

    def test_logging_enabled(self):
        """Test that logging is configured when enabled."""
        # Patch config for this test
        with patch("osdu_mcp_server.shared.logging_manager.ConfigManager") as mock_config:
            with patch("osdu_mcp_server.shared.logging_manager.sys.modules", {}):
                # Mock config to return logging enabled
                mock_config_instance = MagicMock()
                mock_config_instance.get.side_effect = lambda section, key, default=None: True if section == "logging" and key == "enabled" else "INFO" if section == "logging" and key == "level" else default
                mock_config.return_value = mock_config_instance
        
                # Create logging manager and configure
                manager = LoggingManager(mock_config_instance)
                
                # Get the osdu_mcp logger and remove any existing handlers
                test_logger = logging.getLogger("osdu_mcp")
                for handler in test_logger.handlers[:]:
                    test_logger.removeHandler(handler)
                    
                manager.configure()
        
                # Verify log level
                self.assertEqual(test_logger.level, logging.INFO)

    def test_json_formatter(self):
        """Test JSON formatter formats logs correctly."""
        # Create formatter directly
        formatter = JSONFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path",
            lineno=42,
            msg="Test message",
            args={},
            exc_info=None
        )
        
        # Add extra fields
        record.extra = {"test_field": "test_value"}
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON
        log_json = json.loads(formatted)
        
        # Verify JSON structure
        self.assertEqual(log_json["level"], "INFO")
        self.assertEqual(log_json["message"], "Test message")
        self.assertEqual(log_json["tool"], "test_logger")
        self.assertTrue("timestamp" in log_json)
        self.assertTrue("trace_id" in log_json)

    @patch("osdu_mcp_server.shared.logging_manager.ConfigManager")
    def test_get_logger(self, mock_config):
        """Test get_logger returns configured logger."""
        # Mock config to return logging enabled
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda section, key, default=None: True if section == "logging" and key == "enabled" else "INFO" if section == "logging" and key == "level" else default
        mock_config.return_value = mock_config_instance

        # Get a logger
        logger = get_logger("test_module")

        # Verify logger is configured with correct name
        self.assertEqual(logger.name, "osdu_mcp_test.test_module")

    def test_configure_global(self):
        """Test the global configure_logging function."""
        with patch("osdu_mcp_server.shared.logging_manager.ConfigManager") as mock_config:
            # Mock config to return logging enabled
            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = lambda section, key, default=None: True if section == "logging" and key == "enabled" else "DEBUG" if section == "logging" and key == "level" else default
            mock_config.return_value = mock_config_instance
            
            # Configure logging using global function
            configure_logging()
            
            # Verify we didn't modify the root logger
            root_logger = logging.getLogger()
            self.assertEqual(root_logger.level, logging.WARNING)  # Default root logger level


if __name__ == "__main__":
    unittest.main()
