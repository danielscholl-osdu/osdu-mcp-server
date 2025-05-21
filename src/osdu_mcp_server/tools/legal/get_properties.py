"""Tool for getting allowed property values for legal tags."""

from typing import Dict
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.legal_client import LegalClient
from ...shared.exceptions import (
    handle_osdu_exceptions
)

logger = logging.getLogger(__name__)


@handle_osdu_exceptions
async def legaltag_get_properties() -> Dict:
    """Get allowed values for legal tag properties.
    
    Returns:
        Dictionary containing allowed property values with the following structure:
        {
            "success": true,
            "properties": {
                "countriesOfOrigin": {
                    "US": "United States",
                    "GB": "United Kingdom",
                    ...
                },
                "otherRelevantDataCountries": {...},
                "securityClassifications": [
                    "Private",
                    "Public",
                    "Confidential"
                ],
                "exportClassificationControlNumbers": [
                    "No License Required",
                    "EAR99",
                    ...
                ],
                "personalDataTypes": [
                    "Personally Identifiable",
                    "No Personal Data"
                ],
                "dataTypes": [
                    "Public Domain Data",
                    "First Party Data",
                    ...
                ]
            }
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = LegalClient(config, auth)
    
    try:
        # Get properties
        response = await client.get_legal_tag_properties()
        
        # Build response
        result = {
            "success": True,
            "properties": response
        }
        
        logger.info("Retrieved legal tag properties successfully")
        
        return result
        
    finally:
        await client.close()