"""Tool for creating or updating records."""

from typing import Dict, List
import logging

from ...shared.config_manager import ConfigManager
from ...shared.auth_handler import AuthHandler
from ...shared.clients.storage_client import StorageClient
from ...shared.exceptions import handle_osdu_exceptions
from ...shared.logging_manager import get_logger

logger = get_logger(__name__)


@handle_osdu_exceptions
async def storage_create_update_records(
    records: List[Dict],
    skip_dupes: bool = False
) -> Dict:
    """Create new records or update existing ones.
    
    Args:
        records: Array of records to create or update. Each record must contain:
            - kind: Required string - Kind of data 
            - acl: Required object - Access control lists
              - viewers: Required array - Groups with read access
              - owners: Required array - Groups with write access
            - legal: Required object - Legal information
              - legaltags: Required array - Legal tag names
              - otherRelevantDataCountries: Required array - Relevant countries
            - data: Required object - Record payload
            Optional fields include:
            - id: Optional string - Record ID (generated if not provided)
            - ancestry: Optional object - Parent record references
            - meta: Optional array - Additional metadata
            - tags: Optional object - User-defined tags
        skip_dupes: Optional boolean - Skip duplicates when updating (default: false)
    
    Returns:
        Dictionary containing created/updated record information with the structure:
        {
            "success": true,
            "recordCount": int,
            "records": [
                {
                    "id": str,
                    "kind": str,
                    "version": int
                }
            ],
            "created": bool,
            "write_enabled": bool,
            "partition": str
        }
    
    Note: Requires OSDU_MCP_ENABLE_WRITE_MODE=true
    """
    config = ConfigManager()
    auth = AuthHandler(config)
    client = StorageClient(config, auth)
    
    try:
        # Create or update records
        response = await client.create_update_records(records, skip_dupes)
        
        # Build response in MCP format
        result = {
            "success": True,
            "recordCount": response.get("recordCount", len(records)),
            "records": [],
            "created": True,
            "write_enabled": True,
            "partition": config.get("server", "data_partition")
        }
        
        # Transform the OSDU response to our format
        record_ids = response.get("recordIds", [])
        record_versions = response.get("recordIdVersions", [])
        
        for i, record_id in enumerate(record_ids):
            record_info = {
                "id": record_id,
                "kind": records[i].get("kind", "unknown") if i < len(records) else "unknown"
            }
            
            # Add version if available
            if i < len(record_versions):
                record_info["version"] = record_versions[i]
            
            result["records"].append(record_info)
        
        # Handle skipped records if any
        skipped_records = response.get("skippedRecordIds", [])
        if skipped_records:
            result["skippedRecords"] = skipped_records
        
        logger.info(
            f"Successfully created/updated {len(record_ids)} records",
            extra={
                "record_count": len(record_ids),
                "operation": "create_update_records",
                "skipped_count": len(skipped_records)
            }
        )
        
        return result
        
    finally:
        await client.close()