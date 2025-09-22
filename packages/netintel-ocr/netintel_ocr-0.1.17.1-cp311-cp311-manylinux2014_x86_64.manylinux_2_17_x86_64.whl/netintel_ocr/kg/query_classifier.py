"""
Query Intent Classifier for NetIntel-OCR v0.1.17

Classifies query intent for optimal retrieval strategy.
Reference: docs/knowledgegraphs_enhanced.md lines 641-665
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classifications."""
    ENTITY_CENTRIC = "entity_centric"      # Specific entities
    RELATIONAL = "relational"              # Relationships between entities
    TOPOLOGICAL = "topological"            # Network paths and structure
    SEMANTIC = "semantic"                  # General concepts
    ANALYTICAL = "analytical"              # Analysis and aggregation
    EXPLORATORY = "exploratory"            # Open-ended exploration


class QueryIntentClassifier:
    """
    Classifies query intent for optimal retrieval strategy.
    
    Classification is based on:
    - Query keywords and patterns
    - Entity mentions
    - Relationship indicators
    - Topological terms
    - Semantic indicators
    """
    
    def __init__(self):
        """Initialize the query intent classifier."""
        
        # Entity-centric patterns
        self.entity_patterns = [
            r'\b(what|which|where)\s+(is|are)\s+\w+',
            r'\b(details|information|properties)\s+(of|about|for)\b',
            r'\b(show|get|find|display)\s+\w+\s+(details|info|properties)\b',
            r'\b(ip|address|configuration|status)\s+of\b',
            r'\bspecific\s+(device|entity|node)\b'
        ]
        
        # Relational patterns
        self.relational_patterns = [
            r'\b(connect|link|relate|associate)\s+(to|with|between)\b',
            r'\b(relationship|connection|link)\s+between\b',
            r'\bwhat\s+(connects|links)\s+to\b',
            r'\b(neighbor|adjacent|connected)\s+(to|with)\b',
            r'\b(depends|relies)\s+on\b',
            r'\b(upstream|downstream)\s+(from|of)\b'
        ]
        
        # Topological patterns
        self.topological_patterns = [
            r'\b(path|route)\s+(from|between|to)\b',
            r'\b(shortest|longest)\s+path\b',
            r'\b(network|topology)\s+(structure|layout)\b',
            r'\b(trace|follow)\s+the\s+(path|route)\b',
            r'\bhow\s+to\s+(reach|get to)\b',
            r'\b(flow|traffic)\s+(from|to|through)\b',
            r'\b(dmz|zone|segment|subnet)\b'
        ]
        
        # Semantic patterns
        self.semantic_patterns = [
            r'\b(similar|like|resembl)\b',
            r'\b(concept|idea|topic|theme)\b',
            r'\b(general|broad|overall)\b',
            r'\b(best\s+practice|recommendation|guideline)\b',
            r'\b(security|performance|reliability)\s+(issue|concern|problem)\b',
            r'\b(pattern|trend|behavior)\b'
        ]
        
        # Analytical patterns
        self.analytical_patterns = [
            r'\b(count|number|how\s+many)\b',
            r'\b(average|mean|median|sum|total)\b',
            r'\b(analyze|compare|contrast)\b',
            r'\b(distribution|statistics|metrics)\b',
            r'\b(group|cluster|categorize)\b',
            r'\b(rank|sort|order)\s+by\b'
        ]
        
        # Exploratory patterns
        self.exploratory_patterns = [
            r'\b(explore|browse|discover)\b',
            r'\b(what\s+else|other|more)\b',
            r'\b(interesting|unusual|notable)\b',
            r'\b(overview|summary|introduction)\b',
            r'\btell\s+me\s+(about|more)\b'
        ]
        
        # Keywords for different query types
        self.entity_keywords = {
            'router', 'switch', 'firewall', 'server', 'database', 
            'device', 'node', 'host', 'endpoint', 'component',
            'ip', 'address', 'port', 'interface', 'vlan'
        }
        
        self.relational_keywords = {
            'connect', 'link', 'relate', 'associate', 'depend',
            'communicate', 'interact', 'neighbor', 'adjacent',
            'upstream', 'downstream', 'peer', 'parent', 'child'
        }
        
        self.topological_keywords = {
            'path', 'route', 'topology', 'network', 'flow',
            'trace', 'hop', 'distance', 'reach', 'traverse',
            'zone', 'segment', 'subnet', 'vlan', 'dmz'
        }
        
        self.semantic_keywords = {
            'similar', 'like', 'concept', 'idea', 'meaning',
            'related', 'relevant', 'context', 'semantic',
            'understand', 'explain', 'describe', 'definition'
        }
        
        logger.info("Initialized Query Intent Classifier")
    
    def classify(self, query: str) -> QueryType:
        """
        Classify query intent.
        
        Args:
            query: Query string
        
        Returns:
            QueryType enum value
        """
        query_lower = query.lower()
        
        # Calculate scores for each query type
        scores = {
            QueryType.ENTITY_CENTRIC: self._score_entity_centric(query_lower),
            QueryType.RELATIONAL: self._score_relational(query_lower),
            QueryType.TOPOLOGICAL: self._score_topological(query_lower),
            QueryType.SEMANTIC: self._score_semantic(query_lower),
            QueryType.ANALYTICAL: self._score_analytical(query_lower),
            QueryType.EXPLORATORY: self._score_exploratory(query_lower)
        }
        
        # Get the type with highest score
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        
        # If no clear winner, default to semantic
        if max_score < 0.3:
            max_type = QueryType.SEMANTIC
        
        logger.debug(f"Query classification: {max_type.value} (score: {max_score:.2f})")
        logger.debug(f"All scores: {[(t.value, s) for t, s in scores.items()]}")
        
        return max_type
    
    def classify_with_confidence(self, query: str) -> Tuple[QueryType, float]:
        """
        Classify query with confidence score.
        
        Args:
            query: Query string
        
        Returns:
            Tuple of (QueryType, confidence_score)
        """
        query_lower = query.lower()
        
        # Calculate scores
        scores = {
            QueryType.ENTITY_CENTRIC: self._score_entity_centric(query_lower),
            QueryType.RELATIONAL: self._score_relational(query_lower),
            QueryType.TOPOLOGICAL: self._score_topological(query_lower),
            QueryType.SEMANTIC: self._score_semantic(query_lower),
            QueryType.ANALYTICAL: self._score_analytical(query_lower),
            QueryType.EXPLORATORY: self._score_exploratory(query_lower)
        }
        
        # Get top type
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        
        # Calculate confidence based on score distribution
        total_score = sum(scores.values())
        if total_score > 0:
            confidence = max_score / total_score
        else:
            confidence = 0.0
        
        # Adjust for low scores
        if max_score < 0.3:
            max_type = QueryType.SEMANTIC
            confidence = 0.3
        
        return max_type, confidence
    
    def get_recommended_strategy(self, query_type: QueryType) -> str:
        """
        Get recommended retrieval strategy for query type.
        
        Args:
            query_type: Classified query type
        
        Returns:
            Recommended strategy name
        """
        strategy_map = {
            QueryType.ENTITY_CENTRIC: "graph_first",
            QueryType.RELATIONAL: "graph_first",
            QueryType.TOPOLOGICAL: "graph_first",
            QueryType.SEMANTIC: "vector_first",
            QueryType.ANALYTICAL: "parallel",
            QueryType.EXPLORATORY: "adaptive"
        }
        
        return strategy_map.get(query_type, "adaptive")
    
    def _score_entity_centric(self, query: str) -> float:
        """Score query for entity-centric classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.entity_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check keywords
        words = query.split()
        for word in words:
            if word in self.entity_keywords:
                score += 0.2
        
        # Check for specific entity names (capitalized words)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', query)
        if capitalized:
            score += 0.1 * len(capitalized)
        
        # Check for IP addresses
        if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', query):
            score += 0.5
        
        return min(score, 1.0)
    
    def _score_relational(self, query: str) -> float:
        """Score query for relational classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.relational_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check keywords
        words = query.split()
        for word in words:
            if word in self.relational_keywords:
                score += 0.2
        
        # Check for "between" with entities
        if 'between' in query and any(word[0].isupper() for word in words):
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_topological(self, query: str) -> float:
        """Score query for topological classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.topological_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check keywords
        words = query.split()
        for word in words:
            if word in self.topological_keywords:
                score += 0.2
        
        # Check for "from...to" pattern
        if 'from' in query and 'to' in query:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_semantic(self, query: str) -> float:
        """Score query for semantic classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.semantic_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check keywords
        words = query.split()
        for word in words:
            if word in self.semantic_keywords:
                score += 0.2
        
        # Check for question words without specific entities
        question_words = ['what', 'how', 'why', 'when', 'where']
        if any(word in query for word in question_words) and not any(word[0].isupper() for word in words[1:]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_analytical(self, query: str) -> float:
        """Score query for analytical classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.analytical_patterns:
            if re.search(pattern, query):
                score += 0.4
        
        # Check for numbers and comparisons
        if re.search(r'\b\d+\b', query):
            score += 0.1
        
        if any(word in query for word in ['more', 'less', 'greater', 'fewer', 'most', 'least']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_exploratory(self, query: str) -> float:
        """Score query for exploratory classification."""
        score = 0.0
        
        # Check patterns
        for pattern in self.exploratory_patterns:
            if re.search(pattern, query):
                score += 0.3
        
        # Check for open-ended questions
        if query.startswith(('tell me', 'show me', 'what else', 'what more')):
            score += 0.3
        
        # Check for vague terms
        vague_terms = ['interesting', 'important', 'relevant', 'useful', 'notable']
        if any(term in query for term in vague_terms):
            score += 0.2
        
        return min(score, 1.0)
    
    def extract_entities(self, query: str) -> List[str]:
        """
        Extract potential entity mentions from query.
        
        Args:
            query: Query string
        
        Returns:
            List of potential entity names
        """
        entities = []
        
        # Extract capitalized words (potential entity names)
        capitalized = re.findall(r'\b[A-Z][\w-]*\b', query)
        entities.extend(capitalized)
        
        # Extract IP addresses
        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', query)
        entities.extend(ips)
        
        # Extract device patterns (e.g., "router1", "fw-dmz-01")
        device_patterns = re.findall(r'\b\w+[-_]\w+[-_]\d+\b|\b\w+\d+\b', query.lower())
        entities.extend(device_patterns)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity.lower() not in seen:
                seen.add(entity.lower())
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_relationships(self, query: str) -> List[str]:
        """
        Extract relationship types from query.
        
        Args:
            query: Query string
        
        Returns:
            List of relationship types
        """
        relationships = []
        
        # Common relationship terms
        rel_terms = {
            'connects': 'CONNECTS_TO',
            'connected': 'CONNECTS_TO',
            'links': 'LINKS_TO',
            'depends': 'DEPENDS_ON',
            'upstream': 'UPSTREAM_OF',
            'downstream': 'DOWNSTREAM_OF',
            'contains': 'CONTAINS',
            'part of': 'PART_OF',
            'located': 'LOCATED_IN',
            'flows': 'FLOWS_TO'
        }
        
        query_lower = query.lower()
        for term, rel_type in rel_terms.items():
            if term in query_lower:
                relationships.append(rel_type)
        
        return relationships
    
    def get_query_features(self, query: str) -> Dict[str, Any]:
        """
        Extract comprehensive features from query.
        
        Args:
            query: Query string
        
        Returns:
            Dictionary of query features
        """
        query_type, confidence = self.classify_with_confidence(query)
        
        features = {
            'query_type': query_type.value,
            'confidence': confidence,
            'recommended_strategy': self.get_recommended_strategy(query_type),
            'entities': self.extract_entities(query),
            'relationships': self.extract_relationships(query),
            'has_path_query': 'path' in query.lower() or 'route' in query.lower(),
            'has_similarity_query': 'similar' in query.lower() or 'like' in query.lower(),
            'has_aggregation': any(word in query.lower() for word in ['count', 'sum', 'average', 'total']),
            'query_length': len(query.split()),
            'has_question': query.strip().endswith('?')
        }
        
        return features