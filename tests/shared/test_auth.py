"""Tests for the AuthHandler class."""

import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from osdu_mcp_server.shared.auth_handler import AuthHandler, AuthenticationMode
from osdu_mcp_server.shared.config_manager import ConfigManager
from osdu_mcp_server.shared.exceptions import OSMCPAuthError


@pytest.mark.asyncio
async def test_auth_handler_get_token_success():
    """Test successful token retrieval with derived scope."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False  # Default exclusions

    mock_token = AccessToken(
        token="test-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.return_value = mock_token
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}, clear=True):
            auth = AuthHandler(mock_config)
            token = await auth.get_access_token()

            assert token == "test-token"
            # Scope should always be derived from CLIENT_ID
            mock_cred_instance.get_token.assert_called_once_with("test-client-id/.default")


@pytest.mark.asyncio
async def test_auth_handler_token_caching():
    """Test that tokens are cached and reused."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    mock_token = AccessToken(
        token="cached-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.return_value = mock_token
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            # First call
            token1 = await auth.get_access_token()
            # Second call (should use cached token)
            token2 = await auth.get_access_token()

            assert token1 == token2 == "cached-token"
            # get_token should only be called once due to caching
            assert mock_cred_instance.get_token.call_count == 1


@pytest.mark.asyncio
async def test_auth_handler_token_refresh():
    """Test that expired tokens are refreshed."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    # Create an expired token
    expired_token = AccessToken(
        token="expired-token",
        expires_on=int((datetime.now() - timedelta(hours=1)).timestamp())
    )

    # Create a new token
    new_token = AccessToken(
        token="new-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = [expired_token, new_token]
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            # First call (gets expired token)
            token1 = await auth.get_access_token()
            # Second call (should refresh)
            token2 = await auth.get_access_token()

            assert token1 == "expired-token"
            assert token2 == "new-token"
            assert mock_cred_instance.get_token.call_count == 2


@pytest.mark.asyncio
async def test_auth_handler_azure_auto_detection():
    """Test that authentication method is auto-detected based on AZURE_CLIENT_SECRET."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False  # Default for other auth methods

    # Test 1: With client secret (Service Principal)
    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        with patch.dict(os.environ, {"AZURE_CLIENT_SECRET": "test-secret", "AZURE_CLIENT_ID": "test"}):
            # Create the handler but we're only interested in how the credential was instantiated
            AuthHandler(mock_config)

            # Should exclude CLI when secret is present
            call_kwargs = mock_cred.call_args.kwargs
            assert call_kwargs["exclude_azure_cli_credential"] is True
            assert call_kwargs["exclude_interactive_browser_credential"] is True
            assert call_kwargs["exclude_azure_powershell_credential"] is True

    # Test 2: Without client secret (Azure CLI/PowerShell)
    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test"}, clear=True):
            # Create the handler but we're only interested in how the credential was instantiated
            AuthHandler(mock_config)

            # Should allow CLI and PowerShell when no secret
            call_kwargs = mock_cred.call_args.kwargs
            assert call_kwargs["exclude_azure_cli_credential"] is False
            assert call_kwargs["exclude_azure_powershell_credential"] is False
            assert call_kwargs["exclude_interactive_browser_credential"] is True  # Always excluded


@pytest.mark.asyncio
async def test_auth_handler_get_token_failure():
    """Test token retrieval failure with user-friendly error."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = Exception("Unknown error")
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Authentication configuration error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_azure_cli_error():
    """Test Azure CLI authentication error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = ClientAuthenticationError(
            "Please run 'az login' to set up an account"
        )
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Please run 'az login' before using OSDU MCP Server" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_expired_token_error():
    """Test expired token error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = ClientAuthenticationError(
            "The refresh token has expired or is invalid"
        )
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Azure authentication token expired" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_no_credentials_error():
    """Test no credentials error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = ClientAuthenticationError(
            "Environment variables are not fully configured"
        )
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "No Azure credentials found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_service_principal_error():
    """Test service principal authentication error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = ClientAuthenticationError(
            "Environment variables are not fully configured"
        )
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "test-client-id",
            "AZURE_CLIENT_SECRET": "test-secret"
        }):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Service Principal authentication failed" in str(exc_info.value)
            assert "AZURE_CLIENT_ID" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_invalid_scope_error():
    """Test invalid scope error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = ClientAuthenticationError(
            "The scope format is invalid. AADSTS70011: The provided request must include a 'scope' input parameter."
        )
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Invalid Azure client ID" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_network_error():
    """Test network connection error with helpful message."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.side_effect = Exception("Connection timeout")
        mock_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            with pytest.raises(OSMCPAuthError) as exc_info:
                await auth.get_access_token()

            assert "Failed to connect to Azure authentication service" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_handler_validate_token():
    """Test token validation."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    mock_token = AccessToken(
        token="valid-token",
        expires_on=int((datetime.now() + timedelta(hours=1)).timestamp())
    )

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred_instance.get_token.return_value = mock_token
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)

            # Test successful validation
            assert await auth.validate_token() is True

            # Clear the cached token to ensure we try to get a new one
            auth._cached_token = None

            # Test failed validation
            mock_cred_instance.get_token.side_effect = Exception("Auth failed")
            assert await auth.validate_token() is False


def test_auth_handler_close():
    """Test cleanup of authentication resources."""
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get.return_value = False

    with patch("osdu_mcp_server.shared.auth_handler.DefaultAzureCredential") as mock_cred:
        mock_cred_instance = MagicMock()
        mock_cred.return_value = mock_cred_instance

        # Mock environment variable for client ID
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}):
            auth = AuthHandler(mock_config)
        auth._cached_token = AccessToken("token", 123456)

        auth.close()

        # Verify cached token is cleared
        assert auth._cached_token is None

        # Verify credential close is called if available
        if hasattr(mock_cred_instance, "close"):
            mock_cred_instance.close.assert_called_once()


def test_auth_handler_mode_detection_explicit():
    """Test explicit authentication mode detection."""
    mock_config = MagicMock(spec=ConfigManager)

    # Test explicit Azure mode
    with patch.dict(os.environ, {"OSDU_MCP_AUTH_MODE": "azure", "AZURE_CLIENT_ID": "test"}, clear=True):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.AZURE

    # Test explicit AWS mode
    with patch.dict(os.environ, {"OSDU_MCP_AUTH_MODE": "aws"}, clear=True):
        with pytest.raises(NotImplementedError, match="AWS authentication not yet implemented"):
            AuthHandler(mock_config)

    # Test explicit GCP mode
    with patch.dict(os.environ, {"OSDU_MCP_AUTH_MODE": "gcp"}, clear=True):
        with pytest.raises(NotImplementedError, match="GCP authentication not yet implemented"):
            AuthHandler(mock_config)


def test_auth_handler_mode_detection_auto():
    """Test automatic authentication mode detection."""
    mock_config = MagicMock(spec=ConfigManager)

    # Test Azure auto-detection with CLIENT_ID
    with patch.dict(os.environ, {"AZURE_CLIENT_ID": "test-client-id"}, clear=True):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.AZURE

    # Test Azure auto-detection with TENANT_ID only
    with patch.dict(os.environ, {"AZURE_TENANT_ID": "test-tenant"}, clear=True):
        auth = AuthHandler(mock_config)
        assert auth.mode == AuthenticationMode.AZURE

    # Test AWS auto-detection with ACCESS_KEY_ID
    with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test-key"}, clear=True):
        with pytest.raises(NotImplementedError, match="AWS authentication not yet implemented"):
            AuthHandler(mock_config)

    # Test AWS auto-detection with REGION only
    with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}, clear=True):
        with pytest.raises(NotImplementedError, match="AWS authentication not yet implemented"):
            AuthHandler(mock_config)

    # Test GCP auto-detection with APPLICATION_CREDENTIALS
    with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"}, clear=True):
        with pytest.raises(NotImplementedError, match="GCP authentication not yet implemented"):
            AuthHandler(mock_config)

    # Test GCP auto-detection with PROJECT only
    with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "my-project"}, clear=True):
        with pytest.raises(NotImplementedError, match="GCP authentication not yet implemented"):
            AuthHandler(mock_config)


def test_auth_handler_mode_detection_error():
    """Test error when no valid authentication mode can be detected."""
    mock_config = MagicMock(spec=ConfigManager)

    # No credentials available
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OSMCPAuthError, match="Cannot detect authentication mode"):
            AuthHandler(mock_config)


@pytest.mark.asyncio
async def test_auth_handler_aws_token_not_implemented():
    """Test that AWS token retrieval raises NotImplementedError."""

    with patch.dict(os.environ, {"OSDU_MCP_AUTH_MODE": "aws"}, clear=True):
        # Skip initialization which would fail
        auth = AuthHandler.__new__(AuthHandler)
        auth.mode = AuthenticationMode.AWS

        with pytest.raises(NotImplementedError, match="AWS token retrieval not yet implemented"):
            await auth._get_aws_token()


@pytest.mark.asyncio
async def test_auth_handler_gcp_token_not_implemented():
    """Test that GCP token retrieval raises NotImplementedError."""

    with patch.dict(os.environ, {"OSDU_MCP_AUTH_MODE": "gcp"}, clear=True):
        # Skip initialization which would fail
        auth = AuthHandler.__new__(AuthHandler)
        auth.mode = AuthenticationMode.GCP

        with pytest.raises(NotImplementedError, match="GCP token retrieval not yet implemented"):
            await auth._get_gcp_token()
