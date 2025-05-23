"""Health check tool for OSDU MCP Server.

This module implements the health check tool as defined in ADR-007.
"""

from typing import Any

from ..shared.auth_handler import AuthHandler
from ..shared.config_manager import ConfigManager
from ..shared.exceptions import handle_osdu_exceptions
from ..shared.osdu_client import OsduClient
from ..shared.service_urls import OSMCPService, get_service_info_endpoint
from ..shared.utils import get_timestamp


@handle_osdu_exceptions(default_message="Health check failed")
async def health_check(
    include_services: bool = True,
    include_auth: bool = True,
    include_version_info: bool = False,
) -> dict[str, Any]:
    """Check OSDU platform connectivity and service health.

    Args:
        include_services: Test individual service availability
        include_auth: Validate authentication
        include_version_info: Include service version information

    Returns:
        Health status of OSDU connection and services
    """
    # Initialize components
    config = ConfigManager()
    auth_handler = AuthHandler(config)
    client = OsduClient(config, auth_handler)

    result = {
        "connectivity": "pending",
        "server_url": config.get_required("server", "url"),
        "data_partition": config.get_required("server", "data_partition"),
        "timestamp": get_timestamp(),
    }

    try:
        # Check authentication if requested
        if include_auth:
            auth_valid = await auth_handler.validate_token()
            result["authentication"] = {"status": "valid" if auth_valid else "invalid"}

        # Check services if requested
        if include_services:
            services_status = await _check_services(client, include_version_info)
            result["services"] = services_status

        # If we get here, connectivity is successful
        result["connectivity"] = "success"

    except Exception as e:
        result["connectivity"] = "failed"
        result["error"] = str(e)
        raise

    finally:
        # Clean up resources
        await client.close()
        auth_handler.close()

    return result


async def _check_services(
    client: OsduClient, include_versions: bool = False
) -> dict[str, str]:
    """Check individual OSDU service health.

    Args:
        client: OSDU client instance
        include_versions: Include version information

    Returns:
        Dictionary of service health status
    """
    # Check all defined OSDU services
    services = list(OSMCPService)
    health_status = {}
    version_info = {}

    for service in services:
        try:
            # Get the correct info endpoint for each service
            endpoint = get_service_info_endpoint(service)
            response = await client.get(endpoint)

            # Service is healthy if we get a response
            health_status[service.value] = "healthy"

            # Extract version if requested
            if include_versions and "version" in response:
                version_info[f"{service.value}_service"] = response["version"]

        except Exception as e:
            # Mark service as unhealthy if request fails
            health_status[service.value] = f"unhealthy: {str(e)}"
            # TODO: Add logging here to debug the actual error

    # Add version info to result if collected
    if include_versions and version_info:
        health_status["version_info"] = version_info

    return health_status
