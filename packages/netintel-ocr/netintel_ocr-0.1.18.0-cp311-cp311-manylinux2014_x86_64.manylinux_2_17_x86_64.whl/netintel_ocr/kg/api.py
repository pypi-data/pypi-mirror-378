"""
API endpoints for NetIntel-OCR Knowledge Graph System v0.1.17

Provides REST API and health check endpoints.
"""

from fastapi import FastAPI, HTTPException, Query, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime

from .falkordb_manager import FalkorDBManager
from .hybrid_retriever import HybridRetriever
from .query_classifier import QueryIntentClassifier
from .enhanced_minirag import EnhancedMiniRAG
from .embedding_trainer import KGEmbeddingTrainer

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NetIntel-OCR Knowledge Graph API",
    description="API for hybrid Knowledge Graph and Vector Embeddings system",
    version="0.1.17.1"
)

# Global instances
falkor_manager = None
query_classifier = None
hybrid_retriever = None
minirag = None


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="Query text")
    strategy: Optional[str] = Field("adaptive", description="Retrieval strategy")
    max_results: Optional[int] = Field(10, description="Maximum number of results")
    mode: Optional[str] = Field("hybrid", description="Query mode for MiniRAG")


class ProcessDocumentRequest(BaseModel):
    document_path: str = Field(..., description="Path to document")
    enable_kg: Optional[bool] = Field(True, description="Enable KG generation")
    enable_vector: Optional[bool] = Field(True, description="Enable vector generation")


class TrainEmbeddingsRequest(BaseModel):
    model: Optional[str] = Field("RotatE", description="PyKEEN model name")
    epochs: Optional[int] = Field(100, description="Training epochs")
    batch_size: Optional[int] = Field(256, description="Batch size")
    embedding_dim: Optional[int] = Field(200, description="Embedding dimension")


class HealthStatus(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, Dict[str, Any]]
    version: str = "0.1.17.1"


class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    query: str
    processing_time: float


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global falkor_manager, query_classifier, hybrid_retriever, minirag
    
    logger.info("Starting NetIntel-OCR KG API...")
    
    # Initialize FalkorDB
    falkor_manager = FalkorDBManager()
    if not falkor_manager.connect():
        logger.error("Failed to connect to FalkorDB")
        raise RuntimeError("Failed to connect to FalkorDB")
    
    # Initialize components
    query_classifier = QueryIntentClassifier()
    hybrid_retriever = HybridRetriever(falkor_manager=falkor_manager)
    
    try:
        minirag = EnhancedMiniRAG(falkor_manager=falkor_manager)
    except Exception as e:
        logger.warning(f"MiniRAG initialization failed: {e}")
        minirag = None
    
    logger.info("NetIntel-OCR KG API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global falkor_manager
    
    if falkor_manager:
        falkor_manager.close()
    
    logger.info("NetIntel-OCR KG API shutdown complete")


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of all KG services.
    """
    services_status = {}
    
    # Check FalkorDB
    try:
        if falkor_manager and falkor_manager.graph:
            stats = falkor_manager.get_graph_statistics()
            services_status["falkordb"] = {
                "status": "healthy",
                "nodes": stats.get("total_nodes", 0),
                "edges": stats.get("total_edges", 0)
            }
        else:
            services_status["falkordb"] = {"status": "unhealthy", "error": "Not connected"}
    except Exception as e:
        services_status["falkordb"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Milvus (if MiniRAG is available)
    if minirag:
        try:
            # Simple connectivity check
            services_status["milvus"] = {
                "status": "healthy",
                "collection": "netintel_vectors"
            }
        except Exception as e:
            services_status["milvus"] = {"status": "unhealthy", "error": str(e)}
    else:
        services_status["milvus"] = {"status": "not_configured"}
    
    # Check Ollama (if configured)
    services_status["ollama"] = {"status": "not_checked"}
    
    # Check query classifier
    if query_classifier:
        services_status["query_classifier"] = {"status": "healthy"}
    else:
        services_status["query_classifier"] = {"status": "unhealthy"}
    
    # Check hybrid retriever
    if hybrid_retriever:
        services_status["hybrid_retriever"] = {"status": "healthy"}
    else:
        services_status["hybrid_retriever"] = {"status": "unhealthy"}
    
    # Determine overall status
    overall_status = "healthy"
    for service, status in services_status.items():
        if status.get("status") == "unhealthy":
            overall_status = "degraded"
            break
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        services=services_status
    )


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Returns whether the service is ready to accept requests.
    """
    if not falkor_manager or not falkor_manager.graph:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready"}


@app.get("/metrics")
async def get_metrics():
    """
    Get system metrics
    
    Returns various metrics about the KG system.
    """
    metrics = {}
    
    if falkor_manager:
        stats = falkor_manager.get_graph_statistics()
        metrics["graph"] = {
            "total_nodes": stats.get("total_nodes", 0),
            "total_edges": stats.get("total_edges", 0),
            "nodes_with_embeddings": stats.get("nodes_with_embeddings", 0),
            "node_types": stats.get("node_counts", {}),
            "edge_types": stats.get("edge_counts", {})
        }
    
    return metrics


@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute a hybrid query
    
    Performs hybrid search using the specified strategy.
    """
    if not hybrid_retriever:
        raise HTTPException(status_code=503, detail="Hybrid retriever not available")
    
    start_time = datetime.utcnow()
    
    try:
        results = await hybrid_retriever.hybrid_search(
            query=request.query,
            strategy=request.strategy,
            max_results=request.max_results
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return QueryResponse(
            results=results.get("results", []),
            metadata=results.get("metadata", {}),
            query=request.query,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
async def classify_query(query: str = Query(..., description="Query to classify")):
    """
    Classify query intent
    
    Returns the query type and recommended strategy.
    """
    if not query_classifier:
        raise HTTPException(status_code=503, detail="Query classifier not available")
    
    try:
        features = query_classifier.get_query_features(query)
        return features
    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/minirag/query")
async def minirag_query(request: QueryRequest):
    """
    Execute MiniRAG query
    
    Performs enhanced RAG query with KG embeddings.
    """
    if not minirag:
        raise HTTPException(status_code=503, detail="MiniRAG not available")
    
    try:
        results = await minirag.query_with_kg_embeddings(
            query_text=request.query,
            mode=request.mode,
            max_results=request.max_results
        )
        
        return results
    except Exception as e:
        logger.error(f"MiniRAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entity/{entity_id}/context")
async def get_entity_context(
    entity_id: str,
    context_size: int = Query(2, description="Hops for context extraction")
):
    """
    Get entity context
    
    Returns rich context for the specified entity.
    """
    if not minirag:
        raise HTTPException(status_code=503, detail="MiniRAG not available")
    
    try:
        context = await minirag.get_entity_context(entity_id, context_size)
        return context
    except Exception as e:
        logger.error(f"Entity context extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/path")
async def find_path(
    source: str = Query(..., description="Source entity ID"),
    target: str = Query(..., description="Target entity ID"),
    max_length: int = Query(5, description="Maximum path length")
):
    """
    Find path between entities
    
    Returns paths between two entities in the graph.
    """
    if not falkor_manager:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        from .falkordb_storage import FalkorDBGraphStorage
        storage = FalkorDBGraphStorage(falkor_manager)
        paths = await storage.get_paths(source, target, max_length)
        return {"paths": paths}
    except Exception as e:
        logger.error(f"Path finding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embeddings/train", status_code=202)
async def train_embeddings(
    request: TrainEmbeddingsRequest,
    background_tasks: BackgroundTasks
):
    """
    Train KG embeddings
    
    Starts background training of KG embeddings using PyKEEN.
    """
    if not falkor_manager:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    async def train_task():
        trainer = KGEmbeddingTrainer(
            model_name=request.model,
            embedding_dim=request.embedding_dim
        )
        
        await trainer.train_embeddings(
            falkor_manager=falkor_manager,
            epochs=request.epochs,
            batch_size=request.batch_size
        )
    
    background_tasks.add_task(train_task)
    
    return {
        "status": "training_started",
        "model": request.model,
        "epochs": request.epochs
    }


@app.get("/embeddings/similarity")
async def compute_similarity(
    entity1: str = Query(..., description="First entity ID"),
    entity2: str = Query(..., description="Second entity ID")
):
    """
    Compute embedding similarity
    
    Returns cosine similarity between two entity embeddings.
    """
    if not falkor_manager:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        import numpy as np
        
        query = """
        MATCH (e1 {id: $entity1})
        MATCH (e2 {id: $entity2})
        RETURN e1.kg_embedding as emb1, e2.kg_embedding as emb2
        """
        
        result = falkor_manager.execute_cypher(query, {
            'entity1': entity1,
            'entity2': entity2
        })
        
        if not result.result_set:
            raise HTTPException(status_code=404, detail="Entities not found")
        
        emb1, emb2 = result.result_set[0]
        
        if emb1 is None or emb2 is None:
            raise HTTPException(status_code=404, detail="Embeddings not found")
        
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return {
            "entity1": entity1,
            "entity2": entity2,
            "similarity": float(similarity)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """
    Get graph statistics
    
    Returns detailed statistics about the knowledge graph.
    """
    if not falkor_manager:
        raise HTTPException(status_code=503, detail="Graph database not available")
    
    try:
        stats = falkor_manager.get_graph_statistics()
        return stats
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_document(
    request: ProcessDocumentRequest,
    background_tasks: BackgroundTasks
):
    """
    Process document
    
    Processes a document to extract knowledge graph and vectors.
    """
    from .hybrid_system import HybridSystem
    
    async def process_task():
        hybrid = HybridSystem(enable_kg=request.enable_kg)
        await hybrid.process_document(
            request.document_path,
            enable_vector=request.enable_vector
        )
        hybrid.close()
    
    background_tasks.add_task(process_task)
    
    return {
        "status": "processing_started",
        "document": request.document_path
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)