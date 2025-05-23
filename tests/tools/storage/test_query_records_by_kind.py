"""Tests for storage query records by kind operation."""

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from aioresponses import aioresponses
from azure.core.credentials import AccessToken

from osdu_mcp_server.tools.storage.query_records_by_kind import (
    storage_query_records_by_kind,
)


@pytest.mark.asyncio
async def test_storage_query_records_by_kind_success():
    """Test successful query of records by kind."""
    mock_response = {
        "cursor": "next-page-cursor",
        "results": ["test:record:123", "test:record:456", "test:record:789"],
    }

    with patch.dict(
        os.environ,
        {
            "OSDU_MCP_SERVER_URL": "https://test.osdu.com",
            "OSDU_MCP_SERVER_DATA_PARTITION": "test-partition",
            "AZURE_CLIENT_ID": "test-client-id",
        },
    ):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential:
            mock_token = AccessToken(
                "fake_token",
                int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            )
            mock_instance = MagicMock()
            mock_instance.get_token.return_value = mock_token
            mock_credential.return_value = mock_instance

            with aioresponses() as mocked:
                mocked.get(
                    "https://test.osdu.com/api/storage/v2/query/records?kind=test%3Atest%3Atest%3A1.0.0&limit=10",
                    payload=mock_response,
                )

                result = await storage_query_records_by_kind(
                    kind="test:test:test:1.0.0", limit=10
                )

                assert result["success"] is True
                assert result["cursor"] == "next-page-cursor"
                assert result["results"] == mock_response["results"]
                assert result["count"] == 3
                assert result["partition"] == "test-partition"


@pytest.mark.asyncio
async def test_storage_query_records_by_kind_with_cursor():
    """Test query with pagination cursor."""
    mock_response = {"cursor": "another-cursor", "results": ["test:record:999"]}

    with patch.dict(
        os.environ,
        {
            "OSDU_MCP_SERVER_URL": "https://test.osdu.com",
            "OSDU_MCP_SERVER_DATA_PARTITION": "test-partition",
            "AZURE_CLIENT_ID": "test-client-id",
        },
    ):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential:
            mock_token = AccessToken(
                "fake_token",
                int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            )
            mock_instance = MagicMock()
            mock_instance.get_token.return_value = mock_token
            mock_credential.return_value = mock_instance

            with aioresponses() as mocked:
                mocked.get(
                    "https://test.osdu.com/api/storage/v2/query/records?kind=test%3Atest%3Atest%3A1.0.0&limit=5&cursor=previous-cursor",
                    payload=mock_response,
                )

                result = await storage_query_records_by_kind(
                    kind="test:test:test:1.0.0", limit=5, cursor="previous-cursor"
                )

                assert result["success"] is True
                assert result["cursor"] == "another-cursor"
                assert result["count"] == 1
