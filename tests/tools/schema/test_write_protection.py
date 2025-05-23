"""Tests for schema write protection."""

import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from aioresponses import aioresponses
from azure.core.credentials import AccessToken

from osdu_mcp_server.tools.schema.create import schema_create
from osdu_mcp_server.tools.schema.update import schema_update


@pytest.mark.asyncio
async def test_schema_create_write_protection():
    """Test write protection for schema_create."""
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
        "OSDU_MCP_ENABLE_WRITE_MODE": "false",  # Write protection enabled
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with pytest.raises(Exception) as excinfo:
                await schema_create(
                    authority="test",
                    source="test",
                    entity="test",
                    major_version=1,
                    minor_version=0,
                    patch_version=0,
                    schema={"type": "object"},
                )

            assert "Schema write operations are disabled" in str(excinfo.value)
            assert "OSDU_MCP_ENABLE_WRITE_MODE=true" in str(excinfo.value)


@pytest.mark.asyncio
async def test_schema_update_write_protection():
    """Test write protection for schema_update."""
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
        "OSDU_MCP_ENABLE_WRITE_MODE": "false",  # Write protection enabled
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with pytest.raises(Exception) as excinfo:
                await schema_update(
                    id="test:test:test:1.0.0", schema={"type": "object"}
                )

            assert "Schema write operations are disabled" in str(excinfo.value)
            assert "OSDU_MCP_ENABLE_WRITE_MODE=true" in str(excinfo.value)


@pytest.mark.asyncio
async def test_schema_create_write_enabled():
    """Test successful schema creation with write mode enabled."""
    mock_response = {"id": "test:test:test:1.0.0", "status": "DEVELOPMENT"}

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
        "OSDU_MCP_ENABLE_WRITE_MODE": "true",  # Write protection disabled
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
                    "https://test.osdu.com/api/schema-service/v1/schema",
                    payload=mock_response,
                )

                result = await schema_create(
                    authority="test",
                    source="test",
                    entity="test",
                    major_version=1,
                    minor_version=0,
                    patch_version=0,
                    schema={"type": "object"},
                )

            assert result["success"] is True
            assert result["created"] is True
            assert result["id"] == "test:test:test:1.0.0"
            assert result["write_enabled"] is True


@pytest.mark.asyncio
async def test_schema_update_write_enabled():
    """Test successful schema update with write mode enabled."""
    mock_get_response = {
        "id": "test:test:test:1.0.0",
        "schemaInfo": {
            "schemaIdentity": {
                "authority": "test",
                "source": "test",
                "entityType": "test",
                "schemaVersionMajor": 1,
                "schemaVersionMinor": 0,
                "schemaVersionPatch": 0,
                "id": "test:test:test:1.0.0",
            },
            "status": "DEVELOPMENT",
        },
    }

    mock_update_response = {"id": "test:test:test:1.0.0", "status": "DEVELOPMENT"}

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
        "OSDU_MCP_ENABLE_WRITE_MODE": "true",  # Write protection disabled
    }

    with patch.dict(os.environ, test_env):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                # Mock both raw URL and quoted URL to handle aioresponses URL normalization
                test_schema_url = "https://test.osdu.com/api/schema-service/v1/schema/test:test:test:1.0.0"
                mocked.get(test_schema_url, payload=mock_get_response)
                mocked.get(
                    "https://test.osdu.com/api/schema-service/v1/schema/test%3Atest%3Atest%3A1.0.0",
                    payload=mock_get_response,
                )
                mocked.put(
                    "https://test.osdu.com/api/schema-service/v1/schema",
                    payload=mock_update_response,
                )

                result = await schema_update(
                    id="test:test:test:1.0.0",
                    schema={
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                )

            assert result["success"] is True
            assert result["updated"] is True
            assert result["id"] == "test:test:test:1.0.0"
            assert result["write_enabled"] is True
