"""Tests for storage get record operations."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import os
import re

from azure.core.credentials import AccessToken
from aioresponses import aioresponses

from osdu_mcp_server.tools.storage.get_record import storage_get_record
from osdu_mcp_server.tools.storage.get_record_version import storage_get_record_version
from osdu_mcp_server.tools.storage.list_record_versions import storage_list_record_versions


@pytest.mark.asyncio
async def test_storage_get_record_success():
    """Test successful record retrieval."""
    mock_record = {
        "id": "test:record:123",
        "kind": "test:test:test:1.0.0",
        "version": 1234567890,
        "acl": {"viewers": ["test"], "owners": ["test"]},
        "legal": {"legaltags": ["test"], "otherRelevantDataCountries": ["US"]},
        "data": {"name": "Test Record", "value": 42},
        "createTime": "2023-01-01T00:00:00.000Z",
        "createUser": "test@example.com"
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'opendes',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.get(
                    "https://test.osdu.com/api/storage/v2/records/test:record:123",
                    payload=mock_record
                )

                result = await storage_get_record("test:record:123")

                assert result["success"] is True
                assert result["record"]["id"] == "test:record:123"
                assert result["record"]["kind"] == "test:test:test:1.0.0"
                assert result["partition"] == "opendes"


@pytest.mark.asyncio
async def test_storage_get_record_with_attributes():
    """Test record retrieval with attribute filtering."""
    mock_record = {
        "id": "test:record:123",
        "kind": "test:test:test:1.0.0",
        "version": 1234567890,
        "data": {"name": "Test Record"}  # Only requested attribute
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'opendes',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                # Use pattern matching for URL with query parameters
                mocked.get(
                    url=re.compile(r"https://test\.osdu\.com/api/storage/v2/records/test:record:123.*"),
                    payload=mock_record
                )

                result = await storage_get_record("test:record:123", attributes=["data.name"])

                assert result["success"] is True
                assert result["record"]["data"]["name"] == "Test Record"


@pytest.mark.asyncio
async def test_storage_get_record_version_success():
    """Test successful record version retrieval."""
    mock_record = {
        "id": "test:record:123",
        "kind": "test:test:test:1.0.0",
        "version": 1234567890,
        "data": {"name": "Test Record Version"}
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'opendes',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.get(
                    "https://test.osdu.com/api/storage/v2/records/test:record:123/1234567890",
                    payload=mock_record
                )

                result = await storage_get_record_version("test:record:123", 1234567890)

                assert result["success"] is True
                assert result["record"]["version"] == 1234567890


@pytest.mark.asyncio
async def test_storage_list_record_versions_success():
    """Test successful record versions listing."""
    mock_versions = {
        "recordId": "test:record:123",
        "versions": [1234567890, 1234567891, 1234567892]
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'opendes',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                mocked.get(
                    "https://test.osdu.com/api/storage/v2/records/versions/test:record:123",
                    payload=mock_versions
                )

                result = await storage_list_record_versions("test:record:123")

                assert result["success"] is True
                assert result["recordId"] == "test:record:123"
                assert result["count"] == 3
                assert len(result["versions"]) == 3
                assert 1234567890 in result["versions"]
