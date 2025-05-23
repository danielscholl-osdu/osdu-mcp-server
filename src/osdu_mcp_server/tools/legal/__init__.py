"""OSDU Legal service tools."""

from .batch_retrieve import legaltag_batch_retrieve
from .create import legaltag_create
from .delete import legaltag_delete
from .get import legaltag_get
from .get_properties import legaltag_get_properties
from .list import legaltag_list
from .search import legaltag_search
from .update import legaltag_update

__all__ = [
    "legaltag_list",
    "legaltag_get",
    "legaltag_get_properties",
    "legaltag_search",
    "legaltag_batch_retrieve",
    "legaltag_create",
    "legaltag_update",
    "legaltag_delete",
]
