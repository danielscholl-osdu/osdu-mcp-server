"""MCP Resources for OSDU workflow templates and examples."""

from pathlib import Path
from typing import List
from mcp.server.fastmcp.resources import FileResource
from pydantic import AnyUrl

# Get the resources directory path
RESOURCES_DIR = Path(__file__).parent


def get_workflow_resources() -> List[FileResource]:
    """Get all MCP resources for OSDU workflow templates."""
    resources = []

    # Template resources
    template_files = [
        ("legal-tag-template.json", "Working legal tag template structure"),
        (
            "processing-parameter-record.json",
            "Complete record template for ProcessingParameterType",
        ),
    ]

    for filename, description in template_files:
        file_path = RESOURCES_DIR / "templates" / filename
        if file_path.exists():
            resources.append(
                FileResource(
                    uri=AnyUrl(f"template://{filename}"),
                    name=f"Template: {filename}",
                    description=description,
                    mime_type="application/json",
                    path=file_path,
                )
            )

    # Reference resources
    reference_files = [
        (
            "acl-format-examples.json",
            "ACL format examples for different OSDU environments",
        ),
        (
            "search-query-patterns.json",
            "Proven search query patterns for record validation",
        ),
    ]

    for filename, description in reference_files:
        file_path = RESOURCES_DIR / "references" / filename
        if file_path.exists():
            resources.append(
                FileResource(
                    uri=AnyUrl(f"reference://{filename}"),
                    name=f"Reference: {filename}",
                    description=description,
                    mime_type="application/json",
                    path=file_path,
                )
            )

    return resources


__all__ = ["get_workflow_resources"]
