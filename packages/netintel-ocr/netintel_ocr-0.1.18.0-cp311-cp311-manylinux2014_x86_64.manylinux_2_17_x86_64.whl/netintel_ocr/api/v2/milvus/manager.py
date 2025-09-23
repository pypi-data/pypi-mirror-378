"""
Milvus Manager - Comprehensive Collection, Partition, Index, and Alias Management
"""

from typing import Dict, Any, List, Optional, Union
from pymilvus import (
    Collection,
    Partition,
    utility,
    DataType,
    MilvusException,
)
import logging
import time
from datetime import datetime
from .connection import get_milvus_connection
from .schemas import (
    DocumentsCollectionSchema,
    EntitiesCollectionSchema,
    QueriesCollectionSchema,
    DiagramCollectionSchema,
    TableCollectionSchema,
    IndexType,
    MetricType,
)
from ..exceptions import (
    MilvusCollectionError,
    MilvusConnectionError,
    ValidationError,
)


logger = logging.getLogger(__name__)


class MilvusManager:
    """Comprehensive Milvus management class"""

    def __init__(self):
        self.conn = get_milvus_connection()

    # ==================== Collection Management ====================

    def create_collection(
        self,
        collection_name: str,
        collection_type: Optional[str] = None,
        schema: Optional[Any] = None,
        description: Optional[str] = None,
        embedding_dim: int = 768,
        enable_dynamic_field: bool = False,
        consistency_level: str = "Strong",
        num_shards: int = 2,
        auto_index: bool = True,
        index_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new collection"""

        try:
            # Check if collection already exists
            if utility.has_collection(collection_name):
                raise MilvusCollectionError(
                    message=f"Collection '{collection_name}' already exists",
                    collection_name=collection_name,
                    operation="create",
                )

            # Create schema if not provided
            if schema is None:
                if collection_type == "documents":
                    schema = DocumentsCollectionSchema.create_schema(
                        embedding_dim=embedding_dim,
                        enable_dynamic_field=enable_dynamic_field,
                    )
                elif collection_type == "entities":
                    schema = EntitiesCollectionSchema.create_schema(
                        embedding_dim=embedding_dim,
                        enable_dynamic_field=enable_dynamic_field,
                    )
                elif collection_type == "queries":
                    schema = QueriesCollectionSchema.create_schema(
                        embedding_dim=embedding_dim,
                        enable_dynamic_field=enable_dynamic_field,
                    )
                elif collection_type == "diagrams":
                    schema = DiagramCollectionSchema.create_schema(
                        embedding_dim=embedding_dim,
                        enable_dynamic_field=enable_dynamic_field,
                    )
                elif collection_type == "tables":
                    schema = TableCollectionSchema.create_schema(
                        embedding_dim=embedding_dim,
                        enable_dynamic_field=enable_dynamic_field,
                    )
                else:
                    raise ValidationError(
                        message=f"Invalid collection type: {collection_type}",
                        details={"collection_type": collection_type},
                    )

            # Set description if provided
            if description:
                schema.description = description

            # Create collection
            collection = Collection(
                name=collection_name,
                schema=schema,
                consistency_level=consistency_level,
                num_shards=num_shards,
            )

            # Create index if requested
            if auto_index:
                if index_params is None:
                    if collection_type == "documents":
                        index_params = DocumentsCollectionSchema.get_index_params()
                    elif collection_type == "entities":
                        index_params = EntitiesCollectionSchema.get_index_params()
                    else:
                        index_params = {
                            "metric_type": MetricType.IP,
                            "index_type": IndexType.IVF_FLAT,
                            "params": {"nlist": 128},
                        }

                # Find vector field
                vector_field = None
                for field in schema.fields:
                    if field.dtype == DataType.FLOAT_VECTOR:
                        vector_field = field.name
                        break

                if vector_field:
                    collection.create_index(
                        field_name=vector_field,
                        index_params=index_params,
                    )

            # Load collection
            collection.load()

            return {
                "success": True,
                "collection_name": collection_name,
                "created_at": datetime.utcnow().isoformat(),
                "schema": {
                    "fields": len(schema.fields),
                    "enable_dynamic_field": enable_dynamic_field,
                },
                "index_created": auto_index,
                "status": "loaded",
            }

        except MilvusException as e:
            raise MilvusCollectionError(
                message=f"Failed to create collection: {str(e)}",
                collection_name=collection_name,
                operation="create",
            )

    def list_collections(
        self,
        pattern: Optional[str] = None,
        include_system: bool = False,
        show_loaded_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """List all collections"""

        try:
            collections = utility.list_collections()

            result = []
            for name in collections:
                # Filter by pattern if provided
                if pattern and pattern not in name:
                    continue

                # Skip system collections if requested
                if not include_system and name.startswith("_"):
                    continue

                try:
                    collection = Collection(name)

                    # Check if loaded
                    is_loaded = utility.load_state(name) == "Loaded"
                    if show_loaded_only and not is_loaded:
                        continue

                    # Get collection info
                    info = {
                        "name": name,
                        "description": collection.description,
                        "num_entities": collection.num_entities,
                        "loaded": is_loaded,
                        "schema": {
                            "fields": len(collection.schema.fields),
                            "auto_id": collection.schema.auto_id,
                            "enable_dynamic_field": collection.schema.enable_dynamic_field,
                        },
                    }

                    # Get index info
                    indexes = collection.indexes
                    if indexes:
                        info["indexes"] = [idx.params for idx in indexes]

                    result.append(info)

                except Exception as e:
                    logger.warning(f"Failed to get info for collection {name}: {str(e)}")

            return result

        except Exception as e:
            raise MilvusConnectionError(
                message=f"Failed to list collections: {str(e)}"
            )

    def get_collection_details(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Get detailed collection information"""

        try:
            if not utility.has_collection(collection_name):
                raise MilvusCollectionError(
                    message=f"Collection '{collection_name}' not found",
                    collection_name=collection_name,
                    operation="get_details",
                )

            collection = Collection(collection_name)

            # Get partitions
            partitions = []
            for partition in collection.partitions:
                partitions.append({
                    "name": partition.name,
                    "num_entities": partition.num_entities,
                })

            # Get schema details
            fields = []
            for field in collection.schema.fields:
                field_info = {
                    "name": field.name,
                    "type": str(field.dtype),
                    "is_primary": field.is_primary,
                    "auto_id": field.auto_id if hasattr(field, "auto_id") else False,
                }
                if field.dtype == DataType.FLOAT_VECTOR:
                    field_info["dim"] = field.params.get("dim", 0)
                if field.dtype == DataType.VARCHAR:
                    field_info["max_length"] = field.params.get("max_length", 0)

                fields.append(field_info)

            # Get index details
            indexes = []
            for idx in collection.indexes:
                indexes.append({
                    "field_name": idx.field_name,
                    "index_name": idx.index_name,
                    "params": idx.params,
                })

            return {
                "name": collection_name,
                "description": collection.description,
                "num_entities": collection.num_entities,
                "loaded": utility.load_state(collection_name) == "Loaded",
                "consistency_level": collection.consistency_level,
                "num_shards": collection.num_shards if hasattr(collection, "num_shards") else None,
                "schema": {
                    "fields": fields,
                    "enable_dynamic_field": collection.schema.enable_dynamic_field,
                },
                "partitions": partitions,
                "indexes": indexes,
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to get collection details: {str(e)}",
                collection_name=collection_name,
                operation="get_details",
            )

    def drop_collection(
        self,
        collection_name: str,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Drop a collection"""

        try:
            if not confirm:
                raise ValidationError(
                    message="Drop operation requires confirmation",
                    details={"confirm": False},
                )

            if not utility.has_collection(collection_name):
                raise MilvusCollectionError(
                    message=f"Collection '{collection_name}' not found",
                    collection_name=collection_name,
                    operation="drop",
                )

            utility.drop_collection(collection_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "dropped_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to drop collection: {str(e)}",
                collection_name=collection_name,
                operation="drop",
            )

    def load_collection(
        self,
        collection_name: str,
        replica_number: int = 1,
    ) -> Dict[str, Any]:
        """Load collection into memory"""

        try:
            collection = Collection(collection_name)
            collection.load(replica_number=replica_number)

            return {
                "success": True,
                "collection_name": collection_name,
                "status": "loaded",
                "replica_number": replica_number,
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to load collection: {str(e)}",
                collection_name=collection_name,
                operation="load",
            )

    def release_collection(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Release collection from memory"""

        try:
            collection = Collection(collection_name)
            collection.release()

            return {
                "success": True,
                "collection_name": collection_name,
                "status": "released",
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to release collection: {str(e)}",
                collection_name=collection_name,
                operation="release",
            )

    def rename_collection(
        self,
        old_name: str,
        new_name: str,
    ) -> Dict[str, Any]:
        """Rename a collection"""

        try:
            utility.rename_collection(old_name, new_name)

            return {
                "success": True,
                "old_name": old_name,
                "new_name": new_name,
                "renamed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to rename collection: {str(e)}",
                collection_name=old_name,
                operation="rename",
            )

    def get_collection_stats(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Get collection statistics"""

        try:
            collection = Collection(collection_name)
            stats = collection.get_compaction_state()

            return {
                "collection_name": collection_name,
                "row_count": collection.num_entities,
                "loaded": utility.load_state(collection_name) == "Loaded",
                "compaction_state": stats.state if stats else None,
                "partitions": len(collection.partitions),
                "indexes": len(collection.indexes),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to get collection stats: {str(e)}",
                collection_name=collection_name,
                operation="stats",
            )

    # ==================== Partition Management ====================

    def create_partition(
        self,
        collection_name: str,
        partition_name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a partition"""

        try:
            collection = Collection(collection_name)

            if collection.has_partition(partition_name):
                raise MilvusCollectionError(
                    message=f"Partition '{partition_name}' already exists",
                    collection_name=collection_name,
                    operation="create_partition",
                )

            partition = collection.create_partition(partition_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to create partition: {str(e)}",
                collection_name=collection_name,
                operation="create_partition",
            )

    def list_partitions(
        self,
        collection_name: str,
    ) -> List[Dict[str, Any]]:
        """List all partitions in a collection"""

        try:
            collection = Collection(collection_name)
            partitions = []

            for partition in collection.partitions:
                partitions.append({
                    "name": partition.name,
                    "num_entities": partition.num_entities,
                    "description": partition.description if hasattr(partition, "description") else None,
                })

            return partitions

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to list partitions: {str(e)}",
                collection_name=collection_name,
                operation="list_partitions",
            )

    def drop_partition(
        self,
        collection_name: str,
        partition_name: str,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Drop a partition"""

        try:
            if not confirm:
                raise ValidationError(
                    message="Drop operation requires confirmation",
                    details={"confirm": False},
                )

            collection = Collection(collection_name)

            if not collection.has_partition(partition_name):
                raise MilvusCollectionError(
                    message=f"Partition '{partition_name}' not found",
                    collection_name=collection_name,
                    operation="drop_partition",
                )

            collection.drop_partition(partition_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "dropped_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to drop partition: {str(e)}",
                collection_name=collection_name,
                operation="drop_partition",
            )

    def load_partition(
        self,
        collection_name: str,
        partition_name: str,
        replica_number: int = 1,
    ) -> Dict[str, Any]:
        """Load a partition into memory"""

        try:
            collection = Collection(collection_name)
            partition = Partition(collection, partition_name)
            partition.load(replica_number=replica_number)

            return {
                "success": True,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "status": "loaded",
                "replica_number": replica_number,
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to load partition: {str(e)}",
                collection_name=collection_name,
                operation="load_partition",
            )

    def release_partition(
        self,
        collection_name: str,
        partition_name: str,
    ) -> Dict[str, Any]:
        """Release a partition from memory"""

        try:
            collection = Collection(collection_name)
            partition = Partition(collection, partition_name)
            partition.release()

            return {
                "success": True,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "status": "released",
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to release partition: {str(e)}",
                collection_name=collection_name,
                operation="release_partition",
            )

    # ==================== Index Management ====================

    def create_index(
        self,
        collection_name: str,
        field_name: str,
        index_name: Optional[str] = None,
        index_type: str = "IVF_FLAT",
        metric_type: str = "IP",
        params: Optional[Dict[str, Any]] = None,
        wait_for_build: bool = True,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """Create an index on a field"""

        try:
            collection = Collection(collection_name)

            # Default parameters based on index type
            if params is None:
                if index_type == "IVF_FLAT":
                    params = {"nlist": 128}
                elif index_type == "IVF_SQ8":
                    params = {"nlist": 128}
                elif index_type == "HNSW":
                    params = {"M": 16, "efConstruction": 200}
                elif index_type == "AUTOINDEX":
                    params = {}

            index_params = {
                "metric_type": metric_type,
                "index_type": index_type,
                "params": params,
            }

            # Create index
            collection.create_index(
                field_name=field_name,
                index_params=index_params,
                index_name=index_name,
            )

            # Wait for index building if requested
            if wait_for_build:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    progress = utility.index_building_progress(collection_name, field_name)
                    if progress.get("indexed_rows", 0) == progress.get("total_rows", 1):
                        break
                    time.sleep(1)

            return {
                "success": True,
                "collection_name": collection_name,
                "field_name": field_name,
                "index_name": index_name,
                "index_type": index_type,
                "metric_type": metric_type,
                "params": params,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to create index: {str(e)}",
                collection_name=collection_name,
                operation="create_index",
            )

    def list_indexes(
        self,
        collection_name: str,
    ) -> List[Dict[str, Any]]:
        """List all indexes in a collection"""

        try:
            collection = Collection(collection_name)
            indexes = []

            for idx in collection.indexes:
                indexes.append({
                    "field_name": idx.field_name,
                    "index_name": idx.index_name,
                    "params": idx.params,
                })

            return indexes

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to list indexes: {str(e)}",
                collection_name=collection_name,
                operation="list_indexes",
            )

    def drop_index(
        self,
        collection_name: str,
        index_name: str,
    ) -> Dict[str, Any]:
        """Drop an index"""

        try:
            collection = Collection(collection_name)
            collection.drop_index(index_name=index_name)

            return {
                "success": True,
                "collection_name": collection_name,
                "index_name": index_name,
                "dropped_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to drop index: {str(e)}",
                collection_name=collection_name,
                operation="drop_index",
            )

    def get_index_progress(
        self,
        collection_name: str,
        field_name: str,
    ) -> Dict[str, Any]:
        """Get index building progress"""

        try:
            progress = utility.index_building_progress(collection_name, field_name)

            total_rows = progress.get("total_rows", 0)
            indexed_rows = progress.get("indexed_rows", 0)
            progress_percent = (indexed_rows / total_rows * 100) if total_rows > 0 else 0

            return {
                "collection_name": collection_name,
                "field_name": field_name,
                "indexed_rows": indexed_rows,
                "total_rows": total_rows,
                "progress": round(progress_percent, 2),
                "is_completed": indexed_rows == total_rows,
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to get index progress: {str(e)}",
                collection_name=collection_name,
                operation="index_progress",
            )

    # ==================== Alias Management ====================

    def create_alias(
        self,
        alias: str,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Create an alias for a collection"""

        try:
            utility.create_alias(alias, collection_name)

            return {
                "success": True,
                "alias": alias,
                "collection_name": collection_name,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to create alias: {str(e)}",
                collection_name=collection_name,
                operation="create_alias",
            )

    def list_aliases(
        self,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List aliases"""

        try:
            aliases = utility.list_aliases(collection_name) if collection_name else []

            return [{"alias": alias} for alias in aliases]

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to list aliases: {str(e)}",
                collection_name=collection_name,
                operation="list_aliases",
            )

    def alter_alias(
        self,
        alias: str,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Alter an alias to point to a different collection"""

        try:
            utility.alter_alias(alias, collection_name)

            return {
                "success": True,
                "alias": alias,
                "collection_name": collection_name,
                "altered_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to alter alias: {str(e)}",
                collection_name=collection_name,
                operation="alter_alias",
            )

    def drop_alias(
        self,
        alias: str,
    ) -> Dict[str, Any]:
        """Drop an alias"""

        try:
            utility.drop_alias(alias)

            return {
                "success": True,
                "alias": alias,
                "dropped_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to drop alias: {str(e)}",
                operation="drop_alias",
            )

    # ==================== Advanced Operations ====================

    def flush_collection(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Flush collection data to disk"""

        try:
            collection = Collection(collection_name)
            collection.flush()

            return {
                "success": True,
                "collection_name": collection_name,
                "flushed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to flush collection: {str(e)}",
                collection_name=collection_name,
                operation="flush",
            )

    def compact_collection(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Compact collection segments"""

        try:
            collection = Collection(collection_name)
            collection.compact()

            return {
                "success": True,
                "collection_name": collection_name,
                "compacted_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to compact collection: {str(e)}",
                collection_name=collection_name,
                operation="compact",
            )

    def get_compaction_state(
        self,
        collection_name: str,
    ) -> Dict[str, Any]:
        """Get compaction state"""

        try:
            collection = Collection(collection_name)
            state = collection.get_compaction_state()

            return {
                "collection_name": collection_name,
                "state": state.state if state else "unknown",
                "executing_plan_count": state.executing_plan_count if state else 0,
                "timeout_plan_count": state.timeout_plan_count if state else 0,
                "completed_plan_count": state.completed_plan_count if state else 0,
            }

        except Exception as e:
            raise MilvusCollectionError(
                message=f"Failed to get compaction state: {str(e)}",
                collection_name=collection_name,
                operation="compaction_state",
            )