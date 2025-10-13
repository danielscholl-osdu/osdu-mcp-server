"""Tests for multi-cloud authentication in AuthHandler.

This test suite covers:
- USER_TOKEN mode with JWT validation
- AWS boto3 SDK authentication
- GCP Application Default Credentials
- Multi-cloud mode detection priority
"""

import asyncio
import os
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

import jwt
import pytest
from azure.core.credentials import AccessToken

from osdu_mcp_server.shared.auth_handler import AuthenticationMode, AuthHandler
from osdu_mcp_server.shared.config_manager import ConfigManager
from osdu_mcp_server.shared.exceptions import OSMCPAuthError


def create_test_jwt(exp: float | None = None) -> str:
    """Create a test JWT token.

    Args:
        exp: Expiration timestamp (default: 1 hour from now)

    Returns:
        Valid JWT token string
    """

    if exp is None:
        exp = time.time() + 3600

    payload = {"sub": "test-user", "exp": exp}
    return jwt.encode(payload, "secret", algorithm="HS256")


@pytest.mark.asyncio
async def test_user_token_mode_detection():
    """Test USER_TOKEN mode has highest priority."""
    mock_config = MagicMock(spec=ConfigManager)

    valid_token = create_test_jwt()

    with patch.dict(
        os.environ,
        {
            "OSDU_MCP_USER_TOKEN": valid_token,
            "AZURE_CLIENT_ID": "azure-id",  # Should be ignored
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json",  # Should be ignored
        },
    ):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.USER_TOKEN


@pytest.mark.asyncio
async def test_user_token_retrieval():
    """Test successful user token retrieval."""
    mock_config = MagicMock(spec=ConfigManager)

    # Create token that expires 2 hours from now (well in the future)
    valid_token = create_test_jwt(exp=time.time() + 7200)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": valid_token}):
        auth = AuthHandler(mock_config)
        token = await auth.get_access_token()
        assert token == valid_token


@pytest.mark.asyncio
async def test_user_token_validation_expired():
    """Test expired user token is rejected."""
    mock_config = MagicMock(spec=ConfigManager)

    expired_token = create_test_jwt(exp=time.time() - 3600)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": expired_token}):
        auth = AuthHandler(mock_config)
        with pytest.raises(OSMCPAuthError, match="expired"):
            await auth.get_access_token()


@pytest.mark.asyncio
async def test_user_token_validation_invalid_format():
    """Test invalid JWT format is rejected."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": "not-a-valid-jwt"}):
        auth = AuthHandler(mock_config)
        with pytest.raises(OSMCPAuthError, match="Invalid JWT token format"):
            await auth.get_access_token()


@pytest.mark.asyncio
async def test_gcp_mode_detection_explicit():
    """Test GCP mode detection when GOOGLE_APPLICATION_CREDENTIALS is set."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"}, clear=True
    ):
        with patch("google.auth.default") as mock_gcp:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds.token = "gcp-token"
            mock_gcp.return_value = (mock_creds, "test-project")

            auth = AuthHandler(mock_config)
            assert auth.mode == AuthenticationMode.GCP


@pytest.mark.asyncio
async def test_gcp_token_retrieval_with_refresh():
    """Test GCP token retrieval with automatic refresh."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"}, clear=True
    ):
        with patch("google.auth.default") as mock_gcp:
            mock_creds = MagicMock()
            mock_creds.valid = False  # Needs refresh
            mock_creds.token = "gcp-token-123"
            mock_gcp.return_value = (mock_creds, "test-project")

            auth = AuthHandler(mock_config)
            auth._gcp_credentials = mock_creds

            # Mock the refresh method
            with patch("google.auth.transport.requests.Request"):
                token = await auth._get_gcp_token()

                assert token == "gcp-token-123"
                mock_creds.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_gcp_credentials_not_found_error():
    """Test GCP credentials not found error message."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"}, clear=True
    ):
        with patch("google.auth.default") as mock_gcp:
            from google.auth.exceptions import DefaultCredentialsError

            mock_gcp.side_effect = DefaultCredentialsError()

            with pytest.raises(
                OSMCPAuthError, match="GCP Application Default Credentials not found"
            ):
                AuthHandler(mock_config)


@pytest.mark.asyncio
async def test_aws_mode_detection_explicit():
    """Test AWS mode detection when AWS_ACCESS_KEY_ID is set."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE"}, clear=True
    ):
        with patch("boto3.Session") as mock_session:
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            # Mock STS client
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:user/test",
            }
            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)
            assert auth.mode == AuthenticationMode.AWS


@pytest.mark.asyncio
async def test_aws_token_retrieval():
    """Test AWS token retrieval with STS."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE"}, clear=True
    ):
        with patch("boto3.Session") as mock_session:
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            # Mock STS client for initialization
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:user/test",
            }

            # Mock STS get_session_token
            mock_sts.get_session_token.return_value = {
                "Credentials": {
                    "SessionToken": "aws-session-token-123",
                    "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
                    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                }
            }

            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)
            token = await auth._get_aws_token()

            assert token == "aws-session-token-123"


@pytest.mark.asyncio
async def test_aws_credentials_not_found_error():
    """Test AWS credentials not found error message."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE"}, clear=True
    ):
        with patch("boto3.Session") as mock_session:
            from botocore.exceptions import NoCredentialsError

            mock_session_instance = MagicMock()
            mock_session_instance.get_credentials.return_value = None
            mock_session.return_value = mock_session_instance

            with pytest.raises(OSMCPAuthError, match="AWS credentials not found"):
                AuthHandler(mock_config)


@pytest.mark.asyncio
async def test_mode_detection_priority_order():
    """Test authentication mode detection follows correct priority."""
    mock_config = MagicMock(spec=ConfigManager)

    # Priority 1: USER_TOKEN beats everything
    valid_token = create_test_jwt()
    with patch.dict(
        os.environ,
        {
            "OSDU_MCP_USER_TOKEN": valid_token,
            "AZURE_CLIENT_ID": "azure-id",
            "AWS_ACCESS_KEY_ID": "aws-key",
        },
    ):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.USER_TOKEN

    # Priority 2: Azure beats AWS/GCP
    with patch.dict(
        os.environ,
        {
            "AZURE_CLIENT_ID": "azure-id",
            "AWS_ACCESS_KEY_ID": "aws-key",
        },
        clear=True,
    ):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.AZURE

    # Priority 3: AWS explicit beats GCP
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "aws-key",
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json",
        },
        clear=True,
    ):
        with patch("boto3.Session") as mock_session:
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:user/test",
            }
            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)
            assert auth.mode == AuthenticationMode.AWS


@pytest.mark.asyncio
async def test_aws_auto_discovery():
    """Test AWS auto-discovery when no explicit credentials."""
    mock_config = MagicMock(spec=ConfigManager)

    # No explicit AWS env vars, but boto3 can discover credentials
    with patch.dict(os.environ, {}, clear=True):
        with patch("boto3.Session") as mock_session:
            # First call (in detection) - credentials found
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            # Mock STS for initialization
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:role/test-role",
            }
            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)
            assert auth.mode == AuthenticationMode.AWS


@pytest.mark.asyncio
async def test_gcp_auto_discovery():
    """Test GCP auto-discovery when no explicit credentials."""
    mock_config = MagicMock(spec=ConfigManager)

    # No explicit GCP env vars, but google.auth can discover credentials
    with patch.dict(os.environ, {}, clear=True):
        with patch("boto3.Session") as mock_boto:
            # AWS auto-discovery fails
            mock_boto.side_effect = Exception("No AWS credentials")

            with patch("google.auth.default") as mock_gcp:
                # GCP auto-discovery succeeds
                mock_creds = MagicMock()
                mock_creds.valid = True
                mock_creds.token = "gcp-token"
                mock_gcp.return_value = (mock_creds, "test-project")

                auth = AuthHandler(mock_config)
                assert auth.mode == AuthenticationMode.GCP


@pytest.mark.asyncio
async def test_no_credentials_error():
    """Test error when no authentication credentials found."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(os.environ, {}, clear=True):
        with patch("boto3.Session") as mock_boto:
            mock_boto.side_effect = Exception("No AWS")

            with patch("google.auth.default") as mock_gcp:
                mock_gcp.side_effect = Exception("No GCP")

                with pytest.raises(
                    OSMCPAuthError, match="No authentication credentials configured"
                ):
                    AuthHandler(mock_config)


@pytest.mark.asyncio
async def test_close_all_credential_types():
    """Test cleanup of all credential types."""
    mock_config = MagicMock(spec=ConfigManager)

    # Test with USER_TOKEN mode
    valid_token = create_test_jwt()
    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": valid_token}):
        auth = AuthHandler(mock_config)
        auth.close()

        # Verify no errors on cleanup
        assert True

    # Test with Azure mode
    with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-id"}, clear=True):
        with patch(
            "osdu_mcp_server.shared.auth_handler.DefaultAzureCredential"
        ) as mock_cred:
            mock_cred_instance = MagicMock()
            mock_cred.return_value = mock_cred_instance

            auth = AuthHandler(mock_config)
            auth._azure_cached_token = AccessToken("token", 123456)
            auth.close()

            assert auth._azure_cached_token is None
            if hasattr(mock_cred_instance, "close"):
                mock_cred_instance.close.assert_called_once()

    # Test with AWS mode
    with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test-key"}, clear=True):
        with patch("boto3.Session") as mock_session:
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:user/test",
            }
            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)
            auth.close()

            assert auth._aws_session is None

    # Test with GCP mode
    with patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"}, clear=True
    ):
        with patch("google.auth.default") as mock_gcp:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds.token = "gcp-token"
            mock_gcp.return_value = (mock_creds, "test-project")

            auth = AuthHandler(mock_config)
            auth.close()

            assert auth._gcp_credentials is None


@pytest.mark.asyncio
async def test_gcp_token_refresh_error():
    """Test GCP token refresh error handling."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"}, clear=True
    ):
        with patch("google.auth.default") as mock_gcp:
            from google.auth.exceptions import RefreshError

            mock_creds = MagicMock()
            mock_creds.valid = False  # Needs refresh
            mock_gcp.return_value = (mock_creds, "test-project")

            auth = AuthHandler(mock_config)

            # Mock refresh to raise error with "expired" message
            with patch("google.auth.transport.requests.Request"):
                mock_creds.refresh.side_effect = RefreshError("Token expired")

                with pytest.raises(OSMCPAuthError, match="GCP refresh token expired"):
                    await auth._get_gcp_token()


@pytest.mark.asyncio
async def test_aws_token_retrieval_error():
    """Test AWS token retrieval error handling."""
    mock_config = MagicMock(spec=ConfigManager)

    with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test-key"}, clear=True):
        with patch("boto3.Session") as mock_session:
            mock_session_instance = MagicMock()
            mock_creds = MagicMock()
            mock_session_instance.get_credentials.return_value = mock_creds
            mock_session.return_value = mock_session_instance

            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                "Account": "123456789012",
                "Arn": "arn:aws:iam::123456789012:user/test",
            }
            mock_sts.get_session_token.side_effect = Exception("STS error")
            mock_session_instance.client.return_value = mock_sts

            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError, match="AWS token retrieval failed"):
                await auth._get_aws_token()


@pytest.mark.asyncio
async def test_user_token_expiring_soon():
    """Test token still works when expiring soon (with warning logged)."""
    mock_config = MagicMock(spec=ConfigManager)

    # Create token expiring in 2 minutes (120 seconds)
    # Token should still be accepted, but a warning should be logged
    expiring_soon_token = create_test_jwt(exp=time.time() + 120)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": expiring_soon_token}):
        auth = AuthHandler(mock_config)
        # Token should be accepted even though it's expiring soon
        token = await auth.get_access_token()
        assert token == expiring_soon_token
