"""
Embedding Utilities for NetIntel-OCR v0.1.17

Utility functions for KG embeddings including visualization and analysis.
"""

import os
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import seaborn as sns

logger = logging.getLogger(__name__)

# Set style for visualizations
try:
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
except:
    pass


class EmbeddingAnalyzer:
    """
    Analyzes and visualizes KG embeddings.
    
    Provides functionality for:
    - Dimensionality reduction (t-SNE, PCA)
    - Clustering analysis
    - Embedding quality metrics
    - Visualization of embedding space
    """
    
    def __init__(self, embeddings: Dict[str, List[float]], 
                 entity_types: Dict[str, str] = None):
        """
        Initialize the embedding analyzer.
        
        Args:
            embeddings: Dictionary mapping entity IDs to embedding vectors
            entity_types: Optional dictionary mapping entity IDs to types
        """
        self.embeddings = embeddings
        self.entity_types = entity_types or {}
        self.entity_ids = list(embeddings.keys())
        self.embedding_matrix = np.array(list(embeddings.values()))
        
        logger.info(f"Initialized analyzer with {len(self.entity_ids)} embeddings")
    
    def reduce_dimensions(self, method: str = 'tsne', n_components: int = 2) -> np.ndarray:
        """
        Reduce embedding dimensions for visualization.
        
        Args:
            method: Reduction method ('tsne' or 'pca')
            n_components: Number of components (2 or 3)
        
        Returns:
            Reduced embedding matrix
        """
        if method == 'tsne':
            reducer = TSNE(n_components=n_components, random_state=42, 
                          perplexity=min(30, len(self.entity_ids) - 1))
        elif method == 'pca':
            reducer = PCA(n_components=n_components, random_state=42)
        else:
            raise ValueError(f"Unknown reduction method: {method}")
        
        reduced = reducer.fit_transform(self.embedding_matrix)
        
        logger.info(f"Reduced dimensions from {self.embedding_matrix.shape[1]} "
                   f"to {n_components} using {method}")
        
        return reduced
    
    def visualize_embeddings(self, 
                            save_path: str = None,
                            method: str = 'tsne',
                            show_labels: bool = False,
                            color_by_type: bool = True) -> None:
        """
        Visualize embeddings in 2D space.
        
        Args:
            save_path: Path to save the visualization
            method: Dimensionality reduction method
            show_labels: Whether to show entity labels
            color_by_type: Whether to color by entity type
        """
        # Reduce dimensions
        reduced = self.reduce_dimensions(method=method, n_components=2)
        
        # Create figure
        plt.figure(figsize=(14, 10))
        
        if color_by_type and self.entity_types:
            # Color by entity type
            unique_types = list(set(self.entity_types.values()))
            colors = plt.cm.tab20(np.linspace(0, 1, len(unique_types)))
            type_to_color = dict(zip(unique_types, colors))
            
            for entity_type in unique_types:
                mask = [self.entity_types.get(eid, 'unknown') == entity_type 
                       for eid in self.entity_ids]
                points = reduced[mask]
                if len(points) > 0:
                    plt.scatter(points[:, 0], points[:, 1], 
                              label=entity_type, 
                              alpha=0.7, s=50)
            
            plt.legend(title='Entity Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            # Single color
            plt.scatter(reduced[:, 0], reduced[:, 1], alpha=0.7, s=50)
        
        if show_labels and len(self.entity_ids) < 50:
            # Add labels for small graphs
            for i, entity_id in enumerate(self.entity_ids):
                plt.annotate(entity_id, 
                           (reduced[i, 0], reduced[i, 1]),
                           fontsize=8, alpha=0.7)
        
        plt.title(f'KG Embeddings Visualization ({method.upper()})')
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Visualization saved to {save_path}")
        
        plt.show()
    
    def visualize_3d_embeddings(self, 
                               save_path: str = None,
                               method: str = 'pca') -> None:
        """
        Visualize embeddings in 3D space.
        
        Args:
            save_path: Path to save the visualization
            method: Dimensionality reduction method
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # Reduce dimensions
        reduced = self.reduce_dimensions(method=method, n_components=3)
        
        # Create 3D figure
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        if self.entity_types:
            # Color by entity type
            unique_types = list(set(self.entity_types.values()))
            colors = plt.cm.tab20(np.linspace(0, 1, len(unique_types)))
            type_to_color = dict(zip(unique_types, colors))
            
            for entity_type in unique_types:
                mask = [self.entity_types.get(eid, 'unknown') == entity_type 
                       for eid in self.entity_ids]
                points = reduced[mask]
                if len(points) > 0:
                    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                             label=entity_type, alpha=0.7, s=50)
            
            ax.legend(title='Entity Type')
        else:
            ax.scatter(reduced[:, 0], reduced[:, 1], reduced[:, 2], 
                      alpha=0.7, s=50)
        
        ax.set_title(f'3D KG Embeddings Visualization ({method.upper()})')
        ax.set_xlabel('Component 1')
        ax.set_ylabel('Component 2')
        ax.set_zlabel('Component 3')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"3D visualization saved to {save_path}")
        
        plt.show()
    
    def compute_embedding_statistics(self) -> Dict[str, Any]:
        """
        Compute statistics about the embedding space.
        
        Returns:
            Dictionary with various statistics
        """
        stats = {}
        
        # Basic statistics
        stats['num_embeddings'] = len(self.entity_ids)
        stats['embedding_dim'] = self.embedding_matrix.shape[1]
        
        # Norm statistics
        norms = np.linalg.norm(self.embedding_matrix, axis=1)
        stats['mean_norm'] = float(np.mean(norms))
        stats['std_norm'] = float(np.std(norms))
        stats['min_norm'] = float(np.min(norms))
        stats['max_norm'] = float(np.max(norms))
        
        # Distance statistics
        if len(self.entity_ids) < 1000:  # Only for small graphs
            distances = []
            for i in range(len(self.embedding_matrix)):
                for j in range(i + 1, len(self.embedding_matrix)):
                    dist = np.linalg.norm(
                        self.embedding_matrix[i] - self.embedding_matrix[j]
                    )
                    distances.append(dist)
            
            if distances:
                stats['mean_distance'] = float(np.mean(distances))
                stats['std_distance'] = float(np.std(distances))
                stats['min_distance'] = float(np.min(distances))
                stats['max_distance'] = float(np.max(distances))
        
        # Type distribution if available
        if self.entity_types:
            type_counts = {}
            for entity_type in self.entity_types.values():
                type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
            stats['type_distribution'] = type_counts
        
        return stats
    
    def find_nearest_neighbors(self, 
                              entity_id: str, 
                              k: int = 10) -> List[Tuple[str, float]]:
        """
        Find k nearest neighbors for an entity.
        
        Args:
            entity_id: Entity to find neighbors for
            k: Number of neighbors
        
        Returns:
            List of (entity_id, distance) tuples
        """
        if entity_id not in self.embeddings:
            raise ValueError(f"Entity {entity_id} not found")
        
        query_embedding = np.array(self.embeddings[entity_id])
        
        # Compute distances to all other entities
        distances = []
        for other_id, other_embedding in self.embeddings.items():
            if other_id != entity_id:
                dist = np.linalg.norm(query_embedding - np.array(other_embedding))
                distances.append((other_id, float(dist)))
        
        # Sort by distance and return top k
        distances.sort(key=lambda x: x[1])
        
        return distances[:k]
    
    def cluster_embeddings(self, n_clusters: int = 5) -> Dict[str, int]:
        """
        Cluster embeddings using K-means.
        
        Args:
            n_clusters: Number of clusters
        
        Returns:
            Dictionary mapping entity IDs to cluster assignments
        """
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(self.embedding_matrix)
        
        cluster_assignments = {}
        for i, entity_id in enumerate(self.entity_ids):
            cluster_assignments[entity_id] = int(clusters[i])
        
        logger.info(f"Clustered {len(self.entity_ids)} entities into {n_clusters} clusters")
        
        return cluster_assignments
    
    def save_embeddings(self, output_path: str, format: str = 'json'):
        """
        Save embeddings to file.
        
        Args:
            output_path: Path to save embeddings
            format: Format ('json', 'npy', 'tsv')
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump({
                    'embeddings': self.embeddings,
                    'entity_types': self.entity_types
                }, f, indent=2)
        elif format == 'npy':
            np.save(output_path, self.embedding_matrix)
            # Save mapping separately
            mapping_path = output_path.replace('.npy', '_mapping.json')
            with open(mapping_path, 'w') as f:
                json.dump({
                    'entity_ids': self.entity_ids,
                    'entity_types': self.entity_types
                }, f, indent=2)
        elif format == 'tsv':
            with open(output_path, 'w') as f:
                # Write header
                f.write('entity_id\ttype\t' + 
                       '\t'.join(f'dim_{i}' for i in range(self.embedding_matrix.shape[1])) + 
                       '\n')
                # Write data
                for i, entity_id in enumerate(self.entity_ids):
                    entity_type = self.entity_types.get(entity_id, 'unknown')
                    embedding_str = '\t'.join(str(x) for x in self.embedding_matrix[i])
                    f.write(f'{entity_id}\t{entity_type}\t{embedding_str}\n')
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Embeddings saved to {output_path} in {format} format")


class EmbeddingEvaluator:
    """
    Evaluates the quality of KG embeddings.
    """
    
    @staticmethod
    def evaluate_link_prediction(model, test_triples: List[Tuple[str, str, str]]) -> Dict[str, float]:
        """
        Evaluate link prediction performance.
        
        Args:
            model: Trained embedding model
            test_triples: Test triples for evaluation
        
        Returns:
            Dictionary with evaluation metrics
        """
        # This would implement link prediction evaluation
        # For now, returning placeholder metrics
        return {
            'mean_rank': 0.0,
            'mean_reciprocal_rank': 0.0,
            'hits_at_1': 0.0,
            'hits_at_5': 0.0,
            'hits_at_10': 0.0
        }
    
    @staticmethod
    def evaluate_clustering_quality(embeddings: np.ndarray, labels: List[int]) -> Dict[str, float]:
        """
        Evaluate clustering quality of embeddings.
        
        Args:
            embeddings: Embedding matrix
            labels: True labels for entities
        
        Returns:
            Dictionary with clustering metrics
        """
        from sklearn.metrics import silhouette_score, calinski_harabasz_score
        
        try:
            silhouette = silhouette_score(embeddings, labels)
            calinski = calinski_harabasz_score(embeddings, labels)
            
            return {
                'silhouette_score': float(silhouette),
                'calinski_harabasz_score': float(calinski)
            }
        except:
            return {}


def load_embeddings_from_falkordb(falkor_manager) -> Tuple[Dict[str, List[float]], Dict[str, str]]:
    """
    Load embeddings from FalkorDB.
    
    Args:
        falkor_manager: FalkorDBManager instance
    
    Returns:
        Tuple of (embeddings dict, entity types dict)
    """
    embeddings = {}
    entity_types = {}
    
    query = """
    MATCH (n)
    WHERE n.kg_embedding IS NOT NULL
    RETURN n.id, n.kg_embedding, labels(n)[0]
    """
    
    result = falkor_manager.execute_cypher(query)
    
    for row in result.result_set:
        entity_id = row[0]
        embedding = row[1]
        entity_type = row[2]
        
        embeddings[entity_id] = embedding
        entity_types[entity_id] = entity_type
    
    logger.info(f"Loaded {len(embeddings)} embeddings from FalkorDB")
    
    return embeddings, entity_types