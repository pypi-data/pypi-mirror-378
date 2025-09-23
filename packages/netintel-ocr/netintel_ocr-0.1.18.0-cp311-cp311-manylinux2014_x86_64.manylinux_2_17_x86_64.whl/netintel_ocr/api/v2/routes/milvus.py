"""
Milvus Collection Management API Routes
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query, Body
from pydantic import BaseModel, Field
from ..milvus.manager import MilvusManager
from ..milvus.operations import MilvusOperations
from ..milvus.search import MilvusSearchEngine
from ..auth.oauth2 import get_current_user, require_permissions
from ..auth.rbac import ResourceType, Action
from ..monitoring.metrics import metrics_service
from ..monitoring.audit import audit_logger, AuditEventType


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/milvus", tags=["Milvus"])

milvus_manager = MilvusManager()
milvus_operations = MilvusOperations()
search_engine = MilvusSearchEngine()


# ==================== Request/Response Models ====================

class CollectionCreateRequest(BaseModel):
    """Collection creation request"""
    collection_name: str
    description: str
    fields: List[Dict[str, Any]]
    index_params: Optional[Dict[str, Any]] = None
    consistency_level: str = "Strong"
    enable_dynamic_field: bool = False


class PartitionCreateRequest(BaseModel):
    """Partition creation request"""
    partition_name: str
    description: Optional[str] = None


class IndexCreateRequest(BaseModel):
    """Index creation request"""
    field_name: str = "embedding"
    index_name: Optional[str] = None
    index_params: Dict[str, Any]


class VectorInsertRequest(BaseModel):
    """Vector insertion request"""
    partition_name: Optional[str] = None
    entities: List[Dict[str, Any]]
    mode: str = "insert"  # insert or upsert


class VectorSearchRequest(BaseModel):
    """Vector search request"""
    vectors: Optional[List[List[float]]] = None
    query_text: Optional[str] = None
    filter: Optional[str] = None
    output_fields: List[str] = Field(default_factory=lambda: ["*"])
    search_params: Optional[Dict[str, Any]] = None
    limit: int = 20
    offset: int = 0
    partition_names: Optional[List[str]] = None
    consistency_level: str = "Strong"


class HybridSearchRequest(BaseModel):
    """Hybrid search request"""
    vector_query: Dict[str, Any]
    scalar_filters: Optional[Dict[str, Any]] = None
    text_query: Optional[Dict[str, Any]] = None
    weights: Dict[str, float] = Field(default_factory=lambda: {"vector": 0.7, "text": 0.3})
    limit: int = 20
    rerank: bool = True


class QueryRequest(BaseModel):
    """Query by expression request"""
    expr: str
    output_fields: List[str] = Field(default_factory=lambda: ["*"])
    partition_names: Optional[List[str]] = None
    limit: int = 100


class BulkImportRequest(BaseModel):
    """Bulk import request"""
    file_type: str  # json|numpy|parquet
    file_url: str
    partition_name: Optional[str] = None


class DeleteRequest(BaseModel):
    """Delete request"""
    expr: Optional[str] = None
    ids: Optional[List[int]] = None


class AliasRequest(BaseModel):
    """Alias request"""
    alias: str
    collection_name: str


class ResourceGroupRequest(BaseModel):
    """Resource group request"""
    name: str
    requests: Dict[str, Any]
    limits: Dict[str, Any]


class ReplicaRequest(BaseModel):
    """Replica configuration request"""
    replica_number: int
    resource_groups: Optional[List[str]] = None


# ==================== Collection Management Endpoints ====================

@router.post(
    "/collections",
    summary="Create collection",
    description="Create a new Milvus collection with schema",
    dependencies=[Depends(require_permissions(["milvus:manage"]))],
)
async def create_collection(
    request: CollectionCreateRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create a new Milvus collection"""
    
    try:
        # Create collection
        result = milvus_manager.create_collection(
            collection_name=request.collection_name,
            description=request.description,
            fields=request.fields,
            consistency_level=request.consistency_level,
            enable_dynamic_field=request.enable_dynamic_field,
        )
        
        # Create index if specified
        if request.index_params:
            milvus_manager.create_index(
                collection_name=request.collection_name,
                **request.index_params,
            )
        
        # Record metrics
        metrics_service.record_milvus_operation("create_collection", "success")
        
        # Audit log
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_CREATE,
            user_id=current_user.sub,
            resource_type="milvus_collection",
            resource_id=request.collection_name,
            message=f"Created collection {request.collection_name}",
        )
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("create_collection", "failure")
        logger.error(f"Failed to create collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/collections",
    summary="List collections",
    description="List all Milvus collections",
)
async def list_collections(
    include_system: bool = Query(False, description="Include system collections"),
    show_loaded_only: bool = Query(False, description="Show only loaded collections"),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """List all Milvus collections"""
    
    try:
        collections = milvus_manager.list_collections()
        
        result = {"collections": []}
        for collection_name in collections:
            # Get collection details
            details = milvus_manager.get_collection_details(collection_name)
            stats = milvus_manager.get_collection_stats(collection_name)
            
            # Filter based on parameters
            if not include_system and collection_name.startswith("_"):
                continue
            
            if show_loaded_only and not details.get("loaded"):
                continue
            
            result["collections"].append({
                "name": collection_name,
                "description": details.get("description"),
                "num_entities": stats.get("row_count", 0),
                "created_time": details.get("created_time"),
                "loaded": details.get("loaded"),
                "schema": details.get("schema"),
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/collections/{collection_name}",
    summary="Get collection details",
    description="Get detailed information about a collection",
)
async def get_collection(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get collection details"""
    
    try:
        details = milvus_manager.get_collection_details(collection_name)
        stats = milvus_manager.get_collection_stats(collection_name)
        
        return {
            **details,
            "statistics": stats,
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/collections/{collection_name}",
    summary="Drop collection",
    description="Delete a collection",
    dependencies=[Depends(require_permissions(["milvus:manage"]))],
)
async def drop_collection(
    collection_name: str,
    confirm: bool = Query(..., description="Confirm deletion"),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Drop a collection"""
    
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion must be confirmed",
        )
    
    try:
        result = milvus_manager.drop_collection(collection_name, confirm=True)
        
        # Audit log
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_DELETE,
            user_id=current_user.sub,
            resource_type="milvus_collection",
            resource_id=collection_name,
            message=f"Dropped collection {collection_name}",
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to drop collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/load",
    summary="Load collection",
    description="Load collection into memory",
)
async def load_collection(
    collection_name: str,
    replica_number: int = Query(1, description="Number of replicas"),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Load collection into memory"""
    
    try:
        result = milvus_manager.load_collection(
            collection_name,
            replica_number=replica_number,
        )
        
        metrics_service.record_milvus_operation("load_collection", "success")
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("load_collection", "failure")
        logger.error(f"Failed to load collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/release",
    summary="Release collection",
    description="Release collection from memory",
)
async def release_collection(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Release collection from memory"""
    
    try:
        result = milvus_manager.release_collection(collection_name)
        
        metrics_service.record_milvus_operation("release_collection", "success")
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("release_collection", "failure")
        logger.error(f"Failed to release collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/collections/{collection_name}/stats",
    summary="Get collection statistics",
    description="Get detailed statistics for a collection",
)
async def get_collection_stats(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get collection statistics"""
    
    try:
        stats = milvus_manager.get_collection_stats(collection_name)
        
        # Add additional metrics
        stats["index_progress"] = milvus_manager.get_index_building_progress(
            collection_name
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/flush",
    summary="Flush collection",
    description="Flush pending data to disk",
)
async def flush_collection(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Flush collection data"""
    
    try:
        result = milvus_manager.flush_collection(collection_name)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to flush collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/compact",
    summary="Compact collection",
    description="Compact collection segments",
)
async def compact_collection(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Compact collection segments"""
    
    try:
        result = milvus_manager.compact_collection(collection_name)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to compact collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== Partition Management Endpoints ====================

@router.post(
    "/collections/{collection_name}/partitions",
    summary="Create partition",
    description="Create a new partition in collection",
)
async def create_partition(
    collection_name: str,
    request: PartitionCreateRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create partition"""
    
    try:
        result = milvus_manager.create_partition(
            collection_name,
            request.partition_name,
            description=request.description,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to create partition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/collections/{collection_name}/partitions",
    summary="List partitions",
    description="List all partitions in collection",
)
async def list_partitions(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """List partitions"""
    
    try:
        partitions = milvus_manager.list_partitions(collection_name)
        
        return {"partitions": partitions}
        
    except Exception as e:
        logger.error(f"Failed to list partitions: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/collections/{collection_name}/partitions/{partition_name}",
    summary="Drop partition",
    description="Delete a partition",
)
async def drop_partition(
    collection_name: str,
    partition_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Drop partition"""
    
    try:
        result = milvus_manager.drop_partition(
            collection_name,
            partition_name,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to drop partition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== Index Management Endpoints ====================

@router.post(
    "/collections/{collection_name}/indexes",
    summary="Create index",
    description="Create index for collection field",
)
async def create_index(
    collection_name: str,
    request: IndexCreateRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create index"""
    
    try:
        result = milvus_manager.create_index(
            collection_name,
            field_name=request.field_name,
            index_name=request.index_name,
            index_params=request.index_params,
        )
        
        metrics_service.record_milvus_operation("create_index", "success")
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("create_index", "failure")
        logger.error(f"Failed to create index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/collections/{collection_name}/indexes",
    summary="List indexes",
    description="List all indexes in collection",
)
async def list_indexes(
    collection_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """List indexes"""
    
    try:
        indexes = milvus_manager.list_indexes(collection_name)
        
        return {"indexes": indexes}
        
    except Exception as e:
        logger.error(f"Failed to list indexes: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/collections/{collection_name}/indexes/{index_name}/progress",
    summary="Get index progress",
    description="Get index building progress",
)
async def get_index_progress(
    collection_name: str,
    index_name: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get index building progress"""
    
    try:
        progress = milvus_manager.get_index_building_progress(
            collection_name,
            index_name,
        )
        
        return progress
        
    except Exception as e:
        logger.error(f"Failed to get index progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==================== Vector Operations Endpoints ====================

@router.post(
    "/collections/{collection_name}/entities",
    summary="Insert vectors",
    description="Insert vectors into collection",
)
async def insert_vectors(
    collection_name: str,
    request: VectorInsertRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Insert vectors"""
    
    try:
        if request.mode == "upsert":
            result = milvus_operations.upsert(
                collection_name,
                entities=request.entities,
                partition_name=request.partition_name,
            )
        else:
            result = milvus_operations.batch_insert(
                collection_name,
                entities=request.entities,
                partition_name=request.partition_name,
            )
        
        metrics_service.record_milvus_operation("insert", "success")
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("insert", "failure")
        logger.error(f"Failed to insert vectors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/search",
    summary="Vector search",
    description="Perform vector similarity search",
)
async def vector_search(
    collection_name: str,
    request: VectorSearchRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Vector similarity search"""
    
    try:
        # Convert text to vectors if needed
        if request.query_text and not request.vectors:
            from ..services.embedding import get_embedding_service
            embedding_service = get_embedding_service()
            embeddings = await embedding_service.generate_embeddings(
                [request.query_text]
            )
            request.vectors = embeddings
        
        # Perform search
        results = search_engine.vector_search(
            collection_name=collection_name,
            query_vectors=request.vectors,
            filter_expression=request.filter,
            output_fields=request.output_fields,
            search_params=request.search_params,
            limit=request.limit,
            offset=request.offset,
            partition_names=request.partition_names,
        )
        
        metrics_service.record_search_query("vector", 0.1)  # TODO: actual latency
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search vectors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/hybrid-search",
    summary="Hybrid search",
    description="Perform hybrid vector and scalar search",
)
async def hybrid_search(
    collection_name: str,
    request: HybridSearchRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Hybrid search"""
    
    try:
        results = search_engine.hybrid_search(
            collection_name=collection_name,
            vector_query=request.vector_query,
            scalar_filters=request.scalar_filters,
            text_query=request.text_query,
            weights=request.weights,
            limit=request.limit,
            rerank=request.rerank,
        )
        
        metrics_service.record_search_query("hybrid", 0.15)  # TODO: actual latency
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to perform hybrid search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/query",
    summary="Query by expression",
    description="Query collection using boolean expression",
)
async def query_collection(
    collection_name: str,
    request: QueryRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Query collection by expression"""
    
    try:
        results = milvus_operations.query(
            collection_name,
            expression=request.expr,
            output_fields=request.output_fields,
            partition_names=request.partition_names,
            limit=request.limit,
        )
        
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Failed to query collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/collections/{collection_name}/entities",
    summary="Delete entities",
    description="Delete entities by expression or IDs",
)
async def delete_entities(
    collection_name: str,
    request: DeleteRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Delete entities"""
    
    try:
        if request.expr:
            result = milvus_operations.delete(
                collection_name,
                expression=request.expr,
            )
        elif request.ids:
            result = milvus_operations.delete(
                collection_name,
                ids=request.ids,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either expr or ids must be provided",
            )
        
        metrics_service.record_milvus_operation("delete", "success")
        
        return result
        
    except Exception as e:
        metrics_service.record_milvus_operation("delete", "failure")
        logger.error(f"Failed to delete entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/collections/{collection_name}/bulk-import",
    summary="Bulk import",
    description="Import vectors from file",
)
async def bulk_import(
    collection_name: str,
    request: BulkImportRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Bulk import vectors"""
    
    try:
        result = milvus_operations.bulk_import(
            collection_name,
            file_type=request.file_type,
            file_path=request.file_url,
            partition_name=request.partition_name,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to bulk import: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== Alias Management Endpoints ====================

@router.post(
    "/aliases",
    summary="Create alias",
    description="Create collection alias",
)
async def create_alias(
    request: AliasRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create alias"""
    
    try:
        result = milvus_manager.create_alias(
            request.alias,
            request.collection_name,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to create alias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/aliases",
    summary="List aliases",
    description="List all aliases",
)
async def list_aliases(
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """List aliases"""
    
    try:
        aliases = milvus_manager.list_aliases()
        
        return {"aliases": aliases}
        
    except Exception as e:
        logger.error(f"Failed to list aliases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/aliases/{alias}",
    summary="Alter alias",
    description="Change alias target collection",
)
async def alter_alias(
    alias: str,
    collection_name: str = Body(..., embed=True),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Alter alias"""
    
    try:
        result = milvus_manager.alter_alias(
            alias,
            collection_name,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to alter alias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/aliases/{alias}",
    summary="Drop alias",
    description="Delete alias",
)
async def drop_alias(
    alias: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Drop alias"""
    
    try:
        result = milvus_manager.drop_alias(alias)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to drop alias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )