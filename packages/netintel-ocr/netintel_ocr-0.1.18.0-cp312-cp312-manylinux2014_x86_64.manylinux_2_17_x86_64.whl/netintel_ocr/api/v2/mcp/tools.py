"""
Enhanced MCP Tools for NetIntel-OCR API v2
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import asyncio
from mcp import Tool, tool
from ..services.processing import processing_service
from ..services.upload import upload_service
from ..services.versioning import versioning_service
from ..services.pipeline import embedding_pipeline
from ..milvus.search import MilvusSearchEngine
from ..milvus.manager import MilvusManager
from ..milvus.operations import MilvusOperations


# ==================== Document Operation Tools ====================

@tool()
async def intelligent_query(
    query: str,
    mode: str = "auto",  # auto|specific|exploratory
    context_window: int = 5,
    include_reasoning: bool = True
) -> Dict[str, Any]:
    """
    Intelligent query with automatic mode selection

    Modes:
    - auto: Automatically determine best search strategy
    - specific: Direct factual queries
    - exploratory: Broad exploration queries
    """

    search_engine = MilvusSearchEngine()

    # Determine search strategy based on mode
    if mode == "auto":
        # Analyze query to determine best approach
        if "how" in query.lower() or "why" in query.lower():
            strategy = "hybrid"
        elif "similar" in query.lower() or "like" in query.lower():
            strategy = "similarity"
        else:
            strategy = "vector"
    else:
        strategy = "vector" if mode == "specific" else "hybrid"

    # Execute search
    if strategy == "vector":
        results = search_engine.vector_search(
            collection_name="netintel_documents",
            query_texts=query,
            limit=context_window * 2,
        )
    elif strategy == "similarity":
        # Extract reference from query
        results = search_engine.vector_search(
            collection_name="netintel_documents",
            query_texts=query,
            limit=context_window * 2,
        )
    else:  # hybrid
        results = search_engine.hybrid_search(
            collection_name="netintel_documents",
            text_query={"query": query},
            limit=context_window * 2,
        )

    # Add reasoning if requested
    if include_reasoning:
        results["reasoning"] = {
            "mode_used": mode,
            "strategy": strategy,
            "confidence": results.get("confidence", 0.85),
        }

    return results


@tool()
async def compare_documents(
    document_ids: List[str],
    comparison_type: str = "content",  # content|structure|diagrams|tables
    highlight_differences: bool = True
) -> Dict[str, Any]:
    """Compare multiple documents"""

    comparisons = {}

    for i, doc1_id in enumerate(document_ids):
        for doc2_id in document_ids[i+1:]:
            comparison_key = f"{doc1_id}_vs_{doc2_id}"

            # Get document versions for comparison
            v1 = versioning_service.get_current_version(doc1_id)
            v2 = versioning_service.get_current_version(doc2_id)

            if v1 and v2:
                comparison = versioning_service.compare_versions(
                    doc1_id,
                    v1.version_id,
                    v2.version_id,
                )
                comparisons[comparison_key] = comparison

    return {
        "comparison_type": comparison_type,
        "documents": document_ids,
        "comparisons": comparisons,
        "highlight_differences": highlight_differences,
    }


@tool()
async def analyze_network_path(
    source: str,
    destination: str,
    document_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze network paths between devices"""

    # This would integrate with knowledge graph
    # For now, return mock analysis

    paths = [
        {
            "path_id": "path1",
            "nodes": [source, "Router1", "Switch1", destination],
            "hops": 3,
            "latency_ms": 15,
            "bandwidth_mbps": 1000,
        },
        {
            "path_id": "path2",
            "nodes": [source, "Router2", "Switch2", "Switch1", destination],
            "hops": 4,
            "latency_ms": 20,
            "bandwidth_mbps": 500,
        },
    ]

    return {
        "source": source,
        "destination": destination,
        "paths_found": len(paths),
        "optimal_path": paths[0],
        "all_paths": paths,
        "analysis": {
            "redundancy": len(paths) > 1,
            "max_bandwidth": max(p["bandwidth_mbps"] for p in paths),
            "min_latency": min(p["latency_ms"] for p in paths),
        },
    }


@tool()
async def check_compliance(
    document_id: str,
    standards: List[str] = None,
    generate_report: bool = True
) -> Dict[str, Any]:
    """Check document against compliance standards"""

    if standards is None:
        standards = ["NIST", "ISO27001", "PCI-DSS"]

    # This would perform actual compliance checking
    # For now, return mock results

    compliance_results = {}
    for standard in standards:
        compliance_results[standard] = {
            "compliant": True,
            "score": 0.92,
            "violations": [],
            "warnings": [
                "Password policy should be more restrictive",
                "Audit logging retention period not specified",
            ],
        }

    if generate_report:
        report = {
            "document_id": document_id,
            "timestamp": datetime.utcnow().isoformat(),
            "standards_checked": standards,
            "overall_compliance": all(r["compliant"] for r in compliance_results.values()),
            "details": compliance_results,
        }
        return report

    return compliance_results


@tool()
async def extract_entities(
    document_id: str,
    entity_types: List[str] = None,
    include_relationships: bool = True
) -> Dict[str, Any]:
    """Extract specific entities from documents"""

    if entity_types is None:
        entity_types = ["devices", "ip_addresses", "vlans", "protocols"]

    # This would extract actual entities
    # For now, return mock data

    entities = {
        "devices": [
            {"name": "Router-Core-01", "type": "router", "vendor": "Cisco"},
            {"name": "Switch-Dist-01", "type": "switch", "vendor": "Juniper"},
        ],
        "ip_addresses": [
            {"address": "192.168.1.1", "type": "gateway"},
            {"address": "10.0.0.1", "type": "management"},
        ],
        "vlans": [
            {"id": 100, "name": "Production", "subnet": "192.168.100.0/24"},
            {"id": 200, "name": "DMZ", "subnet": "192.168.200.0/24"},
        ],
    }

    relationships = []
    if include_relationships:
        relationships = [
            {"source": "Router-Core-01", "target": "Switch-Dist-01", "type": "connected"},
            {"source": "192.168.1.1", "target": "Router-Core-01", "type": "assigned_to"},
        ]

    return {
        "document_id": document_id,
        "entities": entities,
        "relationships": relationships,
        "total_entities": sum(len(e) for e in entities.values()),
        "total_relationships": len(relationships),
    }


# ==================== Milvus Operation Tools ====================

@tool()
async def create_milvus_collection(
    name: str,
    description: str,
    dimension: int = 768,
    metric_type: str = "IP",
    index_type: str = "IVF_FLAT",
    auto_index: bool = True,
    enable_dynamic_field: bool = False
) -> Dict[str, Any]:
    """
    Create a new Milvus collection for document embeddings

    Args:
        name: Collection name
        description: Collection description
        dimension: Vector dimension (default: 768 for BERT-like models)
        metric_type: Distance metric (IP, L2, COSINE)
        index_type: Index type (IVF_FLAT, IVF_SQ8, HNSW, AUTOINDEX)
        auto_index: Automatically create index after creation
        enable_dynamic_field: Allow dynamic schema fields

    Returns:
        Collection information including schema and status
    """

    manager = MilvusManager()

    result = manager.create_collection(
        collection_name=name,
        description=description,
        embedding_dim=dimension,
        enable_dynamic_field=enable_dynamic_field,
        auto_index=auto_index,
        index_params={
            "metric_type": metric_type,
            "index_type": index_type,
        },
    )

    return result


@tool()
async def milvus_vector_search(
    query_text: Optional[str] = None,
    query_vector: Optional[List[float]] = None,
    collection: str = "netintel_documents",
    limit: int = 10,
    filter_expression: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform vector similarity search in Milvus

    Args:
        query_text: Text to convert to embedding (auto-embedded)
        query_vector: Pre-computed query vector
        collection: Collection name
        limit: Number of results
        filter_expression: Milvus filter expression (e.g., "page > 10")

    Returns:
        Search results with scores and metadata
    """

    search_engine = MilvusSearchEngine()

    results = search_engine.vector_search(
        collection_name=collection,
        query_texts=query_text,
        query_vectors=query_vector,
        filter_expression=filter_expression,
        limit=limit,
    )

    return results


@tool()
async def milvus_hybrid_search(
    vector_query: Dict[str, Any],
    scalar_filters: Dict[str, Any],
    text_search: Optional[Dict[str, Any]] = None,
    weights: Dict[str, float] = None,
    collection: str = "netintel_documents",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Perform hybrid search combining vector and scalar queries

    Combines:
        - Vector similarity search
        - Scalar field filtering
        - Optional text search
        - Result reranking
    """

    if weights is None:
        weights = {"vector": 0.7, "text": 0.3}

    search_engine = MilvusSearchEngine()

    results = search_engine.hybrid_search(
        collection_name=collection,
        vector_query=vector_query,
        scalar_filters=scalar_filters,
        text_query=text_search,
        weights=weights,
        limit=limit,
        rerank=True,
    )

    return results


@tool()
async def manage_milvus_collection(
    collection_name: str,
    operation: str = "load",  # load|release|flush|compact|drop
    partition_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage Milvus collection operations

    Operations:
        - load: Load collection into memory
        - release: Release collection from memory
        - flush: Flush pending data to disk
        - compact: Compact collection segments
        - drop: Delete collection (requires confirmation)
    """

    manager = MilvusManager()

    if operation == "load":
        result = manager.load_collection(collection_name)
    elif operation == "release":
        result = manager.release_collection(collection_name)
    elif operation == "flush":
        result = manager.flush_collection(collection_name)
    elif operation == "compact":
        result = manager.compact_collection(collection_name)
    elif operation == "drop":
        result = manager.drop_collection(collection_name, confirm=True)
    else:
        result = {"error": f"Unknown operation: {operation}"}

    return result


@tool()
async def get_collection_stats(
    collection_name: str,
    include_partitions: bool = True,
    include_indexes: bool = True,
    include_segments: bool = False
) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a Milvus collection

    Returns:
        - Row count and data size
        - Partition information
        - Index details and build progress
        - Memory usage and performance metrics
    """

    manager = MilvusManager()

    stats = manager.get_collection_stats(collection_name)
    details = manager.get_collection_details(collection_name)

    result = {
        **stats,
        **details,
    }

    return result


# ==================== Knowledge Graph Tools ====================

@tool()
async def kg_initialize(
    graph_name: str = "netintel_kg",
    connection_string: str = "redis://localhost:6379",
    create_indices: bool = True,
    schema_version: str = "2.0"
) -> Dict[str, Any]:
    """
    Initialize FalkorDB knowledge graph with schema and indices

    Returns:
        Connection status, schema creation results, index status
    """

    # This would initialize the actual KG
    # For now, return mock response

    return {
        "status": "initialized",
        "graph_name": graph_name,
        "connection": "connected",
        "indices_created": create_indices,
        "schema_version": schema_version,
        "timestamp": datetime.utcnow().isoformat(),
    }


@tool()
async def kg_cypher_query(
    query: str,
    parameters: Optional[Dict] = None,
    limit: int = 100,
    timeout: int = 30,
    return_format: str = "json"  # json|graphml|cytoscape
) -> Dict[str, Any]:
    """
    Execute Cypher query on FalkorDB

    Example queries:
        - MATCH (n:Router) RETURN n LIMIT 10
        - MATCH p=(n:Device)-[:CONNECTS_TO*1..3]-(m:Device) RETURN p
        - MATCH (n) WHERE n.zone = 'DMZ' RETURN n
    """

    # This would execute actual Cypher query
    # For now, return mock results

    return {
        "query": query,
        "results": [
            {"node": {"id": "n1", "type": "Router", "name": "Core-Router-01"}},
            {"node": {"id": "n2", "type": "Switch", "name": "Switch-01"}},
        ],
        "result_count": 2,
        "execution_time": 0.125,
        "format": return_format,
    }


@tool()
async def kg_hybrid_search(
    query: str,
    strategy: str = "adaptive",  # vector_first|graph_first|parallel|adaptive
    vector_weight: float = 0.6,
    graph_weight: float = 0.4,
    intent_classification: bool = True,
    rerank: bool = True,
    limit: int = 20,
    min_confidence: float = 0.5
) -> Dict[str, Any]:
    """
    Perform hybrid search combining KG and vector retrieval

    Strategies:
        - vector_first: Vector search then KG enrichment
        - graph_first: KG traversal then vector similarity
        - parallel: Both searches with RRF fusion
        - adaptive: Auto-select based on query intent

    Returns:
        Merged results with sources, confidence scores, and explanations
    """

    # This would perform actual hybrid search
    # For now, return mock results

    return {
        "query": query,
        "strategy_used": strategy,
        "results": [
            {
                "content": "Network configuration for DMZ router",
                "score": 0.92,
                "source": "hybrid",
                "kg_entities": ["Router-Core-01", "DMZ"],
                "confidence": 0.88,
            },
        ],
        "vector_results": 5,
        "graph_results": 3,
        "merged_results": 8,
        "execution_time": 0.245,
    }


@tool()
async def kg_find_paths(
    source: str,
    target: str,
    max_depth: int = 5,
    path_types: Optional[List[str]] = None,  # ["CONNECTS_TO", "ROUTES_TO"]
    bidirectional: bool = True,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find paths between entities in knowledge graph

    Returns:
        All paths with hop count, intermediate nodes, and properties
    """

    if path_types is None:
        path_types = ["CONNECTS_TO", "ROUTES_TO"]

    # This would find actual paths
    # For now, return mock paths

    return {
        "source": source,
        "target": target,
        "paths": [
            {
                "length": 3,
                "nodes": [source, "Router1", "Switch1", target],
                "relationships": path_types,
                "properties": {},
            },
        ],
        "shortest_path_length": 3,
        "paths_found": 1,
    }


@tool()
async def kg_rag_query(
    question: str,
    mode: str = "hybrid",  # minirag_only|kg_embedding_only|hybrid
    context_window: int = 5,
    include_sources: bool = True,
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Answer questions using RAG with KG context

    Returns:
        Generated answer, source documents, confidence score
    """

    # This would perform actual RAG
    # For now, return mock response

    answer = (
        "Based on the network documentation, the DMZ is protected by "
        "a dual firewall configuration with IPS/IDS monitoring. "
        "Traffic flows through the perimeter firewall first, then "
        "through the internal firewall before reaching production systems."
    )

    sources = []
    if include_sources:
        sources = [
            {"document": "security_guide.pdf", "page": 23, "relevance": 0.92},
            {"document": "network_topology.pdf", "page": 15, "relevance": 0.88},
        ]

    return {
        "question": question,
        "answer": answer,
        "confidence": 0.89,
        "sources": sources,
        "mode_used": mode,
        "tokens_used": len(answer.split()),
    }