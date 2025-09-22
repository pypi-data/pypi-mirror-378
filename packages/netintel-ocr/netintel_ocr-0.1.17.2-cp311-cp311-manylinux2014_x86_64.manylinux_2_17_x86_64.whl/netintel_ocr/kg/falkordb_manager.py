"""
FalkorDB Manager for NetIntel-OCR v0.1.17

Manages FalkorDB for both graph data and KG embeddings.
Reference: docs/knowledgegraphs_enhanced.md lines 385-493
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import json
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from falkordb import FalkorDB
except ImportError:
    logger.warning("FalkorDB not installed. Install with: pip install falkordb")
    FalkorDB = None


class FalkorDBManager:
    """
    Manages FalkorDB for both graph data and KG embeddings.
    
    This class provides:
    - FalkorDB connection management
    - Graph schema creation with indices
    - CRUD operations for nodes and edges
    - Vector index support for KG embeddings
    - Network topology storage
    - Similarity search using KG embeddings
    """
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 password: str = None,
                 graph_name: str = None):
        """
        Initialize FalkorDB connection.
        
        Args:
            host: FalkorDB host (default: from env or localhost)
            port: FalkorDB port (default: from env or 6379)
            password: FalkorDB password (optional)
            graph_name: Graph name (default: netintel_kg)
        """
        self.host = host or os.getenv('FALKORDB_HOST', 'localhost')
        self.port = port or int(os.getenv('FALKORDB_PORT', '6379'))
        self.password = password or os.getenv('FALKORDB_PASSWORD', '')
        self.graph_name = graph_name or os.getenv('FALKORDB_GRAPH', 'netintel_kg')
        
        self.client = None
        self.graph = None
        self._connected = False
        
        logger.info(f"Initializing FalkorDB manager for {self.host}:{self.port}/{self.graph_name}")
    
    def connect(self) -> bool:
        """
        Establish connection to FalkorDB.
        
        Returns:
            bool: True if connection successful
        """
        if not FalkorDB:
            raise ImportError("FalkorDB is not installed. Install with: pip install falkordb")
        
        try:
            # Create FalkorDB client
            if self.password:
                self.client = FalkorDB(host=self.host, port=self.port, password=self.password)
            else:
                self.client = FalkorDB(host=self.host, port=self.port)
            
            # Select or create graph
            self.graph = self.client.select_graph(self.graph_name)
            self._connected = True
            
            logger.info(f"Connected to FalkorDB at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            self._connected = False
            return False
    
    async def create_indices(self):
        """
        Create graph and vector indices for performance.
        
        Creates indices for:
        - Node types and properties
        - Edge types
        - KG embedding vectors for similarity search
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        try:
            # Create node indices
            indices = [
                # Network nodes
                "CREATE INDEX FOR (n:NetworkDevice) ON (n.name)",
                "CREATE INDEX FOR (n:NetworkDevice) ON (n.ip_address)",
                "CREATE INDEX FOR (n:NetworkDevice) ON (n.type)",
                
                # Flow nodes
                "CREATE INDEX FOR (n:Process) ON (n.name)",
                "CREATE INDEX FOR (n:Decision) ON (n.name)",
                "CREATE INDEX FOR (n:DataStore) ON (n.name)",
                
                # General entities
                "CREATE INDEX FOR (n:Entity) ON (n.name)",
                "CREATE INDEX FOR (n:Entity) ON (n.type)",
                
                # Document metadata
                "CREATE INDEX FOR (n:Document) ON (n.md5)",
                "CREATE INDEX FOR (n:Document) ON (n.filename)",
                
                # Vector indices for KG embeddings
                "CREATE VECTOR INDEX FOR (n:NetworkDevice) ON (n.kg_embedding)",
                "CREATE VECTOR INDEX FOR (n:Entity) ON (n.kg_embedding)",
            ]
            
            for index_query in indices:
                try:
                    self.graph.query(index_query)
                    logger.debug(f"Created index: {index_query}")
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation skipped (may already exist): {e}")
            
            logger.info("Graph indices created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indices: {e}")
            raise
    
    async def store_network_topology(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store network diagram as graph structure.
        
        Args:
            network_data: Network diagram data from NetIntel-OCR
                Expected format:
                {
                    'components': [
                        {'id': 'router1', 'type': 'router', 'label': 'Main Router', 
                         'ip_info': '192.168.1.1', 'zone': 'dmz'},
                        ...
                    ],
                    'connections': [
                        {'from': 'router1', 'to': 'switch1', 'type': 'ethernet', 
                         'label': '1Gbps', 'bidirectional': True},
                        ...
                    ],
                    'zones': [
                        {'name': 'dmz', 'security_level': 'untrusted'},
                        ...
                    ],
                    'metadata': {'source_file': 'network.pdf', 'page': 5}
                }
        
        Returns:
            Dict with created nodes and edges count
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        nodes_created = 0
        edges_created = 0
        
        try:
            # Store zones first
            zones_map = {}
            if 'zones' in network_data:
                for zone in network_data['zones']:
                    query = """
                    MERGE (z:Zone {name: $name})
                    SET z.security_level = $security_level,
                        z.subnet = $subnet,
                        z.updated_at = timestamp()
                    RETURN z
                    """
                    params = {
                        'name': zone['name'],
                        'security_level': zone.get('security_level', 'unknown'),
                        'subnet': zone.get('subnet', '')
                    }
                    result = self.graph.query(query, params)
                    zones_map[zone['name']] = True
            
            # Store network components as nodes
            component_map = {}
            for component in network_data.get('components', []):
                # Determine node label based on component type
                node_label = self._get_node_label(component['type'])
                
                query = f"""
                MERGE (n:{node_label} {{id: $id}})
                SET n.name = $name,
                    n.type = $type,
                    n.label = $label,
                    n.ip_address = $ip_address,
                    n.hierarchy_level = $hierarchy_level,
                    n.zone = $zone,
                    n.created_at = timestamp()
                RETURN n
                """
                
                params = {
                    'id': component['id'],
                    'name': component.get('label', component['id']),
                    'type': component['type'],
                    'label': component.get('label', ''),
                    'ip_address': component.get('ip_info', ''),
                    'hierarchy_level': component.get('hierarchy_level', ''),
                    'zone': component.get('zone', '')
                }
                
                result = self.graph.query(query, params)
                nodes_created += 1
                component_map[component['id']] = node_label
                
                # Create relationship to zone if specified
                if component.get('zone') and component['zone'] in zones_map:
                    zone_query = """
                    MATCH (n {id: $component_id})
                    MATCH (z:Zone {name: $zone_name})
                    MERGE (n)-[:LOCATED_IN]->(z)
                    """
                    self.graph.query(zone_query, {
                        'component_id': component['id'],
                        'zone_name': component['zone']
                    })
            
            # Store connections as edges
            for connection in network_data.get('connections', []):
                # Create edge with properties
                edge_type = self._get_edge_type(connection['type'])
                
                if connection.get('bidirectional', False):
                    # Create bidirectional relationship
                    query = f"""
                    MATCH (a {{id: $from_id}})
                    MATCH (b {{id: $to_id}})
                    MERGE (a)-[r1:{edge_type}]->(b)
                    MERGE (b)-[r2:{edge_type}]->(a)
                    SET r1.connection_type = $connection_type,
                        r1.label = $label,
                        r1.protocol = $protocol,
                        r1.created_at = timestamp(),
                        r2.connection_type = $connection_type,
                        r2.label = $label,
                        r2.protocol = $protocol,
                        r2.created_at = timestamp()
                    RETURN r1, r2
                    """
                    edges_created += 2
                else:
                    # Create unidirectional relationship
                    query = f"""
                    MATCH (a {{id: $from_id}})
                    MATCH (b {{id: $to_id}})
                    MERGE (a)-[r:{edge_type}]->(b)
                    SET r.connection_type = $connection_type,
                        r.label = $label,
                        r.protocol = $protocol,
                        r.created_at = timestamp()
                    RETURN r
                    """
                    edges_created += 1
                
                params = {
                    'from_id': connection['from'],
                    'to_id': connection['to'],
                    'connection_type': connection['type'],
                    'label': connection.get('label', ''),
                    'protocol': connection.get('protocol', connection['type'])
                }
                
                self.graph.query(query, params)
            
            # Store document metadata
            if 'metadata' in network_data:
                meta = network_data['metadata']
                doc_query = """
                MERGE (d:Document {filename: $filename})
                SET d.md5 = $md5,
                    d.page = $page,
                    d.processed_at = timestamp()
                RETURN d
                """
                self.graph.query(doc_query, {
                    'filename': meta.get('source_file', 'unknown'),
                    'md5': meta.get('md5', ''),
                    'page': meta.get('page', 0)
                })
            
            logger.info(f"Stored network topology: {nodes_created} nodes, {edges_created} edges")
            
            return {
                'nodes_created': nodes_created,
                'edges_created': edges_created,
                'zones_created': len(zones_map)
            }
            
        except Exception as e:
            logger.error(f"Failed to store network topology: {e}")
            raise
    
    async def store_kg_embeddings(self, embeddings_data: Dict[str, Any]) -> int:
        """
        Store PyKEEN embeddings as node/edge properties.
        
        Args:
            embeddings_data: Dictionary containing entity and relation embeddings
                Expected format:
                {
                    'entities': {
                        'router1': [0.23, -0.45, ...],  # 200-dim vector
                        'switch1': [0.12, 0.34, ...],
                        ...
                    },
                    'relations': {
                        'CONNECTS_TO': [0.1, -0.2, ...],
                        'LOCATED_IN': [0.3, 0.4, ...],
                        ...
                    },
                    'metadata': {
                        'model': 'RotatE',
                        'embedding_dim': 200,
                        'training_epochs': 100
                    }
                }
        
        Returns:
            Number of embeddings stored
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        embeddings_stored = 0
        
        try:
            metadata = embeddings_data.get('metadata', {})
            model_name = metadata.get('model', 'unknown')
            embedding_dim = metadata.get('embedding_dim', 200)
            
            # Store entity embeddings
            for entity_id, embedding in embeddings_data.get('entities', {}).items():
                # Convert embedding to list if it's numpy array
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                query = """
                MATCH (n {id: $entity_id})
                SET n.kg_embedding = $embedding,
                    n.embedding_model = $model,
                    n.embedding_dim = $dim,
                    n.embedding_updated = timestamp()
                RETURN n.name
                """
                
                params = {
                    'entity_id': entity_id,
                    'embedding': embedding,
                    'model': model_name,
                    'dim': embedding_dim
                }
                
                result = self.graph.query(query, params)
                if result.result_set:
                    embeddings_stored += 1
            
            # Store relation embeddings (as edge properties)
            for relation_type, embedding in embeddings_data.get('relations', {}).items():
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                # Update all edges of this type with the embedding
                query = f"""
                MATCH ()-[r:{relation_type}]-()
                SET r.kg_embedding = $embedding,
                    r.embedding_model = $model,
                    r.embedding_dim = $dim,
                    r.embedding_updated = timestamp()
                RETURN count(r) as updated_count
                """
                
                params = {
                    'embedding': embedding,
                    'model': model_name,
                    'dim': embedding_dim
                }
                
                result = self.graph.query(query, params)
                if result.result_set:
                    count = result.result_set[0][0]
                    embeddings_stored += count
            
            logger.info(f"Stored {embeddings_stored} KG embeddings using {model_name} model")
            return embeddings_stored
            
        except Exception as e:
            logger.error(f"Failed to store KG embeddings: {e}")
            raise
    
    async def similarity_search_with_embeddings(self, 
                                               query_embedding: List[float],
                                               limit: int = 10,
                                               threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search using KG embeddings with cosine similarity.
        
        Args:
            query_embedding: Query vector (should match KG embedding dimensions)
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0-1)
        
        Returns:
            List of similar entities with scores
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        try:
            # Use vector similarity search in FalkorDB
            query = """
            MATCH (n)
            WHERE n.kg_embedding IS NOT NULL
            WITH n, 
                 vecf32.cosine_similarity(n.kg_embedding, $query_embedding) AS similarity
            WHERE similarity >= $threshold
            RETURN n.id, n.name, n.type, similarity
            ORDER BY similarity DESC
            LIMIT $limit
            """
            
            params = {
                'query_embedding': query_embedding,
                'threshold': threshold,
                'limit': limit
            }
            
            result = self.graph.query(query, params)
            
            results = []
            for row in result.result_set:
                results.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'similarity': float(row[3])
                })
            
            logger.debug(f"Found {len(results)} similar entities")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the graph.
        
        Returns:
            Dictionary with node counts, edge counts, etc.
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        try:
            stats = {}
            
            # Count nodes by type
            node_query = """
            MATCH (n)
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY count DESC
            """
            result = self.graph.query(node_query)
            
            node_counts = {}
            total_nodes = 0
            for row in result.result_set:
                label = row[0]
                count = row[1]
                node_counts[label] = count
                total_nodes += count
            
            stats['total_nodes'] = total_nodes
            stats['node_counts'] = node_counts
            
            # Count edges by type
            edge_query = """
            MATCH ()-[r]-()
            RETURN type(r) as type, count(r) as count
            ORDER BY count DESC
            """
            result = self.graph.query(edge_query)
            
            edge_counts = {}
            total_edges = 0
            for row in result.result_set:
                edge_type = row[0]
                count = row[1] // 2  # Divide by 2 to avoid counting bidirectional twice
                edge_counts[edge_type] = count
                total_edges += count
            
            stats['total_edges'] = total_edges
            stats['edge_counts'] = edge_counts
            
            # Count nodes with embeddings
            embedding_query = """
            MATCH (n)
            WHERE n.kg_embedding IS NOT NULL
            RETURN count(n) as count
            """
            result = self.graph.query(embedding_query)
            stats['nodes_with_embeddings'] = result.result_set[0][0] if result.result_set else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            raise
    
    def execute_cypher(self, cypher_query: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute a raw Cypher query.
        
        Args:
            cypher_query: Cypher query string
            params: Query parameters
        
        Returns:
            Query results
        """
        if not self._connected:
            raise ConnectionError("Not connected to FalkorDB. Call connect() first.")
        
        try:
            result = self.graph.query(cypher_query, params or {})
            return result
        except Exception as e:
            logger.error(f"Failed to execute Cypher query: {e}")
            raise
    
    def close(self):
        """Close FalkorDB connection."""
        if self.client:
            # FalkorDB client doesn't have explicit close, but we can clear references
            self.client = None
            self.graph = None
            self._connected = False
            logger.info("FalkorDB connection closed")
    
    # Helper methods
    
    def _get_node_label(self, component_type: str) -> str:
        """Map component type to graph node label."""
        label_map = {
            'router': 'NetworkDevice',
            'switch': 'NetworkDevice',
            'firewall': 'NetworkDevice',
            'server': 'NetworkDevice',
            'database': 'DataStore',
            'load_balancer': 'NetworkDevice',
            'cloud': 'CloudService',
            'workstation': 'NetworkDevice',
            'wireless_ap': 'NetworkDevice',
            'process': 'Process',
            'decision': 'Decision',
            'start': 'StartEnd',
            'end': 'StartEnd'
        }
        return label_map.get(component_type.lower(), 'Entity')
    
    def _get_edge_type(self, connection_type: str) -> str:
        """Map connection type to graph edge type."""
        edge_map = {
            'ethernet': 'CONNECTS_TO',
            'wireless': 'CONNECTS_WIRELESSLY',
            'vpn': 'VPN_TUNNEL',
            'data_flow': 'DATA_FLOWS_TO',
            'redundant': 'REDUNDANT_LINK',
            'sequential': 'FLOWS_TO',
            'conditional': 'CONDITIONAL_FLOW'
        }
        return edge_map.get(connection_type.lower(), 'CONNECTS_TO')
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.close()