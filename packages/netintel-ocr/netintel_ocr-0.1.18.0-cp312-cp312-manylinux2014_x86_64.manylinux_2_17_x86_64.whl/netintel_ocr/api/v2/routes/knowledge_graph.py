"""
Knowledge Graph Query API Routes
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


# ==================== Enums and Models ====================

class KGModel(str, Enum):
    """Knowledge graph embedding models"""
    TRANSE = "TransE"
    ROTATE = "RotatE"
    COMPLEX = "ComplEx"
    DISTMULT = "DistMult"
    CONVE = "ConvE"
    TUCKER = "TuckER"
    HOLE = "HolE"
    RESCAL = "RESCAL"


class IntentType(str, Enum):
    """Query intent types"""
    ENTITY_CENTRIC = "entity_centric"
    RELATIONAL = "relational"
    TOPOLOGICAL = "topological"
    SEMANTIC = "semantic"
    ANALYTICAL = "analytical"
    EXPLORATORY = "exploratory"


class RetrievalStrategy(str, Enum):
    """Retrieval strategies"""
    VECTOR_FIRST = "vector_first"
    GRAPH_FIRST = "graph_first"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


# Request/Response Models

class KGInitRequest(BaseModel):
    """Knowledge graph initialization request"""
    database: str = Field(default="falkordb", description="Database type")
    connection_string: str = Field(..., description="Database connection string")
    graph_name: str = Field(default="netintel_kg", description="Graph name")
    schema_version: str = Field(default="2.0", description="Schema version")
    create_indices: bool = Field(default=True, description="Create indices")


class KGProcessRequest(BaseModel):
    """Knowledge graph processing request"""
    document_id: str
    extraction_mode: str = Field(default="full", regex="^(entities|relationships|full)$")
    kg_model: KGModel = Field(default=KGModel.ROTATE)
    embedding_dim: int = Field(default=200, ge=50, le=500)
    include_diagrams: bool = True
    include_tables: bool = True
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class CypherQueryRequest(BaseModel):
    """Cypher query request"""
    cypher: Optional[str] = Field(default=None, description="Cypher query string")
    natural_language: Optional[str] = Field(default=None, description="Natural language query")
    visualization: bool = Field(default=False, description="Include visualization data")
    format: str = Field(default="json", regex="^(json|graphml|gexf|cytoscape)$")
    limit: int = Field(default=100, ge=1, le=1000)
    timeout: int = Field(default=30, ge=1, le=300)


class HybridRetrievalRequest(BaseModel):
    """Hybrid retrieval request"""
    query: str
    strategy: RetrievalStrategy = Field(default=RetrievalStrategy.ADAPTIVE)
    vector_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    graph_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    rerank: bool = True
    include_context: bool = True
    limit: int = Field(default=20, ge=1, le=100)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class EntityExtractionRequest(BaseModel):
    """Entity extraction request"""
    document_id: str
    entity_types: List[str] = Field(
        default=["Router", "Switch", "Firewall", "Server", "VLAN", "IP_Address"]
    )
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    include_attributes: bool = True


class PathFinderRequest(BaseModel):
    """Path finding request"""
    source_entity: str
    target_entity: str
    max_depth: int = Field(default=5, ge=1, le=10)
    path_types: Optional[List[str]] = None
    include_properties: bool = True


class NetworkAnalysisRequest(BaseModel):
    """Network topology analysis request"""
    document_ids: List[str]
    analysis_type: str = Field(default="topology", description="Analysis type")
    output_format: str = Field(default="report", regex="^(report|visualization|data)$")
    include_recommendations: bool = True


class RAGQueryRequest(BaseModel):
    """RAG query request"""
    question: str
    mode: str = Field(default="hybrid", regex="^(minirag_only|kg_embedding_only|hybrid)$")
    context_window: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True
    max_tokens: int = Field(default=500, ge=50, le=2000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


# Response Models

class KGEntity(BaseModel):
    """Knowledge graph entity"""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    confidence: float
    source_documents: List[str]


class KGRelationship(BaseModel):
    """Knowledge graph relationship"""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float


class KGQueryResult(BaseModel):
    """Knowledge graph query result"""
    query: str
    result_count: int
    entities: List[KGEntity]
    relationships: List[KGRelationship]
    execution_time: float
    visualization_data: Optional[Dict[str, Any]] = None


class HybridRetrievalResult(BaseModel):
    """Hybrid retrieval result"""
    query: str
    strategy_used: str
    results: List[Dict[str, Any]]
    vector_results_count: int
    graph_results_count: int
    final_results_count: int
    confidence_scores: Dict[str, float]
    execution_time: float


class IntentClassificationResult(BaseModel):
    """Intent classification result"""
    query: str
    intent_type: IntentType
    confidence: float
    suggested_strategy: RetrievalStrategy
    entity_types: List[str]
    relationship_types: List[str]


class RAGResponse(BaseModel):
    """RAG response"""
    question: str
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    context_used: List[str]
    mode_used: str


# ==================== Knowledge Graph Endpoints ====================

@router.post("/initialize")
async def initialize_knowledge_graph(request: KGInitRequest):
    """Initialize FalkorDB knowledge graph with schema and indices"""

    try:
        # This would initialize the KG database
        # For now, return mock response

        return {
            "status": "initialized",
            "graph_name": request.graph_name,
            "schema_version": request.schema_version,
            "indices_created": request.create_indices,
            "connection_status": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_document_kg(request: KGProcessRequest):
    """Extract knowledge graph from document"""

    try:
        # This would process the document and extract KG
        # For now, return mock response

        return {
            "document_id": request.document_id,
            "extraction_mode": request.extraction_mode,
            "kg_model": request.kg_model,
            "entities_extracted": 120,
            "relationships_extracted": 85,
            "embedding_status": "completed",
            "processing_time": 5.2,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=KGQueryResult)
async def query_knowledge_graph(request: CypherQueryRequest):
    """Execute Cypher query on FalkorDB"""

    try:
        start_time = datetime.utcnow()

        # This would execute the actual Cypher query
        # For now, return mock response

        entities = [
            KGEntity(
                entity_id="e1",
                entity_type="Router",
                name="Core-Router-01",
                properties={"zone": "DMZ", "vendor": "Cisco"},
                confidence=0.95,
                source_documents=["doc1", "doc2"],
            ),
            KGEntity(
                entity_id="e2",
                entity_type="Switch",
                name="Switch-01",
                properties={"ports": 48, "vlan": "100"},
                confidence=0.92,
                source_documents=["doc1"],
            ),
        ]

        relationships = [
            KGRelationship(
                source_id="e1",
                target_id="e2",
                relationship_type="CONNECTS_TO",
                properties={"port": "Gi0/1", "bandwidth": "10Gbps"},
                confidence=0.88,
            )
        ]

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return KGQueryResult(
            query=request.cypher or request.natural_language or "",
            result_count=len(entities),
            entities=entities,
            relationships=relationships,
            execution_time=execution_time,
            visualization_data={"nodes": len(entities), "edges": len(relationships)}
            if request.visualization
            else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid-search", response_model=HybridRetrievalResult)
async def hybrid_kg_search(request: HybridRetrievalRequest):
    """Perform hybrid search combining KG and vector retrieval"""

    try:
        start_time = datetime.utcnow()

        # This would perform actual hybrid search
        # For now, return mock response

        results = [
            {
                "id": "r1",
                "content": "Router configuration for DMZ",
                "score": 0.92,
                "source": "hybrid",
                "entity_matches": ["Core-Router-01"],
            },
            {
                "id": "r2",
                "content": "Network security policies",
                "score": 0.88,
                "source": "vector",
                "entity_matches": [],
            },
        ]

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return HybridRetrievalResult(
            query=request.query,
            strategy_used=request.strategy.value,
            results=results,
            vector_results_count=5,
            graph_results_count=3,
            final_results_count=len(results),
            confidence_scores={
                "vector": 0.85,
                "graph": 0.90,
                "combined": 0.88,
            },
            execution_time=execution_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-intent", response_model=IntentClassificationResult)
async def classify_query_intent(query: str = Body(..., embed=True)):
    """Classify query intent for optimal retrieval strategy"""

    try:
        # This would use ML to classify intent
        # For now, return mock response based on keywords

        intent_type = IntentType.ENTITY_CENTRIC
        suggested_strategy = RetrievalStrategy.GRAPH_FIRST

        if "path" in query.lower() or "route" in query.lower():
            intent_type = IntentType.TOPOLOGICAL
        elif "relationship" in query.lower() or "connected" in query.lower():
            intent_type = IntentType.RELATIONAL
        elif "what" in query.lower() or "how" in query.lower():
            intent_type = IntentType.SEMANTIC
            suggested_strategy = RetrievalStrategy.ADAPTIVE

        return IntentClassificationResult(
            query=query,
            intent_type=intent_type,
            confidence=0.85,
            suggested_strategy=suggested_strategy,
            entity_types=["Router", "Firewall"],
            relationship_types=["CONNECTS_TO", "SECURED_BY"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-entities")
async def extract_entities(request: EntityExtractionRequest):
    """Extract entities from document"""

    try:
        # This would extract entities from document
        # For now, return mock response

        entities = [
            {
                "entity_id": "e1",
                "entity_type": "Router",
                "name": "Core-Router-01",
                "confidence": 0.95,
                "attributes": {"zone": "DMZ", "model": "Cisco ASR"},
                "page": 5,
            },
            {
                "entity_id": "e2",
                "entity_type": "Firewall",
                "name": "FW-Primary",
                "confidence": 0.92,
                "attributes": {"vendor": "Palo Alto", "version": "10.1"},
                "page": 8,
            },
        ]

        return {
            "document_id": request.document_id,
            "entities_found": len(entities),
            "entities": entities,
            "entity_types": request.entity_types,
            "confidence_threshold": request.confidence_threshold,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-paths")
async def find_network_paths(request: PathFinderRequest):
    """Find paths between entities in knowledge graph"""

    try:
        # This would find actual paths in KG
        # For now, return mock response

        paths = [
            {
                "path_id": "p1",
                "length": 3,
                "nodes": ["Router-01", "Switch-01", "Server-01"],
                "edges": [
                    {"from": "Router-01", "to": "Switch-01", "type": "CONNECTS_TO"},
                    {"from": "Switch-01", "to": "Server-01", "type": "CONNECTS_TO"},
                ],
                "total_distance": 3,
            },
            {
                "path_id": "p2",
                "length": 4,
                "nodes": ["Router-01", "Firewall-01", "Switch-02", "Server-01"],
                "edges": [
                    {"from": "Router-01", "to": "Firewall-01", "type": "SECURED_BY"},
                    {"from": "Firewall-01", "to": "Switch-02", "type": "CONNECTS_TO"},
                    {"from": "Switch-02", "to": "Server-01", "type": "CONNECTS_TO"},
                ],
                "total_distance": 4,
            },
        ]

        return {
            "source": request.source_entity,
            "target": request.target_entity,
            "paths_found": len(paths),
            "paths": paths,
            "max_depth": request.max_depth,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-topology")
async def analyze_network_topology(request: NetworkAnalysisRequest):
    """Analyze network topology from documents"""

    try:
        # This would perform actual topology analysis
        # For now, return mock response

        analysis = {
            "document_ids": request.document_ids,
            "analysis_type": request.analysis_type,
            "topology": {
                "total_devices": 45,
                "device_types": {
                    "routers": 8,
                    "switches": 15,
                    "firewalls": 5,
                    "servers": 17,
                },
                "total_connections": 72,
                "network_zones": ["DMZ", "Production", "Development"],
                "redundancy_score": 0.85,
                "security_score": 0.92,
            },
            "findings": [
                {
                    "type": "single_point_of_failure",
                    "severity": "high",
                    "location": "Core-Switch-01",
                    "recommendation": "Add redundant switch for failover",
                },
                {
                    "type": "security_gap",
                    "severity": "medium",
                    "location": "DMZ-to-Production",
                    "recommendation": "Add firewall between zones",
                },
            ],
            "recommendations": [
                "Implement network segmentation for better security",
                "Add monitoring for critical network paths",
                "Consider load balancing for high-traffic routes",
            ] if request.include_recommendations else [],
        }

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/query", response_model=RAGResponse)
async def rag_query(request: RAGQueryRequest):
    """Answer questions using RAG with KG context"""

    try:
        # This would perform actual RAG query
        # For now, return mock response

        answer = (
            "Based on the network documentation, the production network "
            "consists of 3 core routers in a mesh topology with redundant "
            "connections to the distribution layer. The security policies "
            "require all traffic to pass through the perimeter firewall."
        )

        sources = [
            {
                "document_id": "doc1",
                "page": 15,
                "relevance": 0.92,
                "snippet": "Core routers are configured in mesh topology...",
            },
            {
                "document_id": "doc2",
                "page": 23,
                "relevance": 0.88,
                "snippet": "Security policies mandate firewall inspection...",
            },
        ]

        return RAGResponse(
            question=request.question,
            answer=answer,
            confidence=0.89,
            sources=sources,
            context_used=["network topology", "security policies"],
            mode_used=request.mode,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_kg_statistics():
    """Get knowledge graph statistics"""

    try:
        return {
            "total_entities": 25000,
            "total_relationships": 45000,
            "entity_types": {
                "Router": 5000,
                "Switch": 3500,
                "Firewall": 2000,
                "Server": 8000,
                "VLAN": 4000,
                "IP_Address": 2500,
            },
            "relationship_types": {
                "CONNECTS_TO": 20000,
                "SECURED_BY": 5000,
                "ROUTES_TO": 8000,
                "BELONGS_TO": 7000,
                "MANAGES": 5000,
            },
            "avg_degree": 3.6,
            "density": 0.0072,
            "connected_components": 12,
            "largest_component_size": 18500,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))