"""Tests for guide_search_patterns prompt."""

import pytest

from osdu_mcp_server.prompts import guide_search_patterns


@pytest.mark.asyncio
async def test_guide_search_patterns_returns_message_format():
    """Test that search patterns prompt returns correct Message format."""
    result = await guide_search_patterns()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert isinstance(result[0]["content"], str)
    assert len(result[0]["content"]) > 0


@pytest.mark.asyncio
async def test_guide_search_patterns_contains_key_sections():
    """Test that the prompt contains all expected content sections."""
    result = await guide_search_patterns()
    content = result[0]["content"]

    # Check for main sections
    assert "Available Search Tools" in content
    assert "Quick Start Examples" in content
    assert "Common Query Patterns" in content
    assert "Multi-Step Workflows" in content
    assert "Performance Tips" in content

    # Check for tool names
    assert "search_query" in content
    assert "search_by_id" in content
    assert "search_by_kind" in content

    # Check for example patterns
    assert "Boolean Operators" in content
    assert "Wildcards" in content
    assert "Range Queries" in content


@pytest.mark.asyncio
async def test_guide_search_patterns_includes_elasticsearch_examples():
    """Test that the prompt includes Elasticsearch query examples."""
    result = await guide_search_patterns()
    content = result[0]["content"]

    # Check for Elasticsearch syntax examples
    assert "data.UWI" in content
    assert "AND" in content
    assert "OR" in content
    assert "well*" in content
    assert "[2020-01-01 TO 2023-12-31]" in content


@pytest.mark.asyncio
async def test_guide_search_patterns_includes_osdu_patterns():
    """Test that the prompt includes OSDU-specific patterns."""
    result = await guide_search_patterns()
    content = result[0]["content"]

    # Check for OSDU kind patterns
    assert "*:osdu:well:*" in content
    assert "*:*:*:*" in content
    assert "opendes:osdu:wellbore:1.0.0" in content

    # Check for common OSDU fields
    assert "data.Name" in content
    assert "data.SpudDate" in content
    assert "createTime" in content


@pytest.mark.asyncio
async def test_guide_search_patterns_includes_workflows():
    """Test that the prompt includes multi-step workflow guidance."""
    result = await guide_search_patterns()
    content = result[0]["content"]

    # Check for workflow steps
    assert "Explore Data" in content
    assert "Focus Search" in content
    assert "Field Discovery" in content
    assert "Refine Query" in content

    # Check for discovery workflow examples
    assert "search_by_kind(kind=" in content
    assert "limit=" in content
