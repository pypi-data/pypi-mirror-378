"""
Advanced Search API Routes
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ..milvus.search import MilvusSearchEngine
from ..services.embedding import get_embedding_service
from ..exceptions import MilvusSearchError, ValidationError


router = APIRouter(prefix="/search", tags=["Search"])


# ==================== Request/Response Models ====================

class AdvancedSearchRequest(BaseModel):
    """Advanced search request model"""
    query: str = Field(..., description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filter conditions")
    document_types: Optional[List[str]] = Field(default=None, description="Document types to search")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Date range filter")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    search_in: List[str] = Field(default=["content", "diagrams", "tables"])
    aggregations: Optional[Dict[str, Any]] = Field(default=None, description="Aggregation options")
    highlight: bool = Field(default=True, description="Enable highlighting")
    snippet_size: int = Field(default=200, ge=50, le=500)
    rerank: bool = Field(default=True, description="Enable result reranking")
    explain: bool = Field(default=False, description="Include explanation")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class HybridSearchRequest(BaseModel):
    """Hybrid search request"""
    vector_query: Optional[Dict[str, Any]] = Field(default=None, description="Vector search params")
    scalar_filters: Optional[Dict[str, Any]] = Field(default=None, description="Scalar filters")
    text_query: Optional[Dict[str, Any]] = Field(default=None, description="Text search params")
    weights: Dict[str, float] = Field(default={"vector": 0.7, "scalar": 0.3})
    limit: int = Field(default=20, ge=1, le=100)
    rerank: bool = Field(default=True)
    output_fields: Optional[List[str]] = Field(default=None)


class SimilaritySearchRequest(BaseModel):
    """Similarity search request"""
    reference_id: str = Field(..., description="Reference document/entity ID")
    collection: str = Field(default="netintel_documents")
    similarity_type: str = Field(default="vector", description="vector|structural|semantic|hybrid")
    limit: int = Field(default=20, ge=1, le=100)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = Field(default=None)


class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    total_results: int
    returned_results: int
    results: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Any]] = None
    facets: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    execution_time: float
    timestamp: str


class SearchAggregations(BaseModel):
    """Search aggregations response"""
    by_type: Optional[Dict[str, int]] = None
    by_date: Optional[Dict[str, int]] = None
    by_confidence: Optional[Dict[str, int]] = None
    top_entities: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None


# ==================== Search Endpoints ====================

@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(request: AdvancedSearchRequest):
    """
    Perform advanced search with multiple options

    Features:
    - Full-text and vector search
    - Complex filtering
    - Aggregations and facets
    - Result reranking
    - Query explanation
    """

    try:
        start_time = datetime.utcnow()
        search_engine = MilvusSearchEngine()

        # Build filter expression
        filter_expr = _build_filter_expression(
            request.filters,
            request.document_types,
            request.date_range,
            request.confidence_threshold,
        )

        # Perform search based on search_in fields
        all_results = []

        if "content" in request.search_in:
            content_results = await _search_content(
                search_engine,
                request.query,
                filter_expr,
                request.limit * 2,  # Get more for reranking
            )
            all_results.extend(content_results)

        if "diagrams" in request.search_in:
            diagram_results = await _search_diagrams(
                search_engine,
                request.query,
                filter_expr,
                request.limit,
            )
            all_results.extend(diagram_results)

        if "tables" in request.search_in:
            table_results = await _search_tables(
                search_engine,
                request.query,
                filter_expr,
                request.limit,
            )
            all_results.extend(table_results)

        # Rerank results if requested
        if request.rerank and len(all_results) > 0:
            all_results = await _rerank_results(all_results, request.query)

        # Apply pagination
        paginated_results = all_results[request.offset:request.offset + request.limit]

        # Add highlights and snippets
        if request.highlight:
            paginated_results = _add_highlights(
                paginated_results,
                request.query,
                request.snippet_size,
            )

        # Calculate aggregations if requested
        aggregations = None
        if request.aggregations:
            aggregations = _calculate_aggregations(all_results, request.aggregations)

        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return SearchResponse(
            query=request.query,
            total_results=len(all_results),
            returned_results=len(paginated_results),
            results=paginated_results,
            aggregations=aggregations,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(request: HybridSearchRequest):
    """
    Perform hybrid search combining vector and scalar queries

    Combines:
    - Vector similarity search
    - Scalar field filtering
    - Text search
    - Result reranking with weighted fusion
    """

    try:
        start_time = datetime.utcnow()
        search_engine = MilvusSearchEngine()

        result = search_engine.hybrid_search(
            collection_name="netintel_documents",
            vector_query=request.vector_query,
            scalar_filters=request.scalar_filters,
            text_query=request.text_query,
            weights=request.weights,
            limit=request.limit,
            rerank=request.rerank,
            output_fields=request.output_fields,
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return SearchResponse(
            query=str(request.text_query or request.vector_query or "hybrid"),
            total_results=result["result_count"],
            returned_results=len(result["results"]),
            results=result["results"],
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat(),
        )

    except MilvusSearchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similarity", response_model=SearchResponse)
async def similarity_search(request: SimilaritySearchRequest):
    """
    Find similar documents/entities based on a reference

    Types:
    - vector: Embedding similarity
    - structural: Graph structure similarity
    - semantic: Meaning-based similarity
    - hybrid: Combined approach
    """

    try:
        start_time = datetime.utcnow()
        search_engine = MilvusSearchEngine()

        result = search_engine.similarity_search(
            collection_name=request.collection,
            reference_id=request.reference_id,
            output_fields=["document_id", "content", "metadata"],
            limit=request.limit,
            filter_expression=_build_filter_expression(request.filters),
        )

        # Filter by minimum similarity
        filtered_results = [
            r for r in result["results"]
            if r["score"] >= request.min_similarity
        ]

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return SearchResponse(
            query=f"similar_to:{request.reference_id}",
            total_results=len(filtered_results),
            returned_results=len(filtered_results),
            results=filtered_results,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-vector")
async def multi_vector_search(
    queries: List[Dict[str, Any]],
    aggregate_method: str = Query("max", regex="^(max|mean|sum)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Perform multiple vector searches and aggregate results

    Aggregation methods:
    - max: Maximum score across queries
    - mean: Average score
    - sum: Sum of scores
    """

    try:
        search_engine = MilvusSearchEngine()

        result = search_engine.multi_vector_search(
            collection_name="netintel_documents",
            queries=queries,
            aggregate_method=aggregate_method,
            limit=limit,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest")
async def search_suggestions(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
):
    """Get search suggestions based on partial query"""

    # This would implement search suggestions
    # For now, return mock suggestions

    suggestions = [
        f"{query} configuration",
        f"{query} setup",
        f"{query} troubleshooting",
        f"{query} best practices",
    ][:limit]

    return {
        "query": query,
        "suggestions": suggestions,
    }


@router.get("/facets")
async def get_search_facets(collection: str = "netintel_documents"):
    """Get available search facets for filtering"""

    # This would return available facets from the collection

    return {
        "collection": collection,
        "facets": {
            "content_type": ["text", "table", "diagram"],
            "confidence_range": [0.0, 0.5, 0.8, 0.9, 1.0],
            "page_range": [1, 10, 50, 100],
            "document_types": ["pdf", "docx", "txt"],
        },
    }


# ==================== Helper Functions ====================

def _build_filter_expression(
    filters: Optional[Dict[str, Any]] = None,
    document_types: Optional[List[str]] = None,
    date_range: Optional[Dict[str, str]] = None,
    confidence_threshold: float = 0.0,
) -> Optional[str]:
    """Build Milvus filter expression from parameters"""

    expressions = []

    if filters:
        for field, value in filters.items():
            if isinstance(value, list):
                values_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                expressions.append(f"{field} in [{values_str}]")
            elif isinstance(value, str):
                expressions.append(f'{field} == "{value}"')
            else:
                expressions.append(f"{field} == {value}")

    if document_types:
        types_str = ", ".join([f'"{t}"' for t in document_types])
        expressions.append(f"content_type in [{types_str}]")

    if date_range:
        if "start" in date_range:
            expressions.append(f"created_at >= {date_range['start']}")
        if "end" in date_range:
            expressions.append(f"created_at <= {date_range['end']}")

    if confidence_threshold > 0:
        expressions.append(f"confidence >= {confidence_threshold}")

    return " && ".join(expressions) if expressions else None


async def _search_content(
    engine: MilvusSearchEngine,
    query: str,
    filter_expr: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    """Search in document content"""

    result = engine.vector_search(
        collection_name="netintel_documents",
        query_texts=query,
        filter_expression=filter_expr,
        limit=limit,
        output_fields=["document_id", "content", "page_number", "metadata"],
    )

    return result.get("results", [])


async def _search_diagrams(
    engine: MilvusSearchEngine,
    query: str,
    filter_expr: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    """Search in diagrams"""

    # Add content_type filter for diagrams
    diagram_filter = 'content_type == "diagram"'
    if filter_expr:
        filter_expr = f"({filter_expr}) && {diagram_filter}"
    else:
        filter_expr = diagram_filter

    result = engine.vector_search(
        collection_name="netintel_documents",
        query_texts=query,
        filter_expression=filter_expr,
        limit=limit,
    )

    return result.get("results", [])


async def _search_tables(
    engine: MilvusSearchEngine,
    query: str,
    filter_expr: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    """Search in tables"""

    # Add content_type filter for tables
    table_filter = 'content_type == "table"'
    if filter_expr:
        filter_expr = f"({filter_expr}) && {table_filter}"
    else:
        filter_expr = table_filter

    result = engine.vector_search(
        collection_name="netintel_documents",
        query_texts=query,
        filter_expression=filter_expr,
        limit=limit,
    )

    return result.get("results", [])


async def _rerank_results(
    results: List[Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Rerank search results"""

    # Simple reranking based on score
    # In production, this would use a more sophisticated reranking model

    return sorted(results, key=lambda x: x.get("score", 0), reverse=True)


def _add_highlights(
    results: List[Dict[str, Any]],
    query: str,
    snippet_size: int,
) -> List[Dict[str, Any]]:
    """Add highlights and snippets to results"""

    query_terms = query.lower().split()

    for result in results:
        content = result.get("content", "")

        # Find query terms in content
        highlights = []
        for term in query_terms:
            if term in content.lower():
                highlights.append(term)

        # Create snippet
        snippet = content[:snippet_size]
        if len(content) > snippet_size:
            snippet += "..."

        result["highlights"] = highlights
        result["snippet"] = snippet

    return results


def _calculate_aggregations(
    results: List[Dict[str, Any]],
    agg_options: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate aggregations from results"""

    aggregations = {}

    # Count by content type
    if agg_options.get("by_type"):
        type_counts = {}
        for result in results:
            content_type = result.get("content_type", "unknown")
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        aggregations["by_type"] = type_counts

    # Statistics
    if agg_options.get("statistics"):
        scores = [r.get("score", 0) for r in results]
        if scores:
            aggregations["statistics"] = {
                "min_score": min(scores),
                "max_score": max(scores),
                "avg_score": sum(scores) / len(scores),
            }

    return aggregations