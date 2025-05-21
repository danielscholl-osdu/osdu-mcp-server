"""Main entry point for OSDU MCP Server."""

from .server import mcp
from .shared.logging_manager import configure_logging


def main() -> None:
    """Run the MCP server."""
    # Configure logging based on environment variables
    configure_logging()

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
