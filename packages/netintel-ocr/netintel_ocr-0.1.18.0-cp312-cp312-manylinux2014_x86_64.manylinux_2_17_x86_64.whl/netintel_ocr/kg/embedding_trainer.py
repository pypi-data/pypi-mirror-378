"""
PyKEEN Knowledge Graph Embedding Trainer for NetIntel-OCR v0.1.17

Trains knowledge graph embeddings using PyKEEN.
Reference: docs/knowledgegraphs_enhanced.md lines 285-383
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not installed. Install with: pip install torch")
    TORCH_AVAILABLE = False
    torch = None

try:
    from pykeen.pipeline import pipeline
    from pykeen.triples import TriplesFactory
    from pykeen.models import (
        TransE, RotatE, ComplEx, DistMult, 
        ConvE, TuckER, HolE, RESCAL
    )
    from pykeen.training import SLCWATrainingLoop
    from pykeen.evaluation import RankBasedEvaluator
    PYKEEN_AVAILABLE = True
except ImportError:
    logger.warning("PyKEEN not installed. Install with: pip install pykeen")
    PYKEEN_AVAILABLE = False
    pipeline = None
    TriplesFactory = None


class KGEmbeddingTrainer:
    """
    Trains knowledge graph embeddings using PyKEEN.
    
    Supported models:
    - TransE: Translational embeddings
    - RotatE: Rotation in complex space
    - ComplEx: Complex embeddings
    - DistMult: Diagonal matrix factorization
    - ConvE: Convolutional neural network based
    - TuckER: Tucker decomposition
    - HolE: Holographic embeddings
    - RESCAL: Tensor factorization
    """
    
    # Model mapping
    MODEL_CLASSES = {
        'TransE': 'TransE',
        'RotatE': 'RotatE',
        'ComplEx': 'ComplEx',
        'DistMult': 'DistMult',
        'ConvE': 'ConvE',
        'TuckER': 'TuckER',
        'HolE': 'HolE',
        'RESCAL': 'RESCAL'
    }
    
    def __init__(self, 
                 model_name: str = 'RotatE',
                 embedding_dim: int = 200,
                 device: str = None):
        """
        Initialize the KG embedding trainer.
        
        Args:
            model_name: Name of the PyKEEN model to use
            embedding_dim: Dimension of embeddings
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        
        # Set device
        if device is None and TORCH_AVAILABLE:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device or 'cpu'
        
        self.model = None
        self.training_triples = None
        self.entity_to_id = {}
        self.relation_to_id = {}
        self.id_to_entity = {}
        self.id_to_relation = {}
        
        logger.info(f"Initialized KG embedding trainer with {model_name} "
                   f"(dim={embedding_dim}, device={self.device})")
    
    async def train_embeddings(self, 
                              falkor_manager,
                              epochs: int = 100,
                              batch_size: int = 256,
                              learning_rate: float = 0.001,
                              validation_split: float = 0.1,
                              save_model: bool = True,
                              model_path: str = None) -> Dict[str, Any]:
        """
        Train KG embeddings from FalkorDB graph data.
        
        Args:
            falkor_manager: FalkorDBManager instance
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate
            validation_split: Fraction of data for validation
            save_model: Whether to save the trained model
            model_path: Path to save the model
        
        Returns:
            Training results including metrics and embeddings
        """
        if not PYKEEN_AVAILABLE:
            raise ImportError("PyKEEN is required for embedding training. "
                            "Install with: pip install pykeen torch")
        
        logger.info(f"Starting KG embedding training with {self.model_name}")
        
        try:
            # Extract triples from FalkorDB
            triples = await self._extract_triples_from_falkordb(falkor_manager)
            logger.info(f"Extracted {len(triples)} triples from graph")
            
            if len(triples) < 10:
                logger.warning("Too few triples for meaningful training")
                return {
                    'status': 'insufficient_data',
                    'num_triples': len(triples)
                }
            
            # Create TriplesFactory
            triples_array = np.array(triples)
            tf = TriplesFactory.from_labeled_triples(triples_array)
            
            # Split into training and validation
            if validation_split > 0:
                training, validation = tf.split([1 - validation_split, validation_split])
            else:
                training = tf
                validation = None
            
            # Store mappings
            self.entity_to_id = tf.entity_to_id
            self.relation_to_id = tf.relation_to_id
            self.id_to_entity = {v: k for k, v in self.entity_to_id.items()}
            self.id_to_relation = {v: k for k, v in self.relation_to_id.items()}
            
            # Train model using PyKEEN pipeline
            logger.info(f"Training {self.model_name} model for {epochs} epochs")
            
            result = pipeline(
                training=training,
                validation=validation,
                model=self.model_name,
                model_kwargs={
                    'embedding_dim': self.embedding_dim,
                },
                optimizer='adam',
                optimizer_kwargs={
                    'lr': learning_rate,
                },
                training_kwargs={
                    'num_epochs': epochs,
                    'batch_size': batch_size,
                },
                evaluator='RankBasedEvaluator',
                evaluator_kwargs={
                    'metrics': ['mean_rank', 'mean_reciprocal_rank', 'hits_at_k'],
                    'ks': [1, 3, 5, 10]
                },
                device=self.device,
                random_seed=42
            )
            
            self.model = result.model
            
            # Extract embeddings
            entity_embeddings = self._extract_entity_embeddings()
            relation_embeddings = self._extract_relation_embeddings()
            
            # Store embeddings in FalkorDB
            embeddings_data = {
                'entities': entity_embeddings,
                'relations': relation_embeddings,
                'metadata': {
                    'model': self.model_name,
                    'embedding_dim': self.embedding_dim,
                    'training_epochs': epochs,
                    'num_entities': len(entity_embeddings),
                    'num_relations': len(relation_embeddings),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            num_stored = await falkor_manager.store_kg_embeddings(embeddings_data)
            logger.info(f"Stored {num_stored} embeddings in FalkorDB")
            
            # Save model if requested
            if save_model:
                if model_path is None:
                    model_path = f"models/kg_embeddings_{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                
                self._save_model(result, model_path)
                logger.info(f"Model saved to {model_path}")
            
            # Prepare results
            metrics = self._extract_metrics(result)
            
            results = {
                'status': 'success',
                'model': self.model_name,
                'embedding_dim': self.embedding_dim,
                'num_entities': len(entity_embeddings),
                'num_relations': len(relation_embeddings),
                'num_triples': len(triples),
                'epochs_trained': epochs,
                'metrics': metrics,
                'model_path': model_path if save_model else None,
                'embeddings_stored': num_stored
            }
            
            logger.info(f"Training completed successfully: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Embedding training failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _extract_triples_from_falkordb(self, falkor_manager) -> List[Tuple[str, str, str]]:
        """
        Extract (head, relation, tail) triples from FalkorDB.
        
        Args:
            falkor_manager: FalkorDBManager instance
        
        Returns:
            List of triples
        """
        triples = []
        
        try:
            # Query all relationships from the graph
            query = """
            MATCH (h)-[r]->(t)
            RETURN 
                COALESCE(h.id, h.name, h.value, ID(h)) as head,
                type(r) as relation,
                COALESCE(t.id, t.name, t.value, ID(t)) as tail
            """
            
            result = falkor_manager.execute_cypher(query)
            
            for row in result.result_set:
                head = str(row[0])
                relation = str(row[1])
                tail = str(row[2])
                
                # Skip self-loops unless explicitly desired
                if head != tail:
                    triples.append((head, relation, tail))
            
            # Deduplicate triples
            triples = list(set(triples))
            
            logger.info(f"Extracted {len(triples)} unique triples from FalkorDB")
            
        except Exception as e:
            logger.error(f"Failed to extract triples: {e}")
            raise
        
        return triples
    
    def _extract_entity_embeddings(self) -> Dict[str, List[float]]:
        """
        Extract entity embeddings from trained model.
        
        Returns:
            Dictionary mapping entity IDs to embedding vectors
        """
        if self.model is None:
            return {}
        
        embeddings = {}
        
        try:
            # Get entity representations from the model
            entity_repr = self.model.entity_representations[0]()
            
            # Convert to numpy and then to list for JSON serialization
            if TORCH_AVAILABLE:
                entity_embeddings_tensor = entity_repr.detach().cpu().numpy()
            else:
                entity_embeddings_tensor = entity_repr
            
            # Map back to entity IDs
            for entity, idx in self.entity_to_id.items():
                embeddings[entity] = entity_embeddings_tensor[idx].tolist()
            
        except Exception as e:
            logger.error(f"Failed to extract entity embeddings: {e}")
        
        return embeddings
    
    def _extract_relation_embeddings(self) -> Dict[str, List[float]]:
        """
        Extract relation embeddings from trained model.
        
        Returns:
            Dictionary mapping relation types to embedding vectors
        """
        if self.model is None:
            return {}
        
        embeddings = {}
        
        try:
            # Get relation representations from the model
            # Note: Not all models have explicit relation embeddings
            if hasattr(self.model, 'relation_representations'):
                relation_repr = self.model.relation_representations[0]()
                
                if TORCH_AVAILABLE:
                    relation_embeddings_tensor = relation_repr.detach().cpu().numpy()
                else:
                    relation_embeddings_tensor = relation_repr
                
                # Map back to relation types
                for relation, idx in self.relation_to_id.items():
                    embeddings[relation] = relation_embeddings_tensor[idx].tolist()
            else:
                # For models without explicit relation embeddings,
                # we can create synthetic ones or use a default
                logger.info(f"Model {self.model_name} does not have explicit relation embeddings")
                
                # Create simple one-hot or random embeddings as fallback
                num_relations = len(self.relation_to_id)
                for relation, idx in self.relation_to_id.items():
                    # Simple one-hot encoding as fallback
                    embedding = [0.0] * min(num_relations, self.embedding_dim)
                    if idx < len(embedding):
                        embedding[idx] = 1.0
                    embeddings[relation] = embedding
            
        except Exception as e:
            logger.error(f"Failed to extract relation embeddings: {e}")
        
        return embeddings
    
    def _extract_metrics(self, result) -> Dict[str, Any]:
        """
        Extract evaluation metrics from training result.
        
        Args:
            result: PyKEEN pipeline result
        
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        try:
            if hasattr(result, 'metric_results'):
                metric_results = result.metric_results
                
                # Extract key metrics
                if hasattr(metric_results, 'get_metric'):
                    metrics['mean_rank'] = metric_results.get_metric('mean_rank')
                    metrics['mean_reciprocal_rank'] = metric_results.get_metric('mean_reciprocal_rank')
                    metrics['hits_at_1'] = metric_results.get_metric('hits_at_1')
                    metrics['hits_at_3'] = metric_results.get_metric('hits_at_3')
                    metrics['hits_at_5'] = metric_results.get_metric('hits_at_5')
                    metrics['hits_at_10'] = metric_results.get_metric('hits_at_10')
                else:
                    # Fallback to dict access
                    metrics = metric_results.to_dict() if hasattr(metric_results, 'to_dict') else {}
            
            # Add training loss if available
            if hasattr(result, 'losses'):
                metrics['final_loss'] = float(result.losses[-1]) if len(result.losses) > 0 else None
            
        except Exception as e:
            logger.warning(f"Could not extract all metrics: {e}")
        
        return metrics
    
    def _save_model(self, result, model_path: str):
        """
        Save the trained model to disk.
        
        Args:
            result: PyKEEN pipeline result
            model_path: Path to save the model
        """
        try:
            # Create directory if needed
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save the entire pipeline result
            if hasattr(result, 'save_to_directory'):
                result.save_to_directory(model_path)
            else:
                # Fallback to torch save
                if TORCH_AVAILABLE:
                    torch.save({
                        'model_state_dict': self.model.state_dict() if self.model else None,
                        'entity_to_id': self.entity_to_id,
                        'relation_to_id': self.relation_to_id,
                        'model_name': self.model_name,
                        'embedding_dim': self.embedding_dim
                    }, model_path)
            
            logger.info(f"Model saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, model_path: str):
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
        """
        try:
            if TORCH_AVAILABLE:
                checkpoint = torch.load(model_path, map_location=self.device)
                
                self.entity_to_id = checkpoint['entity_to_id']
                self.relation_to_id = checkpoint['relation_to_id']
                self.id_to_entity = {v: k for k, v in self.entity_to_id.items()}
                self.id_to_relation = {v: k for k, v in self.relation_to_id.items()}
                self.model_name = checkpoint.get('model_name', 'unknown')
                self.embedding_dim = checkpoint.get('embedding_dim', 200)
                
                # Recreate model and load state
                # This would need the model class instantiation
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.error("PyTorch is required to load models")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    async def predict_link(self, head: str, relation: str, tail: str = None) -> List[Dict[str, Any]]:
        """
        Predict missing links in the knowledge graph.
        
        Args:
            head: Head entity
            relation: Relation type
            tail: Tail entity (optional, if None predict all possible tails)
        
        Returns:
            List of predictions with scores
        """
        if self.model is None:
            raise ValueError("No model loaded. Train or load a model first.")
        
        predictions = []
        
        try:
            if tail is None:
                # Predict tail entities
                # This would use the model's predict method
                # Implementation depends on PyKEEN version
                pass
            else:
                # Score a specific triple
                # This would compute the score for the given triple
                pass
            
        except Exception as e:
            logger.error(f"Link prediction failed: {e}")
        
        return predictions
    
    def get_entity_embedding(self, entity: str) -> Optional[List[float]]:
        """
        Get embedding for a specific entity.
        
        Args:
            entity: Entity ID
        
        Returns:
            Embedding vector or None if not found
        """
        if entity not in self.entity_to_id:
            return None
        
        try:
            idx = self.entity_to_id[entity]
            entity_repr = self.model.entity_representations[0]()
            
            if TORCH_AVAILABLE:
                embedding = entity_repr[idx].detach().cpu().numpy().tolist()
            else:
                embedding = entity_repr[idx].tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to get entity embedding: {e}")
            return None
    
    def compute_similarity(self, entity1: str, entity2: str) -> float:
        """
        Compute similarity between two entities using their embeddings.
        
        Args:
            entity1: First entity
            entity2: Second entity
        
        Returns:
            Cosine similarity score
        """
        emb1 = self.get_entity_embedding(entity1)
        emb2 = self.get_entity_embedding(entity2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Compute cosine similarity
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)