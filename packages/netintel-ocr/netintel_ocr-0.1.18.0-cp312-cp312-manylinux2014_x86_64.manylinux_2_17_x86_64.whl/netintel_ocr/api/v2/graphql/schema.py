"""
GraphQL Schema for NetIntel-OCR API v2
"""

import strawberry
from strawberry.types import Info
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


# ==================== Type Definitions ====================

@strawberry.type
class DocumentMetadata:
    """Document metadata type"""
    title: Optional[str]
    author: Optional[str]
    created_at: datetime
    modified_at: datetime
    file_size: int
    page_count: int
    processing_status: str
    tags: List[str]
    confidence_score: float


@strawberry.type
class DocumentContent:
    """Document content type"""
    page: int
    text: str
    confidence: float
    language: Optional[str]
    word_count: int
    character_count: int


@strawberry.type
class TableData:
    """Table data type"""
    table_id: str
    page: int
    headers: List[str]
    rows: List[List[str]]
    row_count: int
    column_count: int
    caption: Optional[str]


@strawberry.type
class DiagramDevice:
    """Network device in diagram"""
    device_id: str
    device_type: str
    name: str
    properties: Optional[str]  # JSON string


@strawberry.type
class DiagramConnection:
    """Connection in network diagram"""
    source: str
    target: str
    connection_type: Optional[str]
    properties: Optional[str]  # JSON string


@strawberry.type
class NetworkDiagram:
    """Network diagram type"""
    diagram_id: str
    page: int
    diagram_type: str
    description: Optional[str]
    mermaid_code: Optional[str]
    devices: List[DiagramDevice]
    connections: List[DiagramConnection]


@strawberry.type
class KnowledgeEntity:
    """Knowledge graph entity"""
    entity_id: str
    entity_type: str
    name: str
    properties: Optional[str]  # JSON string
    confidence: float


@strawberry.type
class KnowledgeRelationship:
    """Knowledge graph relationship"""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Optional[str]  # JSON string
    confidence: float


@strawberry.type
class KnowledgeGraph:
    """Knowledge graph type"""
    document_id: str
    entities: List[KnowledgeEntity]
    relationships: List[KnowledgeRelationship]
    entity_count: int
    relationship_count: int


@strawberry.type
class SearchResult:
    """Search result type"""
    document_id: str
    score: float
    snippet: str
    highlights: List[str]
    metadata: DocumentMetadata
    page: Optional[int]


@strawberry.type
class Document:
    """Main document type"""
    id: str
    metadata: DocumentMetadata
    content: List[DocumentContent]
    tables: List[TableData]
    diagrams: List[NetworkDiagram]
    knowledge_graph: Optional[KnowledgeGraph]

    @strawberry.field
    async def content_by_page(self, page: int) -> Optional[DocumentContent]:
        """Get content for a specific page"""
        for content in self.content:
            if content.page == page:
                return content
        return None

    @strawberry.field
    async def search_in_document(self, query: str) -> List[SearchResult]:
        """Search within this document"""
        # Implementation would search within document
        return []


@strawberry.type
class ProcessingJob:
    """Processing job type"""
    job_id: str
    document_id: str
    status: str
    progress: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]


@strawberry.type
class VectorSearchResult:
    """Vector search result"""
    id: str
    score: float
    distance: float
    document_id: str
    content: str
    metadata: Optional[str]  # JSON string


@strawberry.type
class CollectionInfo:
    """Milvus collection information"""
    name: str
    description: Optional[str]
    num_entities: int
    loaded: bool
    index_progress: float
    partitions: List[str]


@strawberry.type
class AnalyticsData:
    """Analytics data type"""
    total_documents: int
    total_pages: int
    total_tables: int
    total_diagrams: int
    total_entities: int
    total_relationships: int
    processing_jobs: int
    average_processing_time: float
    storage_used: int
    vector_count: int


# ==================== Input Types ====================

@strawberry.input
class DocumentUploadInput:
    """Input for document upload"""
    filename: str
    file_size: int
    content_type: str
    options: Optional[str]  # JSON string with processing options


@strawberry.input
class SearchInput:
    """Input for search queries"""
    query: str
    document_types: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    confidence_threshold: Optional[float] = 0.8
    limit: Optional[int] = 20
    offset: Optional[int] = 0


@strawberry.input
class VectorSearchInput:
    """Input for vector search"""
    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    collection: str = "netintel_documents"
    limit: int = 20
    filter_expression: Optional[str] = None


@strawberry.input
class KnowledgeGraphQueryInput:
    """Input for knowledge graph queries"""
    cypher_query: Optional[str] = None
    natural_language: Optional[str] = None
    document_ids: Optional[List[str]] = None
    entity_types: Optional[List[str]] = None
    limit: int = 100


# ==================== Query Root ====================

@strawberry.type
class Query:
    """GraphQL Query root"""

    @strawberry.field
    async def document(self, id: str) -> Optional[Document]:
        """Get a document by ID"""
        # Implementation would fetch from database
        return None

    @strawberry.field
    async def documents(
        self,
        limit: int = 20,
        offset: int = 0,
        filter: Optional[str] = None,
    ) -> List[Document]:
        """List documents with pagination"""
        # Implementation would fetch from database
        return []

    @strawberry.field
    async def search(self, input: SearchInput) -> List[SearchResult]:
        """Search across documents"""
        # Implementation would perform search
        return []

    @strawberry.field
    async def vector_search(self, input: VectorSearchInput) -> List[VectorSearchResult]:
        """Perform vector similarity search"""
        # Implementation would search Milvus
        return []

    @strawberry.field
    async def knowledge_graph_query(
        self,
        input: KnowledgeGraphQueryInput,
    ) -> KnowledgeGraph:
        """Query knowledge graph"""
        # Implementation would query knowledge graph
        return KnowledgeGraph(
            document_id="",
            entities=[],
            relationships=[],
            entity_count=0,
            relationship_count=0,
        )

    @strawberry.field
    async def processing_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get processing job status"""
        # Implementation would fetch job status
        return None

    @strawberry.field
    async def collection_info(self, name: str) -> Optional[CollectionInfo]:
        """Get Milvus collection information"""
        # Implementation would fetch collection info
        return None

    @strawberry.field
    async def analytics(self) -> AnalyticsData:
        """Get analytics data"""
        # Implementation would aggregate analytics
        return AnalyticsData(
            total_documents=0,
            total_pages=0,
            total_tables=0,
            total_diagrams=0,
            total_entities=0,
            total_relationships=0,
            processing_jobs=0,
            average_processing_time=0.0,
            storage_used=0,
            vector_count=0,
        )

    @strawberry.field
    async def find_similar_documents(
        self,
        document_id: str,
        limit: int = 10,
    ) -> List[Document]:
        """Find similar documents"""
        # Implementation would find similar documents
        return []

    @strawberry.field
    async def network_path(
        self,
        source: str,
        destination: str,
        document_ids: Optional[List[str]] = None,
    ) -> List[DiagramConnection]:
        """Find network path between devices"""
        # Implementation would find path
        return []


# ==================== Mutation Root ====================

@strawberry.type
class Mutation:
    """GraphQL Mutation root"""

    @strawberry.mutation
    async def upload_document(
        self,
        input: DocumentUploadInput,
    ) -> ProcessingJob:
        """Upload a document for processing"""
        # Implementation would start upload
        return ProcessingJob(
            job_id="",
            document_id="",
            status="queued",
            progress=0,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            error=None,
        )

    @strawberry.mutation
    async def reprocess_document(
        self,
        document_id: str,
        options: Optional[str] = None,
    ) -> ProcessingJob:
        """Reprocess an existing document"""
        # Implementation would start reprocessing
        return ProcessingJob(
            job_id="",
            document_id=document_id,
            status="queued",
            progress=0,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            error=None,
        )

    @strawberry.mutation
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        # Implementation would delete document
        return False

    @strawberry.mutation
    async def update_document_metadata(
        self,
        document_id: str,
        metadata: str,  # JSON string
    ) -> Document:
        """Update document metadata"""
        # Implementation would update metadata
        return Document(
            id=document_id,
            metadata=DocumentMetadata(
                title=None,
                author=None,
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                file_size=0,
                page_count=0,
                processing_status="",
                tags=[],
                confidence_score=0.0,
            ),
            content=[],
            tables=[],
            diagrams=[],
            knowledge_graph=None,
        )

    @strawberry.mutation
    async def create_collection(
        self,
        name: str,
        collection_type: str,
        embedding_dim: int = 768,
    ) -> CollectionInfo:
        """Create a new Milvus collection"""
        # Implementation would create collection
        return CollectionInfo(
            name=name,
            description=None,
            num_entities=0,
            loaded=False,
            index_progress=0.0,
            partitions=[],
        )

    @strawberry.mutation
    async def build_knowledge_graph(
        self,
        document_ids: List[str],
    ) -> KnowledgeGraph:
        """Build knowledge graph from documents"""
        # Implementation would build KG
        return KnowledgeGraph(
            document_id="",
            entities=[],
            relationships=[],
            entity_count=0,
            relationship_count=0,
        )


# ==================== Subscription Root ====================

@strawberry.type
class Subscription:
    """GraphQL Subscription root"""

    @strawberry.subscription
    async def processing_status(self, document_id: str) -> ProcessingJob:
        """Subscribe to processing status updates"""
        # Implementation would stream updates
        import asyncio
        while True:
            await asyncio.sleep(1)
            yield ProcessingJob(
                job_id="",
                document_id=document_id,
                status="processing",
                progress=50,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=None,
                error=None,
            )

    @strawberry.subscription
    async def search_updates(self, query: str) -> SearchResult:
        """Subscribe to search result updates"""
        # Implementation would stream new results
        import asyncio
        while True:
            await asyncio.sleep(5)
            yield SearchResult(
                document_id="",
                score=0.95,
                snippet="Sample snippet",
                highlights=["highlight"],
                metadata=DocumentMetadata(
                    title="Sample",
                    author=None,
                    created_at=datetime.utcnow(),
                    modified_at=datetime.utcnow(),
                    file_size=0,
                    page_count=0,
                    processing_status="",
                    tags=[],
                    confidence_score=0.0,
                ),
                page=1,
            )


# Create the schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)