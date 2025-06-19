"""
OSDU MCP Server Prompts.

This package contains MCP prompts that provide guided interaction capabilities
for discovering and understanding server capabilities.
"""

from .guide_record_lifecycle import guide_record_lifecycle
from .guide_search_patterns import guide_search_patterns
from .list_assets import list_mcp_assets

__all__ = ["list_mcp_assets", "guide_search_patterns", "guide_record_lifecycle"]
