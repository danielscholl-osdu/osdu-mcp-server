"""Tests for schema_get tool."""

import pytest
from aioresponses import aioresponses
from unittest.mock import patch, MagicMock
import os
from datetime import datetime, timedelta

from azure.core.credentials import AccessToken

from osdu_mcp_server.tools.schema.get import schema_get


@pytest.mark.asyncio
async def test_schema_get_success():
    """Test successful retrieval of schema by ID."""
    mock_response = {
        "id": "osdu:wks:wellbore:1.0.0",
        "schemaInfo": {
            "schemaIdentity": {
                "authority": "osdu",
                "source": "wks",
                "entityType": "wellbore",
                "schemaVersionMajor": 1,
                "schemaVersionMinor": 0,
                "schemaVersionPatch": 0,
                "id": "osdu:wks:wellbore:1.0.0"
            },
            "createdBy": "user@example.com",
            "dateCreated": "2025-01-15T10:30:00Z",
            "status": "PUBLISHED",
            "scope": "INTERNAL"
        },
        "schema": {
            "$id": "https://schema.osdu.opengroup.org/json/wks/wellbore.1.0.0.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Wellbore",
            "description": "Wellbore schema definition",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Wellbore name"
                }
            },
            "required": ["name"]
        }
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
                    "https://test.osdu.com/api/schema-service/v1/schema/osdu:wks:wellbore:1.0.0",
                    payload=mock_response
                )
                
                result = await schema_get(id="osdu:wks:wellbore:1.0.0")
        
        assert result["success"] is True
        assert result["id"] == "osdu:wks:wellbore:1.0.0"
        assert result["partition"] == "opendes"
        assert "schemaInfo" in result
        assert "schema" in result
        
        # Check schema details
        assert result["schemaInfo"]["schemaIdentity"]["authority"] == "osdu"
        assert result["schemaInfo"]["schemaIdentity"]["source"] == "wks"
        assert result["schemaInfo"]["schemaIdentity"]["entityType"] == "wellbore"
        assert result["schema"]["title"] == "Wellbore"
