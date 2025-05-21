"""Client for OSDU Partition Service operations."""

import logging
from typing import Any, Dict, List, Optional

from ..auth_handler import AuthHandler
from ..config_manager import ConfigManager
from ..exceptions import OSMCPAPIError, OSMCPValidationError
from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url

logger = logging.getLogger(__name__)


class PartitionClient(OsduClient):
    """Client for OSDU Partition Service operations."""

    def __init__(self, config: ConfigManager, auth_handler: AuthHandler):
        """Initialize partition client.

        Args:
            config: Configuration manager instance
            auth_handler: Authentication handler instance
        """
        super().__init__(config, auth_handler)
        self._base_path = get_service_base_url(OSMCPService.PARTITION)

    async def list_partitions(self) -> List[str]:
        """List all accessible partitions.

        Returns:
            List of partition IDs

        Raises:
            OSMCPAPIError: For API errors
            OSMCPConnectionError: For connection errors
        """
        path = f"{self._base_path}/partitions"
        
        try:
            response = await self.get(path)
            
            # The partition service returns a list of strings
            if isinstance(response, list):
                logger.info(f"Retrieved {len(response)} partitions")
                return response
            else:
                logger.warning(f"Unexpected response format: {type(response)}")
                return []
                
        except OSMCPAPIError as e:
            if e.status_code == 404:
                logger.info("No partitions found")
                return []
            elif e.status_code == 403:
                logger.warning("Insufficient permissions to list partitions")
                raise OSMCPAPIError("Insufficient permissions to list partitions", e.status_code)
            else:
                logger.error(f"API error listing partitions: {e}")
                raise

    async def get_partition(self, partition_id: str) -> Dict[str, Any]:
        """Get properties for a specific partition.

        Args:
            partition_id: ID of the partition to retrieve

        Returns:
            Dictionary of partition properties

        Raises:
            OSMCPAPIError: For API errors
            OSMCPValidationError: For invalid partition ID
            OSMCPConnectionError: For connection errors
        """
        if not partition_id or not partition_id.strip():
            raise OSMCPValidationError("Partition ID cannot be empty")
            
        path = f"{self._base_path}/partitions/{partition_id}"
        
        try:
            # Set custom headers for this specific request
            headers = {
                "data-partition-id": partition_id,  # Use specific partition ID
            }
            
            response = await self.get(path, headers=headers)
            
            logger.info(f"Retrieved properties for partition: {partition_id}")
            return response
            
        except OSMCPAPIError as e:
            if e.status_code == 404:
                # Handle plain text 404 response
                logger.info(f"Partition not found: {partition_id}")
                raise OSMCPAPIError(f"Partition '{partition_id}' not found", 404)
            elif e.status_code == 401:
                logger.warning(f"Authentication required for partition: {partition_id}")
                raise
            elif e.status_code == 403:
                logger.warning(f"Insufficient permissions for partition: {partition_id}")
                raise OSMCPAPIError(f"Insufficient permissions for partition '{partition_id}'", 403)
            else:
                logger.error(f"API error getting partition {partition_id}: {e}")
                raise

    async def create_partition(self, partition_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new partition.

        Note: This operation requires write permissions to be enabled via
        OSDU_MCP_ENABLE_WRITE_MODE=true environment variable.

        Args:
            partition_id: ID for the new partition
            properties: Partition properties

        Returns:
            Created partition details

        Raises:
            OSMCPAPIError: For API errors or write permissions disabled
            OSMCPValidationError: For invalid partition data
        """
        if not self._is_write_allowed():
            raise OSMCPAPIError("Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable.", 403)

        if not partition_id or not partition_id.strip():
            raise OSMCPValidationError("Partition ID cannot be empty")

        path = f"{self._base_path}/partitions/{partition_id}"
        
        # Ensure sensitive properties are marked correctly
        data = {"properties": self._validate_properties(properties)}
        
        headers = {
            "data-partition-id": partition_id,
        }
        
        try:
            response = await self.post(path, data, headers=headers)
            logger.info(f"Created partition: {partition_id}")
            return response
        except OSMCPAPIError as e:
            if e.status_code == 409:
                raise OSMCPAPIError(f"Partition '{partition_id}' already exists", 409)
            raise

    async def update_partition(self, partition_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update partition properties.

        Note: This operation requires write permissions to be enabled.

        Args:
            partition_id: ID of the partition to update
            properties: Updated properties

        Returns:
            Updated partition details

        Raises:
            OSMCPAPIError: For API errors or write permissions disabled
            OSMCPValidationError: For invalid partition data
        """
        if not self._is_write_allowed():
            raise OSMCPAPIError("Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable.", 403)

        if not partition_id or not partition_id.strip():
            raise OSMCPValidationError("Partition ID cannot be empty")

        path = f"{self._base_path}/partitions/{partition_id}"
        
        # Ensure sensitive properties are marked correctly
        data = {"properties": self._validate_properties(properties)}
        
        headers = {
            "data-partition-id": partition_id,
        }
        
        try:
            response = await self.put(path, data, headers=headers)
            logger.info(f"Updated partition: {partition_id}")
            return response
        except OSMCPAPIError as e:
            if e.status_code == 404:
                raise OSMCPAPIError(f"Partition '{partition_id}' not found", 404)
            raise

    async def delete_partition(self, partition_id: str) -> None:
        """Delete a partition.

        Note: This operation requires write permissions to be enabled.

        Args:
            partition_id: ID of the partition to delete

        Raises:
            OSMCPAPIError: For API errors or write permissions disabled
            OSMCPValidationError: For invalid partition ID
        """
        if not self._is_write_allowed():
            raise OSMCPAPIError("Write operations are disabled. Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable.", 403)

        if not partition_id or not partition_id.strip():
            raise OSMCPValidationError("Partition ID cannot be empty")

        path = f"{self._base_path}/partitions/{partition_id}"
        
        headers = {
            "data-partition-id": partition_id,
        }
        
        try:
            await self.delete(path, headers=headers)
            logger.info(f"Deleted partition: {partition_id}")
        except OSMCPAPIError as e:
            if e.status_code == 404:
                raise OSMCPAPIError(f"Partition '{partition_id}' not found", 404)
            raise

    def _is_write_allowed(self) -> bool:
        """Check if write operations are allowed."""
        import os
        return os.environ.get("OSDU_MCP_ENABLE_WRITE_MODE", "false").lower() == "true"

    def _validate_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize partition properties.

        Args:
            properties: Properties to validate

        Returns:
            Validated properties

        Raises:
            OSMCPValidationError: For invalid property format
        """
        validated = {}
        
        for key, value in properties.items():
            if isinstance(value, dict):
                # Already in correct format
                if "value" not in value:
                    raise OSMCPValidationError(f"Property '{key}' must have a 'value' field")
                validated[key] = value
            else:
                # Convert simple value to property format
                validated[key] = {
                    "value": value,
                    "sensitive": False
                }
        
        return validated