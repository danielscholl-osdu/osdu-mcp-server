"""Authentication handler for OSDU MCP Server.

This module implements authentication support for multiple cloud providers
with mode-based selection following OSDU CLI patterns.
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from .config_manager import ConfigManager
from .exceptions import OSMCPAuthError


class AuthenticationMode(Enum):
    """Supported authentication modes."""
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"


class AuthHandler:
    """Authentication handler with support for multiple cloud providers."""

    def __init__(self, config: ConfigManager):
        """Initialize authentication handler.

        Args:
            config: Configuration manager instance
        """
        self.config = config
        self._credential: Optional[DefaultAzureCredential] = None
        self._cached_token: Optional[AccessToken] = None
        self.mode = self._detect_authentication_mode()
        self._initialize_credential()
    
    def _detect_authentication_mode(self) -> AuthenticationMode:
        """Auto-detect authentication mode based on environment variables.
        
        Detection priority:
        1. Provider-specific environment variables (auto-detection)
        2. Explicit OSDU_MCP_AUTH_MODE (optional override)
        
        Returns:
            AuthenticationMode: Detected authentication mode
            
        Raises:
            OSMCPAuthError: If no valid authentication mode can be determined
        """
        # Auto-detect based on provider credentials
        if os.environ.get("AZURE_CLIENT_ID") or os.environ.get("AZURE_TENANT_ID"):
            detected_mode = AuthenticationMode.AZURE
        elif os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_REGION"):
            detected_mode = AuthenticationMode.AWS
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
            detected_mode = AuthenticationMode.GCP
        else:
            detected_mode = None
            
        # Check for explicit override (optional)
        explicit_mode = os.environ.get("OSDU_MCP_AUTH_MODE", "").lower()
        if explicit_mode and explicit_mode in [m.value for m in AuthenticationMode]:
            # If explicit mode conflicts with detected mode, warn but use explicit
            if detected_mode and detected_mode.value != explicit_mode:
                # In production, you might want to log a warning here
                pass
            return AuthenticationMode(explicit_mode)
            
        # Use detected mode or raise error
        if detected_mode:
            return detected_mode
        
        raise OSMCPAuthError(
            "Cannot detect authentication mode from environment variables. "
            "Set Azure (AZURE_CLIENT_ID), AWS (AWS_ACCESS_KEY_ID), or "
            "GCP (GOOGLE_APPLICATION_CREDENTIALS) credentials."
        )

    def _initialize_credential(self) -> None:
        """Initialize credential based on authentication mode."""
        if self.mode == AuthenticationMode.AZURE:
            self._initialize_azure_credential()
        elif self.mode == AuthenticationMode.AWS:
            self._initialize_aws_credential()
        elif self.mode == AuthenticationMode.GCP:
            self._initialize_gcp_credential()
    
    def _initialize_azure_credential(self) -> None:
        """Initialize Azure credential with appropriate exclusions."""
        # Auto-detect authentication method based on available credentials
        has_client_secret = bool(os.environ.get("AZURE_CLIENT_SECRET"))
        
        if has_client_secret:
            # Service Principal authentication - exclude other methods
            exclude_cli = True
            exclude_powershell = True
            exclude_interactive_browser = True
        else:
            # No secret, allow Azure CLI and PowerShell, never interactive
            exclude_cli = False
            exclude_powershell = False
            exclude_interactive_browser = True

        # Create credential with exclusions
        self._credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=exclude_interactive_browser,
            exclude_azure_cli_credential=exclude_cli,
            exclude_azure_powershell_credential=exclude_powershell,
            # Always exclude Visual Studio Code credential in production
            exclude_visual_studio_code_credential=True,
        )
    
    def _initialize_aws_credential(self) -> None:
        """Initialize AWS credential (future implementation)."""
        raise NotImplementedError(
            "AWS authentication not yet implemented. "
            "Please use Azure authentication by setting AZURE_CLIENT_ID and AZURE_TENANT_ID."
        )
    
    def _initialize_gcp_credential(self) -> None:
        """Initialize GCP credential (future implementation)."""
        raise NotImplementedError(
            "GCP authentication not yet implemented. "
            "Please use Azure authentication by setting AZURE_CLIENT_ID and AZURE_TENANT_ID."
        )

    async def get_access_token(self) -> str:
        """Get valid access token with automatic refresh.

        Returns:
            Valid access token for OSDU API

        Raises:
            OSMCPAuthError: If authentication fails
        """
        if self.mode == AuthenticationMode.AZURE:
            return await self._get_azure_token()
        elif self.mode == AuthenticationMode.AWS:
            return await self._get_aws_token()
        elif self.mode == AuthenticationMode.GCP:
            return await self._get_gcp_token()
    
    async def _get_azure_token(self) -> str:
        """Get Azure access token.
        
        Returns:
            Valid Azure access token
            
        Raises:
            OSMCPAuthError: If authentication fails
        """
        try:
            # Check if we have a cached token that's still valid
            if self._is_token_valid():
                return self._cached_token.token

            # Get client ID from standard Azure environment variable
            client_id = os.environ.get("AZURE_CLIENT_ID")
            if not client_id:
                raise OSMCPAuthError(
                    "AZURE_CLIENT_ID environment variable is required for Azure authentication"
                )
            
            # Derive OAuth scope from client ID
            scope = f"{client_id}/.default"

            # Get new token
            self._cached_token = self._credential.get_token(scope)
            return self._cached_token.token

        except ClientAuthenticationError as e:
            # Handle specific authentication errors with user-friendly messages
            error_message = str(e).lower()
            
            if "az login" in error_message or "azurecli" in error_message:
                raise OSMCPAuthError(
                    "Authentication failed. Please run 'az login' before using OSDU MCP Server"
                )
            elif "expired" in error_message or "refresh token" in error_message:
                raise OSMCPAuthError(
                    "Azure authentication token expired. Please run 'az login' to refresh"
                )
            elif "invalid_scope" in error_message or "scope format is invalid" in error_message:
                raise OSMCPAuthError(
                    "Invalid Azure client ID. Please verify your AZURE_CLIENT_ID is correct"
                )
            elif "no accounts were found" in error_message or "environment variables are not fully configured" in error_message:
                if os.environ.get("AZURE_CLIENT_SECRET"):
                    raise OSMCPAuthError(
                        "Service Principal authentication failed. Please check your AZURE_CLIENT_ID, "
                        "AZURE_TENANT_ID, and AZURE_CLIENT_SECRET environment variables"
                    )
                else:
                    raise OSMCPAuthError(
                        "No Azure credentials found. Please set up Service Principal credentials "
                        "or run 'az login' for CLI authentication"
                    )
            else:
                # Generic authentication error
                raise OSMCPAuthError(
                    "Authentication failed. Please check your Azure credentials"
                )
        except Exception as e:
            # Handle non-authentication errors (network issues, etc.)
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise OSMCPAuthError(
                    "Failed to connect to Azure authentication service. Please check your network connection"
                )
            else:
                # Unexpected error - provide minimal details to user
                raise OSMCPAuthError(
                    "Authentication configuration error. Please check your environment setup"
                )
    
    async def _get_aws_token(self) -> str:
        """Get AWS access token (future implementation).
        
        Returns:
            Valid AWS access token
            
        Raises:
            NotImplementedError: AWS authentication not yet implemented
        """
        raise NotImplementedError(
            "AWS token retrieval not yet implemented. "
            "Please use Azure authentication by setting AZURE_CLIENT_ID and AZURE_TENANT_ID."
        )
    
    async def _get_gcp_token(self) -> str:
        """Get GCP access token (future implementation).
        
        Returns:
            Valid GCP access token
            
        Raises:
            NotImplementedError: GCP authentication not yet implemented
        """
        raise NotImplementedError(
            "GCP token retrieval not yet implemented. "
            "Please use Azure authentication by setting AZURE_CLIENT_ID and AZURE_TENANT_ID."
        )

    async def validate_token(self) -> bool:
        """Validate current token against OSDU.

        This method can be enhanced to make an actual API call
        to validate the token against OSDU services.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # For now, just check if we can get a token
            await self.get_access_token()
            return True
        except OSMCPAuthError:
            return False

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid.

        Returns:
            True if token exists and hasn't expired
        """
        if not self._cached_token:
            return False

        # Add a buffer of 5 minutes before expiration
        expiry_buffer = timedelta(minutes=5)
        token_expiry = datetime.fromtimestamp(self._cached_token.expires_on)
        return datetime.now() < (token_expiry - expiry_buffer)

    def close(self) -> None:
        """Clean up authentication resources."""
        # Clear cached token
        self._cached_token = None

        # Close credential if it has a close method
        if hasattr(self._credential, "close"):
            self._credential.close()