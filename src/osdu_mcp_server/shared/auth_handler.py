"""Authentication handler for OSDU MCP Server.

This module implements authentication support for multiple cloud providers
with mode-based selection following OSDU CLI patterns.

Supports:
- Azure: DefaultAzureCredential (native SDK)
- AWS: boto3 SDK credentials
- GCP: Application Default Credentials
- Generic: Manual OAuth Bearer token via OSDU_MCP_USER_TOKEN
"""

import asyncio
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from .config_manager import ConfigManager
from .exceptions import OSMCPAuthError
from .logging_manager import get_logger

logger = get_logger(__name__)


class AuthenticationMode(Enum):
    """Supported authentication modes."""

    USER_TOKEN = "user_token"  # Manual Bearer token from environment
    AZURE = "azure"  # Azure DefaultAzureCredential
    AWS = "aws"  # AWS boto3 SDK credentials
    GCP = "gcp"  # GCP Application Default Credentials


class AuthHandler:
    """Multi-cloud authentication handler with automatic mode detection.

    Supports:
    - Azure: DefaultAzureCredential (current)
    - AWS: boto3 SDK credentials (new)
    - GCP: Application Default Credentials (new)
    - Generic: Manual token from environment (new)

    Attributes:
        mode: Detected authentication mode
        config: Configuration manager
        _azure_credential: Azure credential instance
        _azure_cached_token: Cached Azure token
        _aws_session: AWS boto3 session
        _gcp_credentials: GCP credentials instance
        _gcp_project: GCP project ID
    """

    def __init__(self, config: ConfigManager):
        """Initialize authentication handler with automatic mode detection.

        Args:
            config: Configuration manager instance
        """
        self.config = config

        # Azure credentials
        self._azure_credential: DefaultAzureCredential | None = None
        self._azure_cached_token: AccessToken | None = None

        # AWS credentials
        self._aws_session: Any = None

        # GCP credentials
        self._gcp_credentials: Any = None
        self._gcp_project: str | None = None

        # Detect mode and initialize
        self.mode = self._detect_authentication_mode()
        self._initialize_credential()

    def _detect_authentication_mode(self) -> AuthenticationMode:
        """Auto-detect authentication mode with simple priority order.

        Priority Order (no overrides, just precedence):
        1. OSDU_MCP_USER_TOKEN (manual token - always highest)
        2. Azure credentials (AZURE_CLIENT_ID or AZURE_TENANT_ID)
        3. AWS explicit (AWS_ACCESS_KEY_ID or AWS_PROFILE)
        4. GCP explicit (GOOGLE_APPLICATION_CREDENTIALS)
        5. AWS auto-discovery (IAM roles, SSO)
        6. GCP auto-discovery (gcloud, metadata)
        7. Error (no credentials found)

        Returns:
            AuthenticationMode: Detected authentication mode

        Raises:
            OSMCPAuthError: If no authentication credentials found
        """
        # Priority 1: User token ALWAYS takes precedence
        if os.environ.get("OSDU_MCP_USER_TOKEN"):
            logger.info("Authentication mode: USER_TOKEN (manual Bearer token)")
            return AuthenticationMode.USER_TOKEN

        # Priority 2: Azure credentials
        if os.environ.get("AZURE_CLIENT_ID") or os.environ.get("AZURE_TENANT_ID"):
            logger.info("Authentication mode: AZURE (DefaultAzureCredential)")
            return AuthenticationMode.AZURE

        # Priority 3: AWS explicit credentials
        if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
            logger.info("Authentication mode: AWS (explicit credentials)")
            return AuthenticationMode.AWS

        # Priority 4: GCP explicit path
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.info("Authentication mode: GCP (explicit credentials)")
            return AuthenticationMode.GCP

        # Priority 5: Try AWS auto-discovery
        try:
            import boto3

            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                logger.info("Authentication mode: AWS (auto-discovered)")
                return AuthenticationMode.AWS
        except Exception:
            pass

        # Priority 6: Try GCP auto-discovery
        try:
            import google.auth

            credentials, _ = google.auth.default()
            if credentials:
                logger.info("Authentication mode: GCP (auto-discovered)")
                return AuthenticationMode.GCP
        except Exception:
            pass

        # Priority 7: No credentials found
        raise OSMCPAuthError(
            "No authentication credentials configured. Set up one of:\n\n"
            "  Manual Token (Highest Priority):\n"
            "    export OSDU_MCP_USER_TOKEN=your-bearer-token\n\n"
            "  Azure (Automatic):\n"
            "    az login\n"
            "    OR export AZURE_CLIENT_ID=... AZURE_TENANT_ID=...\n\n"
            "  AWS (Automatic):\n"
            "    aws sso login\n"
            "    OR export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...\n\n"
            "  GCP (Automatic):\n"
            "    gcloud auth application-default login\n"
            "    OR export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json\n\n"
            "  See: https://github.com/danielscholl-osdu/osdu-mcp-server#authentication"
        )

    def _initialize_credential(self) -> None:
        """Initialize credential based on authentication mode."""
        if self.mode == AuthenticationMode.AZURE:
            self._initialize_azure_credential()
        elif self.mode == AuthenticationMode.AWS:
            self._initialize_aws_credential()
        elif self.mode == AuthenticationMode.GCP:
            self._initialize_gcp_credential()
        elif self.mode == AuthenticationMode.USER_TOKEN:
            # No initialization needed for manual tokens
            pass

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
        self._azure_credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=exclude_interactive_browser,
            exclude_azure_cli_credential=exclude_cli,
            exclude_azure_powershell_credential=exclude_powershell,
            # Always exclude Visual Studio Code credential in production
            exclude_visual_studio_code_credential=True,
        )

        logger.info("Initialized Azure DefaultAzureCredential")

    def _initialize_aws_credential(self) -> None:
        """Initialize AWS boto3 session with automatic credential discovery.

        Discovers credentials from:
        1. Environment variables (AWS_ACCESS_KEY_ID, etc.)
        2. AWS CLI profiles (~/.aws/config)
        3. EC2/ECS instance metadata
        4. AWS SSO

        Raises:
            OSMCPAuthError: If no AWS credentials found
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, ProfileNotFound

            # Create session - boto3 handles credential chain
            self._aws_session = boto3.Session()

            # Verify credentials are available
            credentials = self._aws_session.get_credentials()
            if not credentials:
                raise NoCredentialsError()

            # Get AWS account/region info for logging
            sts = self._aws_session.client("sts")
            identity = sts.get_caller_identity()

            logger.info(
                f"Initialized AWS credentials for account: {identity['Account']}, "
                f"user/role: {identity['Arn']}"
            )

        except ProfileNotFound as e:
            raise OSMCPAuthError(
                f"AWS profile not found: {e}. "
                "Check AWS_PROFILE environment variable or ~/.aws/config"
            )
        except NoCredentialsError:
            raise OSMCPAuthError(
                "AWS credentials not found. "
                "Set up authentication using one of these methods:\n\n"
                "  AWS SSO:\n"
                "    aws sso login --profile <profile-name>\n"
                "    export AWS_PROFILE=<profile-name>\n\n"
                "  Access Keys:\n"
                "    export AWS_ACCESS_KEY_ID=...\n"
                "    export AWS_SECRET_ACCESS_KEY=...\n\n"
                "  For more info: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html"
            )
        except ImportError:
            raise OSMCPAuthError(
                "boto3 library not installed. " "Install with: pip install boto3"
            )

    def _initialize_gcp_credential(self) -> None:
        """Initialize GCP Application Default Credentials.

        Discovers credentials from:
        1. GOOGLE_APPLICATION_CREDENTIALS environment variable
        2. gcloud application-default credentials
        3. Compute Engine/GKE metadata service

        Raises:
            OSMCPAuthError: If no GCP credentials found
        """
        try:
            import google.auth
            from google.auth.exceptions import DefaultCredentialsError

            # Get default credentials with cloud-platform scope
            # This is the broadest GCP scope, equivalent to Azure's /.default
            self._gcp_credentials, self._gcp_project = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )

            logger.info(
                f"Initialized GCP Application Default Credentials "
                f"for project: {self._gcp_project}"
            )

        except DefaultCredentialsError:
            # Provide helpful error message with multiple options
            raise OSMCPAuthError(
                "GCP Application Default Credentials not found. "
                "Set up authentication using one of these methods:\n\n"
                "  Local Development:\n"
                "    gcloud auth application-default login\n\n"
                "  Service Account Key:\n"
                "    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json\n\n"
                "  For more info: https://cloud.google.com/docs/authentication/provide-credentials-adc"
            )
        except ImportError:
            raise OSMCPAuthError(
                "google-auth library not installed. "
                "Install with: pip install google-auth"
            )

    async def get_access_token(self) -> str:
        """Get token from detected provider.

        Returns:
            Raw access token string (without "Bearer " prefix).
            Caller adds "Bearer " when constructing Authorization header.

        Raises:
            OSMCPAuthError: If token retrieval fails
        """
        if self.mode == AuthenticationMode.USER_TOKEN:
            return self._get_user_token()
        elif self.mode == AuthenticationMode.AZURE:
            return await self._get_azure_token()
        elif self.mode == AuthenticationMode.AWS:
            return await self._get_aws_token()
        elif self.mode == AuthenticationMode.GCP:
            return await self._get_gcp_token()

        raise OSMCPAuthError(f"Unsupported authentication mode: {self.mode}")

    def _get_user_token(self) -> str:
        """Get and validate user token from environment.

        Returns:
            OAuth Bearer token string (without "Bearer " prefix)

        Raises:
            OSMCPAuthError: If token not set or invalid
        """
        token = os.environ.get("OSDU_MCP_USER_TOKEN")
        if not token:
            raise OSMCPAuthError(
                "USER_TOKEN mode but OSDU_MCP_USER_TOKEN not set"
            )

        # Validate JWT format
        self._validate_jwt_token(token)

        return token  # Return raw token, "Bearer " added by client

    def _validate_jwt_token(self, token: str) -> None:
        """Validate JWT token format and expiration.

        Security checks:
        1. Valid JWT format (header.payload.signature)
        2. Not expired (if exp claim present)
        3. Warning if expires soon (< 5 minutes)

        Does NOT validate:
        - Signature (already validated by OAuth provider)
        - Audience (OSDU platform validates)
        - Issuer (OSDU platform validates)

        Args:
            token: JWT token to validate

        Raises:
            OSMCPAuthError: If token invalid or expired
        """
        try:
            import jwt

            # Decode without verification (already validated by provider)
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # Already verified by provider
                    "verify_exp": False,  # We check manually below
                    "verify_aud": False,  # OSDU platform validates
                },
            )

            # Check expiration if present
            if "exp" in payload:
                import time as time_module

                exp_timestamp = payload["exp"]
                now_timestamp = time_module.time()

                if now_timestamp > exp_timestamp:
                    raise OSMCPAuthError("Token has expired")

                # Warn if expiring soon (< 5 minutes)
                time_remaining = exp_timestamp - now_timestamp
                if time_remaining < 300:
                    logger.warning(f"Token expires in {time_remaining:.0f} seconds")

            logger.info("User token validation passed")

        except jwt.DecodeError as e:
            raise OSMCPAuthError(f"Invalid JWT token format: {e}")

    async def _get_azure_token(self) -> str:
        """Get Azure access token with automatic refresh.

        Returns:
            Valid Azure access token

        Raises:
            OSMCPAuthError: If authentication fails
        """
        try:
            # Check if we have a cached token that's still valid
            if self._is_azure_token_valid():
                return self._azure_cached_token.token

            # Get client ID from standard Azure environment variable
            client_id = os.environ.get("AZURE_CLIENT_ID")
            if not client_id:
                raise OSMCPAuthError(
                    "AZURE_CLIENT_ID environment variable is required for Azure authentication"
                )

            # Derive OAuth scope from client ID or custom scope
            custom_scope = os.environ.get("OSDU_MCP_AUTH_SCOPE")
            if custom_scope:
                scope = custom_scope
            else:
                scope = f"{client_id}/.default"

            # Get new token
            self._azure_cached_token = self._azure_credential.get_token(scope)
            logger.info("Azure token obtained successfully")
            return self._azure_cached_token.token

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
            elif (
                "invalid_scope" in error_message
                or "scope format is invalid" in error_message
            ):
                raise OSMCPAuthError(
                    "Invalid Azure client ID. Please verify your AZURE_CLIENT_ID is correct"
                )
            elif (
                "no accounts were found" in error_message
                or "environment variables are not fully configured" in error_message
            ):
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
        """Get AWS token for OSDU authentication.

        Note: AWS doesn't use Bearer tokens directly. This method depends
        on how OSDU on AWS expects authentication:
        - Option 1: AWS Cognito (returns JWT Bearer tokens)
        - Option 2: STS tokens (for API Gateway with IAM auth)
        - Option 3: Signed requests (AWS Signature V4)

        For now, we use STS session tokens which can be formatted as pseudo-Bearer tokens.

        Returns:
            Token string appropriate for OSDU on AWS

        Raises:
            OSMCPAuthError: If token retrieval fails
        """
        try:
            # Option 2: Get STS session token (for IAM-based auth)
            sts = self._aws_session.client("sts")

            # Run synchronous boto3 call in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: sts.get_session_token(DurationSeconds=3600)
            )

            # Return session token (OSDU would need to accept this)
            credentials = response["Credentials"]

            # Format as a pseudo-Bearer token for OSDU
            # Real implementation depends on OSDU AWS requirements
            token = credentials["SessionToken"]

            logger.info("AWS session token obtained successfully")
            return token

        except Exception as e:
            raise OSMCPAuthError(f"AWS token retrieval failed: {e}")

    async def _get_gcp_token(self) -> str:
        """Get GCP access token with automatic refresh.

        Returns:
            Valid GCP access token string

        Raises:
            OSMCPAuthError: If token refresh fails
        """
        try:
            from google.auth.exceptions import RefreshError
            from google.auth.transport.requests import Request

            # Check if token needs refresh
            # GCP credentials have .valid property
            if not self._gcp_credentials.valid:
                logger.debug("GCP token invalid/expired, refreshing...")

                # Refresh token (synchronous operation)
                # Run in executor to avoid blocking async event loop
                loop = asyncio.get_event_loop()
                request = Request()

                await loop.run_in_executor(
                    None, self._gcp_credentials.refresh, request
                )

                logger.info("GCP token refreshed successfully")

            # Return the access token string
            token = self._gcp_credentials.token
            if not token:
                raise OSMCPAuthError("GCP token is None after refresh")

            return token

        except RefreshError as e:
            error_msg = str(e).lower()

            if "file not found" in error_msg or "no such file" in error_msg:
                raise OSMCPAuthError(
                    "GCP credentials file not found. "
                    "Check GOOGLE_APPLICATION_CREDENTIALS path"
                )
            elif "invalid" in error_msg or "malformed" in error_msg:
                raise OSMCPAuthError(
                    "GCP credentials invalid. "
                    "Run 'gcloud auth application-default login' to re-authenticate"
                )
            elif "expired" in error_msg:
                raise OSMCPAuthError(
                    "GCP refresh token expired. "
                    "Run 'gcloud auth application-default login' to re-authenticate"
                )
            else:
                raise OSMCPAuthError(f"GCP token refresh failed: {e}")

        except Exception as e:
            raise OSMCPAuthError(f"Unexpected GCP authentication error: {e}")

    async def validate_token(self) -> bool:
        """Validate current token.

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

    def _is_azure_token_valid(self) -> bool:
        """Check if cached Azure token is still valid.

        Returns:
            True if token exists and hasn't expired
        """
        if not self._azure_cached_token:
            return False

        # Add a buffer of 5 minutes before expiration
        expiry_buffer = timedelta(minutes=5)
        token_expiry = datetime.fromtimestamp(self._azure_cached_token.expires_on)
        return datetime.now() < (token_expiry - expiry_buffer)

    def close(self) -> None:
        """Clean up all authentication resources."""
        # Clear Azure resources
        self._azure_cached_token = None
        if self._azure_credential and hasattr(self._azure_credential, "close"):
            self._azure_credential.close()

        # AWS session doesn't need explicit cleanup
        self._aws_session = None

        # GCP credentials don't need explicit cleanup
        self._gcp_credentials = None

        logger.debug("Authentication resources cleaned up")
