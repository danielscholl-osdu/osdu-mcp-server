"""OSDU Storage service client."""

import os
from typing import Dict, Any, List, Optional

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError, OSMCPValidationError
from ..logging_manager import get_logger

logger = get_logger(__name__)


class StorageClient(OsduClient):
    """Client for OSDU Storage service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize StorageClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.STORAGE)
    
    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override get to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().get(full_path, **kwargs)
    
    async def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override post to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().post(full_path, **kwargs)
    
    async def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override put to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().put(full_path, **kwargs)
    
    async def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override delete to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().delete(full_path, **kwargs)
    
    def validate_record(self, record: Dict[str, Any]) -> None:
        """Validate basic record structure.
        
        Args:
            record: Record to validate
            
        Raises:
            OSMCPValidationError: If record validation fails
        """
        required_fields = ["kind", "acl", "legal", "data"]
        for field in required_fields:
            if field not in record:
                raise OSMCPValidationError(
                    f"Missing required field '{field}' in record. Records must contain: {', '.join(required_fields)}"
                )
        
        # Validate ACL
        if "acl" in record:
            acl = record["acl"]
            if not isinstance(acl, dict):
                raise OSMCPValidationError(
                    "ACL must be an object. Access control lists must be dictionary objects"
                )
            if "viewers" not in acl or "owners" not in acl:
                raise OSMCPValidationError(
                    "ACL must contain both 'viewers' and 'owners' arrays. Access control lists define who can read and modify the record"
                )
            if not isinstance(acl["viewers"], list) or not isinstance(acl["owners"], list):
                raise OSMCPValidationError(
                    "ACL viewers and owners must be arrays. Access control lists must contain arrays of group names"
                )
        
        # Validate Legal
        if "legal" in record:
            legal = record["legal"]
            if not isinstance(legal, dict):
                raise OSMCPValidationError(
                    "Legal must be an object. Legal information must be a dictionary object"
                )
            if "legaltags" not in legal or "otherRelevantDataCountries" not in legal:
                raise OSMCPValidationError(
                    "Legal must contain both 'legaltags' and 'otherRelevantDataCountries' arrays. Legal information is required for compliance"
                )
            if not isinstance(legal["legaltags"], list) or not isinstance(legal["otherRelevantDataCountries"], list):
                raise OSMCPValidationError(
                    "Legal legaltags and otherRelevantDataCountries must be arrays. Legal information must contain arrays of strings"
                )
    
    def check_write_permission(self) -> None:
        """Check if write operations are enabled.
        
        Raises:
            OSMCPAPIError: If write operations are disabled
        """
        if not os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true":
            raise OSMCPAPIError(
                "Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable record creation and updates",
                status_code=403
            )
            
    def check_delete_permission(self) -> None:
        """Check if delete operations are enabled.
        
        Raises:
            OSMCPAPIError: If delete operations are disabled
        """
        if not os.environ.get("OSDU_MCP_ENABLE_DELETE_MODE", "false").lower() == "true":
            raise OSMCPAPIError(
                "Delete operations are disabled. Set OSDU_MCP_ENABLE_DELETE_MODE=true to enable record deletion",
                status_code=403
            )
    
    async def create_update_records(self, records: List[Dict[str, Any]],
                                    skip_dupes: bool = False) -> Dict[str, Any]:
        """Create or update records.
        
        Args:
            records: List of records to create or update
            skip_dupes: Skip duplicates when updating (default: False)
            
        Returns:
            Dictionary containing operation results
        """
        # Validate records
        for i, record in enumerate(records):
            try:
                self.validate_record(record)
            except OSMCPValidationError as e:
                raise OSMCPValidationError(
                    f"Record {i + 1} validation failed: {e}"
                )
        
        # Check write permission for create/update operations
        self.check_write_permission()
        
        params = {}
        if skip_dupes:
            params["skipdupes"] = "true"
        
        logger.info(
            f"Creating/updating {len(records)} records",
            extra={
                "record_count": len(records),
                "operation": "create_update_records",
                "has_ids": any(record.get("id") for record in records),
                "skip_dupes": skip_dupes
            }
        )
        
        return await self.put("/records", json=records, params=params)
    
    async def get_record(self, id: str, attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get the latest version of a record by ID.
        
        Args:
            id: Record ID
            attributes: Optional data fields to return
            
        Returns:
            Dictionary containing record information
        """
        params = {}
        if attributes:
            params["attribute"] = attributes
        
        logger.info(
            f"Retrieving record {id}",
            extra={
                "record_id": id,
                "operation": "get_record",
                "attributes": attributes
            }
        )
        
        return await self.get(f"/records/{id}", params=params)
    
    async def get_record_version(self, id: str, version: int,
                                     attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific version of a record by ID.
        
        Args:
            id: Record ID
            version: Record version
            attributes: Optional data fields to return
            
        Returns:
            Dictionary containing record information
        """
        params = {}
        if attributes:
            params["attribute"] = attributes
        
        logger.info(
            f"Retrieving record {id} version {version}",
            extra={
                "record_id": id,
                "version": version,
                "operation": "get_record_version",
                "attributes": attributes
            }
        )
        
        return await self.get(f"/records/{id}/{version}", params=params)
    
    async def list_record_versions(self, id: str) -> Dict[str, Any]:
        """List all versions of a record.
        
        Args:
            id: Record ID
            
        Returns:
            Dictionary containing list of versions
        """
        logger.info(
            f"Listing versions for record {id}",
            extra={
                "record_id": id,
                "operation": "list_record_versions"
            }
        )
        
        return await self.get(f"/records/versions/{id}")
    
    async def query_records_by_kind(self, kind: str, limit: int = 10,
                                       cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get record IDs of a specific kind.
        
        Args:
            kind: Kind to query for
            limit: Maximum number of results (default: 10)
            cursor: Pagination cursor
            
        Returns:
            Dictionary containing record IDs and pagination info
        """
        params = {"kind": kind, "limit": str(limit)}
        if cursor:
            params["cursor"] = cursor
        
        logger.info(
            f"Querying records by kind {kind}",
            extra={
                "kind": kind,
                "limit": limit,
                "operation": "query_records_by_kind",
                "has_cursor": bool(cursor)
            }
        )
        
        return await self.get("/query/records", params=params)
    
    async def fetch_records(self, record_ids: List[str],
                                attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve multiple records at once.
        
        Args:
            record_ids: List of record IDs
            attributes: Optional data fields to return
            
        Returns:
            Dictionary containing multiple records
        """
        if len(record_ids) > 100:
            raise OSMCPValidationError(
                "Too many record IDs requested. Maximum 100 records can be fetched at once. Split the request into smaller batches"
            )
        
        body = {"records": record_ids}
        if attributes:
            body["attributes"] = attributes
        
        logger.info(
            f"Fetching {len(record_ids)} records",
            extra={
                "record_count": len(record_ids),
                "operation": "fetch_records",
                "attributes": attributes
            }
        )
        
        return await self.post("/query/records", json=body)
    
    async def delete_record(self, id: str) -> Dict[str, Any]:
        """Logically delete a record.
        
        Args:
            id: Record ID to delete
            
        Returns:
            Dictionary containing deletion confirmation
        """
        # Check delete permission for delete operations
        self.check_delete_permission()
        
        logger.warning(
            f"Deleting record {id}",
            extra={
                "record_id": id,
                "operation": "delete_record",
                "destructive": True
            }
        )
        
        return await self.post(f"/records/{id}:delete")
    
    async def purge_record(self, id: str, confirm: bool = False) -> Dict[str, Any]:
        """Physically delete a record permanently.
        
        Args:
            id: Record ID to purge
            confirm: Explicit confirmation (must be True)
            
        Returns:
            Dictionary containing purge confirmation
            
        Raises:
            OSMCPValidationError: If confirmation is not provided
        """
        if not confirm:
            raise OSMCPValidationError(
                "Purge operation requires explicit confirmation. Set confirm=True to proceed with permanent deletion"
            )
        
        # Check delete permission for purge operations
        self.check_delete_permission()
        
        logger.error(
            f"Purging record {id} permanently",
            extra={
                "record_id": id,
                "operation": "purge_record",
                "destructive": True,
                "permanent": True
            }
        )
        
        return await self.delete(f"/records/{id}")
