"""Tests for entitlements_mine tool."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch, MagicMock
import os
from datetime import datetime, timedelta

from azure.core.credentials import AccessToken

from osdu_mcp_server.tools.entitlements import entitlements_mine


@pytest.mark.asyncio
async def test_entitlements_mine_success():
    """Test successful retrieval of user groups."""
    mock_response = {
        "groups": [
            {
                "name": "users",
                "email": "users@opendes.dataservices.energy",
                "description": "All users"
            },
            {
                "name": "users.datalake.viewers",
                "email": "users.datalake.viewers@opendes.dataservices.energy",
                "description": "Data Lake read access"
            }
        ]
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'test-partition',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        # Mock the Azure credential to avoid real authentication
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                # Mock the actual API call
                mocked.get(
                    url=str("https://test.osdu.com/api/entitlements/v2/groups"),
                    payload=mock_response
                )

                result = await entitlements_mine()

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["groups"]) == 2
        assert result["groups"][0]["name"] == "users"
        assert result["groups"][1]["name"] == "users.datalake.viewers"

        # Test we return all fields from API
        assert "email" in result["groups"][0]
        assert "description" in result["groups"][0]


@pytest.mark.asyncio
async def test_entitlements_mine_empty():
    """Test when user has no groups."""
    mock_response = {
        "groups": []
    }

    mock_token = AccessToken(
        token="fake-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    test_env = {
        'OSDU_MCP_SERVER_URL': 'https://test.osdu.com',
        'OSDU_MCP_SERVER_DATA_PARTITION': 'test-partition',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_SECRET': 'test-secret'
    }

    with patch.dict(os.environ, test_env):
        # Mock the Azure credential to avoid real authentication
        with patch('osdu_mcp_server.shared.auth_handler.DefaultAzureCredential') as mock_credential_class:
            mock_credential = MagicMock()
            mock_credential.get_token.return_value = mock_token
            mock_credential_class.return_value = mock_credential

            with aioresponses() as mocked:
                # Mock the actual API call
                mocked.get(
                    url=str("https://test.osdu.com/api/entitlements/v2/groups"),
                    payload=mock_response
                )

                result = await entitlements_mine()

        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["groups"]) == 0
        assert result["partition"] == "test-partition"
