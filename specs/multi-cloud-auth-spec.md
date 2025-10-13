# Feature Specification: Multi-Cloud Authentication (Azure, GCP, AWS)

## Overview

Add native multi-cloud authentication support to OSDU MCP Server, enabling AWS, GCP, and other OAuth provider users while maintaining the excellent developer experience Azure users currently enjoy. This specification defines three authentication enhancements: native AWS SDK support, native GCP Application Default Credentials support, and generic OAuth token override capability.

## Goals

1. **Native AWS Support** - First-class AWS authentication with boto3 SDK
2. **Native GCP Support** - First-class GCP authentication with automatic token refresh
3. **Generic OAuth Support** - Fallback for any OAuth provider via environment variable
4. **Consistent UX** - Same developer experience across all cloud providers
5. **Zero API Changes** - No modifications to tool signatures
6. **Standards Compliant** - Follow MCP STDIO guidance and cloud provider best practices
7. **HTTP Ready** - Design compatible with future HTTP transport migration

## Non-Goals

- HTTP transport implementation (future work)
- Token parameter passing (rejected - security risk)
- Custom OAuth flows (use provider SDKs)
- Non-standard cloud providers (use generic OAuth token)

---

## Environment Variable Strategy

### Design Principles

1. **Respect Provider Standards** - Use native variable names for cloud providers
2. **Namespace Custom Variables** - Prefix OSDU-specific variables with `OSDU_MCP_`
3. **Clear Ownership** - Provider variables vs. application variables
4. **SDK Compatibility** - Work with existing cloud tooling

### Variable Naming Convention

**Cloud Provider Variables (Native - No Prefix):**
```bash
# Azure - Used by azure-identity library
AZURE_CLIENT_ID          # Azure app/service principal client ID
AZURE_TENANT_ID          # Azure AD tenant ID
AZURE_CLIENT_SECRET      # Service principal secret (optional)

# GCP - Used by google-auth library
GOOGLE_APPLICATION_CREDENTIALS  # Path to service account key JSON
GOOGLE_CLOUD_PROJECT            # GCP project ID (optional)

# AWS - Used by boto3 library
AWS_ACCESS_KEY_ID              # AWS IAM access key ID
AWS_SECRET_ACCESS_KEY          # AWS IAM secret access key
AWS_SESSION_TOKEN              # Temporary session token (optional)
AWS_PROFILE                    # Named profile from ~/.aws/config (optional)
AWS_REGION                     # AWS region (e.g., us-east-1)
```

**OSDU MCP Variables (Application - Prefixed):**
```bash
# OSDU Platform Configuration
OSDU_MCP_SERVER_URL           # OSDU platform URL
OSDU_MCP_SERVER_DATA_PARTITION # Data partition ID

# Generic OAuth Token Override
OSDU_MCP_USER_TOKEN          # Manual OAuth Bearer token (highest priority - overrides all)
OSDU_MCP_AUTH_SCOPE          # Optional custom OAuth scope (for v1.0 Azure tokens)
```

**Rationale:**
- Native variables work with cloud SDKs automatically
- OSDU_MCP_ prefix clearly identifies application-specific configuration
- No conflicts with standard cloud tooling
- Easy to document and understand

---

## Feature 1: Generic OAuth Token Support

### User Story

**As a developer using a custom OAuth provider**
**I want to provide my OAuth token via environment variable**
**So that I can authenticate to OSDU without Azure/GCP SDKs**

### Use Cases

1. **Non-standard OAuth provider** - Custom corporate OAuth
2. **Testing** - Use specific tokens for testing scenarios
3. **Token debugging** - Inspect behavior with known tokens
4. **Unsupported clouds** - IBM Cloud, Oracle Cloud, etc.

### Configuration

```bash
# Required - provide your OAuth Bearer token
export OSDU_MCP_USER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# OSDU configuration (still required)
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
```

### Behavior

**Token Validation:**
- Validate JWT format (3-part base64 structure)
- Check expiration claim if present
- Warn if token expires soon (< 5 minutes)
- Never log token value

**Error Messages:**
```bash
# Token not set
Error: OSDU_MCP_USER_TOKEN environment variable not set

# Invalid format
Error: OSDU_MCP_USER_TOKEN is not a valid JWT token

# Expired
Error: OSDU_MCP_USER_TOKEN has expired. Please obtain a new token.
```

### Implementation Requirements

```python
class AuthenticationMode(Enum):
    USER_TOKEN = "user_token"  # Manual Bearer token from environment
    AZURE = "azure"            # Azure DefaultAzureCredential
    GCP = "gcp"                # GCP Application Default Credentials
    AWS = "aws"                # AWS boto3 SDK credentials

class AuthHandler:
    def _detect_authentication_mode(self) -> AuthenticationMode:
        """Auto-detect authentication mode with simple priority order.

        Priority:
        1. USER_TOKEN - Always highest priority if set
        2. AZURE - If Azure credentials configured
        3. AWS - If AWS credentials configured (explicit or discovered)
        4. GCP - If GCP credentials configured (explicit or discovered)
        """

        # Priority 1: User token ALWAYS wins if provided
        if os.environ.get("OSDU_MCP_USER_TOKEN"):
            return AuthenticationMode.USER_TOKEN

        # Priority 2: Azure credentials
        if os.environ.get("AZURE_CLIENT_ID") or os.environ.get("AZURE_TENANT_ID"):
            return AuthenticationMode.AZURE

        # Priority 3: AWS credentials (explicit)
        if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
            return AuthenticationMode.AWS

        # Priority 4: GCP credentials (explicit path)
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            return AuthenticationMode.GCP

        # Priority 5: Try AWS auto-discovery (IAM roles, SSO)
        try:
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                return AuthenticationMode.AWS
        except:
            pass

        # Priority 6: Try GCP auto-discovery (gcloud, metadata service)
        try:
            import google.auth
            credentials, _ = google.auth.default()
            return AuthenticationMode.GCP
        except:
            pass

        raise OSMCPAuthError("No authentication credentials found")

    def _get_user_token(self) -> str:
        """Get and validate user token from environment.

        Returns:
            OAuth Bearer token string (without "Bearer " prefix)
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
        """Validate JWT token format and expiration."""
        try:
            import jwt
            from datetime import datetime

            # Decode without verification (already validated by provider)
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False
                }
            )

            # Check expiration if present
            if "exp" in payload:
                exp_time = datetime.fromtimestamp(payload["exp"])
                now = datetime.utcnow()

                if now > exp_time:
                    raise OSMCPAuthError("Token has expired")

                # Warn if expiring soon (< 5 minutes)
                time_remaining = exp_time - now
                if time_remaining.total_seconds() < 300:
                    logger.warning(
                        f"Token expires in {time_remaining.total_seconds():.0f} seconds"
                    )

            logger.info("User token validation passed")

        except jwt.DecodeError as e:
            raise OSMCPAuthError(f"Invalid JWT token format: {e}")
```

---

## Feature 2: Native AWS Authentication

### User Story

**As an AWS developer**
**I want automatic authentication using AWS credentials**
**So that I have the same seamless experience as Azure users**

### Use Cases

1. **Local Development** - Use AWS CLI/SSO authentication
2. **EC2/ECS Deployment** - Use IAM instance roles
3. **Lambda Functions** - Use execution roles
4. **CI/CD** - Use IAM access keys or OIDC federation
5. **Cross-Account** - Use STS AssumeRole

### Configuration

**Local Development (AWS SSO):**
```bash
# One-time setup
aws sso login --profile dev-profile

# Use MCP server
export AWS_PROFILE=dev-profile
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server  # Automatic AWS authentication!
```

**Production (IAM Access Keys):**
```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server
```

**Production (EC2/ECS Instance Role):**
```yaml
# No AWS environment variables needed!
# Uses instance metadata service automatically
containers:
- name: mcp-server
  env:
  - name: OSDU_MCP_SERVER_URL
    value: "https://osdu.example.com"
  - name: OSDU_MCP_SERVER_DATA_PARTITION
    value: "opendes"
```

### Credential Discovery

**AWS SDK (boto3) Discovery Order:**

1. **Environment Variables** - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
2. **AWS Profile** - AWS_PROFILE or default profile
3. **Credentials File** - ~/.aws/credentials
4. **Config File with SSO** - ~/.aws/config with SSO configuration
5. **EC2 Instance Metadata** - When running on EC2
6. **ECS Task Role** - When running on ECS/Fargate
7. **Lambda Execution Role** - When running in Lambda

### Implementation Requirements

```python
class AuthHandler:
    def __init__(self, config: ConfigManager):
        self.config = config

        # Azure credentials
        self._azure_credential: DefaultAzureCredential | None = None
        self._azure_cached_token: AccessToken | None = None

        # AWS credentials
        self._aws_session: boto3.Session | None = None
        self._aws_credentials = None

        # GCP credentials
        self._gcp_credentials = None
        self._gcp_project: str | None = None

        # Detect mode and initialize
        self.mode = self._detect_authentication_mode()
        self._initialize_credential()

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
            sts = self._aws_session.client('sts')
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
                "boto3 library not installed. "
                "Install with: pip install boto3"
            )

    async def _get_aws_token(self) -> str:
        """Get AWS token for OSDU authentication.

        Note: AWS doesn't use Bearer tokens directly. This method depends
        on how OSDU on AWS expects authentication:
        - Option 1: AWS Cognito (returns JWT Bearer tokens)
        - Option 2: STS tokens (for API Gateway with IAM auth)
        - Option 3: Signed requests (AWS Signature V4)

        Returns:
            Token string appropriate for OSDU on AWS

        Raises:
            OSMCPAuthError: If token retrieval fails
        """
        try:
            # Option 1: If OSDU uses Cognito (most likely for Bearer tokens)
            # This would require additional configuration for Cognito pool

            # Option 2: Get STS session token (for IAM-based auth)
            sts = self._aws_session.client('sts')

            # Run synchronous boto3 call in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                sts.get_session_token,
                {'DurationSeconds': 3600}  # 1 hour
            )

            # Return session token (OSDU would need to accept this)
            credentials = response['Credentials']

            # Format as a pseudo-Bearer token for OSDU
            # Real implementation depends on OSDU AWS requirements
            token = credentials['SessionToken']

            logger.info("AWS session token obtained successfully")
            return token

        except Exception as e:
            raise OSMCPAuthError(f"AWS token retrieval failed: {e}")
```

---

## Feature 3: Native GCP Authentication

### User Story

**As a GCP developer**
**I want automatic authentication using Application Default Credentials**
**So that I have the same seamless experience as Azure users**

### Use Cases

1. **Local Development** - Use gcloud CLI authentication
2. **GKE Deployment** - Use workload identity
3. **Cloud Run** - Use service account metadata
4. **CI/CD** - Use service account key file
5. **Testing** - Use gcloud application-default credentials

### Configuration

**Local Development:**
```bash
# One-time setup
gcloud auth application-default login

# Use MCP server
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server  # Automatic GCP authentication!
```

**Production (Service Account Key):**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server
```

**Production (Workload Identity on GKE):**
```yaml
# Kubernetes deployment
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: osdu-mcp-sa  # Linked to GCP service account
  containers:
  - name: mcp-server
    env:
    - name: OSDU_MCP_SERVER_URL
      value: "https://osdu.example.com"
    # GOOGLE_APPLICATION_CREDENTIALS not needed - automatic!
```

### Credential Discovery

**GCP ADC Discovery Order:**

1. **GOOGLE_APPLICATION_CREDENTIALS** - Explicit service account key
2. **gcloud ADC** - Developer credentials from `gcloud auth application-default login`
3. **Compute Engine Metadata** - When running on GCP
4. **Workload Identity** - When running on GKE with service account binding

### Implementation Requirements

```python
class AuthHandler:
    def __init__(self, config: ConfigManager):
        self.config = config

        # Azure credentials
        self._azure_credential: DefaultAzureCredential | None = None
        self._azure_cached_token: AccessToken | None = None

        # GCP credentials
        self._gcp_credentials = None
        self._gcp_project: str | None = None

        # Detect mode and initialize
        self.mode = self._detect_authentication_mode()
        self._initialize_credential()

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
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )

            logger.info(
                f"Initialized GCP Application Default Credentials "
                f"for project: {self._gcp_project}"
            )

        except DefaultCredentialsError as e:
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

    async def _get_gcp_token(self) -> str:
        """Get GCP access token with automatic refresh.

        Returns:
            Valid GCP access token string

        Raises:
            OSMCPAuthError: If token refresh fails
        """
        try:
            from google.auth.transport.requests import Request
            from google.auth.exceptions import RefreshError

            # Check if token needs refresh
            # GCP credentials have .valid property
            if not self._gcp_credentials.valid:
                logger.debug("GCP token invalid/expired, refreshing...")

                # Refresh token (synchronous operation)
                # Run in executor to avoid blocking async event loop
                loop = asyncio.get_event_loop()
                request = Request()

                await loop.run_in_executor(
                    None,
                    self._gcp_credentials.refresh,
                    request
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

    def close(self) -> None:
        """Clean up authentication resources."""
        # Clear Azure resources
        self._azure_cached_token = None
        if self._azure_credential and hasattr(self._azure_credential, "close"):
            self._azure_credential.close()

        # GCP credentials don't need explicit cleanup
        self._gcp_credentials = None
```

---

## Environment Variable Design

### Naming Principles

1. **Use Cloud Provider Native Names** - Respect existing standards
2. **Prefix OSDU-Specific Variables** - Use `OSDU_MCP_` for custom variables
3. **Clear Ownership** - Provider-managed vs. application-managed
4. **SDK Compatibility** - Variables work with standard SDKs

### Variable Reference

#### Azure Native Variables (No Prefix)

```bash
# Used by azure-identity library
AZURE_CLIENT_ID          # Required: Application/Service Principal ID
AZURE_TENANT_ID          # Required: Azure AD tenant ID
AZURE_CLIENT_SECRET      # Optional: For service principal authentication
AZURE_CLIENT_CERTIFICATE_PATH  # Optional: For certificate authentication
```

**Rationale:** These are Azure SDK standard variables. `DefaultAzureCredential` expects them.

#### GCP Native Variables (No Prefix)

```bash
# Used by google-auth library
GOOGLE_APPLICATION_CREDENTIALS  # Path to service account JSON key
GOOGLE_CLOUD_PROJECT           # Optional: GCP project ID
```

**Rationale:** These are GCP SDK standard variables. `google.auth.default()` expects them.

#### OSDU MCP Variables (Prefixed)

```bash
# OSDU Platform Configuration
OSDU_MCP_SERVER_URL           # Required: OSDU platform base URL
OSDU_MCP_SERVER_DATA_PARTITION # Required: Data partition ID

# Authentication Configuration
OSDU_MCP_USER_TOKEN          # Optional: Manual OAuth Bearer token (highest priority)
OSDU_MCP_AUTH_SCOPE          # Optional: Custom OAuth scope for v1.0 Azure tokens

# Security Configuration
OSDU_MCP_ENABLE_WRITE_MODE   # Optional: Enable write operations (default: false)
OSDU_MCP_ENABLE_DELETE_MODE  # Optional: Enable delete operations (default: false)

# Logging Configuration
OSDU_MCP_LOGGING_ENABLED     # Optional: Enable logging (default: false)
OSDU_MCP_LOGGING_LEVEL       # Optional: Log level (default: INFO)
```

**Rationale:** Application-specific variables get consistent OSDU_MCP_ prefix for clarity.

### Authentication Mode Detection

**Priority Order (Automatic):**

```python
def _detect_authentication_mode(self) -> AuthenticationMode:
    """Auto-detect authentication mode with clear, simple priority.

    Priority Order (no overrides, just precedence):
    1. OSDU_MCP_USER_TOKEN (manual token - always highest)
    2. Azure credentials (AZURE_CLIENT_ID or AZURE_TENANT_ID)
    3. AWS explicit (AWS_ACCESS_KEY_ID or AWS_PROFILE)
    4. GCP explicit (GOOGLE_APPLICATION_CREDENTIALS)
    5. AWS auto-discovery (IAM roles, SSO)
    6. GCP auto-discovery (gcloud, metadata)
    7. Error (no credentials found)
    """

    # Priority 1: User token ALWAYS takes precedence
    if os.environ.get("OSDU_MCP_USER_TOKEN"):
        return AuthenticationMode.USER_TOKEN

    # Priority 2: Azure credentials
    if os.environ.get("AZURE_CLIENT_ID") or os.environ.get("AZURE_TENANT_ID"):
        return AuthenticationMode.AZURE

    # Priority 3: AWS explicit credentials
    if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
        return AuthenticationMode.AWS

    # Priority 4: GCP explicit path
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return AuthenticationMode.GCP

    # Priority 5: Try AWS auto-discovery
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            return AuthenticationMode.AWS
    except Exception:
        pass

    # Priority 6: Try GCP auto-discovery
    try:
        import google.auth
        credentials, _ = google.auth.default()
        if credentials:
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
```

---

## Architecture Design

### Token Acquisition Flow

```
┌─────────────────────────────────────────┐
│         Tool Invocation                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      AuthHandler.get_access_token()     │
└──────────────┬──────────────────────────┘
               │
               ▼
       ┌───────┴────────┐
       │ Detect Mode    │
       └───────┬────────┘
               │
       ┌───────┴────────────────────────┐
       │                                │
       ▼                                ▼
┌─────────────┐              ┌──────────────────┐
│ USER_TOKEN  │              │ Cloud Provider   │
└─────────────┘              └──────────────────┘
       │                                │
       ▼                                ▼
┌─────────────────┐      ┌──────────────────────┐
│ Read from env   │      │   Azure: get_token() │
│ OSDU_MCP_USER_  │      │   GCP: refresh()     │
│ TOKEN           │      │                      │
└─────────────────┘      └──────────────────────┘
       │                                │
       └────────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  Return Token    │
         │  (String)        │
         └──────────────────┘
```

### Class Structure

```python
class AuthHandler:
    """Multi-cloud authentication handler.

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
        _aws_credentials: AWS credentials instance
        _gcp_credentials: GCP credentials instance
        _gcp_project: GCP project ID
    """

    def __init__(self, config: ConfigManager):
        """Initialize with automatic mode detection."""
        ...

    # Mode Detection
    def _detect_authentication_mode(self) -> AuthenticationMode:
        """Auto-detect with priority order."""
        ...

    # Credential Initialization
    def _initialize_credential(self) -> None:
        """Initialize provider-specific credential."""
        ...

    def _initialize_azure_credential(self) -> None:
        """Initialize Azure DefaultAzureCredential (existing)."""
        ...

    def _initialize_aws_credential(self) -> None:
        """Initialize AWS boto3 session and credentials (new)."""
        ...

    def _initialize_gcp_credential(self) -> None:
        """Initialize GCP Application Default Credentials (new)."""
        ...

    # Token Acquisition
    async def get_access_token(self) -> str:
        """Get token from detected provider.

        Returns:
            Raw access token string (without "Bearer " prefix).
            Caller adds "Bearer " when constructing Authorization header.
        """
        ...

    async def _get_azure_token(self) -> str:
        """Get Azure token (existing)."""
        ...

    async def _get_gcp_token(self) -> str:
        """Get GCP token with refresh (new)."""
        ...

    def _get_user_token(self) -> str:
        """Get manual token from environment (new)."""
        ...

    # Token Validation
    def _validate_jwt_token(self, token: str) -> None:
        """Validate JWT format and expiration (new)."""
        ...

    # Cleanup
    def close(self) -> None:
        """Clean up all credentials."""
        ...


# Integration point - OsduClient always uses Bearer
class OsduClient:
    """OSDU API client that uses AuthHandler tokens."""

    async def _get_headers(self) -> dict[str, str]:
        """Get headers with Bearer token for OSDU API requests."""
        token = await self.auth.get_access_token()

        return {
            "Authorization": f"Bearer {token}",  # Always Bearer, hard-coded
            "Content-Type": "application/json",
            "data-partition-id": self.data_partition
        }
```

---

## Dependencies

### Current Dependencies

```toml
dependencies = [
    "azure-identity==1.25.1",
    "azure-core==1.35.1",
    "PyJWT>=2.10.1",  # Already added for scope validation
]
```

### New Dependencies

```toml
dependencies = [
    "azure-identity==1.25.1",
    "azure-core==1.35.1",
    "boto3>=1.35.0",            # AWS SDK for Python
    "google-auth>=2.35.0",      # GCP Application Default Credentials
    "PyJWT>=2.10.1",
]
```

**Rationale:**
- `boto3` is the official AWS SDK for Python
- Well-maintained, battle-tested in production
- Provides automatic credential chain discovery
- `google-auth` is the official GCP authentication library
- Lightweight (~500KB), well-maintained
- Same role as `azure-identity` for Azure
- Required for any GCP/AWS client libraries

---

## Tool Impact Analysis

### Tool Signature Changes

**Current and Future (No Changes):**
```python
@handle_osdu_exceptions
async def storage_get_record(
    id: str,
    attributes: list[str] | None = None
) -> dict:
    """Get record by ID.

    Authentication is automatic from environment.
    Supports: Azure, GCP, or manual Bearer token.
    """
    config = ConfigManager()
    auth = AuthHandler(config)  # Auto-detects mode
    client = StorageClient(config, auth)
    ...
```

**No changes to any of the 31 tool signatures!**

### Why No Changes Needed?

**Authentication is encapsulated in AuthHandler:**
- Tools create `AuthHandler(config)`
- AuthHandler auto-detects mode
- AuthHandler provides token
- Tools remain cloud-agnostic

This is **excellent architecture** - tools don't care about cloud providers!

---

## User Documentation

### Azure Users (Existing - No Change)

```bash
# Local development
az login
export AZURE_CLIENT_ID=<osdu-app-id>

# Production
export AZURE_CLIENT_ID=<app-id>
export AZURE_TENANT_ID=<tenant-id>
export AZURE_CLIENT_SECRET=<secret>

# Run server
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server
```

### AWS Users (New)

```bash
# Local development (AWS SSO)
aws sso login --profile dev-profile
export AWS_PROFILE=dev-profile

# Production (IAM Access Keys)
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1

# Production (EC2/ECS Instance Role)
# No environment variables needed!

# Run server
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server
```

### GCP Users (New)

```bash
# Local development
gcloud auth application-default login

# Production (Service Account Key)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Production (GKE Workload Identity)
# No environment variables needed!

# Run server
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server
```

### Generic OAuth Users (New)

```bash
# Obtain Bearer token using your OAuth provider
TOKEN=$(your-oauth-command)

# Set token (must be a valid OAuth Bearer token)
export OSDU_MCP_USER_TOKEN="$TOKEN"

# Run server
export OSDU_MCP_SERVER_URL="https://osdu.example.com"
export OSDU_MCP_SERVER_DATA_PARTITION="opendes"
osdu-mcp-server

# Note: Bearer token expires - you'll need to refresh manually
```

---

## Error Handling

### Clear Error Messages by Scenario

**No Credentials Found:**
```
Error: No authentication credentials configured. Set up one of:

  Azure (Automatic):
    az login
    OR export AZURE_CLIENT_ID=... AZURE_TENANT_ID=...

  AWS (Automatic):
    aws sso login
    OR export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...

  GCP (Automatic):
    gcloud auth application-default login
    OR export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

  Manual Token (Any Provider):
    export OSDU_MCP_USER_TOKEN=your-token

  See: https://github.com/danielscholl-osdu/osdu-mcp-server#authentication
```

**AWS Credentials Not Found:**
```
Error: AWS credentials not found.

Set up authentication using one of these methods:

  AWS SSO:
    aws sso login --profile <profile-name>
    export AWS_PROFILE=<profile-name>

  Access Keys:
    export AWS_ACCESS_KEY_ID=...
    export AWS_SECRET_ACCESS_KEY=...

  For more info: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html
```

**GCP Credentials Not Found:**
```
Error: GCP Application Default Credentials not found.

Set up authentication using one of these methods:

  Local Development:
    gcloud auth application-default login

  Service Account Key:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

  For more info: https://cloud.google.com/docs/authentication/provide-credentials-adc
```

**Token Expired:**
```
Error: Authentication token has expired.

Azure: Run 'az login' to refresh
AWS: Run 'aws sso login' to refresh
GCP: Run 'gcloud auth application-default login' to refresh
Manual: Set new OSDU_MCP_USER_TOKEN
```

---

## Testing Strategy

### Unit Tests

**Test Coverage:**
```python
# test_auth_handler_multicloud.py

@pytest.mark.asyncio
async def test_gcp_mode_detection_from_env():
    """Test GCP mode detection when GOOGLE_APPLICATION_CREDENTIALS is set."""
    with patch.dict(os.environ, {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"
    }, clear=True):
        config = ConfigManager()
        auth = AuthHandler(config)
        assert auth.mode == AuthenticationMode.GCP

@pytest.mark.asyncio
async def test_user_token_mode_detection():
    """Test USER_TOKEN mode has highest priority."""
    with patch.dict(os.environ, {
        "OSDU_MCP_USER_TOKEN": "eyJhbGc...",
        "AZURE_CLIENT_ID": "azure-id",  # Should be ignored
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"  # Should be ignored
    }):
        config = ConfigManager()
        auth = AuthHandler(config)
        assert auth.mode == AuthenticationMode.USER_TOKEN

@pytest.mark.asyncio
async def test_gcp_token_retrieval_with_refresh():
    """Test GCP token retrieval with automatic refresh."""
    with patch("google.auth.default") as mock_default:
        mock_creds = MagicMock()
        mock_creds.valid = False  # Needs refresh
        mock_creds.token = "gcp-token-123"
        mock_default.return_value = (mock_creds, "test-project")

        auth = AuthHandler(config)
        token = await auth.get_access_token()

        assert token == "gcp-token-123"
        mock_creds.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_user_token_validation():
    """Test user token JWT validation."""
    valid_token = create_test_jwt(exp=time.time() + 3600)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": valid_token}):
        auth = AuthHandler(config)
        token = await auth.get_access_token()
        assert token == valid_token

@pytest.mark.asyncio
async def test_user_token_expiration_check():
    """Test expired user token is rejected."""
    expired_token = create_test_jwt(exp=time.time() - 3600)

    with patch.dict(os.environ, {"OSDU_MCP_USER_TOKEN": expired_token}):
        auth = AuthHandler(config)
        with pytest.raises(OSMCPAuthError, match="expired"):
            await auth.get_access_token()
```

### Integration Tests

```python
# test_multicloud_integration.py

@pytest.mark.asyncio
async def test_health_check_with_gcp_credentials():
    """Test health check works with GCP authentication."""
    with patch("google.auth.default") as mock_gcp:
        setup_mock_gcp_credentials(mock_gcp)

        result = await health_check(include_auth=True)

        assert result["authentication"]["status"] == "valid"
        assert result["connectivity"] == "success"

@pytest.mark.asyncio
async def test_storage_operations_with_user_token():
    """Test storage operations work with manual token."""
    with patch.dict(os.environ, {
        "OSDU_MCP_USER_TOKEN": create_valid_test_token()
    }):
        with aioresponses() as mocked:
            setup_mock_storage_responses(mocked)

            result = await storage_get_record(id="test-record")
            assert result["success"] is True
```

---

## Security Requirements

### Token Handling

**Must Never:**
- ❌ Log tokens in plaintext
- ❌ Include tokens in error messages
- ❌ Pass tokens as function parameters (except internal)
- ❌ Store tokens in files without encryption

**Must Always:**
- ✅ Validate token format (JWT structure)
- ✅ Check token expiration
- ✅ Use secure credential storage (provider SDKs)
- ✅ Sanitize logs to remove token patterns

### Token Validation (USER_TOKEN Mode)

```python
def _validate_jwt_token(self, token: str) -> None:
    """Validate user-provided JWT Bearer token.

    Security checks:
    1. Valid JWT format (header.payload.signature)
    2. Not expired (if exp claim present)
    3. Warning if expires soon (< 5 minutes)

    Does NOT validate:
    - Signature (already validated by OAuth provider)
    - Audience (OSDU platform validates)
    - Issuer (OSDU platform validates)
    - Token type (always assumed to be Bearer)
    """
    try:
        import jwt

        # Decode without signature verification
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,  # Already verified by provider
                "verify_exp": False,        # We check manually below
                "verify_aud": False         # OSDU platform validates
            }
        )

        # Check expiration
        if "exp" in payload:
            from datetime import datetime
            exp_time = datetime.fromtimestamp(payload["exp"])
            now = datetime.utcnow()

            if now > exp_time:
                raise OSMCPAuthError(
                    "Token has expired. Please obtain a new token."
                )

            # Warn if expiring soon
            seconds_remaining = (exp_time - now).total_seconds()
            if seconds_remaining < 300:  # Less than 5 minutes
                logger.warning(
                    f"Token expires in {int(seconds_remaining)} seconds. "
                    "Consider refreshing soon."
                )

        # Log successful validation (no token value!)
        logger.info("User token validation passed")

    except jwt.DecodeError as e:
        raise OSMCPAuthError(
            f"Invalid JWT token format: {e}. "
            "Ensure OSDU_MCP_USER_TOKEN is a valid JWT."
        )
```

---

## HTTP Transport Compatibility

### Current STDIO Design
```
User sets environment → AuthHandler detects → Gets token → Uses for OSDU API
```

### Future HTTP Design
```
User authenticates via OAuth → Client gets token → Sends in Authorization header
→ Server validates → Uses for OSDU API
```

### Making Code Transport-Agnostic

**Key insight:** Separate "get token" from "validate token"

```python
class AuthHandler:
    # STDIO mode - GET tokens
    async def get_access_token(self) -> str:
        """Get token from environment/SDK (STDIO transport)."""
        ...

    # HTTP mode - VALIDATE tokens (future)
    async def validate_token(self, token: str, required_audience: str) -> dict:
        """Validate OAuth token from HTTP header (HTTP transport).

        Args:
            token: Bearer token from Authorization header
            required_audience: Expected audience claim

        Returns:
            Decoded token claims

        Raises:
            OSMCPAuthError: If token invalid
        """
        # Verify signature, audience, issuer, expiration
        # This is for future HTTP transport
        ...
```

**Benefits:**
- STDIO: Use `get_access_token()`
- HTTP: Use `validate_token()`
- Same class supports both transports!

---

## Acceptance Criteria

### Functional Requirements

- [ ] AWS boto3 SDK credentials supported
- [ ] Auto-detects AWS credentials (access keys, profiles, IAM roles)
- [ ] AWS credential chain discovery working
- [ ] GCP Application Default Credentials supported
- [ ] Auto-detects GCP credentials (GOOGLE_APPLICATION_CREDENTIALS or gcloud)
- [ ] GCP tokens auto-refresh when expired
- [ ] Manual token mode via OSDU_MCP_USER_TOKEN
- [ ] Token validation (format, expiration) for manual tokens
- [ ] Clear error messages for each authentication method
- [ ] Mode detection follows documented priority order
- [ ] Backward compatible with existing Azure deployments
- [ ] No changes to any tool signatures

### Non-Functional Requirements

- [ ] Performance: Token refresh < 100ms
- [ ] Zero breaking changes to existing API
- [ ] No impact on Azure users
- [ ] Token never logged in plaintext
- [ ] Comprehensive error messages with actionable guidance

### Security Requirements

- [ ] JWT token validation for manual tokens
- [ ] Token expiration checking
- [ ] Secure credential storage (provider SDKs)
- [ ] No tokens in logs, errors, or traces
- [ ] Provider-specific error handling

### Documentation Requirements

- [ ] README updated with AWS, GCP, and manual token auth
- [ ] Environment variable reference table
- [ ] Setup guides for Azure, AWS, GCP, and manual token
- [ ] Migration guide from Azure-only to multi-cloud
- [ ] Troubleshooting section for authentication errors

---

## Implementation Steps

### Step 1: Add AWS and GCP Dependencies

```bash
# Add to pyproject.toml
dependencies = [
    "boto3>=1.35.0",       # AWS SDK
    "google-auth>=2.35.0", # GCP ADC
]

# Install
uv sync
```

### Step 2: Enhance AuthHandler

1. Add `AuthenticationMode.USER_TOKEN`, `AuthenticationMode.AWS`, and `AuthenticationMode.GCP`
2. Add AWS and GCP credential attributes to `__init__`
3. Implement `_initialize_aws_credential()`
4. Implement `_initialize_gcp_credential()`
5. Implement `_get_aws_token()` with async wrapper
6. Implement `_get_gcp_token()` with async wrapper
7. Implement `_get_user_token()` with validation
8. Update `_detect_authentication_mode()` with priority order
9. Update `close()` to handle all credential types

### Step 3: Add Token Validation

1. Implement `_validate_jwt_token()` helper
2. Add expiration checking
3. Add format validation
4. Add security: never log tokens

### Step 4: Update Documentation

1. Update README with AWS, GCP, and manual token sections
2. Add environment variable reference
3. Create setup guides for each method (Azure, AWS, GCP, manual)
4. Add troubleshooting section

### Step 5: Testing

1. Unit tests for mode detection
2. Unit tests for AWS credential discovery
3. Unit tests for GCP token retrieval
4. Unit tests for user token validation
5. Integration tests for each authentication mode
6. Test with real AWS credentials
7. Test with real GCP credentials

---

## Migration Plan

### Existing Deployments (Azure)

**No changes required!**

```bash
# Current setup continues to work
export AZURE_CLIENT_ID=...
export AZURE_TENANT_ID=...
osdu-mcp-server  # Still works!
```

### New AWS Deployments

```bash
# AWS users get same experience
aws sso login --profile dev
export AWS_PROFILE=dev
osdu-mcp-server  # Just works!
```

### New GCP Deployments

```bash
# GCP users get same experience
gcloud auth application-default login
osdu-mcp-server  # Just works!
```

### Testing/Development

```bash
# Can test with any OAuth token
export OSDU_MCP_USER_TOKEN="$(get-token-from-anywhere)"
osdu-mcp-server
```

---

## Future Enhancements (Out of Scope)

### HTTP Transport with OAuth 2.1

**Separate specification needed for:**
- FastAPI HTTP server
- OAuth resource server endpoints
- WWW-Authenticate headers
- Token validation (signature, audience)
- Protected Resource Metadata

---

## Comparison to PR #113

### What PR #113 Proposes

- Add `user_token` parameter to all 31 tools
- Pass token in every function call
- No auto-refresh, no native providers

### What This Spec Proposes

- Add `OSDU_MCP_USER_TOKEN` environment variable
- Add native GCP Application Default Credentials
- Auto-refresh, clean API, standards-compliant

### Why This Is Better

| Aspect | PR #113 | This Spec |
|--------|---------|-----------|
| **Security** | ❌ Tokens in parameters | ✅ Environment/SDK |
| **UX** | ❌ Manual every call | ✅ Automatic |
| **API** | ❌ 31 tools changed | ✅ Zero tools changed |
| **Auto-refresh** | ❌ No | ✅ Yes (GCP/Azure) |
| **Standards** | ❌ Non-compliant | ✅ Best practice |
| **Production** | ❌ Not sustainable | ✅ Production-ready |

---

## Summary

### Problem
AWS and GCP users can't use OSDU MCP Server (Azure-only authentication)

### Solution
1. **Native AWS SDK** - Automatic credentials via boto3
2. **Native GCP ADC** - Automatic credentials like Azure has
3. **OSDU_MCP_USER_TOKEN** - Fallback for any OAuth provider (Bearer tokens only)

### Benefits
- ✅ AWS developers get first-class support
- ✅ GCP developers get first-class support
- ✅ Any OAuth provider supported (fallback)
- ✅ Zero tool changes (clean API)
- ✅ Auto-refresh for Azure and GCP
- ✅ Credential chain discovery for AWS
- ✅ Standards-compliant (MCP STDIO, OAuth best practices)
- ✅ HTTP transport compatible (future)

### Implementation
- ~5 hours development (additional AWS integration)
- ~3 hours testing (all three providers)
- ~1.5 hours documentation
- **Total: ~9.5 hours**

### Dependencies
- `boto3>=1.35.0` (AWS SDK)
- `google-auth>=2.35.0` (~500KB)
- `PyJWT>=2.10.1` (already have)

---

## Recommendation

**Implement this specification instead of PR #113.**

This provides:
- Better security (environment-based)
- Better UX (automatic for GCP)
- Better code (no API pollution)
- Better standards compliance (MCP + OAuth)
- Better long-term architecture (HTTP compatible)

**PR #113 feedback:**
"Thank you for identifying the multi-cloud authentication gap! However, passing tokens as parameters has security and UX concerns. We're implementing native GCP Application Default Credentials support instead, which provides the same automatic experience as Azure users have. We'll also add OSDU_MCP_USER_TOKEN environment variable as a fallback for any OAuth provider."
