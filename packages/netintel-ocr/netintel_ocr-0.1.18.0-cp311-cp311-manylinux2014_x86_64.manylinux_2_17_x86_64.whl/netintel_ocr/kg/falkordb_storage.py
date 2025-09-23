"""
FalkorDB Storage Adapter for MiniRAG in NetIntel-OCR v0.1.17

Custom MiniRAG storage adapter for FalkorDB with KG embeddings.
Reference: docs/knowledgegraphs_enhanced.md lines 591-686
"""

import os
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Try to import MiniRAG components
try:
    from minirag import BaseGraphStorage
    MINIRAG_AVAILABLE = True
except ImportError:
    # Silently handle missing MiniRAG - the check-requirements command will report it
    MINIRAG_AVAILABLE = False
    # Create a dummy base class for development
    class BaseGraphStorage:
        pass


class FalkorDBGraphStorage(BaseGraphStorage):
    """
    Custom MiniRAG storage adapter for FalkorDB with KG embeddings.
    
    This adapter provides:
    - Access to KG embeddings from node/edge properties
    - Similarity search using embeddings
    - Hybrid graph + embedding queries
    - Integration with MiniRAG's BaseGraphStorage interface
    """
    
    def __init__(self, falkor_manager, use_kg_embeddings: bool = True):
        """
        Initialize the FalkorDB storage adapter.
        
        Args:
            falkor_manager: FalkorDBManager instance
            use_kg_embeddings: Whether to use KG embeddings for similarity
        """
        self.falkor = falkor_manager
        self.use_kg_embeddings = use_kg_embeddings
        
        if not self.falkor._connected:
            raise ConnectionError("FalkorDB manager not connected")
        
        logger.info(f"Initialized FalkorDB storage adapter "
                   f"(KG embeddings: {'enabled' if use_kg_embeddings else 'disabled'})")
    
    async def get_node(self, entity_name: str) -> Dict[str, Any]:
        """
        Get node with KG embeddings from FalkorDB.
        
        Args:
            entity_name: Name or ID of the entity
        
        Returns:
            Node data including properties and embeddings
        """
        try:
            query = """
            MATCH (n)
            WHERE n.name = $name OR n.id = $name
            RETURN n, labels(n) as labels
            LIMIT 1
            """
            
            result = self.falkor.execute_cypher(query, {'name': entity_name})
            
            if not result.result_set:
                return None
            
            node = result.result_set[0][0]
            labels = result.result_set[0][1]
            
            node_data = {
                'id': node.properties.get('id', entity_name),
                'name': node.properties.get('name', entity_name),
                'labels': labels,
                'properties': dict(node.properties)
            }
            
            # Include KG embedding if available and requested
            if self.use_kg_embeddings and 'kg_embedding' in node.properties:
                node_data['kg_embedding'] = node.properties['kg_embedding']
                node_data['embedding_model'] = node.properties.get('embedding_model', 'unknown')
                node_data['embedding_dim'] = node.properties.get('embedding_dim', len(node.properties['kg_embedding']))
            
            return node_data
            
        except Exception as e:
            logger.error(f"Failed to get node {entity_name}: {e}")
            return None
    
    async def get_node_with_embedding_similarity(self, 
                                                query_embedding: List[float],
                                                threshold: float = 0.7,
                                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get nodes similar to query using KG embeddings.
        
        Args:
            query_embedding: Query embedding vector
            threshold: Minimum similarity threshold
            limit: Maximum number of results
        
        Returns:
            List of similar nodes with similarity scores
        """
        if not self.use_kg_embeddings:
            logger.warning("KG embeddings disabled, returning empty results")
            return []
        
        try:
            # Use FalkorDB's vector similarity search
            similar_entities = await self.falkor.similarity_search_with_embeddings(
                query_embedding=query_embedding,
                limit=limit,
                threshold=threshold
            )
            
            # Fetch full node data for each similar entity
            results = []
            for entity in similar_entities:
                node_data = await self.get_node(entity['id'])
                if node_data:
                    node_data['similarity_score'] = entity['similarity']
                    results.append(node_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            return []
    
    async def get_edges(self, source_id: str, 
                        edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get edges from a source node.
        
        Args:
            source_id: Source node ID
            edge_type: Optional edge type filter
        
        Returns:
            List of edges with properties
        """
        try:
            if edge_type:
                query = f"""
                MATCH (s {{id: $source_id}})-[r:{edge_type}]->(t)
                RETURN r, type(r) as rel_type, t.id as target_id, t.name as target_name
                """
            else:
                query = """
                MATCH (s {id: $source_id})-[r]->(t)
                RETURN r, type(r) as rel_type, t.id as target_id, t.name as target_name
                """
            
            result = self.falkor.execute_cypher(query, {'source_id': source_id})
            
            edges = []
            for row in result.result_set:
                edge = row[0]
                edge_data = {
                    'type': row[1],
                    'target_id': row[2],
                    'target_name': row[3],
                    'properties': dict(edge.properties) if hasattr(edge, 'properties') else {}
                }
                
                # Include KG embedding if available
                if self.use_kg_embeddings and 'kg_embedding' in edge_data['properties']:
                    edge_data['kg_embedding'] = edge_data['properties']['kg_embedding']
                
                edges.append(edge_data)
            
            return edges
            
        except Exception as e:
            logger.error(f"Failed to get edges for {source_id}: {e}")
            return []
    
    async def get_edges_with_embeddings(self, source_id: str) -> List[Dict[str, Any]]:
        """
        Get edges with their KG embeddings.
        
        Args:
            source_id: Source node ID
        
        Returns:
            List of edges with embeddings
        """
        edges = await self.get_edges(source_id)
        
        # Filter to only edges with embeddings
        edges_with_embeddings = [
            edge for edge in edges 
            if 'kg_embedding' in edge.get('properties', {})
        ]
        
        return edges_with_embeddings
    
    async def hybrid_graph_search(self, 
                                 query_text: str,
                                 query_embedding: Optional[List[float]] = None,
                                 max_hops: int = 2,
                                 limit: int = 20) -> Dict[str, Any]:
        """
        Perform hybrid search using both graph structure and embeddings.
        
        Args:
            query_text: Text query for entity/relationship matching
            query_embedding: Optional embedding for similarity search
            max_hops: Maximum graph traversal depth
            limit: Maximum number of results
        
        Returns:
            Combined results from graph and embedding search
        """
        results = {
            'graph_results': [],
            'embedding_results': [],
            'combined_results': []
        }
        
        try:
            # 1. Graph-based search (entity and relationship matching)
            graph_query = f"""
            MATCH (n)
            WHERE n.name CONTAINS $query OR n.label CONTAINS $query
            OPTIONAL MATCH path = (n)-[*1..{max_hops}]-(connected)
            RETURN DISTINCT n, connected, path
            LIMIT {limit}
            """
            
            graph_result = self.falkor.execute_cypher(graph_query, {'query': query_text})
            
            for row in graph_result.result_set:
                node = row[0]
                if node:
                    node_data = {
                        'id': node.properties.get('id'),
                        'name': node.properties.get('name'),
                        'type': 'graph_match',
                        'score': 1.0  # Direct match
                    }
                    results['graph_results'].append(node_data)
            
            # 2. Embedding-based search (if embedding provided)
            if query_embedding and self.use_kg_embeddings:
                similar_nodes = await self.get_node_with_embedding_similarity(
                    query_embedding=query_embedding,
                    threshold=0.5,
                    limit=limit
                )
                
                for node in similar_nodes:
                    node_data = {
                        'id': node['id'],
                        'name': node['name'],
                        'type': 'embedding_match',
                        'score': node['similarity_score']
                    }
                    results['embedding_results'].append(node_data)
            
            # 3. Combine and rank results
            all_results = {}
            
            # Add graph results
            for result in results['graph_results']:
                key = result['id']
                if key not in all_results:
                    all_results[key] = result
                else:
                    # Combine scores if entity appears in both
                    all_results[key]['score'] = max(all_results[key]['score'], result['score'])
                    all_results[key]['type'] = 'hybrid_match'
            
            # Add embedding results
            for result in results['embedding_results']:
                key = result['id']
                if key not in all_results:
                    all_results[key] = result
                else:
                    # Weighted combination of scores
                    all_results[key]['score'] = (all_results[key]['score'] + result['score']) / 2
                    all_results[key]['type'] = 'hybrid_match'
            
            # Sort by score
            combined = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
            results['combined_results'] = combined[:limit]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            return results
    
    async def get_subgraph(self, 
                          entity_ids: List[str],
                          max_hops: int = 2,
                          include_embeddings: bool = True) -> Dict[str, Any]:
        """
        Get subgraph around specified entities.
        
        Args:
            entity_ids: List of entity IDs to center subgraph around
            max_hops: Maximum distance from center entities
            include_embeddings: Whether to include KG embeddings
        
        Returns:
            Subgraph data with nodes and edges
        """
        subgraph = {
            'nodes': {},
            'edges': []
        }
        
        try:
            # Get subgraph using Cypher
            query = f"""
            UNWIND $entity_ids AS entity_id
            MATCH (center {{id: entity_id}})
            OPTIONAL MATCH path = (center)-[*0..{max_hops}]-(connected)
            WITH center, connected, relationships(path) as rels
            RETURN DISTINCT center, connected, rels
            """
            
            result = self.falkor.execute_cypher(query, {'entity_ids': entity_ids})
            
            # Process nodes
            for row in result.result_set:
                center = row[0]
                connected = row[1]
                
                # Add center node
                if center and center.properties.get('id') not in subgraph['nodes']:
                    node_data = dict(center.properties)
                    if not include_embeddings and 'kg_embedding' in node_data:
                        del node_data['kg_embedding']
                    subgraph['nodes'][center.properties.get('id')] = node_data
                
                # Add connected node
                if connected and connected.properties.get('id') not in subgraph['nodes']:
                    node_data = dict(connected.properties)
                    if not include_embeddings and 'kg_embedding' in node_data:
                        del node_data['kg_embedding']
                    subgraph['nodes'][connected.properties.get('id')] = node_data
                
                # Add edges
                rels = row[2]
                if rels:
                    for rel in rels:
                        edge_data = {
                            'source': rel.start_node,
                            'target': rel.end_node,
                            'type': rel.type,
                            'properties': dict(rel.properties) if hasattr(rel, 'properties') else {}
                        }
                        if not include_embeddings and 'kg_embedding' in edge_data['properties']:
                            del edge_data['properties']['kg_embedding']
                        subgraph['edges'].append(edge_data)
            
            return subgraph
            
        except Exception as e:
            logger.error(f"Failed to get subgraph: {e}")
            return subgraph
    
    async def get_paths(self,
                       source_id: str,
                       target_id: str,
                       max_length: int = 5) -> List[List[Dict[str, Any]]]:
        """
        Find paths between two entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            max_length: Maximum path length
        
        Returns:
            List of paths, each path is a list of nodes/edges
        """
        paths = []
        
        try:
            query = f"""
            MATCH path = shortestPath((s {{id: $source_id}})-[*..{max_length}]-(t {{id: $target_id}}))
            RETURN path
            LIMIT 10
            """
            
            result = self.falkor.execute_cypher(query, {
                'source_id': source_id,
                'target_id': target_id
            })
            
            for row in result.result_set:
                path = row[0]
                path_data = []
                
                # Extract nodes and relationships from path
                for i, node in enumerate(path.nodes):
                    path_data.append({
                        'type': 'node',
                        'id': node.properties.get('id'),
                        'name': node.properties.get('name'),
                        'properties': dict(node.properties)
                    })
                    
                    if i < len(path.relationships):
                        rel = path.relationships[i]
                        path_data.append({
                            'type': 'edge',
                            'rel_type': rel.type,
                            'properties': dict(rel.properties) if hasattr(rel, 'properties') else {}
                        })
                
                paths.append(path_data)
            
            return paths
            
        except Exception as e:
            logger.error(f"Failed to find paths: {e}")
            return paths
    
    async def get_node_neighbors(self,
                                entity_id: str,
                                edge_types: Optional[List[str]] = None,
                                direction: str = 'both') -> List[Dict[str, Any]]:
        """
        Get neighboring nodes of an entity.
        
        Args:
            entity_id: Entity ID
            edge_types: Optional list of edge types to filter
            direction: 'in', 'out', or 'both'
        
        Returns:
            List of neighboring nodes
        """
        neighbors = []
        
        try:
            # Build query based on direction and edge types
            if edge_types:
                edge_pattern = '|'.join(edge_types)
                edge_filter = f":{edge_pattern}"
            else:
                edge_filter = ""
            
            if direction == 'out':
                query = f"MATCH (n {{id: $entity_id}})-[r{edge_filter}]->(neighbor)"
            elif direction == 'in':
                query = f"MATCH (n {{id: $entity_id}})<-[r{edge_filter}]-(neighbor)"
            else:  # both
                query = f"MATCH (n {{id: $entity_id}})-[r{edge_filter}]-(neighbor)"
            
            query += " RETURN DISTINCT neighbor, type(r) as rel_type"
            
            result = self.falkor.execute_cypher(query, {'entity_id': entity_id})
            
            for row in result.result_set:
                neighbor = row[0]
                rel_type = row[1]
                
                neighbor_data = {
                    'id': neighbor.properties.get('id'),
                    'name': neighbor.properties.get('name'),
                    'relationship': rel_type,
                    'properties': dict(neighbor.properties)
                }
                
                if self.use_kg_embeddings and 'kg_embedding' in neighbor.properties:
                    neighbor_data['has_embedding'] = True
                
                neighbors.append(neighbor_data)
            
            return neighbors
            
        except Exception as e:
            logger.error(f"Failed to get neighbors: {e}")
            return neighbors
    
    async def compute_node_importance(self,
                                     entity_id: str,
                                     method: str = 'degree') -> float:
        """
        Compute importance score for a node.
        
        Args:
            entity_id: Entity ID
            method: Importance metric ('degree', 'betweenness', 'pagerank')
        
        Returns:
            Importance score
        """
        try:
            if method == 'degree':
                # Simple degree centrality
                query = """
                MATCH (n {id: $entity_id})-[r]-()
                RETURN count(r) as degree
                """
                result = self.falkor.execute_cypher(query, {'entity_id': entity_id})
                
                if result.result_set:
                    return float(result.result_set[0][0])
                return 0.0
                
            elif method == 'betweenness':
                # This would require more complex graph algorithm
                # For now, return placeholder
                return 0.5
                
            elif method == 'pagerank':
                # This would require PageRank implementation
                # For now, return placeholder
                return 0.5
                
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to compute importance: {e}")
            return 0.0
    
    # MiniRAG BaseGraphStorage interface methods
    
    async def add_node(self, node_data: Dict[str, Any]) -> bool:
        """Add a new node to the graph."""
        try:
            query = """
            CREATE (n:Entity {id: $id, name: $name})
            SET n += $properties
            RETURN n
            """
            
            params = {
                'id': node_data.get('id'),
                'name': node_data.get('name'),
                'properties': node_data.get('properties', {})
            }
            
            self.falkor.execute_cypher(query, params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node: {e}")
            return False
    
    async def add_edge(self, edge_data: Dict[str, Any]) -> bool:
        """Add a new edge to the graph."""
        try:
            query = f"""
            MATCH (a {{id: $source_id}})
            MATCH (b {{id: $target_id}})
            CREATE (a)-[r:{edge_data.get('type', 'RELATES_TO')}]->(b)
            SET r += $properties
            RETURN r
            """
            
            params = {
                'source_id': edge_data.get('source'),
                'target_id': edge_data.get('target'),
                'properties': edge_data.get('properties', {})
            }
            
            self.falkor.execute_cypher(query, params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add edge: {e}")
            return False
    
    async def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update node properties."""
        try:
            query = """
            MATCH (n {id: $node_id})
            SET n += $updates
            RETURN n
            """
            
            self.falkor.execute_cypher(query, {
                'node_id': node_id,
                'updates': updates
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to update node: {e}")
            return False
    
    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and its relationships."""
        try:
            query = """
            MATCH (n {id: $node_id})
            DETACH DELETE n
            """
            
            self.falkor.execute_cypher(query, {'node_id': node_id})
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete node: {e}")
            return False