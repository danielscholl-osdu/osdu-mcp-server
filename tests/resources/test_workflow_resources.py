"""Tests for workflow resource registration and accessibility."""

import pytest
from pathlib import Path
import json

from src.osdu_mcp_server.resources import get_workflow_resources


class TestWorkflowResources:
    """Test workflow resource discovery and validation."""

    def test_get_workflow_resources_returns_list(self):
        """Test that get_workflow_resources returns a list."""
        resources = get_workflow_resources()
        assert isinstance(resources, list)

    def test_resources_have_required_fields(self):
        """Test that all resources have required MCP Resource fields."""
        resources = get_workflow_resources()

        for resource in resources:
            # Check required FileResource fields
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert hasattr(resource, "description")
            assert hasattr(resource, "mime_type")
            assert hasattr(resource, "path")

            # Validate field types and content
            assert str(resource.uri).startswith(("template://", "reference://"))
            assert isinstance(resource.name, str)
            assert len(resource.name) > 0
            assert isinstance(resource.description, str)
            assert len(resource.description) > 0
            assert resource.mime_type == "application/json"

    def test_expected_template_resources_exist(self):
        """Test that expected template resources are registered."""
        resources = get_workflow_resources()
        resource_names = [r.name for r in resources]

        expected_templates = [
            "Template: legal-tag-template.json",
            "Template: processing-parameter-record.json",
        ]

        for template_name in expected_templates:
            assert (
                template_name in resource_names
            ), f"Expected template {template_name} not found in resources"

    def test_expected_reference_resources_exist(self):
        """Test that expected reference resources are registered."""
        resources = get_workflow_resources()
        resource_names = [r.name for r in resources]

        expected_references = [
            "Reference: acl-format-examples.json",
            "Reference: search-query-patterns.json",
        ]

        for reference_name in expected_references:
            assert (
                reference_name in resource_names
            ), f"Expected reference {reference_name} not found in resources"

    def test_resource_files_exist_and_valid_json(self):
        """Test that resource files exist and contain valid JSON."""
        resources = get_workflow_resources()

        for resource in resources:
            # Use the path attribute from FileResource
            path = resource.path

            # Verify file exists
            assert path.exists(), f"Resource file does not exist: {path}"

            # Verify file contains valid JSON
            with open(path, "r") as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Resource file {path} contains invalid JSON: {e}")

    def test_legal_tag_template_structure(self):
        """Test that legal tag template has expected structure."""
        resources = get_workflow_resources()
        legal_template = next(
            (r for r in resources if r.name == "Template: legal-tag-template.json"),
            None,
        )
        assert legal_template is not None, "Legal tag template not found"

        # Load and validate structure
        with open(legal_template.path, "r") as f:
            data = json.load(f)

        # Check for key sections
        assert "_description" in data
        assert "_usage" in data
        assert "template" in data
        assert "_notes" in data

        # Validate template structure
        template = data["template"]
        assert "name" in template
        assert "description" in template
        assert "country_of_origin" in template
        assert "contract_id" in template

    def test_record_template_structure(self):
        """Test that record template has expected structure."""
        resources = get_workflow_resources()
        record_template = next(
            (
                r
                for r in resources
                if r.name == "Template: processing-parameter-record.json"
            ),
            None,
        )
        assert record_template is not None, "Record template not found"

        # Load and validate structure
        with open(record_template.path, "r") as f:
            data = json.load(f)

        # Check for key sections
        assert "_description" in data
        assert "_usage" in data
        assert "template" in data
        assert "required_fields" in data

        # Validate template structure - OSDU record format
        template = data["template"]
        assert "kind" in template
        assert "acl" in template
        assert "legal" in template
        assert "data" in template

        # Validate ACL structure
        acl = template["acl"]
        assert "viewers" in acl
        assert "owners" in acl

        # Validate legal structure
        legal = template["legal"]
        assert "legaltags" in legal
        assert "otherRelevantDataCountries" in legal

    def test_acl_examples_structure(self):
        """Test that ACL examples have expected structure."""
        resources = get_workflow_resources()
        acl_examples = next(
            (r for r in resources if r.name == "Reference: acl-format-examples.json"),
            None,
        )
        assert acl_examples is not None, "ACL examples not found"

        # Load and validate structure
        with open(acl_examples.path, "r") as f:
            data = json.load(f)

        # Check for key sections
        assert "_description" in data
        assert "_usage" in data
        assert "standard_osdu_format" in data
        assert "troubleshooting" in data

        # Validate that examples contain ACL structures
        for format_name in ["standard_osdu_format", "azure_deployment_format"]:
            if format_name in data:
                format_data = data[format_name]
                assert "acl" in format_data
                acl = format_data["acl"]
                assert "viewers" in acl
                assert "owners" in acl

    def test_search_patterns_structure(self):
        """Test that search patterns have expected structure."""
        resources = get_workflow_resources()
        search_patterns = next(
            (r for r in resources if r.name == "Reference: search-query-patterns.json"),
            None,
        )
        assert search_patterns is not None, "Search patterns not found"

        # Load and validate structure
        with open(search_patterns.path, "r") as f:
            data = json.load(f)

        # Check for key sections
        assert "_description" in data
        assert "_usage" in data
        assert "search_by_record_id" in data
        assert "validation_workflow" in data
        assert "timing_guidance" in data

        # Validate that patterns contain MCP tool references
        search_by_id = data["search_by_record_id"]
        assert "mcp_tool" in search_by_id
        assert "example" in search_by_id

        # Validate validation workflow has steps
        workflow = data["validation_workflow"]
        assert "step_1" in workflow
        assert "step_2" in workflow
