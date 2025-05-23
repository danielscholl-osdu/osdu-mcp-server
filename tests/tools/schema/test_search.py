"""Tests for schema_search tool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osdu_mcp_server.tools.schema.search import schema_search


@pytest.mark.asyncio
async def test_schema_search_basic():
    """Test that schema_search handles API response correctly."""
    # Mock SchemaClient.search_schemas
    mock_response = {
        "schemaInfos": [
            {
                "schemaIdentity": {
                    "authority": "osdu",
                    "source": "wks",
                    "entityType": "TestSchema",
                    "schemaVersionMajor": 1,
                    "schemaVersionMinor": 0,
                    "schemaVersionPatch": 0,
                    "id": "osdu:wks:TestSchema:1.0.0",
                },
                "status": "PUBLISHED",
                "scope": "SHARED",
            }
        ],
        "count": 1,
        "totalCount": 1,
        "offset": 0,
    }

    with (
        patch("osdu_mcp_server.tools.schema.search.ConfigManager"),
        patch("osdu_mcp_server.tools.schema.search.AuthHandler"),
        patch("osdu_mcp_server.tools.schema.search.SchemaClient") as mock_client_class,
    ):

        # Setup the mock client
        mock_client = AsyncMock()
        mock_client.search_schemas.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Mock config
        mock_client.config = MagicMock()
        mock_client.config.get.return_value = "test-partition"

        # Call the function
        result = await schema_search()

        # Verify the result contains the expected data
        assert result["success"] is True
        assert len(result["schemas"]) == 1
        assert result["count"] == 1
        assert "schemas" in result
        assert (
            result["schemas"][0]["schemaIdentity"]["id"] == "osdu:wks:TestSchema:1.0.0"
        )

        # Verify the mock was called correctly
        mock_client.search_schemas.assert_called_once()


@pytest.mark.asyncio
async def test_schema_search_with_text():
    """Test schema_search with text search capability."""
    # Mock the initial schema list response
    mock_list_response = {
        "schemaInfos": [
            {
                "schemaIdentity": {
                    "authority": "osdu",
                    "source": "wks",
                    "entityType": "TestSchema",
                    "schemaVersionMajor": 1,
                    "schemaVersionMinor": 0,
                    "schemaVersionPatch": 0,
                    "id": "osdu:wks:TestSchema:1.0.0",
                },
                "status": "PUBLISHED",
                "scope": "SHARED",
            }
        ],
        "count": 1,
        "totalCount": 1,
        "offset": 0,
    }

    # Mock the schema content response
    mock_schema_content = {
        "title": "Test Schema",
        "description": "This is a schema for testing",
        "properties": {
            "testField": {
                "type": "string",
                "description": "Test field with pressure measurements",
            }
        },
    }

    with (
        patch("osdu_mcp_server.tools.schema.search.ConfigManager"),
        patch("osdu_mcp_server.tools.schema.search.AuthHandler"),
        patch("osdu_mcp_server.tools.schema.search.SchemaClient") as mock_client_class,
    ):

        # Setup the mock client
        mock_client = AsyncMock()
        mock_client.search_schemas.return_value = mock_list_response
        mock_client.get_schema.return_value = {"schema": mock_schema_content}
        mock_client_class.return_value = mock_client

        # Mock config
        mock_client.config = MagicMock()
        mock_client.config.get.return_value = "test-partition"

        # Call the function with text search
        result = await schema_search(text="pressure")

        # Verify the result contains the expected data
        assert result["success"] is True
        assert (
            len(result["schemas"]) == 1
        )  # Should find the schema with "pressure" in description
        assert result["count"] == 1
        assert result["query"] == "pressure"

        # Verify mocks were called correctly
        mock_client.search_schemas.assert_called_once()
        mock_client.get_schema.assert_called_once_with("osdu:wks:TestSchema:1.0.0")
