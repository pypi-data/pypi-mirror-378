"""
Enhanced MiniRAG for NetIntel-OCR v0.1.17

Extended MiniRAG that understands FalkorDB's unified storage.
Reference: docs/knowledgegraphs_enhanced.md lines 688-752
"""

import os
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import MiniRAG and dependencies
try:
    from minirag import MiniRAG
    from minirag.config import MiniRAGConfig
    MINIRAG_AVAILABLE = True
except ImportError:
    # Silently handle missing MiniRAG - the check-requirements command will report it
    MINIRAG_AVAILABLE = False
    MiniRAG = object  # Dummy for inheritance
    MiniRAGConfig = None

try:
    from pymilvus import Collection, connections
    MILVUS_AVAILABLE = True
except ImportError:
    logger.warning("Milvus client not installed. Install with: pip install pymilvus")
    MILVUS_AVAILABLE = False

from .falkordb_storage import FalkorDBGraphStorage


class EnhancedMiniRAG(MiniRAG if MINIRAG_AVAILABLE else object):
    """
    Extended MiniRAG that understands FalkorDB's unified storage.
    
    Uses:
    - Ollama models: gemma3:4b-it-qat (LLM) and Qwen3-Embedding-8B (4096 dims)
    - Text embeddings stored in Milvus
    - KG embeddings stored in FalkorDB
    
    Query modes:
    - minirag_only: Standard graph traversal
    - kg_embedding_only: Pure KG embedding search
    - hybrid: Combined graph + embeddings
    """
    
    def __init__(self,
                 falkor_manager,
                 milvus_client=None,
                 llm_model: str = None,
                 embedding_model: str = None,
                 embedding_dim: int = None,
                 ollama_host: str = None,
                 ollama_port: int = None,
                 **kwargs):
        """
        Initialize Enhanced MiniRAG.
        
        Args:
            falkor_manager: FalkorDBManager instance
            milvus_client: Milvus client for text embeddings (optional)
            llm_model: LLM model name (from env or param)
            embedding_model: Embedding model name (from env or param)
            embedding_dim: Embedding dimensions
            ollama_host: Ollama server host
            ollama_port: Ollama server port
            **kwargs: Additional MiniRAG configuration
        """
        # Configure models from environment or parameters
        llm_model = llm_model or os.getenv('MINIRAG_LLM')
        embedding_model = embedding_model or os.getenv('MINIRAG_EMBEDDING')
        embedding_dim = embedding_dim or int(os.getenv('MINIRAG_EMBEDDING_DIM', '4096'))
        
        if not llm_model or not embedding_model:
            # Use recommended defaults if not specified
            llm_model = llm_model or 'ollama/gemma3:4b-it-qat'
            embedding_model = embedding_model or 'ollama/Qwen3-Embedding-8B'
            logger.info(f"Using default models - LLM: {llm_model}, Embedding: {embedding_model}")
        
        # Configure Ollama connection
        ollama_config = {
            'host': ollama_host or os.getenv('OLLAMA_HOST', 'localhost'),
            'port': ollama_port or int(os.getenv('OLLAMA_PORT', '11434'))
        }
        
        # Set up MiniRAG configuration
        if MINIRAG_AVAILABLE and MiniRAGConfig:
            config = MiniRAGConfig(
                llm_model_name=llm_model,
                embedding_model_name=embedding_model,
                embedding_dim=embedding_dim,
                ollama_config=ollama_config,
                **kwargs
            )
            
            # Initialize base MiniRAG
            super().__init__(config)
        else:
            logger.warning("MiniRAG not available, running in limited mode")
            self.config = {
                'llm_model': llm_model,
                'embedding_model': embedding_model,
                'embedding_dim': embedding_dim,
                'ollama_config': ollama_config
            }
        
        # Set up graph storage with FalkorDB
        self.graph_storage = FalkorDBGraphStorage(falkor_manager, use_kg_embeddings=True)
        self.falkor = falkor_manager
        
        # Set up Milvus client for text embeddings
        self.milvus_client = milvus_client
        self.milvus_collection = None
        
        if milvus_client and MILVUS_AVAILABLE:
            self._setup_milvus()
        
        logger.info(f"Initialized Enhanced MiniRAG with:")
        logger.info(f"  LLM: {llm_model}")
        logger.info(f"  Embedding: {embedding_model} (dim={embedding_dim})")
        logger.info(f"  Ollama: {ollama_config['host']}:{ollama_config['port']}")
        logger.info(f"  Milvus: {'connected' if self.milvus_collection else 'not connected'}")
    
    def _setup_milvus(self):
        """Set up Milvus connection for text embeddings."""
        try:
            # Connect to Milvus
            milvus_host = os.getenv('MILVUS_HOST', 'localhost')
            milvus_port = os.getenv('MILVUS_PORT', '19530')
            
            connections.connect(
                alias="default",
                host=milvus_host,
                port=milvus_port
            )
            
            # Get or create collection
            collection_name = os.getenv('MILVUS_COLLECTION', 'netintel_vectors')
            self.milvus_collection = Collection(collection_name)
            
            # Load collection for searching
            self.milvus_collection.load()
            
            logger.info(f"Connected to Milvus collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup Milvus: {e}")
            self.milvus_collection = None
    
    async def query_with_kg_embeddings(self,
                                      query_text: str,
                                      mode: str = 'hybrid',
                                      max_results: int = 10,
                                      **kwargs) -> Dict[str, Any]:
        """
        Enhanced query with three modes.
        
        Args:
            query_text: Query string
            mode: Query mode - 'minirag_only', 'kg_embedding_only', or 'hybrid'
            max_results: Maximum number of results
            **kwargs: Additional query parameters
        
        Returns:
            Query results with different strategies
        """
        results = {
            'query': query_text,
            'mode': mode,
            'results': [],
            'metadata': {}
        }
        
        try:
            if mode == 'minirag_only':
                # Standard MiniRAG graph traversal
                results['results'] = await self._query_graph_only(query_text, max_results)
                results['metadata']['strategy'] = 'graph_traversal'
                
            elif mode == 'kg_embedding_only':
                # Pure KG embedding search
                results['results'] = await self._query_kg_embeddings_only(query_text, max_results)
                results['metadata']['strategy'] = 'kg_embedding_similarity'
                
            elif mode == 'hybrid':
                # Combined approach
                results['results'] = await self._query_hybrid(query_text, max_results)
                results['metadata']['strategy'] = 'hybrid_graph_embedding'
                
            else:
                raise ValueError(f"Unknown query mode: {mode}")
            
            # Add timing and statistics
            results['metadata']['num_results'] = len(results['results'])
            results['metadata']['timestamp'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _query_graph_only(self, query_text: str, limit: int) -> List[Dict[str, Any]]:
        """
        Query using only graph traversal (standard MiniRAG).
        
        Args:
            query_text: Query string
            limit: Maximum results
        
        Returns:
            List of results from graph traversal
        """
        results = []
        
        try:
            # Extract entities from query
            entities = await self._extract_entities_from_query(query_text)
            
            # For each entity, traverse the graph
            for entity in entities:
                # Get node
                node = await self.graph_storage.get_node(entity)
                if not node:
                    continue
                
                # Get neighbors and paths
                neighbors = await self.graph_storage.get_node_neighbors(
                    entity,
                    direction='both'
                )
                
                # Score based on graph structure
                importance = await self.graph_storage.compute_node_importance(entity)
                
                results.append({
                    'entity': entity,
                    'node_data': node,
                    'neighbors': neighbors[:5],  # Top 5 neighbors
                    'importance_score': importance,
                    'match_type': 'graph'
                })
            
            # Sort by importance
            results.sort(key=lambda x: x['importance_score'], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return []
    
    async def _query_kg_embeddings_only(self, query_text: str, limit: int) -> List[Dict[str, Any]]:
        """
        Query using only KG embeddings.
        
        Args:
            query_text: Query string
            limit: Maximum results
        
        Returns:
            List of results from embedding similarity
        """
        results = []
        
        try:
            # Get query embedding
            query_embedding = await self._get_text_embedding(query_text)
            
            if query_embedding:
                # Search using KG embeddings in FalkorDB
                similar_nodes = await self.graph_storage.get_node_with_embedding_similarity(
                    query_embedding=query_embedding,
                    threshold=0.5,
                    limit=limit
                )
                
                for node in similar_nodes:
                    results.append({
                        'entity': node['id'],
                        'node_data': node,
                        'similarity_score': node['similarity_score'],
                        'match_type': 'kg_embedding'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"KG embedding query failed: {e}")
            return []
    
    async def _query_hybrid(self, query_text: str, limit: int) -> List[Dict[str, Any]]:
        """
        Query using hybrid approach (graph + embeddings).
        
        Args:
            query_text: Query string
            limit: Maximum results
        
        Returns:
            Combined results from both approaches
        """
        try:
            # Get query embedding
            query_embedding = await self._get_text_embedding(query_text)
            
            # Perform hybrid search
            hybrid_results = await self.graph_storage.hybrid_graph_search(
                query_text=query_text,
                query_embedding=query_embedding,
                max_hops=2,
                limit=limit
            )
            
            # Process combined results
            results = []
            for item in hybrid_results.get('combined_results', []):
                # Fetch full node data
                node = await self.graph_storage.get_node(item['id'])
                
                # Get context from neighbors
                neighbors = await self.graph_storage.get_node_neighbors(
                    item['id'],
                    direction='both'
                )
                
                results.append({
                    'entity': item['id'],
                    'node_data': node,
                    'score': item['score'],
                    'match_type': item['type'],
                    'context': {
                        'neighbors': neighbors[:3],
                        'neighbor_count': len(neighbors)
                    }
                })
            
            # If Milvus is available, also search text embeddings
            if self.milvus_collection and query_embedding:
                text_results = await self._search_text_embeddings(query_embedding, limit=5)
                
                # Add text embedding results
                for text_result in text_results:
                    results.append({
                        'entity': text_result.get('id'),
                        'content': text_result.get('content'),
                        'score': text_result.get('score'),
                        'match_type': 'text_embedding',
                        'source': 'milvus'
                    })
            
            # Re-rank results based on combined scores
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid query failed: {e}")
            return []
    
    async def _extract_entities_from_query(self, query_text: str) -> List[str]:
        """
        Extract entity mentions from query text.
        
        Args:
            query_text: Query string
        
        Returns:
            List of entity IDs/names
        """
        entities = []
        
        try:
            # Simple entity extraction (in production, use NER)
            # Look for capitalized words or known patterns
            words = query_text.split()
            for word in words:
                if word[0].isupper() or '-' in word:
                    entities.append(word)
            
            # Also check if any word matches known entities in graph
            query = """
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower($query) OR 
                  toLower(n.id) CONTAINS toLower($query)
            RETURN n.id, n.name
            LIMIT 10
            """
            
            result = self.falkor.execute_cypher(query, {'query': query_text})
            
            for row in result.result_set:
                entities.append(row[0])  # Add entity ID
            
            # Deduplicate
            entities = list(set(entities))
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        return entities
    
    async def _get_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get text embedding using configured embedding model.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None
        """
        try:
            if MINIRAG_AVAILABLE and hasattr(self, 'embedding_model'):
                # Use MiniRAG's embedding model
                embedding = await self.embedding_model.embed(text)
                return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            else:
                # Fallback: generate random embedding for testing
                logger.warning("Using random embeddings (MiniRAG not available)")
                embedding_dim = self.config.get('embedding_dim', 4096)
                return np.random.randn(embedding_dim).tolist()
                
        except Exception as e:
            logger.error(f"Failed to get text embedding: {e}")
            return None
    
    async def _search_text_embeddings(self, 
                                     query_embedding: List[float],
                                     limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search text embeddings in Milvus.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
        
        Returns:
            List of similar text chunks
        """
        if not self.milvus_collection:
            return []
        
        try:
            # Search in Milvus
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = self.milvus_collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=["id", "content", "source"]
            )
            
            # Process results
            text_results = []
            for hit in results[0]:
                text_results.append({
                    'id': hit.id,
                    'content': hit.entity.get('content', ''),
                    'source': hit.entity.get('source', ''),
                    'score': hit.score
                })
            
            return text_results
            
        except Exception as e:
            logger.error(f"Milvus search failed: {e}")
            return []
    
    async def explain_result(self, result: Dict[str, Any]) -> str:
        """
        Generate explanation for a query result.
        
        Args:
            result: Query result to explain
        
        Returns:
            Human-readable explanation
        """
        explanation = []
        
        if result.get('match_type') == 'graph':
            explanation.append(f"Found through graph traversal from '{result['entity']}'")
            explanation.append(f"Graph importance score: {result.get('importance_score', 0):.2f}")
            
        elif result.get('match_type') == 'kg_embedding':
            explanation.append(f"Found through KG embedding similarity")
            explanation.append(f"Similarity score: {result.get('similarity_score', 0):.2f}")
            
        elif result.get('match_type') == 'hybrid_match':
            explanation.append(f"Found through both graph and embedding search")
            explanation.append(f"Combined score: {result.get('score', 0):.2f}")
            
        elif result.get('match_type') == 'text_embedding':
            explanation.append(f"Found in text content via embedding similarity")
            explanation.append(f"Text similarity: {result.get('score', 0):.2f}")
        
        # Add context information
        if 'context' in result:
            context = result['context']
            if 'neighbors' in context:
                explanation.append(f"Connected to {context.get('neighbor_count', 0)} other entities")
        
        return ' | '.join(explanation)
    
    async def get_entity_context(self, 
                                entity_id: str,
                                context_size: int = 2) -> Dict[str, Any]:
        """
        Get rich context for an entity.
        
        Args:
            entity_id: Entity ID
            context_size: Hops for context extraction
        
        Returns:
            Entity with full context
        """
        context = {
            'entity': entity_id,
            'node': None,
            'neighbors': [],
            'subgraph': None,
            'embeddings': {}
        }
        
        try:
            # Get node data
            context['node'] = await self.graph_storage.get_node(entity_id)
            
            # Get neighbors
            context['neighbors'] = await self.graph_storage.get_node_neighbors(
                entity_id,
                direction='both'
            )
            
            # Get subgraph
            context['subgraph'] = await self.graph_storage.get_subgraph(
                [entity_id],
                max_hops=context_size,
                include_embeddings=False
            )
            
            # Check for embeddings
            if context['node'] and 'kg_embedding' in context['node'].get('properties', {}):
                context['embeddings']['kg'] = {
                    'model': context['node']['properties'].get('embedding_model'),
                    'dim': context['node']['properties'].get('embedding_dim'),
                    'has_embedding': True
                }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get entity context: {e}")
            return context