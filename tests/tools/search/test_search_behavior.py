"""Behavior-driven tests for search tools following ADR-010."""

import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from aioresponses import aioresponses
from azure.core.credentials import AccessToken
from mcp.shared.exceptions import McpError

from osdu_mcp_server.tools.search import search_query, search_by_id, search_by_kind


@pytest.mark.asyncio
async def test_search_query_returns_structured_results():
    """Test that search_query returns properly structured search results."""
    mock_response = {
        "results": [
            {
                "id": "test:well:123",
                "kind": "test:osdu:well:1.0.0",
                "data": {"Name": "Test Well", "Location": "Texas"},
                "createTime": "2023-01-01T00:00:00Z",
                "version": 123456789,
            }
        ],
        "totalCount": 1,
        "took": 125,
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp()),
    )

    test_env = {
        "OSDU_MCP_SERVER_URL": "https://test.osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "opendes",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_SECRET": "test-secret",
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.post(
                    "https://test.osdu.com/api/search/v2/query",
                    payload=mock_response,
                )

                result = await search_query("data.Name:*test*")

                # Test observable behavior - what the user sees
                assert result["success"] is True
                assert result["totalCount"] == 1
                assert len(result["results"]) == 1
                assert result["results"][0]["id"] == "test:well:123"
                assert result["results"][0]["kind"] == "test:osdu:well:1.0.0"
                assert result["searchMeta"]["query_executed"] == "data.Name:*test*"
                assert result["searchMeta"]["execution_time_ms"] == 125
                assert result["partition"] == "opendes"


@pytest.mark.asyncio
async def test_search_by_id_finds_specific_record():
    """Test that search_by_id correctly finds a record by its ID."""
    mock_response = {
        "results": [
            {
                "id": "test:record:123",
                "kind": "test:osdu:record:1.0.0",
                "data": {"Name": "Found Record"},
                "createTime": "2023-01-01T00:00:00Z",
            }
        ],
        "totalCount": 1,
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp()),
    )

    test_env = {
        "OSDU_MCP_SERVER_URL": "https://test.osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "opendes",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_SECRET": "test-secret",
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.post(
                    "https://test.osdu.com/api/search/v2/query",
                    payload=mock_response,
                )

                result = await search_by_id("test:record:123")

                # Verify the HTTP call was made correctly
                assert len(mocked.requests) == 1
                # Extract the request from the mocked calls
                request_key = list(mocked.requests.keys())[0]
                request = mocked.requests[request_key][0]
                request_data = request.kwargs["json"]
                assert request_data["query"] == 'id:("test:record:123")'
                assert request_data["kind"] == "*:*:*:*"

                # Test observable behavior
                assert result["success"] is True
                assert len(result["results"]) == 1
                assert result["results"][0]["id"] == "test:record:123"


@pytest.mark.asyncio
async def test_search_by_kind_handles_no_results():
    """Test that search_by_kind gracefully handles when no records are found."""
    mock_response = {"results": [], "totalCount": 0}

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp()),
    )

    test_env = {
        "OSDU_MCP_SERVER_URL": "https://test.osdu.com",
        "OSDU_MCP_SERVER_DATA_PARTITION": "opendes",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_SECRET": "test-secret",
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.post(
                    "https://test.osdu.com/api/search/v2/query",
                    payload=mock_response,
                )

                result = await search_by_kind("nonexistent:kind:1.0.0")

                # Test observable behavior - graceful handling of empty results
                assert result["success"] is True
                assert result["results"] == []
                assert result["totalCount"] == 0


@pytest.mark.asyncio
async def test_search_query_validates_required_parameters():
    """Test that search_query validates required parameters."""
    # Test behavior when invalid input is provided - exception decorator converts to McpError
    with pytest.raises(McpError, match="Query parameter is required"):
        await search_query("")


@pytest.mark.asyncio
async def test_search_by_id_validates_required_parameters():
    """Test that search_by_id validates required parameters."""
    # Test behavior when invalid input is provided - exception decorator converts to McpError
    with pytest.raises(McpError, match="ID parameter is required"):
        await search_by_id("")


@pytest.mark.asyncio
async def test_search_by_kind_validates_required_parameters():
    """Test that search_by_kind validates required parameters."""
    # Test behavior when invalid input is provided - exception decorator converts to McpError
    with pytest.raises(McpError, match="Kind parameter is required"):
        await search_by_kind("")
