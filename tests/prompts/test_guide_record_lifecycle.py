"""
Tests for guide_record_lifecycle prompt.

Following ADR-010 Testing Philosophy: Test the data provider (prompt function),
not the data consumer (AI model). Focus on contract compliance and data structure.
"""

import pytest
from osdu_mcp_server.prompts.guide_record_lifecycle import guide_record_lifecycle


@pytest.mark.asyncio
async def test_guide_record_lifecycle_returns_message_list():
    """Test that guide_record_lifecycle returns a list of messages."""
    result = await guide_record_lifecycle()

    assert isinstance(result, list)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_guide_record_lifecycle_returns_proper_message_format():
    """Test that guide_record_lifecycle returns properly formatted MCP messages."""
    result = await guide_record_lifecycle()
    message = result[0]

    # Verify Message structure
    assert isinstance(message, dict)
    assert "role" in message
    assert "content" in message

    # Verify message content
    assert message["role"] == "user"
    assert isinstance(message["content"], str)
    assert len(message["content"]) > 0


@pytest.mark.asyncio
async def test_guide_record_lifecycle_content_has_required_sections():
    """Test that generated content includes all required workflow sections."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify main workflow sections are present
    assert "Record Lifecycle Workflow" in content
    assert "Prerequisites" in content
    assert "Step-by-Step Workflow Guide" in content
    assert "Validation Checkpoints" in content
    assert "Common Issues & Solutions" in content
    assert "Best Practices" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_workflow_phases():
    """Test that content includes all expected workflow phases."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify all workflow phases are documented
    assert "Legal Compliance Setup" in content
    assert "Schema Validation" in content
    assert "Record Creation" in content
    assert "Record Verification" in content
    assert "Search Validation" in content
    assert "Cleanup" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_all_relevant_tools():
    """Test that content includes all MCP tools referenced in workflow."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify legal service tools
    assert "legaltag_create" in content
    assert "legaltag_get" in content
    assert "legaltag_delete" in content

    # Verify schema service tools
    assert "schema_get" in content

    # Verify storage service tools
    assert "storage_create_update_records" in content
    assert "storage_get_record" in content
    assert "storage_list_record_versions" in content
    assert "storage_delete_record" in content

    # Verify search service tools
    assert "search_query" in content

    # Verify foundation tools
    assert "health_check" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_permission_information():
    """Test that content includes write protection and permission guidance."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify permission sections
    assert "OSDU_MCP_ENABLE_WRITE_MODE" in content
    assert "OSDU_MCP_ENABLE_DELETE_MODE" in content
    assert "Required Permissions" in content
    assert (
        "write and delete operations" in content
        or "enable both write and delete" in content
    )


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_validation_guidance():
    """Test that content includes validation checkpoints and success criteria."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify validation sections
    assert "Success Criteria" in content
    assert "Validation Points" in content
    assert "Validation Steps" in content or "Validation Checkpoints" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_error_handling():
    """Test that content includes error handling and troubleshooting guidance."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify error handling sections
    assert "Permission Errors" in content
    assert "Schema Validation Errors" in content
    assert "Common Issues" in content or "Troubleshooting" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_timing_information():
    """Test that content includes timing and delay guidance."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify timing information
    assert "Time Estimate" in content
    assert "30-60 seconds" in content  # Search indexing delay information


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_example_data():
    """Test that content includes example data and parameters."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify example data is included
    assert "ProcessingParameterType" in content or "example" in content.lower()
    assert "public-usa-test" in content or "test" in content.lower()


@pytest.mark.asyncio
async def test_guide_record_lifecycle_function_executes_without_errors():
    """Test that the prompt function executes without raising exceptions."""
    # This should complete without raising any exceptions
    result = await guide_record_lifecycle()

    # Basic sanity check that we got something
    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_guide_record_lifecycle_content_has_substantial_length():
    """Test that generated content has substantial length for comprehensive workflow."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Content should be substantial for comprehensive workflow guide
    assert len(content) >= 5000  # Should be much longer than basic prompts


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_step_numbering():
    """Test that content includes numbered workflow steps."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify step numbering is present
    assert "Step 1:" in content
    assert "Step 2:" in content
    assert "Step 3:" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_includes_record_structure_guidance():
    """Test that content includes proper record structure examples."""
    result = await guide_record_lifecycle()
    content = result[0]["content"]

    # Verify record structure elements are documented
    assert "kind" in content
    assert "acl" in content
    assert "legal" in content
    assert "data" in content


@pytest.mark.asyncio
async def test_guide_record_lifecycle_consistent_content_generation():
    """Test that content generation is consistent across multiple calls."""
    # Execute multiple times to ensure consistency
    result1 = await guide_record_lifecycle()
    result2 = await guide_record_lifecycle()

    # Content should be identical (static generation)
    assert result1[0]["content"] == result2[0]["content"]
