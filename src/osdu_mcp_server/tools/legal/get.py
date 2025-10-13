"""Tool for getting a specific legal tag."""

import logging

from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.config_manager import ConfigManager
from ...shared.exceptions import handle_osdu_exceptions

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_get(name: str, user_token: str | None = None) -> dict:
    """Retrieve a specific legal tag by name.

    Args:
        name: Name of the legal tag (can include partition prefix or not)
        user_token: Optional user-provided token to use for this request.

    Returns:
        Dictionary containing legal tag details with the following structure:
        {
            "success": true,
            "legalTag": {
                "name": "opendes-Private-USA-EHC",
                "description": "Private data for USA with EHC compliance",
                "properties": {...}
            },
            "fullName": "opendes-Private-USA-EHC",
            "simplifiedName": "Private-USA-EHC",
            "partition": "opendes"
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config, user_token=user_token)
    client = LegalClient(config, auth)

    try:
        # Get current partition
        partition = config.get("server", "data_partition")

        # Get legal tag
        response = await client.get_legal_tag(name)

        # Extract tag data
        tag = response
        full_name = tag.get("name", name)

        # Build response
        result = {
            "success": True,
            "legalTag": tag,
            "fullName": full_name,
            "simplifiedName": client.simplify_tag_name(full_name),
            "partition": partition,
        }

        logger.info(
            "Retrieved legal tag successfully",
            extra={"name": name, "full_name": full_name, "partition": partition},
        )

        return result

    finally:
        await client.close()
