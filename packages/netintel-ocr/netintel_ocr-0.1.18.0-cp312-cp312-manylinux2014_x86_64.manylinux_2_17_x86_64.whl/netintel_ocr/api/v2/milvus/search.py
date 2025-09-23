"""
Milvus Search Engine for Vector and Hybrid Search
"""

from typing import Dict, Any, List, Optional, Union
from pymilvus import Collection, utility
import numpy as np
import logging
from datetime import datetime
from ..services.embedding import get_embedding_service
from ..exceptions import MilvusSearchError, ValidationError
from .connection import get_milvus_connection
from .schemas import DocumentsCollectionSchema, EntitiesCollectionSchema


logger = logging.getLogger(__name__)


class MilvusSearchEngine:
    """Advanced search engine for Milvus collections"""

    def __init__(self):
        self.conn = get_milvus_connection()
        self.embedding_service = get_embedding_service()

    def vector_search(
        self,
        collection_name: str,
        query_vectors: Optional[Union[List[float], List[List[float]]]] = None,
        query_texts: Optional[Union[str, List[str]]] = None,
        filter_expression: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        partition_names: Optional[List[str]] = None,
        search_params: Optional[Dict[str, Any]] = None,
        consistency_level: str = "Strong",
        guarantee_timestamp: Optional[int] = None,
        travel_timestamp: Optional[int] = None,
        metric_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform vector similarity search

        Args:
            collection_name: Collection to search
            query_vectors: Query vectors
            query_texts: Query texts (will be embedded)
            filter_expression: Filter expression
            output_fields: Fields to return
            limit: Number of results
            offset: Result offset
            partition_names: Partitions to search
            search_params: Search parameters
            consistency_level: Consistency level
            guarantee_timestamp: Guarantee timestamp for consistency
            travel_timestamp: Time travel search
            metric_type: Override metric type

        Returns:
            Search results
        """

        try:
            collection = Collection(collection_name)

            # Ensure collection is loaded
            if utility.load_state(collection_name) != "Loaded":
                collection.load()

            # Generate embeddings if text provided
            if query_texts and not query_vectors:
                if isinstance(query_texts, str):
                    query_texts = [query_texts]
                embeddings = self.embedding_service.encode_batch(query_texts)
                query_vectors = embeddings.tolist()
            elif query_vectors:
                if not isinstance(query_vectors[0], list):
                    query_vectors = [query_vectors]

            if not query_vectors:
                raise ValidationError(
                    message="Either query_vectors or query_texts must be provided",
                )

            # Find vector field
            vector_field = None
            for field in collection.schema.fields:
                if field.dtype == 101:  # FLOAT_VECTOR
                    vector_field = field.name
                    break

            if not vector_field:
                raise ValidationError(
                    message=f"No vector field found in collection {collection_name}",
                )

            # Default search params based on collection type
            if search_params is None:
                if collection_name.endswith("documents"):
                    search_params = DocumentsCollectionSchema.get_search_params()
                elif collection_name.endswith("entities"):
                    search_params = EntitiesCollectionSchema.get_search_params()
                else:
                    search_params = {"nprobe": 10}

            # Default output fields
            if output_fields is None:
                output_fields = ["*"]

            # Perform search
            search_results = collection.search(
                data=query_vectors,
                anns_field=vector_field,
                param=search_params,
                limit=limit,
                offset=offset,
                expr=filter_expression,
                output_fields=output_fields,
                partition_names=partition_names,
                consistency_level=consistency_level,
                guarantee_timestamp=guarantee_timestamp,
                travel_timestamp=travel_timestamp,
            )

            # Format results
            results = []
            for hits in search_results:
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "score": hit.score,
                        "distance": hit.distance,
                    }

                    # Add output fields
                    for field in output_fields:
                        if field != "*" and hasattr(hit.entity, field):
                            result[field] = getattr(hit.entity, field)

                    results.append(result)

            return {
                "success": True,
                "collection_name": collection_name,
                "query_count": len(query_vectors),
                "result_count": len(results),
                "results": results,
                "search_params": search_params,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Vector search failed: {str(e)}",
                collection=collection_name,
            )

    def hybrid_search(
        self,
        collection_name: str,
        vector_query: Optional[Dict[str, Any]] = None,
        scalar_filters: Optional[Dict[str, Any]] = None,
        text_query: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
        limit: int = 20,
        rerank: bool = True,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining vector and scalar queries

        Args:
            collection_name: Collection to search
            vector_query: Vector search parameters
            scalar_filters: Scalar filter conditions
            text_query: Text search parameters
            weights: Weights for different search types
            limit: Number of results
            rerank: Whether to rerank results
            output_fields: Fields to return

        Returns:
            Hybrid search results
        """

        try:
            # Default weights
            if weights is None:
                weights = {
                    "vector": 0.7,
                    "scalar": 0.3,
                }

            results = []
            scores = {}

            # Vector search
            if vector_query:
                vector_results = self.vector_search(
                    collection_name=collection_name,
                    query_texts=vector_query.get("text"),
                    query_vectors=vector_query.get("vector"),
                    filter_expression=self._build_filter_expression(scalar_filters),
                    limit=limit * 2,  # Get more results for reranking
                    output_fields=output_fields,
                )

                for result in vector_results["results"]:
                    result_id = str(result["id"])
                    scores[result_id] = scores.get(result_id, 0) + (
                        result["score"] * weights.get("vector", 0.7)
                    )
                    results.append(result)

            # Text search (using vector similarity with text query)
            if text_query and text_query.get("query"):
                text_results = self.vector_search(
                    collection_name=collection_name,
                    query_texts=text_query["query"],
                    filter_expression=self._build_filter_expression(scalar_filters),
                    limit=limit * 2,
                    output_fields=output_fields,
                )

                for result in text_results["results"]:
                    result_id = str(result["id"])
                    if result_id not in scores:
                        results.append(result)
                    scores[result_id] = scores.get(result_id, 0) + (
                        result["score"] * weights.get("text", 0.3)
                    )

            # Rerank results
            if rerank and results:
                # Sort by combined score
                for result in results:
                    result["hybrid_score"] = scores.get(str(result["id"]), 0)

                results = sorted(results, key=lambda x: x["hybrid_score"], reverse=True)
                results = results[:limit]

            return {
                "success": True,
                "collection_name": collection_name,
                "result_count": len(results),
                "results": results,
                "weights": weights,
                "reranked": rerank,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Hybrid search failed: {str(e)}",
                collection=collection_name,
            )

    def range_search(
        self,
        collection_name: str,
        query_vectors: Optional[Union[List[float], List[List[float]]]] = None,
        query_texts: Optional[Union[str, List[str]]] = None,
        radius: float = 0.5,
        range_filter: Optional[float] = None,
        filter_expression: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform range search (find all vectors within a distance)

        Args:
            collection_name: Collection to search
            query_vectors: Query vectors
            query_texts: Query texts (will be embedded)
            radius: Search radius
            range_filter: Additional range filter
            filter_expression: Filter expression
            output_fields: Fields to return
            partition_names: Partitions to search

        Returns:
            Range search results
        """

        try:
            # Perform search with high limit
            results = self.vector_search(
                collection_name=collection_name,
                query_vectors=query_vectors,
                query_texts=query_texts,
                filter_expression=filter_expression,
                output_fields=output_fields,
                limit=10000,  # High limit for range search
                partition_names=partition_names,
            )

            # Filter by radius
            filtered_results = []
            for result in results["results"]:
                if result["distance"] <= radius:
                    if range_filter is None or result["distance"] >= range_filter:
                        filtered_results.append(result)

            return {
                "success": True,
                "collection_name": collection_name,
                "radius": radius,
                "range_filter": range_filter,
                "result_count": len(filtered_results),
                "results": filtered_results,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Range search failed: {str(e)}",
                collection=collection_name,
            )

    def similarity_search(
        self,
        collection_name: str,
        reference_id: Union[int, str],
        output_fields: Optional[List[str]] = None,
        limit: int = 20,
        filter_expression: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find similar items based on a reference item

        Args:
            collection_name: Collection to search
            reference_id: ID of reference item
            output_fields: Fields to return
            limit: Number of results
            filter_expression: Additional filters

        Returns:
            Similar items
        """

        try:
            # Get reference item
            collection = Collection(collection_name)

            # Find primary key field
            primary_field = None
            vector_field = None
            for field in collection.schema.fields:
                if field.is_primary:
                    primary_field = field.name
                if field.dtype == 101:  # FLOAT_VECTOR
                    vector_field = field.name

            # Query reference item
            if isinstance(reference_id, str):
                expr = f'{primary_field} == "{reference_id}"'
            else:
                expr = f"{primary_field} == {reference_id}"

            reference = collection.query(
                expr=expr,
                output_fields=[vector_field],
                limit=1,
            )

            if not reference:
                raise ValidationError(
                    message=f"Reference item {reference_id} not found",
                )

            # Get reference vector
            reference_vector = reference[0][vector_field]

            # Search for similar items
            # Exclude the reference item itself
            if filter_expression:
                filter_expression = f"({filter_expression}) and ({primary_field} != {reference_id})"
            else:
                if isinstance(reference_id, str):
                    filter_expression = f'{primary_field} != "{reference_id}"'
                else:
                    filter_expression = f"{primary_field} != {reference_id}"

            return self.vector_search(
                collection_name=collection_name,
                query_vectors=[reference_vector],
                filter_expression=filter_expression,
                output_fields=output_fields,
                limit=limit,
            )

        except Exception as e:
            raise MilvusSearchError(
                message=f"Similarity search failed: {str(e)}",
                collection=collection_name,
            )

    def multi_vector_search(
        self,
        collection_name: str,
        queries: List[Dict[str, Any]],
        aggregate_method: str = "max",
        limit: int = 20,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform multiple vector searches and aggregate results

        Args:
            collection_name: Collection to search
            queries: List of query configurations
            aggregate_method: How to aggregate scores (max, mean, sum)
            limit: Number of results
            output_fields: Fields to return

        Returns:
            Aggregated search results
        """

        try:
            all_results = {}
            all_scores = {}

            # Perform each search
            for i, query in enumerate(queries):
                search_result = self.vector_search(
                    collection_name=collection_name,
                    query_texts=query.get("text"),
                    query_vectors=query.get("vector"),
                    filter_expression=query.get("filter"),
                    limit=limit * 2,
                    output_fields=output_fields,
                )

                weight = query.get("weight", 1.0)

                for result in search_result["results"]:
                    result_id = str(result["id"])

                    if result_id not in all_results:
                        all_results[result_id] = result
                        all_scores[result_id] = []

                    all_scores[result_id].append(result["score"] * weight)

            # Aggregate scores
            final_results = []
            for result_id, result in all_results.items():
                scores = all_scores[result_id]

                if aggregate_method == "max":
                    final_score = max(scores)
                elif aggregate_method == "mean":
                    final_score = sum(scores) / len(scores)
                elif aggregate_method == "sum":
                    final_score = sum(scores)
                else:
                    final_score = max(scores)

                result["aggregated_score"] = final_score
                result["query_scores"] = scores
                final_results.append(result)

            # Sort by aggregated score
            final_results = sorted(
                final_results,
                key=lambda x: x["aggregated_score"],
                reverse=True,
            )[:limit]

            return {
                "success": True,
                "collection_name": collection_name,
                "query_count": len(queries),
                "aggregate_method": aggregate_method,
                "result_count": len(final_results),
                "results": final_results,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Multi-vector search failed: {str(e)}",
                collection=collection_name,
            )

    def _build_filter_expression(
        self,
        filters: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """Build filter expression from dictionary"""

        if not filters:
            return None

        expressions = []

        for field, value in filters.items():
            if isinstance(value, str):
                expressions.append(f'{field} == "{value}"')
            elif isinstance(value, (list, tuple)):
                if value and isinstance(value[0], str):
                    values_str = ", ".join([f'"{v}"' for v in value])
                else:
                    values_str = ", ".join([str(v) for v in value])
                expressions.append(f"{field} in [{values_str}]")
            elif isinstance(value, dict):
                # Range filters
                if "min" in value:
                    expressions.append(f"{field} >= {value['min']}")
                if "max" in value:
                    expressions.append(f"{field} <= {value['max']}")
                if "ne" in value:
                    if isinstance(value["ne"], str):
                        expressions.append(f'{field} != "{value["ne"]}"')
                    else:
                        expressions.append(f"{field} != {value['ne']}")
            else:
                expressions.append(f"{field} == {value}")

        return " && ".join(expressions) if expressions else None