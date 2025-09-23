"""
Analytics Dashboard API Routes
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from ..milvus.manager import MilvusManager
from ..milvus.operations import MilvusOperations
import asyncio


router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ==================== Response Models ====================

class SystemMetrics(BaseModel):
    """System metrics model"""
    documents_processed: int
    total_pages: int
    total_vectors: int
    total_storage_gb: float
    avg_processing_time_seconds: float
    success_rate: float
    active_collections: int
    total_queries_today: int


class ProcessingTrends(BaseModel):
    """Processing trends model"""
    period: str
    data_points: List[Dict[str, Any]]
    trend_direction: str  # up, down, stable
    percentage_change: float


class SearchAnalytics(BaseModel):
    """Search analytics model"""
    total_searches: int
    unique_queries: int
    avg_response_time_ms: float
    popular_queries: List[Dict[str, Any]]
    search_volume_by_hour: List[Dict[str, int]]
    zero_result_queries: List[str]


class DocumentAnalytics(BaseModel):
    """Document analytics model"""
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    avg_document_size_mb: float
    avg_pages_per_document: float
    recently_added: List[Dict[str, Any]]
    most_accessed: List[Dict[str, Any]]


class EntityAnalytics(BaseModel):
    """Entity analytics model"""
    total_entities: int
    entities_by_type: Dict[str, int]
    top_entities: List[Dict[str, Any]]
    relationship_count: int
    avg_relationships_per_entity: float
    entity_clusters: List[Dict[str, Any]]


class VectorAnalytics(BaseModel):
    """Vector database analytics"""
    total_vectors: int
    collections: List[Dict[str, Any]]
    index_coverage: float
    avg_vector_dimension: int
    search_performance_metrics: Dict[str, float]
    storage_distribution: Dict[str, float]


class DashboardData(BaseModel):
    """Complete dashboard data"""
    system_metrics: SystemMetrics
    processing_trends: ProcessingTrends
    search_analytics: SearchAnalytics
    document_analytics: DocumentAnalytics
    entity_analytics: EntityAnalytics
    vector_analytics: VectorAnalytics
    generated_at: datetime


# ==================== Analytics Endpoints ====================

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    period: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
    refresh: bool = Query(False, description="Force refresh cached data"),
):
    """
    Get complete analytics dashboard data

    Periods:
    - 1d: Last 24 hours
    - 7d: Last 7 days
    - 30d: Last 30 days
    - 90d: Last 90 days
    """

    try:
        # Gather all analytics data in parallel
        results = await asyncio.gather(
            _get_system_metrics(),
            _get_processing_trends(period),
            _get_search_analytics(period),
            _get_document_analytics(),
            _get_entity_analytics(),
            _get_vector_analytics(),
            return_exceptions=True,
        )

        # Handle any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching analytics component {i}: {str(result)}",
                )

        return DashboardData(
            system_metrics=results[0],
            processing_trends=results[1],
            search_analytics=results[2],
            document_analytics=results[3],
            entity_analytics=results[4],
            vector_analytics=results[5],
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Get current system metrics"""

    try:
        metrics = await _get_system_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=ProcessingTrends)
async def get_processing_trends(
    period: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
    metric: str = Query("documents", regex="^(documents|pages|vectors|processing_time)$"),
):
    """Get processing trends for specified metric and period"""

    try:
        trends = await _get_processing_trends(period, metric)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=SearchAnalytics)
async def get_search_analytics(
    period: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
):
    """Get search analytics for specified period"""

    try:
        analytics = await _get_search_analytics(period)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentAnalytics)
async def get_document_analytics():
    """Get document analytics"""

    try:
        analytics = await _get_document_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities", response_model=EntityAnalytics)
async def get_entity_analytics():
    """Get entity and knowledge graph analytics"""

    try:
        analytics = await _get_entity_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectors", response_model=VectorAnalytics)
async def get_vector_analytics():
    """Get vector database analytics"""

    try:
        analytics = await _get_vector_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights():
    """Get AI-generated insights and recommendations"""

    try:
        # This would use analytics data to generate insights
        insights = {
            "performance": {
                "status": "optimal",
                "recommendations": [
                    "Consider adding more processing workers during peak hours",
                    "Index optimization recommended for collection 'netintel_documents'",
                ],
            },
            "usage_patterns": {
                "peak_hours": ["9:00-11:00", "14:00-16:00"],
                "common_query_patterns": ["network configuration", "security policies"],
                "underutilized_features": ["knowledge graph queries", "diagram search"],
            },
            "optimization_opportunities": [
                {
                    "area": "search_performance",
                    "impact": "high",
                    "recommendation": "Enable query caching for frequent searches",
                },
                {
                    "area": "storage",
                    "impact": "medium",
                    "recommendation": "Archive documents older than 90 days",
                },
            ],
        }

        return insights

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_analytics(
    format: str = Query("json", regex="^(json|csv|excel)$"),
    period: str = Query("30d", regex="^(1d|7d|30d|90d)$"),
):
    """Export analytics data in various formats"""

    try:
        # Get dashboard data
        data = await get_dashboard_data(period=period)

        if format == "json":
            return data.dict()
        elif format == "csv":
            # Would convert to CSV format
            return {"message": "CSV export not yet implemented"}
        elif format == "excel":
            # Would generate Excel file
            return {"message": "Excel export not yet implemented"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

async def _get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""

    # In production, these would come from actual data sources
    # For now, using mock data

    return SystemMetrics(
        documents_processed=1250,
        total_pages=45000,
        total_vectors=150000,
        total_storage_gb=12.5,
        avg_processing_time_seconds=3.2,
        success_rate=0.98,
        active_collections=5,
        total_queries_today=450,
    )


async def _get_processing_trends(period: str, metric: str = "documents") -> ProcessingTrends:
    """Get processing trends"""

    # Calculate period in days
    period_days = {
        "1d": 1,
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }.get(period, 7)

    # Generate mock trend data
    data_points = []
    base_value = 100

    for i in range(period_days):
        date = datetime.utcnow() - timedelta(days=period_days - i)
        value = base_value + (i * 10)  # Upward trend

        data_points.append({
            "date": date.isoformat(),
            "value": value,
            "metric": metric,
        })

    # Calculate trend
    first_value = data_points[0]["value"]
    last_value = data_points[-1]["value"]
    percentage_change = ((last_value - first_value) / first_value) * 100

    trend_direction = "up" if percentage_change > 0 else "down" if percentage_change < 0 else "stable"

    return ProcessingTrends(
        period=period,
        data_points=data_points,
        trend_direction=trend_direction,
        percentage_change=percentage_change,
    )


async def _get_search_analytics(period: str) -> SearchAnalytics:
    """Get search analytics"""

    # Mock data
    return SearchAnalytics(
        total_searches=3450,
        unique_queries=890,
        avg_response_time_ms=125.5,
        popular_queries=[
            {"query": "firewall configuration", "count": 45},
            {"query": "network topology", "count": 38},
            {"query": "security policies", "count": 32},
        ],
        search_volume_by_hour=[
            {"hour": i, "count": 50 + (i % 10) * 5}
            for i in range(24)
        ],
        zero_result_queries=["obscure query", "typo serarch"],
    )


async def _get_document_analytics() -> DocumentAnalytics:
    """Get document analytics"""

    return DocumentAnalytics(
        total_documents=1250,
        documents_by_type={
            "pdf": 850,
            "docx": 250,
            "txt": 150,
        },
        documents_by_status={
            "processed": 1200,
            "processing": 30,
            "failed": 20,
        },
        avg_document_size_mb=2.5,
        avg_pages_per_document=36,
        recently_added=[
            {
                "id": "doc_1",
                "name": "Network Security Guide.pdf",
                "added": datetime.utcnow().isoformat(),
            },
            {
                "id": "doc_2",
                "name": "Firewall Configuration.docx",
                "added": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            },
        ],
        most_accessed=[
            {
                "id": "doc_3",
                "name": "Best Practices.pdf",
                "access_count": 234,
            },
            {
                "id": "doc_4",
                "name": "Troubleshooting Guide.pdf",
                "access_count": 189,
            },
        ],
    )


async def _get_entity_analytics() -> EntityAnalytics:
    """Get entity analytics"""

    return EntityAnalytics(
        total_entities=25000,
        entities_by_type={
            "Router": 5000,
            "Switch": 3500,
            "Firewall": 2000,
            "Server": 8000,
            "VLAN": 4000,
            "IP_Address": 2500,
        },
        top_entities=[
            {"name": "Core-Router-01", "type": "Router", "references": 145},
            {"name": "Main-Firewall", "type": "Firewall", "references": 98},
            {"name": "DMZ-Switch", "type": "Switch", "references": 76},
        ],
        relationship_count=45000,
        avg_relationships_per_entity=1.8,
        entity_clusters=[
            {"cluster_id": "1", "name": "Production Network", "size": 450},
            {"cluster_id": "2", "name": "DMZ", "size": 120},
            {"cluster_id": "3", "name": "Development", "size": 230},
        ],
    )


async def _get_vector_analytics() -> VectorAnalytics:
    """Get vector analytics"""

    milvus_manager = MilvusManager()

    try:
        # Get collection information
        collections = milvus_manager.list_collections()

        collection_data = []
        total_vectors = 0

        for collection in collections:
            collection_data.append({
                "name": collection["name"],
                "vectors": collection["num_entities"],
                "loaded": collection["loaded"],
                "indexes": len(collection.get("indexes", [])),
            })
            total_vectors += collection["num_entities"]

        return VectorAnalytics(
            total_vectors=total_vectors,
            collections=collection_data,
            index_coverage=0.95,
            avg_vector_dimension=768,
            search_performance_metrics={
                "avg_latency_ms": 12.5,
                "p95_latency_ms": 25.0,
                "p99_latency_ms": 45.0,
                "qps": 150,
            },
            storage_distribution={
                "documents": 0.6,
                "entities": 0.25,
                "queries": 0.15,
            },
        )

    except Exception:
        # Return mock data if Milvus is not available
        return VectorAnalytics(
            total_vectors=150000,
            collections=[
                {"name": "netintel_documents", "vectors": 100000, "loaded": True, "indexes": 1},
                {"name": "netintel_entities", "vectors": 30000, "loaded": True, "indexes": 1},
                {"name": "netintel_queries", "vectors": 20000, "loaded": False, "indexes": 0},
            ],
            index_coverage=0.95,
            avg_vector_dimension=768,
            search_performance_metrics={
                "avg_latency_ms": 12.5,
                "p95_latency_ms": 25.0,
                "p99_latency_ms": 45.0,
                "qps": 150,
            },
            storage_distribution={
                "documents": 0.6,
                "entities": 0.25,
                "queries": 0.15,
            },
        )