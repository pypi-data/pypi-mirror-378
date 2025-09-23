"""
Result Reranking Service
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from sentence_transformers import CrossEncoder
from sklearn.preprocessing import MinMaxScaler
from .embedding import get_embedding_service


logger = logging.getLogger(__name__)


class RerankingService:
    """Service for reranking search results using various strategies"""

    def __init__(
        self,
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        enable_cross_encoder: bool = True,
        enable_feature_reranking: bool = True,
        enable_reciprocal_rank_fusion: bool = True,
    ):
        self.enable_cross_encoder = enable_cross_encoder
        self.enable_feature_reranking = enable_feature_reranking
        self.enable_rrf = enable_reciprocal_rank_fusion

        # Initialize cross-encoder for reranking
        if enable_cross_encoder:
            try:
                self.cross_encoder = CrossEncoder(cross_encoder_model)
                logger.info(f"Initialized cross-encoder: {cross_encoder_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize cross-encoder: {e}")
                self.cross_encoder = None
                self.enable_cross_encoder = False

        # Get embedding service
        self.embedding_service = get_embedding_service()

        # Feature scaler for normalization
        self.scaler = MinMaxScaler()

    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        strategy: str = "hybrid",
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results using specified strategy

        Args:
            query: Search query
            results: List of search results
            strategy: Reranking strategy (cross_encoder, features, rrf, hybrid)
            top_k: Return only top K results

        Returns:
            Reranked results
        """

        if not results:
            return results

        start_time = datetime.utcnow()

        # Apply reranking strategy
        if strategy == "cross_encoder" and self.enable_cross_encoder:
            reranked = self._cross_encoder_rerank(query, results)
        elif strategy == "features" and self.enable_feature_reranking:
            reranked = self._feature_based_rerank(query, results)
        elif strategy == "rrf" and self.enable_rrf:
            reranked = self._reciprocal_rank_fusion(results)
        elif strategy == "hybrid":
            reranked = self._hybrid_rerank(query, results)
        else:
            # Default: sort by original score
            reranked = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        # Apply top_k if specified
        if top_k:
            reranked = reranked[:top_k]

        # Add reranking metadata
        for i, result in enumerate(reranked):
            result["rerank_position"] = i + 1
            result["rerank_strategy"] = strategy

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Reranked {len(results)} results using {strategy} strategy "
            f"in {execution_time:.3f} seconds"
        )

        return reranked

    def _cross_encoder_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Rerank using cross-encoder model"""

        if not self.cross_encoder:
            return results

        # Prepare query-document pairs
        pairs = []
        for result in results:
            content = result.get("content", "") or result.get("snippet", "")
            pairs.append([query, content])

        # Get cross-encoder scores
        try:
            scores = self.cross_encoder.predict(pairs)

            # Add scores and sort
            for result, score in zip(results, scores):
                result["cross_encoder_score"] = float(score)

            return sorted(
                results,
                key=lambda x: x.get("cross_encoder_score", 0),
                reverse=True,
            )

        except Exception as e:
            logger.error(f"Cross-encoder reranking failed: {e}")
            return results

    def _feature_based_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Rerank based on multiple features"""

        features = []
        for result in results:
            feature_vector = self._extract_features(query, result)
            features.append(feature_vector)

        # Normalize features
        if features:
            features = np.array(features)
            if features.shape[0] > 1:
                features = self.scaler.fit_transform(features)

            # Calculate composite score
            # Weights for different features
            weights = np.array([
                0.3,  # Original score
                0.2,  # Query term coverage
                0.15,  # Document length
                0.15,  # Freshness
                0.1,  # Source quality
                0.1,  # Confidence
            ])

            # Ensure weights match feature dimensions
            if len(weights) > features.shape[1]:
                weights = weights[: features.shape[1]]

            composite_scores = np.dot(features, weights)

            # Add scores and sort
            for result, score in zip(results, composite_scores):
                result["feature_score"] = float(score)

            return sorted(
                results,
                key=lambda x: x.get("feature_score", 0),
                reverse=True,
            )

        return results

    def _extract_features(
        self,
        query: str,
        result: Dict[str, Any],
    ) -> np.ndarray:
        """Extract features for reranking"""

        features = []

        # 1. Original score (normalized)
        original_score = result.get("score", 0.0)
        features.append(original_score)

        # 2. Query term coverage
        query_terms = set(query.lower().split())
        content = result.get("content", "") or result.get("snippet", "")
        content_terms = set(content.lower().split())
        if query_terms:
            coverage = len(query_terms & content_terms) / len(query_terms)
        else:
            coverage = 0.0
        features.append(coverage)

        # 3. Document length (inverse, shorter is better for snippets)
        doc_length = len(content.split())
        length_score = 1.0 / (1.0 + doc_length / 100.0)
        features.append(length_score)

        # 4. Freshness (if timestamp available)
        created_at = result.get("created_at")
        if created_at:
            try:
                if isinstance(created_at, str):
                    doc_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    doc_time = created_at

                age_days = (datetime.utcnow() - doc_time.replace(tzinfo=None)).days
                freshness = 1.0 / (1.0 + age_days / 365.0)
            except:
                freshness = 0.5
        else:
            freshness = 0.5
        features.append(freshness)

        # 5. Source quality (based on content type)
        content_type = result.get("content_type", "text")
        quality_scores = {
            "text": 0.7,
            "table": 0.8,
            "diagram": 0.9,
            "entity": 0.85,
        }
        source_quality = quality_scores.get(content_type, 0.5)
        features.append(source_quality)

        # 6. Confidence score
        confidence = result.get("confidence", 0.5)
        features.append(confidence)

        return np.array(features)

    def _reciprocal_rank_fusion(
        self,
        results: List[Dict[str, Any]],
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion for combining multiple result lists

        Args:
            results: Results with potential multiple scores
            k: Constant for RRF (default 60)

        Returns:
            Reranked results
        """

        # Group results by ID
        result_groups = {}
        for result in results:
            result_id = result.get("id") or result.get("document_id")
            if result_id:
                if result_id not in result_groups:
                    result_groups[result_id] = []
                result_groups[result_id].append(result)

        # Calculate RRF scores
        rrf_scores = {}
        for result_id, group in result_groups.items():
            rrf_score = 0.0

            for item in group:
                # Get rank from position or calculate from score
                rank = item.get("rank")
                if rank is None and "score" in item:
                    # Estimate rank based on score (higher score = lower rank)
                    rank = int((1.0 - item["score"]) * 100) + 1

                if rank:
                    rrf_score += 1.0 / (k + rank)

            rrf_scores[result_id] = rrf_score

            # Use the first result as template
            result_groups[result_id][0]["rrf_score"] = rrf_score

        # Sort by RRF score
        sorted_results = sorted(
            [group[0] for group in result_groups.values()],
            key=lambda x: x.get("rrf_score", 0),
            reverse=True,
        )

        return sorted_results

    def _hybrid_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Hybrid reranking combining multiple strategies"""

        # Apply different reranking strategies
        strategies_scores = {}

        # Cross-encoder scores
        if self.enable_cross_encoder and self.cross_encoder:
            ce_results = self._cross_encoder_rerank(query, results.copy())
            for i, result in enumerate(ce_results):
                result_id = result.get("id") or result.get("document_id")
                if result_id not in strategies_scores:
                    strategies_scores[result_id] = {}
                strategies_scores[result_id]["cross_encoder"] = (
                    1.0 - i / len(ce_results)
                )  # Convert rank to score

        # Feature-based scores
        if self.enable_feature_reranking:
            feature_results = self._feature_based_rerank(query, results.copy())
            for i, result in enumerate(feature_results):
                result_id = result.get("id") or result.get("document_id")
                if result_id not in strategies_scores:
                    strategies_scores[result_id] = {}
                strategies_scores[result_id]["features"] = result.get("feature_score", 0)

        # Original scores
        for result in results:
            result_id = result.get("id") or result.get("document_id")
            if result_id not in strategies_scores:
                strategies_scores[result_id] = {}
            strategies_scores[result_id]["original"] = result.get("score", 0)

        # Combine scores with weights
        weights = {
            "cross_encoder": 0.4,
            "features": 0.3,
            "original": 0.3,
        }

        final_scores = {}
        for result_id, scores in strategies_scores.items():
            final_score = 0.0
            total_weight = 0.0

            for strategy, score in scores.items():
                weight = weights.get(strategy, 0.1)
                final_score += score * weight
                total_weight += weight

            if total_weight > 0:
                final_scores[result_id] = final_score / total_weight
            else:
                final_scores[result_id] = 0.0

        # Apply final scores to results
        for result in results:
            result_id = result.get("id") or result.get("document_id")
            result["hybrid_score"] = final_scores.get(result_id, 0.0)

        # Sort by hybrid score
        return sorted(results, key=lambda x: x.get("hybrid_score", 0), reverse=True)

    def learn_from_feedback(
        self,
        query: str,
        results: List[Dict[str, Any]],
        clicked_positions: List[int],
    ):
        """
        Learn from user feedback to improve reranking

        Args:
            query: Search query
            results: Original results
            clicked_positions: Positions of clicked results (0-indexed)
        """

        # This would implement learning from user feedback
        # For example, adjusting weights based on click patterns

        logger.info(
            f"Received feedback for query '{query}': "
            f"clicks at positions {clicked_positions}"
        )

        # Store feedback for future model updates
        # In production, this would update a feedback database

    def evaluate_reranking(
        self,
        original_results: List[Dict[str, Any]],
        reranked_results: List[Dict[str, Any]],
        relevant_ids: List[str],
    ) -> Dict[str, float]:
        """
        Evaluate reranking performance

        Args:
            original_results: Original result order
            reranked_results: Reranked result order
            relevant_ids: IDs of relevant documents

        Returns:
            Evaluation metrics
        """

        def calculate_metrics(results):
            """Calculate ranking metrics"""

            precisions = []
            recalls = []
            relevant_found = 0

            for i, result in enumerate(results):
                result_id = result.get("id") or result.get("document_id")
                if result_id in relevant_ids:
                    relevant_found += 1
                    precision = relevant_found / (i + 1)
                    recall = relevant_found / len(relevant_ids)
                    precisions.append(precision)
                    recalls.append(recall)

            # Mean Average Precision (MAP)
            map_score = sum(precisions) / len(relevant_ids) if precisions else 0

            # Precision at K
            p_at_5 = (
                sum(
                    1
                    for r in results[:5]
                    if (r.get("id") or r.get("document_id")) in relevant_ids
                )
                / min(5, len(results))
                if results
                else 0
            )

            p_at_10 = (
                sum(
                    1
                    for r in results[:10]
                    if (r.get("id") or r.get("document_id")) in relevant_ids
                )
                / min(10, len(results))
                if results
                else 0
            )

            return {
                "map": map_score,
                "p@5": p_at_5,
                "p@10": p_at_10,
            }

        original_metrics = calculate_metrics(original_results)
        reranked_metrics = calculate_metrics(reranked_results)

        improvement = {
            "map_improvement": reranked_metrics["map"] - original_metrics["map"],
            "p@5_improvement": reranked_metrics["p@5"] - original_metrics["p@5"],
            "p@10_improvement": reranked_metrics["p@10"] - original_metrics["p@10"],
        }

        return {
            "original": original_metrics,
            "reranked": reranked_metrics,
            "improvement": improvement,
        }


# Global reranking service instance
reranking_service = RerankingService()