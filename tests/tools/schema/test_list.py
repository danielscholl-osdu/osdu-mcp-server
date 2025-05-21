"""Tests for schema_list tool."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch, MagicMock
import os
import re
from datetime import datetime, timedelta

from azure.core.credentials import AccessToken

from osdu_mcp_server.tools.schema import list as schema_list_module
from osdu_mcp_server.tools.schema.list import schema_list


@pytest.mark.asyncio
async def test_schema_list_success():
    """Test successful retrieval of schemas."""
    mock_response = {
        "schemas": [
            {
                "id": "osdu:wks:wellbore:1.0.0",
                "authority": "osdu",
                "source": "wks",
                "entityType": "wellbore",
                "version": "1.0.0",
                "status": "PUBLISHED",
                "scope": "INTERNAL",
                "createdBy": "user@example.com",
                "dateCreated": "2025-01-15T10:30:00Z"
            },
            {
                "id": "osdu:wks:welllog:2.0.0",
                "authority": "osdu",
                "source": "wks",
                "entityType": "welllog",
                "version": "2.0.0",
                "status": "PUBLISHED",
                "scope": "INTERNAL",
                "createdBy": "user@example.com",
                "dateCreated": "2025-02-20T14:45:00Z"
            }
        ],
        "totalCount": 2
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
                    "https://test.osdu.com/api/schema-service/v1/schema?limit=10",
                    payload=mock_response
                )
                
                result = await schema_list()
        
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["schemas"]) == 2
        assert result["partition"] == "opendes"
        assert result["totalCount"] == 2
        
        # Check schema details
        assert result["schemas"][0]["id"] == "osdu:wks:wellbore:1.0.0"
        assert result["schemas"][1]["id"] == "osdu:wks:welllog:2.0.0"


@pytest.mark.asyncio
async def test_schema_list_with_filters():
    """Test retrieval of schemas with filtering."""
    mock_response = {
        "schemas": [
            {
                "id": "osdu:wks:wellbore:1.0.0",
                "authority": "osdu",
                "source": "wks",
                "entityType": "wellbore",
                "version": "1.0.0",
                "status": "PUBLISHED",
                "scope": "INTERNAL",
                "createdBy": "user@example.com",
                "dateCreated": "2025-01-15T10:30:00Z"
            }
        ],
        "totalCount": 1
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
                    re.compile(r"https://test\.osdu\.com/api/schema-service/v1/schema\?(?=.*authority=osdu)(?=.*entityType=wellbore)(?=.*limit=10)(?=.*source=wks).*"),
                    payload=mock_response
                )
                
                result = await schema_list(
                    authority="osdu",
                    source="wks",
                    entity="wellbore"
                )
        
        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["schemas"]) == 1
        assert result["schemas"][0]["authority"] == "osdu"
        assert result["schemas"][0]["source"] == "wks"
        assert result["schemas"][0]["entityType"] == "wellbore"


@pytest.mark.asyncio
async def test_schema_list_empty():
    """Test when no schemas exist or match filters."""
    mock_response = {
        "schemas": [],
        "totalCount": 0
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
                    re.compile(r"https://test\.osdu\.com/api/schema-service/v1/schema\?(?=.*authority=unknown)(?=.*limit=10).*"),
                    payload=mock_response
                )
                
                result = await schema_list(authority="unknown")
        
        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["schemas"]) == 0
        assert result["totalCount"] == 0