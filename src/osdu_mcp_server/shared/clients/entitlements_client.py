"""Minimal OSDU Entitlements service client."""

from typing import Dict, Any

from ..osdu_client import OsduClient
from ..service_urls import OSMCPService, get_service_base_url
from ..exceptions import OSMCPAPIError


class EntitlementsClient(OsduClient):
    """Minimal client for OSDU Entitlements service operations."""
    
    def __init__(self, *args, **kwargs):
        """Initialize EntitlementsClient with service-specific configuration."""
        super().__init__(*args, **kwargs)
        self._base_path = get_service_base_url(OSMCPService.ENTITLEMENTS)
    
    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Override get to include service base path."""
        full_path = f"{self._base_path}{path}"
        return await super().get(full_path, **kwargs)
    
    async def get_my_groups(self) -> Dict[str, Any]:
        """Get groups for the authenticated user."""
        return await self.get("/groups")