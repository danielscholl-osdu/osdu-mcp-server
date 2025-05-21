"""Tool for fetching multiple records at once."""

from typing import Dict, List, Optional

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_fetch_records(
    records: List[str],
    attributes: Optional[List[str]] = None
) -> Dict:
    """Retrieve multiple records at once.

    Args:
        records: Required array of strings - Record IDs (max 100)
        attributes: Optional array of strings - Specific data fields to return

    Returns:
        Dictionary containing multiple records with the structure:
        {
            "success": true,
            "records": [
                {
                    "id": str,
                    "kind": str,
                    "version": int,
                    "data": {...},
                    ...
                },
                ...
            ],
            "count": int,
            "invalidRecords": [str, ...],
            "partition": str
        }
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)

    try:
        # Fetch multiple records
        response = await client.fetch_records(records, attributes)

        # Build response
        result = {
            "success": True,
            "records": response.get("records", []),
            "count": len(response.get("records", [])),
            "invalidRecords": response.get("invalidRecords", []),
            "partition": config.get("server", "data_partition")
        }

        # Include retry records if present
        if "retryRecords" in response:
            result["retryRecords"] = response["retryRecords"]

        logger.info(
            f"Fetched {result['count']} records out of {len(records)} requested",
            extra={
                "requested_count": len(records),
                "fetched_count": result["count"],
                "invalid_count": len(result["invalidRecords"]),
                "operation": "fetch_records",
                "has_attributes": bool(attributes)
            }
        )

        return result

    finally:
        await client.close()
