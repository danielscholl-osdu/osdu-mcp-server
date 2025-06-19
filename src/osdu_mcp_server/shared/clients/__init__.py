"""OSDU service-specific clients."""

from .entitlements_client import EntitlementsClient
from .legal_client import LegalClient
from .partition_client import PartitionClient
from .schema_client import SchemaClient
from .search_client import SearchClient
from .storage_client import StorageClient

__all__ = [
    "PartitionClient",
    "EntitlementsClient",
    "LegalClient",
    "SchemaClient",
    "SearchClient",
    "StorageClient",
]
