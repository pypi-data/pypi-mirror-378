"""
NetIntel-OCR Knowledge Graph Module v0.1.17

This module provides hybrid Knowledge Graph and Vector Embeddings functionality,
building upon the existing vector generation capabilities.

Phase 1 Components (COMPLETED):
- FalkorDBManager: Graph database management
- KnowledgeGraphConstructor: Graph construction from OCR content
- HybridSystem: Main orchestrator for KG+Vector processing
- CLI Commands: kg init, stats, process, query, export

Phase 2 Components (COMPLETED):
- KGEmbeddingTrainer: PyKEEN integration for training KG embeddings
- EmbeddingAnalyzer: Analysis and visualization of embeddings
- Enhanced CLI: train-embeddings, similarity, find-similar, visualize, cluster
- Embedding storage and retrieval from FalkorDB

Phase 3 Components (COMPLETED):
- FalkorDBGraphStorage: Custom MiniRAG storage adapter for FalkorDB
- EnhancedMiniRAG: Extended MiniRAG with KG embeddings support
- Hybrid query modes: minirag_only, kg_embedding_only, hybrid
- Enhanced CLI: rag-query, entity-context, path-find
- Integration with Milvus for text embeddings

Phase 4-5 Components (To be implemented):
- Query intent classifier
- Advanced hybrid retrieval strategies
- Full integration and testing
"""

from .falkordb_manager import FalkorDBManager
from .graph_constructor import KnowledgeGraphConstructor
from .hybrid_system import HybridSystem
from .cli_commands import kg_cli, add_kg_commands
from .embedding_trainer import KGEmbeddingTrainer
from .embedding_utils import EmbeddingAnalyzer, EmbeddingEvaluator, load_embeddings_from_falkordb
from .falkordb_storage import FalkorDBGraphStorage
from .enhanced_minirag import EnhancedMiniRAG
from .query_classifier import QueryIntentClassifier, QueryType
from .hybrid_retriever import HybridRetriever

__all__ = [
    'FalkorDBManager',
    'KnowledgeGraphConstructor',
    'HybridSystem',
    'KGEmbeddingTrainer',
    'EmbeddingAnalyzer',
    'EmbeddingEvaluator',
    'load_embeddings_from_falkordb',
    'FalkorDBGraphStorage',
    'EnhancedMiniRAG',
    'QueryIntentClassifier',
    'QueryType',
    'HybridRetriever',
    'kg_cli',
    'add_kg_commands'
]

__version__ = '0.1.17'

# Phase implementation status
PHASE_STATUS = {
    'phase_1': {
        'name': 'Foundation',
        'status': 'COMPLETED',
        'components': [
            'FalkorDB Integration',
            'Knowledge Graph Constructor',
            'Basic CLI Commands',
            'Configuration Schema'
        ]
    },
    'phase_2': {
        'name': 'KG Embeddings',
        'status': 'COMPLETED',
        'components': [
            'PyKEEN Integration (8 models supported)',
            'Embedding Training with metrics',
            'Storage and retrieval in FalkorDB',
            'Similarity search',
            'Visualization (2D/3D)',
            'Clustering analysis',
            'Enhanced CLI commands'
        ]
    },
    'phase_3': {
        'name': 'MiniRAG Enhancement',
        'status': 'COMPLETED',
        'components': [
            'FalkorDB Storage Adapter with BaseGraphStorage interface',
            'Enhanced MiniRAG with KG embeddings',
            'Three query modes (minirag_only, kg_embedding_only, hybrid)',
            'Hybrid search with graph + embeddings',
            'Entity context extraction',
            'Path finding between entities',
            'Integration with Milvus for text embeddings',
            'CLI commands (rag-query, entity-context, path-find)'
        ]
    },
    'phase_4': {
        'name': 'Hybrid Retrieval',
        'status': 'COMPLETED',
        'components': [
            'Query Intent Classifier with 6 query types',
            'Hybrid Retriever with 4 strategies',
            'Retrieval Strategies (vector_first, graph_first, parallel, adaptive)',
            'Reciprocal Rank Fusion for parallel search',
            'Query router and adaptive strategy selection',
            'Advanced CLI commands (classify-query, hybrid-search, compare-strategies, batch-query)',
            'Reranking methods (score_based, diversity, relevance)'
        ]
    },
    'phase_5': {
        'name': 'Integration & Testing',
        'status': 'COMPLETED',
        'components': [
            'Comprehensive test suite with pytest',
            'Docker Compose configuration for all services',
            'Kubernetes deployment manifests with auto-scaling',
            'REST API with health check endpoints',
            'Performance benchmarking tools',
            'Integration tests for all phases',
            'Deployment documentation',
            'Monitoring with Prometheus and Grafana'
        ]
    }
}