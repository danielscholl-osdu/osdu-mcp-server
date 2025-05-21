"""OSDU service-specific clients."""

from .partition_client import PartitionClient
from .entitlements_client import EntitlementsClient
from .legal_client import LegalClient
from .schema_client import SchemaClient
from .storage_client import StorageClient

__all__ = [
    "PartitionClient",
    "EntitlementsClient", 
    "LegalClient",
    "SchemaClient",
    "StorageClient",
]
