"""Service URL configuration for OSDU services."""

from enum import Enum
from typing import Dict


class OSMCPService(Enum):
    """OSDU service identifiers."""
    
    STORAGE = "storage"
    SEARCH = "search"
    LEGAL = "legal"
    SCHEMA = "schema"
    FILE = "file"
    WORKFLOW = "workflow"
    ENTITLEMENTS = "entitlements"
    DATASET = "dataset"
    PARTITION = "partition"


# Service base URL patterns
SERVICE_BASE_URLS: Dict[OSMCPService, str] = {
    OSMCPService.STORAGE: "/api/storage/v2",
    OSMCPService.SEARCH: "/api/search/v2",
    OSMCPService.LEGAL: "/api/legal/v1",  # Legal uses v1
    OSMCPService.SCHEMA: "/api/schema-service/v1",
    OSMCPService.FILE: "/api/file/v2",
    OSMCPService.WORKFLOW: "/api/workflow/v1",
    OSMCPService.ENTITLEMENTS: "/api/entitlements/v2",
    OSMCPService.DATASET: "/api/dataset/v1",
    OSMCPService.PARTITION: "/api/partition/v1",
}


def get_service_base_url(service: OSMCPService) -> str:
    """Get the base URL for a given OSDU service.
    
    Args:
        service: The OSDU service enum
        
    Returns:
        The base URL path for the service
    """
    return SERVICE_BASE_URLS.get(service, f"/api/{service.value}/v2")


def get_service_info_endpoint(service: OSMCPService) -> str:
    """Get the info/health endpoint for a given OSDU service.
    
    Args:
        service: The OSDU service enum
        
    Returns:
        The full path to the service info endpoint
    """
    base_url = get_service_base_url(service)
    return f"{base_url}/info"
