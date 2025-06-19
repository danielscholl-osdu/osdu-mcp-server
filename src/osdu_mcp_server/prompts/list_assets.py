"""
List MCP Assets prompt for comprehensive server capability overview.

Provides dynamic listing of all available prompts, tools, and resources
with usage examples and quick start guidance.
"""

from typing import List, Dict, Any
from ..shared.assets_generator import AssetsGenerator

# Define Message type for development/testing
Message = Dict[str, Any]


async def list_mcp_assets() -> List[Message]:
    """
    List MCP Assets prompt for comprehensive server capability overview.

    Provides dynamic listing of all available prompts, tools, and resources
    with usage examples and quick start guidance.

    Returns:
        List containing user message with comprehensive server documentation
    """
    generator = AssetsGenerator()
    content = generator.generate_comprehensive_overview()

    return [{"role": "user", "content": content}]
