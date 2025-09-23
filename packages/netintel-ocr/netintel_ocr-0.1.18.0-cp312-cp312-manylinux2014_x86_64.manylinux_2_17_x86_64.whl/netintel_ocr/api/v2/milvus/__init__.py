"""
Milvus Integration Module for NetIntel-OCR API v2
"""

from .connection import MilvusConnectionManager, get_milvus_connection, ensure_connection
from .manager import MilvusManager
from .schemas import (
    DocumentsCollectionSchema,
    EntitiesCollectionSchema,
    QueriesCollectionSchema,
    create_collection_schema,
)
from .operations import MilvusOperations
from .search import MilvusSearchEngine

__all__ = [
    "MilvusConnectionManager",
    "MilvusManager",
    "MilvusOperations",
    "MilvusSearchEngine",
    "get_milvus_connection",
    "ensure_connection",
    "DocumentsCollectionSchema",
    "EntitiesCollectionSchema",
    "QueriesCollectionSchema",
    "create_collection_schema",
]