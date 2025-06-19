"""
Tests for AssetsGenerator.

Following ADR-010 Testing Philosophy: Test content generation functionality
without testing subjective content quality.
"""

import pytest
from osdu_mcp_server.shared.assets_generator import AssetsGenerator


def test_assets_generator_initialization():
    """Test that AssetsGenerator can be initialized."""
    generator = AssetsGenerator()
    assert generator is not None


def test_generate_comprehensive_overview_returns_string():
    """Test that generate_comprehensive_overview returns a string."""
    generator = AssetsGenerator()
    result = generator.generate_comprehensive_overview()

    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_comprehensive_overview_includes_required_sections():
    """Test that generated overview includes all required sections."""
    generator = AssetsGenerator()
    content = generator.generate_comprehensive_overview()

    # Verify main structural sections are present
    assert "OSDU MCP Server Assets" in content
    assert "Server Overview" in content
    assert "Prompts" in content
    assert "Tools" in content
    assert "Configuration" in content
    assert "Workflows" in content
    assert "Pro Tips" in content


def test_generate_header_returns_title():
    """Test that header generation returns proper title."""
    generator = AssetsGenerator()
    header = generator._generate_header()

    assert isinstance(header, str)
    assert "OSDU MCP Server Assets" in header


def test_generate_server_overview_returns_content():
    """Test that server overview generation returns content."""
    generator = AssetsGenerator()
    overview = generator._generate_server_overview()

    assert isinstance(overview, str)
    assert len(overview) > 0
    assert "OSDU MCP Server" in overview


def test_generate_prompts_section_includes_list_assets():
    """Test that prompts section includes list_mcp_assets prompt."""
    generator = AssetsGenerator()
    prompts = generator._generate_prompts_section()

    assert isinstance(prompts, str)
    assert "list_mcp_assets" in prompts
    assert "Prompts" in prompts


def test_generate_tools_section_includes_all_services():
    """Test that tools section includes all service categories."""
    generator = AssetsGenerator()
    tools = generator._generate_tools_section()

    assert isinstance(tools, str)

    # Verify all service categories are present
    assert "Foundation" in tools
    assert "Partition Service" in tools
    assert "Entitlements Service" in tools
    assert "Legal Service" in tools
    assert "Schema Service" in tools
    assert "Storage Service" in tools

    # Verify some key tools are present
    assert "health_check" in tools
    assert "partition_list" in tools
    assert "legaltag_list" in tools
    assert "schema_list" in tools
    assert "storage_get_record" in tools


def test_generate_configuration_section_includes_env_vars():
    """Test that configuration section includes environment variables."""
    generator = AssetsGenerator()
    config = generator._generate_configuration_section()

    assert isinstance(config, str)
    assert "OSDU_MCP_SERVER_URL" in config
    assert "AZURE_CLIENT_ID" in config
    assert "OSDU_MCP_ENABLE_WRITE_MODE" in config
    assert "OSDU_MCP_ENABLE_DELETE_MODE" in config


def test_generate_workflows_section_includes_examples():
    """Test that workflows section includes workflow examples."""
    generator = AssetsGenerator()
    workflows = generator._generate_workflows_section()

    assert isinstance(workflows, str)
    assert "Quick Start Workflows" in workflows
    assert "health_check" in workflows  # Should be recommended first step


def test_generate_tips_section_includes_guidance():
    """Test that tips section includes helpful guidance."""
    generator = AssetsGenerator()
    tips = generator._generate_tips_section()

    assert isinstance(tips, str)
    assert "Pro Tips" in tips
    assert "Security" in tips or "security" in tips
    assert "Performance" in tips or "performance" in tips


def test_generate_footer_includes_next_steps():
    """Test that footer includes next steps guidance."""
    generator = AssetsGenerator()
    footer = generator._generate_footer()

    assert isinstance(footer, str)
    assert len(footer) > 0
    # Should encourage action
    assert "Ready" in footer or "ready" in footer
