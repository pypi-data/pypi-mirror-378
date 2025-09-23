"""
Hybrid Retriever for NetIntel-OCR v0.1.17

Hybrid retrieval combining vector and graph approaches.
Reference: docs/knowledgegraphs_enhanced.md lines 754-947
"""

import os
import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from collections import defaultdict

from .query_classifier import QueryIntentClassifier, QueryType
from .enhanced_minirag import EnhancedMiniRAG
from .falkordb_manager import FalkorDBManager
from .falkordb_storage import FalkorDBGraphStorage

logger = logging.getLogger(__name__)

try:
    from pymilvus import Collection, connections
    MILVUS_AVAILABLE = True
except ImportError:
    logger.warning("Milvus client not installed")
    MILVUS_AVAILABLE = False


class HybridRetriever:
    """
    Hybrid retrieval combining vector and graph approaches.
    
    Embedding Storage:
    - Text embeddings (Qwen3-8B, 4096d) → Milvus
    - KG embeddings (PyKEEN, 200d) → FalkorDB properties
    
    Strategies:
    - vector_first: Vector search → graph expansion
    - graph_first: Graph traversal → vector retrieval  
    - parallel: Simultaneous search with RRF
    - adaptive: Automatic based on query type
    """
    
    def __init__(self,
                 falkor_manager: FalkorDBManager,
                 milvus_client=None,
                 llm_model: str = None,
                 embedding_model: str = None,
                 embedding_dim: int = None,
                 ollama_host: str = None,
                 ollama_port: int = None):
        """
        Initialize the Hybrid Retriever.
        
        Args:
            falkor_manager: FalkorDBManager instance
            milvus_client: Milvus client for text embeddings
            llm_model: LLM model for MiniRAG
            embedding_model: Embedding model for MiniRAG
            embedding_dim: Embedding dimensions
            ollama_host: Ollama server host
            ollama_port: Ollama server port
        """
        self.falkor = falkor_manager
        self.milvus = milvus_client
        
        # Initialize Enhanced MiniRAG
        self.minirag = EnhancedMiniRAG(
            falkor_manager=falkor_manager,
            milvus_client=milvus_client,
            llm_model=llm_model or os.getenv('MINIRAG_LLM'),
            embedding_model=embedding_model or os.getenv('MINIRAG_EMBEDDING'),
            embedding_dim=embedding_dim or int(os.getenv('MINIRAG_EMBEDDING_DIM', '4096')),
            ollama_host=ollama_host or os.getenv('OLLAMA_HOST', 'localhost'),
            ollama_port=ollama_port or int(os.getenv('OLLAMA_PORT', '11434'))
        )
        
        # Initialize query classifier
        self.classifier = QueryIntentClassifier()
        
        # Initialize graph storage
        self.graph_storage = FalkorDBGraphStorage(falkor_manager)
        
        logger.info("Initialized Hybrid Retriever")
    
    async def hybrid_search(self,
                          query: str,
                          strategy: str = 'adaptive',
                          max_results: int = 20,
                          **kwargs) -> Dict[str, Any]:
        """
        Perform hybrid search with specified strategy.
        
        Args:
            query: Query string
            strategy: Retrieval strategy ('vector_first', 'graph_first', 'parallel', 'adaptive')
            max_results: Maximum number of results
            **kwargs: Additional strategy-specific parameters
        
        Returns:
            Search results with metadata
        """
        start_time = datetime.now()
        
        # Extract query features
        query_features = self.classifier.get_query_features(query)
        
        results = {
            'query': query,
            'strategy': strategy,
            'query_features': query_features,
            'results': [],
            'metadata': {}
        }
        
        try:
            # Route to appropriate strategy
            if strategy == 'adaptive':
                # Use classifier to determine best strategy
                recommended_strategy = query_features['recommended_strategy']
                logger.info(f"Adaptive mode selected strategy: {recommended_strategy}")
                strategy = recommended_strategy
            
            if strategy == 'vector_first':
                results['results'] = await self._vector_first_strategy(
                    query, query_features, max_results, **kwargs
                )
            elif strategy == 'graph_first':
                results['results'] = await self._graph_first_strategy(
                    query, query_features, max_results, **kwargs
                )
            elif strategy == 'parallel':
                results['results'] = await self._parallel_strategy(
                    query, query_features, max_results, **kwargs
                )
            else:
                # Default to parallel for unknown strategies
                logger.warning(f"Unknown strategy '{strategy}', using parallel")
                results['results'] = await self._parallel_strategy(
                    query, query_features, max_results, **kwargs
                )
            
            # Add metadata
            results['metadata'] = {
                'num_results': len(results['results']),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'strategy_used': strategy,
                'query_type': query_features['query_type'],
                'confidence': query_features['confidence']
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _vector_first_strategy(self,
                                   query: str,
                                   features: Dict[str, Any],
                                   limit: int,
                                   expansion_hops: int = 2,
                                   **kwargs) -> List[Dict[str, Any]]:
        """
        Vector-first strategy: Semantic search followed by graph expansion.
        
        Args:
            query: Query string
            features: Query features
            limit: Maximum results
            expansion_hops: Graph expansion depth
        
        Returns:
            List of results
        """
        results = []
        
        try:
            # Step 1: Vector search using MiniRAG
            vector_results = await self.minirag.query_with_kg_embeddings(
                query_text=query,
                mode='kg_embedding_only',
                max_results=limit // 2  # Get half from vectors
            )
            
            # Step 2: Extract entities from vector results
            entities = set()
            for result in vector_results.get('results', []):
                if 'entity' in result:
                    entities.add(result['entity'])
            
            # Step 3: Graph expansion from found entities
            expanded_results = []
            for entity in entities:
                # Get subgraph around entity
                subgraph = await self.graph_storage.get_subgraph(
                    [entity],
                    max_hops=expansion_hops,
                    include_embeddings=False
                )
                
                # Add nodes from subgraph
                for node_id, node_data in subgraph['nodes'].items():
                    if node_id != entity:  # Don't duplicate the seed entity
                        expanded_results.append({
                            'entity': node_id,
                            'node_data': node_data,
                            'source': 'graph_expansion',
                            'seed_entity': entity,
                            'distance': expansion_hops
                        })
            
            # Step 4: Combine and rank results
            all_results = []
            
            # Add vector results with scores
            for result in vector_results.get('results', []):
                result['retrieval_method'] = 'vector'
                result['final_score'] = result.get('similarity_score', 0.8)
                all_results.append(result)
            
            # Add expanded results with lower scores
            for result in expanded_results[:limit // 2]:
                result['retrieval_method'] = 'graph_expansion'
                result['final_score'] = 0.5 / result.get('distance', 1)
                all_results.append(result)
            
            # Sort by final score
            all_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
            
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Vector-first strategy failed: {e}")
            return []
    
    async def _graph_first_strategy(self,
                                  query: str,
                                  features: Dict[str, Any],
                                  limit: int,
                                  vector_augment: bool = True,
                                  **kwargs) -> List[Dict[str, Any]]:
        """
        Graph-first strategy: Entity recognition, graph search, vector chunks.
        
        Args:
            query: Query string
            features: Query features
            limit: Maximum results
            vector_augment: Whether to augment with vector search
        
        Returns:
            List of results
        """
        results = []
        
        try:
            # Step 1: Extract entities from query
            entities = features.get('entities', [])
            
            # Step 2: Graph search using MiniRAG
            graph_results = await self.minirag.query_with_kg_embeddings(
                query_text=query,
                mode='minirag_only',
                max_results=limit // 2
            )
            
            # Step 3: Extract nodes from graph results
            found_entities = set()
            for result in graph_results.get('results', []):
                if 'entity' in result:
                    found_entities.add(result['entity'])
                    result['retrieval_method'] = 'graph'
                    result['final_score'] = result.get('importance_score', 0.7)
                    results.append(result)
            
            # Step 4: Augment with vector search if enabled
            if vector_augment and found_entities:
                # Get embeddings for found entities
                for entity in list(found_entities)[:5]:  # Limit to top 5
                    node = await self.graph_storage.get_node(entity)
                    if node and 'kg_embedding' in node.get('properties', {}):
                        # Find similar entities using embedding
                        similar = await self.graph_storage.get_node_with_embedding_similarity(
                            query_embedding=node['properties']['kg_embedding'],
                            threshold=0.6,
                            limit=3
                        )
                        
                        for sim_node in similar:
                            if sim_node['id'] not in found_entities:
                                sim_node['retrieval_method'] = 'vector_augment'
                                sim_node['final_score'] = sim_node.get('similarity_score', 0.5)
                                sim_node['source_entity'] = entity
                                results.append(sim_node)
            
            # Sort by final score
            results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Graph-first strategy failed: {e}")
            return []
    
    async def _parallel_strategy(self,
                               query: str,
                               features: Dict[str, Any],
                               limit: int,
                               rrf_k: int = 60,
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Parallel strategy: Simultaneous search with Reciprocal Rank Fusion.
        
        Args:
            query: Query string
            features: Query features
            limit: Maximum results
            rrf_k: RRF constant (default 60)
        
        Returns:
            List of results
        """
        try:
            # Step 1: Execute parallel searches
            vector_task = self.minirag.query_with_kg_embeddings(
                query_text=query,
                mode='kg_embedding_only',
                max_results=limit
            )
            
            graph_task = self.minirag.query_with_kg_embeddings(
                query_text=query,
                mode='minirag_only',
                max_results=limit
            )
            
            # Run both searches in parallel
            vector_results, graph_results = await asyncio.gather(
                vector_task, graph_task
            )
            
            # Step 2: Apply Reciprocal Rank Fusion
            rrf_scores = defaultdict(float)
            entity_data = {}
            
            # Process vector results
            for rank, result in enumerate(vector_results.get('results', [])):
                entity = result.get('entity')
                if entity:
                    # RRF formula: 1 / (k + rank)
                    rrf_scores[entity] += 1.0 / (rrf_k + rank + 1)
                    entity_data[entity] = result
                    entity_data[entity]['vector_rank'] = rank + 1
            
            # Process graph results
            for rank, result in enumerate(graph_results.get('results', [])):
                entity = result.get('entity')
                if entity:
                    rrf_scores[entity] += 1.0 / (rrf_k + rank + 1)
                    if entity not in entity_data:
                        entity_data[entity] = result
                    entity_data[entity]['graph_rank'] = rank + 1
            
            # Step 3: Create final results with RRF scores
            final_results = []
            for entity, rrf_score in rrf_scores.items():
                result = entity_data[entity].copy()
                result['rrf_score'] = rrf_score
                result['retrieval_method'] = 'parallel_rrf'
                result['final_score'] = rrf_score
                
                # Add source information
                sources = []
                if 'vector_rank' in result:
                    sources.append(f"vector(#{result['vector_rank']})")
                if 'graph_rank' in result:
                    sources.append(f"graph(#{result['graph_rank']})")
                result['sources'] = ', '.join(sources)
                
                final_results.append(result)
            
            # Sort by RRF score
            final_results.sort(key=lambda x: x['rrf_score'], reverse=True)
            
            return final_results[:limit]
            
        except Exception as e:
            logger.error(f"Parallel strategy failed: {e}")
            return []
    
    async def rerank_results(self,
                           results: List[Dict[str, Any]],
                           query: str,
                           method: str = 'score_based') -> List[Dict[str, Any]]:
        """
        Rerank results using specified method.
        
        Args:
            results: Initial results
            query: Original query
            method: Reranking method
        
        Returns:
            Reranked results
        """
        if method == 'score_based':
            # Simple score-based reranking
            return sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)
        
        elif method == 'diversity':
            # Diversity-based reranking to avoid redundancy
            reranked = []
            seen_types = set()
            
            # First pass: add diverse types
            for result in results:
                node_type = result.get('node_data', {}).get('type', 'unknown')
                if node_type not in seen_types:
                    reranked.append(result)
                    seen_types.add(node_type)
            
            # Second pass: add remaining
            for result in results:
                if result not in reranked:
                    reranked.append(result)
            
            return reranked
        
        elif method == 'relevance':
            # Would use LLM for relevance scoring in production
            # For now, use keyword matching
            query_words = set(query.lower().split())
            
            for result in results:
                relevance = 0
                # Check entity name
                entity_name = result.get('entity', '').lower()
                for word in query_words:
                    if word in entity_name:
                        relevance += 1
                
                # Check node properties
                if 'node_data' in result:
                    for key, value in result['node_data'].get('properties', {}).items():
                        if isinstance(value, str):
                            for word in query_words:
                                if word in value.lower():
                                    relevance += 0.5
                
                result['relevance_score'] = relevance
            
            return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        else:
            return results
    
    async def explain_retrieval(self,
                              result: Dict[str, Any],
                              query: str) -> str:
        """
        Generate explanation for retrieval result.
        
        Args:
            result: Single result
            query: Original query
        
        Returns:
            Human-readable explanation
        """
        explanations = []
        
        # Explain retrieval method
        method = result.get('retrieval_method', 'unknown')
        if method == 'vector':
            explanations.append("Found through semantic similarity search")
        elif method == 'graph':
            explanations.append("Found through graph traversal")
        elif method == 'graph_expansion':
            seed = result.get('seed_entity', 'unknown')
            explanations.append(f"Found by expanding from '{seed}'")
        elif method == 'vector_augment':
            source = result.get('source_entity', 'unknown')
            explanations.append(f"Similar to graph result '{source}'")
        elif method == 'parallel_rrf':
            sources = result.get('sources', '')
            explanations.append(f"Found by multiple methods: {sources}")
        
        # Explain scores
        if 'final_score' in result:
            score_pct = int(result['final_score'] * 100)
            explanations.append(f"Relevance: {score_pct}%")
        
        if 'rrf_score' in result:
            explanations.append(f"RRF score: {result['rrf_score']:.3f}")
        
        # Explain entity type
        if 'node_data' in result:
            node_type = result['node_data'].get('type', 'entity')
            explanations.append(f"Type: {node_type}")
        
        return " | ".join(explanations)
    
    async def get_retrieval_statistics(self,
                                     results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics about retrieval results.
        
        Args:
            results: Retrieval results
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_results': len(results),
            'by_method': defaultdict(int),
            'by_type': defaultdict(int),
            'score_distribution': {
                'min': 0,
                'max': 0,
                'mean': 0,
                'std': 0
            }
        }
        
        scores = []
        
        for result in results:
            # Count by retrieval method
            method = result.get('retrieval_method', 'unknown')
            stats['by_method'][method] += 1
            
            # Count by entity type
            if 'node_data' in result:
                entity_type = result['node_data'].get('type', 'unknown')
                stats['by_type'][entity_type] += 1
            
            # Collect scores
            if 'final_score' in result:
                scores.append(result['final_score'])
        
        # Calculate score statistics
        if scores:
            stats['score_distribution']['min'] = float(np.min(scores))
            stats['score_distribution']['max'] = float(np.max(scores))
            stats['score_distribution']['mean'] = float(np.mean(scores))
            stats['score_distribution']['std'] = float(np.std(scores))
        
        # Convert defaultdicts to regular dicts for JSON serialization
        stats['by_method'] = dict(stats['by_method'])
        stats['by_type'] = dict(stats['by_type'])
        
        return stats