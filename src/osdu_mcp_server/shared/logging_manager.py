"""Logging configuration for OSDU MCP Server.

This module implements structured logging with a JSON format according to ADR-016.
Logging can be enabled/disabled via environment variable.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Optional

from .config_manager import ConfigManager
from .utils import get_trace_id


class LoggingManager:
    """Manages logging configuration with feature flag support."""

    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize logging manager.

        Args:
            config: Configuration manager instance (if None, one will be created)
        """
        self.config = config or ConfigManager()
        self._initialized = False
        
    def configure(self) -> None:
        """Configure logging system according to settings.
        
        Reads configuration from:
        - OSDU_MCP_LOGGING_ENABLED: Whether logging is enabled (default: False)
        - OSDU_MCP_LOGGING_LEVEL: Log level (default: INFO)
        """
        if self._initialized:
            return
            
        # Check if we're running in a test environment
        is_test = "pytest" in sys.modules
            
        # Check if logging is enabled via environment variable
        logging_enabled = self.config.get("logging", "enabled", False)
        
        # Get logger but don't reconfigure root logger during tests
        logger_name = "osdu_mcp" if not is_test else "osdu_mcp_test"
        logger = logging.getLogger(logger_name)
        
        # Configure logger if logging is enabled
        if logging_enabled and not is_test:
            # Get log level from config
            log_level_str = self.config.get("logging", "level", "INFO")
            log_level = getattr(logging, log_level_str.upper(), logging.INFO)
            
            # Configure logger
            logger.setLevel(log_level)
            
            # Remove any existing handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Add stdout handler with JSON formatter
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            handler.setFormatter(JSONFormatter())
            logger.addHandler(handler)
        else:
            # If logging is disabled, set logger to ERROR level
            logger.setLevel(logging.ERROR)
        
        # Mark as initialized
        self._initialized = True
        
    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger instance.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured logger instance
        """
        if not self._initialized:
            self.configure()
            
        # Use module name with osdu_mcp prefix to ensure isolation
        # We're not modifying the root logger so this shouldn't affect existing tests
        logger_name = f"osdu_mcp.{name}" if "pytest" not in sys.modules else f"osdu_mcp_test.{name}"
        return logging.getLogger(logger_name)


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format according to ADR-016."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted log entry
        """
        # Extract the module and function name
        module_parts = record.name.split('.')
        tool = module_parts[-1] if len(module_parts) > 0 else ""
        
        # Build the JSON structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "trace_id": getattr(record, "trace_id", get_trace_id()),
            "level": record.levelname,
            "tool": tool,
            "message": record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add any extra attributes
        if hasattr(record, "extra") and record.extra:
            log_entry.update(record.extra)
            
        # Add any extra fields passed in the log call
        extra_args = getattr(record, "args", {})
        if isinstance(extra_args, dict):
            for key, value in extra_args.items():
                if key not in log_entry:
                    log_entry[key] = value
        
        return json.dumps(log_entry)


# Global instance for easy access
_manager = LoggingManager()


def configure_logging() -> None:
    """Configure logging system (convenience function)."""
    _manager.configure()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger (convenience function).
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return _manager.get_logger(name)
