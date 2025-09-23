"""
Hybrid Knowledge Graph System for NetIntel-OCR v0.1.17

Main orchestrator for the hybrid KG+Vector system.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import asyncio

from .falkordb_manager import FalkorDBManager
from .graph_constructor import KnowledgeGraphConstructor

logger = logging.getLogger(__name__)


class HybridSystem:
    """
    Main orchestrator for the hybrid Knowledge Graph and Vector system.
    
    This class coordinates:
    - Document processing with KG generation
    - Integration with existing NetIntel-OCR pipeline
    - Hybrid storage management (FalkorDB + Milvus)
    """
    
    def __init__(self, ocr_instance=None, enable_kg: bool = True):
        """
        Initialize the hybrid system.
        
        Args:
            ocr_instance: NetIntel-OCR instance (optional)
            enable_kg: Whether to enable KG features
        """
        self.ocr = ocr_instance
        self.enable_kg = enable_kg
        self.falkor_manager = None
        self.graph_constructor = None
        
        if self.enable_kg:
            self._initialize_kg_components()
    
    def _initialize_kg_components(self):
        """Initialize Knowledge Graph components."""
        try:
            # Initialize FalkorDB manager
            self.falkor_manager = FalkorDBManager()
            if self.falkor_manager.connect():
                logger.info("FalkorDB connected successfully")
                
                # Initialize graph constructor
                self.graph_constructor = KnowledgeGraphConstructor(self.falkor_manager)
                logger.info("Knowledge Graph components initialized")
            else:
                logger.error("Failed to connect to FalkorDB")
                self.enable_kg = False
                
        except Exception as e:
            logger.error(f"Failed to initialize KG components: {e}")
            self.enable_kg = False
    
    async def process_document(self, 
                              document_path: str,
                              enable_vector: bool = True,
                              kg_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a document with hybrid KG+Vector generation.
        
        Args:
            document_path: Path to the document
            enable_vector: Whether to generate vectors (default: True)
            kg_config: KG-specific configuration
        
        Returns:
            Processing results dictionary
        """
        results = {
            'document': document_path,
            'vector_generation': enable_vector,
            'kg_generation': self.enable_kg,
            'status': 'processing'
        }
        
        try:
            # Process with existing NetIntel-OCR pipeline if available
            if self.ocr:
                ocr_results = await self._process_with_ocr(document_path, enable_vector)
                results['ocr_results'] = ocr_results
                
                # Extract content for KG processing
                if self.enable_kg and ocr_results.get('success'):
                    kg_results = await self._build_knowledge_graph(ocr_results)
                    results['kg_results'] = kg_results
            else:
                # Direct KG processing without OCR
                if self.enable_kg:
                    logger.warning("Processing without OCR - limited KG extraction")
                    # This would need document parsing logic
            
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    async def _process_with_ocr(self, document_path: str, enable_vector: bool) -> Dict[str, Any]:
        """Process document using NetIntel-OCR pipeline."""
        # This would integrate with the existing NetIntel-OCR processing
        # For now, returning a mock structure
        return {
            'success': True,
            'network_diagrams': [],
            'flow_diagrams': [],
            'tables': [],
            'text_content': []
        }
    
    async def _build_knowledge_graph(self, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build knowledge graph from OCR results."""
        kg_results = {
            'network_graphs': [],
            'flow_graphs': [],
            'table_entities': [],
            'text_entities': []
        }
        
        try:
            # Process network diagrams
            for diagram in ocr_results.get('network_diagrams', []):
                result = await self.graph_constructor.process_network_diagram(diagram)
                kg_results['network_graphs'].append(result)
            
            # Process flow diagrams
            for flow in ocr_results.get('flow_diagrams', []):
                result = await self.graph_constructor.process_flow_diagram(flow)
                kg_results['flow_graphs'].append(result)
            
            # Process tables
            for table in ocr_results.get('tables', []):
                result = await self.graph_constructor.process_table(table)
                kg_results['table_entities'].append(result)
            
            # Process text content
            for text in ocr_results.get('text_content', []):
                result = await self.graph_constructor.process_text(text)
                kg_results['text_entities'].append(result)
            
            return kg_results
            
        except Exception as e:
            logger.error(f"Knowledge graph construction failed: {e}")
            return {'error': str(e)}
    
    async def initialize_indices(self):
        """Initialize FalkorDB indices and schema."""
        if self.falkor_manager and self.falkor_manager._connected:
            await self.falkor_manager.create_indices()
            logger.info("FalkorDB indices created")
        else:
            logger.error("Cannot create indices - FalkorDB not connected")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        if self.falkor_manager and self.falkor_manager._connected:
            return self.falkor_manager.get_graph_statistics()
        return {'error': 'FalkorDB not connected'}
    
    def close(self):
        """Close all connections."""
        if self.falkor_manager:
            self.falkor_manager.close()
            logger.info("Hybrid system connections closed")