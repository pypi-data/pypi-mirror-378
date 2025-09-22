"""
Knowledge Graph Constructor for NetIntel-OCR v0.1.17

Constructs knowledge graphs from NetIntel-OCR extracted content.
Reference: docs/knowledgegraphs_enhanced.md lines 173-283
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EntityNode, EpisodicNode
    from graphiti_core.edges import EntityEdge, EpisodicEdge
except ImportError:
    logger.warning("Graphiti not installed. Install with: pip install graphiti-core")
    Graphiti = None
    EntityNode = None
    EpisodicNode = None
    EntityEdge = None
    EpisodicEdge = None


class KnowledgeGraphConstructor:
    """
    Constructs knowledge graphs from NetIntel-OCR extracted content.
    
    This class:
    - Converts network diagrams to graph entities and relationships
    - Processes flow diagrams as process graphs
    - Extracts entities and relationships from tables
    - Uses NLP to extract entities from text
    - Integrates with Graphiti for intelligent graph construction
    """
    
    def __init__(self, falkor_manager):
        """
        Initialize the Knowledge Graph Constructor.
        
        Args:
            falkor_manager: FalkorDBManager instance
        """
        self.falkor = falkor_manager
        
        # Initialize Graphiti if available
        if Graphiti and self.falkor._connected:
            try:
                self.graphiti = Graphiti(
                    llm_client=None,  # We'll use our own LLM integration
                    graph_database=self.falkor,
                    enable_reasoning=True
                )
                logger.info("Graphiti initialized for intelligent graph construction")
            except Exception as e:
                logger.warning(f"Could not initialize Graphiti: {e}")
                self.graphiti = None
        else:
            self.graphiti = None
            logger.info("Operating without Graphiti - using direct graph construction")
        
        # Entity extraction patterns
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b')
        self.mac_pattern = re.compile(r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}')
        self.port_pattern = re.compile(r'\b(?:port|Port)\s*(\d{1,5})\b')
        self.protocol_pattern = re.compile(r'\b(TCP|UDP|HTTP|HTTPS|SSH|FTP|SMTP|DNS|DHCP|ICMP)\b', re.IGNORECASE)
        
    async def process_network_diagram(self, diagram_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert network diagram to graph entities and relationships.
        
        Args:
            diagram_data: Network diagram data from NetIntel-OCR
                Expected format matches FalkorDBManager.store_network_topology()
        
        Returns:
            Dictionary with processing results
        """
        logger.info("Processing network diagram for knowledge graph")
        
        try:
            # First store the basic topology using FalkorDB
            topology_result = await self.falkor.store_network_topology(diagram_data)
            
            # Then enhance with additional intelligence if Graphiti is available
            if self.graphiti:
                await self._enhance_with_graphiti(diagram_data)
            
            # Extract and store additional relationships
            additional_relationships = await self._extract_implicit_relationships(diagram_data)
            
            result = {
                'status': 'success',
                'nodes_created': topology_result['nodes_created'],
                'edges_created': topology_result['edges_created'],
                'zones_created': topology_result['zones_created'],
                'additional_relationships': additional_relationships
            }
            
            logger.info(f"Network diagram processed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process network diagram: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def process_flow_diagram(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flow diagram to process graph.
        
        Args:
            flow_data: Flow diagram data from NetIntel-OCR
                Expected format:
                {
                    'elements': [
                        {'id': 'start1', 'type': 'start', 'label': 'Start Process'},
                        {'id': 'process1', 'type': 'process', 'label': 'Initialize System'},
                        {'id': 'decision1', 'type': 'decision', 'label': 'Is Valid?'},
                        {'id': 'data1', 'type': 'datastore', 'label': 'Config DB'},
                        ...
                    ],
                    'flows': [
                        {'from': 'start1', 'to': 'process1', 'label': ''},
                        {'from': 'process1', 'to': 'decision1', 'label': ''},
                        {'from': 'decision1', 'to': 'process2', 'label': 'Yes'},
                        {'from': 'decision1', 'to': 'error1', 'label': 'No'},
                        ...
                    ],
                    'lanes': [
                        {'name': 'User', 'elements': ['start1', 'process1']},
                        {'name': 'System', 'elements': ['decision1', 'data1']},
                        ...
                    ]
                }
        
        Returns:
            Dictionary with processing results
        """
        logger.info("Processing flow diagram for knowledge graph")
        
        nodes_created = 0
        edges_created = 0
        
        try:
            # Create swim lanes as containers
            lanes_map = {}
            if 'lanes' in flow_data:
                for lane in flow_data['lanes']:
                    query = """
                    MERGE (l:SwimLane {name: $name})
                    SET l.created_at = timestamp()
                    RETURN l
                    """
                    self.falkor.graph.query(query, {'name': lane['name']})
                    lanes_map[lane['name']] = lane.get('elements', [])
            
            # Process flow elements
            element_map = {}
            for element in flow_data.get('elements', []):
                node_label = self._get_flow_node_label(element['type'])
                
                query = f"""
                MERGE (n:{node_label} {{id: $id}})
                SET n.name = $name,
                    n.label = $label,
                    n.element_type = $type,
                    n.created_at = timestamp()
                RETURN n
                """
                
                params = {
                    'id': element['id'],
                    'name': element.get('label', element['id']),
                    'label': element.get('label', ''),
                    'type': element['type']
                }
                
                self.falkor.graph.query(query, params)
                nodes_created += 1
                element_map[element['id']] = node_label
                
                # Link to swim lane if applicable
                for lane_name, elements in lanes_map.items():
                    if element['id'] in elements:
                        lane_query = """
                        MATCH (n {id: $element_id})
                        MATCH (l:SwimLane {name: $lane_name})
                        MERGE (n)-[:IN_LANE]->(l)
                        """
                        self.falkor.graph.query(lane_query, {
                            'element_id': element['id'],
                            'lane_name': lane_name
                        })
            
            # Process flows
            for flow in flow_data.get('flows', []):
                edge_type = 'FLOWS_TO' if not flow.get('label') else 'CONDITIONAL_FLOW'
                
                query = f"""
                MATCH (a {{id: $from_id}})
                MATCH (b {{id: $to_id}})
                MERGE (a)-[r:{edge_type}]->(b)
                SET r.label = $label,
                    r.condition = $condition,
                    r.created_at = timestamp()
                RETURN r
                """
                
                params = {
                    'from_id': flow['from'],
                    'to_id': flow['to'],
                    'label': flow.get('label', ''),
                    'condition': flow.get('label', '')  # Store condition for decision branches
                }
                
                self.falkor.graph.query(query, params)
                edges_created += 1
            
            # Analyze flow for critical paths and bottlenecks
            analysis = await self._analyze_flow_diagram(flow_data)
            
            result = {
                'status': 'success',
                'nodes_created': nodes_created,
                'edges_created': edges_created,
                'lanes_created': len(lanes_map),
                'analysis': analysis
            }
            
            logger.info(f"Flow diagram processed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process flow diagram: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def process_table(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities and relationships from tables.
        
        Args:
            table_data: Table data from NetIntel-OCR
                Expected format:
                {
                    'headers': ['Device', 'IP Address', 'Location', 'Status'],
                    'rows': [
                        ['Router-1', '192.168.1.1', 'Data Center', 'Active'],
                        ['Switch-1', '192.168.1.2', 'Data Center', 'Active'],
                        ...
                    ],
                    'metadata': {
                        'page': 10,
                        'table_type': 'network_inventory'
                    }
                }
        
        Returns:
            Dictionary with processing results
        """
        logger.info("Processing table for knowledge graph")
        
        entities_created = 0
        relationships_created = 0
        
        try:
            headers = table_data.get('headers', [])
            rows = table_data.get('rows', [])
            
            # Identify key columns
            device_col = self._find_column_index(headers, ['device', 'name', 'hostname', 'system'])
            ip_col = self._find_column_index(headers, ['ip', 'address', 'ip_address', 'ipv4'])
            location_col = self._find_column_index(headers, ['location', 'site', 'datacenter', 'zone'])
            status_col = self._find_column_index(headers, ['status', 'state', 'condition'])
            
            # Process each row
            for row in rows:
                if device_col is not None and device_col < len(row):
                    device_name = row[device_col]
                    
                    # Create entity node
                    query = """
                    MERGE (n:Entity {name: $name})
                    SET n.source_type = 'table',
                        n.created_at = timestamp()
                    """
                    params = {'name': device_name}
                    
                    # Add IP address if available
                    if ip_col is not None and ip_col < len(row):
                        query += ", n.ip_address = $ip_address"
                        params['ip_address'] = row[ip_col]
                    
                    # Add location if available
                    if location_col is not None and location_col < len(row):
                        query += ", n.location = $location"
                        params['location'] = row[location_col]
                    
                    # Add status if available
                    if status_col is not None and status_col < len(row):
                        query += ", n.status = $status"
                        params['status'] = row[status_col]
                    
                    query += " RETURN n"
                    self.falkor.graph.query(query, params)
                    entities_created += 1
                    
                    # Create location relationship if applicable
                    if location_col is not None and location_col < len(row):
                        location = row[location_col]
                        loc_query = """
                        MERGE (l:Location {name: $location})
                        WITH l
                        MATCH (n:Entity {name: $device})
                        MERGE (n)-[:LOCATED_AT]->(l)
                        """
                        self.falkor.graph.query(loc_query, {
                            'location': location,
                            'device': device_name
                        })
                        relationships_created += 1
            
            # Extract relationships from table structure
            additional_rels = await self._extract_table_relationships(table_data)
            relationships_created += additional_rels
            
            result = {
                'status': 'success',
                'entities_created': entities_created,
                'relationships_created': relationships_created,
                'table_type': table_data.get('metadata', {}).get('table_type', 'unknown')
            }
            
            logger.info(f"Table processed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process table: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def process_text(self, text_content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract entities and relationships from text using NLP.
        
        Args:
            text_content: Text content to process
            metadata: Optional metadata about the text source
        
        Returns:
            Dictionary with processing results
        """
        logger.info("Processing text for knowledge graph")
        
        entities = []
        relationships = []
        
        try:
            # Extract IP addresses
            ip_addresses = self.ip_pattern.findall(text_content)
            for ip in ip_addresses:
                entities.append({
                    'type': 'IPAddress',
                    'value': ip,
                    'context': self._get_context(text_content, ip)
                })
            
            # Extract MAC addresses
            mac_addresses = self.mac_pattern.findall(text_content)
            for mac in mac_addresses:
                entities.append({
                    'type': 'MACAddress',
                    'value': mac,
                    'context': self._get_context(text_content, mac)
                })
            
            # Extract ports
            ports = self.port_pattern.findall(text_content)
            for port in ports:
                entities.append({
                    'type': 'Port',
                    'value': port,
                    'context': self._get_context(text_content, f"port {port}")
                })
            
            # Extract protocols
            protocols = self.protocol_pattern.findall(text_content)
            for protocol in set(protocols):  # Use set to avoid duplicates
                entities.append({
                    'type': 'Protocol',
                    'value': protocol.upper(),
                    'context': self._get_context(text_content, protocol)
                })
            
            # Store entities in graph
            entities_created = 0
            for entity in entities:
                query = f"""
                MERGE (n:{entity['type']} {{value: $value}})
                SET n.context = $context,
                    n.source_type = 'text',
                    n.created_at = timestamp()
                RETURN n
                """
                
                self.falkor.graph.query(query, {
                    'value': entity['value'],
                    'context': entity['context'][:500]  # Limit context length
                })
                entities_created += 1
            
            # Extract relationships based on proximity and context
            relationships_created = await self._extract_text_relationships(entities, text_content)
            
            result = {
                'status': 'success',
                'entities_created': entities_created,
                'relationships_created': relationships_created,
                'entity_types': list(set(e['type'] for e in entities))
            }
            
            logger.info(f"Text processed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process text: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # Helper methods
    
    async def _enhance_with_graphiti(self, diagram_data: Dict[str, Any]):
        """Use Graphiti for intelligent relationship inference."""
        if not self.graphiti:
            return
        
        try:
            # Create episodic context for the diagram
            episode = {
                'content': f"Network diagram from {diagram_data.get('metadata', {}).get('source_file', 'unknown')}",
                'timestamp': datetime.now(),
                'metadata': diagram_data.get('metadata', {})
            }
            
            # Let Graphiti analyze and enhance the graph
            await self.graphiti.add_episode(episode)
            
        except Exception as e:
            logger.warning(f"Graphiti enhancement failed: {e}")
    
    async def _extract_implicit_relationships(self, diagram_data: Dict[str, Any]) -> int:
        """Extract implicit relationships from network topology."""
        relationships_created = 0
        
        try:
            # Find redundant paths
            for conn in diagram_data.get('connections', []):
                if 'redundant' in conn.get('type', '').lower():
                    query = """
                    MATCH (a {id: $from_id})
                    MATCH (b {id: $to_id})
                    MERGE (a)-[:HAS_REDUNDANCY_WITH]->(b)
                    """
                    self.falkor.graph.query(query, {
                        'from_id': conn['from'],
                        'to_id': conn['to']
                    })
                    relationships_created += 1
            
            # Identify critical paths
            # (This would involve more complex graph analysis in production)
            
            return relationships_created
            
        except Exception as e:
            logger.error(f"Failed to extract implicit relationships: {e}")
            return 0
    
    async def _analyze_flow_diagram(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze flow diagram for bottlenecks and critical paths."""
        analysis = {
            'bottlenecks': [],
            'critical_paths': [],
            'decision_points': []
        }
        
        try:
            # Find decision points
            for element in flow_data.get('elements', []):
                if element['type'] == 'decision':
                    analysis['decision_points'].append({
                        'id': element['id'],
                        'label': element.get('label', '')
                    })
            
            # Identify potential bottlenecks (nodes with many incoming edges)
            # This would require graph analysis queries in production
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze flow diagram: {e}")
            return analysis
    
    async def _extract_table_relationships(self, table_data: Dict[str, Any]) -> int:
        """Extract relationships from table structure."""
        relationships_created = 0
        
        # In production, this would analyze table content for relationships
        # For example, if a table shows "Connected To" columns, etc.
        
        return relationships_created
    
    async def _extract_text_relationships(self, entities: List[Dict], text_content: str) -> int:
        """Extract relationships between entities based on text proximity."""
        relationships_created = 0
        
        # Simple proximity-based relationship extraction
        # In production, this would use NLP to understand actual relationships
        
        return relationships_created
    
    def _get_flow_node_label(self, element_type: str) -> str:
        """Map flow element type to graph node label."""
        label_map = {
            'start': 'StartEnd',
            'end': 'StartEnd',
            'process': 'Process',
            'decision': 'Decision',
            'datastore': 'DataStore',
            'document': 'Document',
            'subprocess': 'SubProcess',
            'preparation': 'Preparation',
            'manual': 'ManualOperation',
            'delay': 'Delay',
            'terminator': 'Terminator'
        }
        return label_map.get(element_type.lower(), 'FlowElement')
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by matching keywords."""
        for i, header in enumerate(headers):
            header_lower = header.lower()
            for keyword in keywords:
                if keyword in header_lower:
                    return i
        return None
    
    def _get_context(self, text: str, term: str, window: int = 50) -> str:
        """Get context around a term in text."""
        index = text.find(term)
        if index == -1:
            return ""
        
        start = max(0, index - window)
        end = min(len(text), index + len(term) + window)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context