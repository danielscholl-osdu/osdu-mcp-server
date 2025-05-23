"""Tool for creating legal tags (write-protected)."""

import logging
import os
from typing import Any

from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import OSMCPAPIError, handle_osdu_exceptions

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_create(
    name: str,
    description: str,
    country_of_origin: list[str],
    contract_id: str,
    security_classification: str,
    personal_data: str,
    export_classification: str,
    data_type: str,
    expiration_date: str | None = None,
    extension_properties: dict[str, Any] | None = None,
) -> dict:
    """Create a new legal tag.

    Args:
        name: Legal tag name (without partition prefix)
        description: Tag description
        country_of_origin: ISO country codes
        contract_id: Associated contract ID
        security_classification: Security level
        personal_data: Personal data type
        export_classification: Export classification control number
        data_type: Type of data
        expiration_date: Optional expiration date (YYYY-MM-DD format)
        extension_properties: Optional custom properties

    Returns:
        Dictionary containing created legal tag

    Note: Requires OSDU_MCP_ENABLE_WRITE_MODE=true
    """
    # Check write protection
    if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
        raise OSMCPAPIError(
            "Legal tag write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable write operations",
            status_code=403,
        )

    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)

    try:
        # Get current partition
        partition = config.get("server", "data_partition")

        # Build properties
        properties = {
            "countryOfOrigin": country_of_origin,
            "contractId": contract_id,
            "securityClassification": security_classification,
            "personalData": personal_data,
            "exportClassification": export_classification,
            "dataType": data_type,
        }

        if expiration_date:
            properties["expirationDate"] = expiration_date

        if extension_properties:
            properties["extensionProperties"] = extension_properties

        # Create legal tag
        response = await client.create_legal_tag(
            name=name, description=description, properties=properties
        )

        # Extract tag data
        tag = response

        # Build response
        result = {
            "success": True,
            "legalTag": tag,
            "created": True,
            "write_enabled": True,
            "partition": partition,
        }

        logger.info(
            "Legal tag created",
            extra={
                "operation": "create_legal_tag",
                "tag_name": name,
                "partition": partition,
                "destructive": False,
                "permanent": False,
            },
        )

        return result

    finally:
        await client.close()
