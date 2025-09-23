"""
Milvus Collection Schemas
"""

from typing import Dict, Any, List, Optional
from pymilvus import (
    FieldSchema,
    CollectionSchema,
    DataType,
)
from dataclasses import dataclass
from enum import Enum


class IndexType(str, Enum):
    """Supported index types"""

    FLAT = "FLAT"
    IVF_FLAT = "IVF_FLAT"
    IVF_SQ8 = "IVF_SQ8"
    IVF_PQ = "IVF_PQ"
    HNSW = "HNSW"
    ANNOY = "ANNOY"
    AUTOINDEX = "AUTOINDEX"
    DISKANN = "DISKANN"


class MetricType(str, Enum):
    """Distance metric types"""

    L2 = "L2"  # Euclidean distance
    IP = "IP"  # Inner product
    COSINE = "COSINE"  # Cosine similarity


@dataclass
class CollectionConfig:
    """Collection configuration"""

    name: str
    description: str
    fields: List[FieldSchema]
    enable_dynamic_field: bool = False
    consistency_level: str = "Strong"
    partition_key_field: Optional[str] = None
    num_shards: int = 2
    replica_number: int = 1


# Document Collection Schema
class DocumentsCollectionSchema:
    """Schema for the main documents collection"""

    @staticmethod
    def create_schema(
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
    ) -> CollectionSchema:
        """Create schema for documents collection"""

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
                description="Auto-generated unique ID",
            ),
            FieldSchema(
                name="document_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Document identifier",
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT32,
                description="Page number in document",
            ),
            FieldSchema(
                name="content_type",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Content type (text, diagram, table)",
            ),
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Actual content text",
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
                description="Content embedding vector",
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
                description="Additional metadata",
            ),
            FieldSchema(
                name="created_at",
                dtype=DataType.INT64,
                description="Creation timestamp",
            ),
            FieldSchema(
                name="updated_at",
                dtype=DataType.INT64,
                description="Last update timestamp",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Document content and embeddings",
            enable_dynamic_field=enable_dynamic_field,
        )

        return schema

    @staticmethod
    def get_index_params(index_type: str = "IVF_FLAT") -> Dict[str, Any]:
        """Get recommended index parameters"""

        if index_type == "IVF_FLAT":
            return {
                "metric_type": MetricType.IP,
                "index_type": IndexType.IVF_FLAT,
                "params": {"nlist": 1024},
            }
        elif index_type == "IVF_SQ8":
            return {
                "metric_type": MetricType.IP,
                "index_type": IndexType.IVF_SQ8,
                "params": {"nlist": 1024},
            }
        elif index_type == "HNSW":
            return {
                "metric_type": MetricType.IP,
                "index_type": IndexType.HNSW,
                "params": {"M": 16, "efConstruction": 200},
            }
        elif index_type == "AUTOINDEX":
            return {
                "metric_type": MetricType.IP,
                "index_type": IndexType.AUTOINDEX,
            }
        else:
            return {
                "metric_type": MetricType.IP,
                "index_type": IndexType.IVF_FLAT,
                "params": {"nlist": 128},
            }

    @staticmethod
    def get_search_params(index_type: str = "IVF_FLAT") -> Dict[str, Any]:
        """Get recommended search parameters"""

        if index_type in ["IVF_FLAT", "IVF_SQ8"]:
            return {"nprobe": 16}
        elif index_type == "HNSW":
            return {"ef": 64}
        else:
            return {}


# Entity Collection Schema
class EntitiesCollectionSchema:
    """Schema for the entities collection"""

    @staticmethod
    def create_schema(
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
    ) -> CollectionSchema:
        """Create schema for entities collection"""

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
                description="Auto-generated unique ID",
            ),
            FieldSchema(
                name="entity_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Entity identifier",
            ),
            FieldSchema(
                name="entity_type",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Entity type (Router, Switch, Firewall, etc.)",
            ),
            FieldSchema(
                name="entity_name",
                dtype=DataType.VARCHAR,
                max_length=500,
                description="Entity name",
            ),
            FieldSchema(
                name="description",
                dtype=DataType.VARCHAR,
                max_length=2000,
                description="Entity description",
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
                description="Entity embedding vector",
            ),
            FieldSchema(
                name="relationships",
                dtype=DataType.JSON,
                description="Entity relationships",
            ),
            FieldSchema(
                name="source_documents",
                dtype=DataType.JSON,
                description="Source document IDs",
            ),
            FieldSchema(
                name="properties",
                dtype=DataType.JSON,
                description="Entity properties",
            ),
            FieldSchema(
                name="created_at",
                dtype=DataType.INT64,
                description="Creation timestamp",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Named entities and their embeddings",
            enable_dynamic_field=enable_dynamic_field,
        )

        return schema

    @staticmethod
    def get_index_params(index_type: str = "HNSW") -> Dict[str, Any]:
        """Get recommended index parameters for entities"""

        if index_type == "HNSW":
            return {
                "metric_type": MetricType.COSINE,
                "index_type": IndexType.HNSW,
                "params": {"M": 16, "efConstruction": 200},
            }
        else:
            return {
                "metric_type": MetricType.COSINE,
                "index_type": IndexType.IVF_FLAT,
                "params": {"nlist": 512},
            }


# Query Cache Collection Schema
class QueriesCollectionSchema:
    """Schema for the query cache collection"""

    @staticmethod
    def create_schema(
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
    ) -> CollectionSchema:
        """Create schema for queries collection"""

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
                description="Auto-generated unique ID",
            ),
            FieldSchema(
                name="query_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Query identifier",
            ),
            FieldSchema(
                name="query_text",
                dtype=DataType.VARCHAR,
                max_length=1000,
                description="Query text",
            ),
            FieldSchema(
                name="query_embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
                description="Query embedding vector",
            ),
            FieldSchema(
                name="results",
                dtype=DataType.JSON,
                description="Cached query results",
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
                description="Query metadata",
            ),
            FieldSchema(
                name="timestamp",
                dtype=DataType.INT64,
                description="Query timestamp",
            ),
            FieldSchema(
                name="user_feedback",
                dtype=DataType.FLOAT,
                description="User feedback score",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Query history and cache",
            enable_dynamic_field=enable_dynamic_field,
        )

        return schema


# Diagram Collection Schema
class DiagramCollectionSchema:
    """Schema for network diagrams collection"""

    @staticmethod
    def create_schema(
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
    ) -> CollectionSchema:
        """Create schema for diagrams collection"""

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="diagram_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Diagram identifier",
            ),
            FieldSchema(
                name="document_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Source document ID",
            ),
            FieldSchema(
                name="diagram_type",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Diagram type (network, flow, architecture)",
            ),
            FieldSchema(
                name="description",
                dtype=DataType.VARCHAR,
                max_length=5000,
                description="Diagram description",
            ),
            FieldSchema(
                name="mermaid_code",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Mermaid diagram code",
            ),
            FieldSchema(
                name="devices",
                dtype=DataType.JSON,
                description="Devices in diagram",
            ),
            FieldSchema(
                name="connections",
                dtype=DataType.JSON,
                description="Network connections",
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
                description="Diagram embedding",
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
                description="Additional metadata",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Network diagrams and their embeddings",
            enable_dynamic_field=enable_dynamic_field,
        )

        return schema


# Table Collection Schema
class TableCollectionSchema:
    """Schema for extracted tables collection"""

    @staticmethod
    def create_schema(
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
    ) -> CollectionSchema:
        """Create schema for tables collection"""

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="table_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Table identifier",
            ),
            FieldSchema(
                name="document_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Source document ID",
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT32,
                description="Page number",
            ),
            FieldSchema(
                name="table_content",
                dtype=DataType.JSON,
                description="Table data as JSON",
            ),
            FieldSchema(
                name="headers",
                dtype=DataType.JSON,
                description="Table headers",
            ),
            FieldSchema(
                name="summary",
                dtype=DataType.VARCHAR,
                max_length=2000,
                description="Table summary",
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
                description="Table content embedding",
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
                description="Additional metadata",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Extracted tables and their embeddings",
            enable_dynamic_field=enable_dynamic_field,
        )

        return schema


def create_collection_schema(
    collection_type: str,
    embedding_dim: int = 768,
    enable_dynamic_field: bool = False,
    **kwargs,
) -> CollectionSchema:
    """Factory function to create collection schemas"""

    schema_map = {
        "documents": DocumentsCollectionSchema,
        "entities": EntitiesCollectionSchema,
        "queries": QueriesCollectionSchema,
        "diagrams": DiagramCollectionSchema,
        "tables": TableCollectionSchema,
    }

    if collection_type not in schema_map:
        raise ValueError(f"Unknown collection type: {collection_type}")

    schema_class = schema_map[collection_type]
    return schema_class.create_schema(
        embedding_dim=embedding_dim,
        enable_dynamic_field=enable_dynamic_field,
    )