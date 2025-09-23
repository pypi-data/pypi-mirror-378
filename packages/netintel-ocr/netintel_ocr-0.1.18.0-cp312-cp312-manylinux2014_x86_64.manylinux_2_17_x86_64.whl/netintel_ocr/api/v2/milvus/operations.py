"""
Milvus Batch Vector Operations
"""

from typing import Dict, Any, List, Optional, Union
from pymilvus import Collection, utility
import numpy as np
import logging
import time
import uuid
from datetime import datetime
from ..services.embedding import get_embedding_service
from ..exceptions import MilvusInsertError, MilvusSearchError, ValidationError
from .connection import get_milvus_connection


logger = logging.getLogger(__name__)


class MilvusOperations:
    """Batch vector operations for Milvus"""

    def __init__(self):
        self.conn = get_milvus_connection()
        self.embedding_service = get_embedding_service()

    # ==================== Insert Operations ====================

    def insert_vectors(
        self,
        collection_name: str,
        data: List[Dict[str, Any]],
        partition_name: Optional[str] = None,
        auto_embed: bool = True,
        embedding_field: str = "embedding",
        text_field: str = "content",
        batch_size: int = 1000,
    ) -> Dict[str, Any]:
        """
        Insert vectors into collection

        Args:
            collection_name: Collection name
            data: List of dictionaries with data to insert
            partition_name: Optional partition name
            auto_embed: Whether to auto-generate embeddings
            embedding_field: Name of the embedding field
            text_field: Name of the text field for embedding generation
            batch_size: Batch size for insertion

        Returns:
            Insert result with statistics
        """

        try:
            collection = Collection(collection_name)

            # Ensure collection is loaded
            if utility.load_state(collection_name) != "Loaded":
                collection.load()

            # Process data in batches
            total_inserted = 0
            insert_ids = []
            failed_batches = []

            for batch_start in range(0, len(data), batch_size):
                batch_end = min(batch_start + batch_size, len(data))
                batch_data = data[batch_start:batch_end]

                try:
                    # Generate embeddings if needed
                    if auto_embed and embedding_field not in batch_data[0]:
                        texts = [item.get(text_field, "") for item in batch_data]
                        embeddings = self.embedding_service.encode_batch(texts)

                        for i, item in enumerate(batch_data):
                            item[embedding_field] = embeddings[i].tolist()

                    # Add timestamps if not present
                    timestamp = int(datetime.utcnow().timestamp())
                    for item in batch_data:
                        if "created_at" not in item:
                            item["created_at"] = timestamp
                        if "updated_at" not in item:
                            item["updated_at"] = timestamp

                    # Prepare data for insertion
                    insert_data = []
                    for field in collection.schema.fields:
                        if field.auto_id and field.is_primary:
                            continue

                        field_data = []
                        for item in batch_data:
                            if field.name in item:
                                field_data.append(item[field.name])
                            elif field.dtype == 5:  # JSON field
                                field_data.append({})
                            elif field.dtype in [2, 3, 4]:  # Integer fields
                                field_data.append(0)
                            elif field.dtype == 10:  # Float field
                                field_data.append(0.0)
                            elif field.dtype == 21:  # VARCHAR field
                                field_data.append("")
                            else:
                                field_data.append(None)

                        insert_data.append(field_data)

                    # Insert into collection
                    if partition_name:
                        partition = collection.partition(partition_name)
                        result = partition.insert(insert_data)
                    else:
                        result = collection.insert(insert_data)

                    insert_ids.extend(result.primary_keys)
                    total_inserted += len(batch_data)

                    logger.info(f"Inserted batch {batch_start // batch_size + 1}: {len(batch_data)} entities")

                except Exception as e:
                    logger.error(f"Failed to insert batch {batch_start // batch_size + 1}: {str(e)}")
                    failed_batches.append({
                        "batch": batch_start // batch_size + 1,
                        "start": batch_start,
                        "end": batch_end,
                        "error": str(e),
                    })

            # Flush to ensure data persistence
            collection.flush()

            return {
                "success": total_inserted > 0,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "total_entities": len(data),
                "inserted_entities": total_inserted,
                "failed_batches": failed_batches,
                "insert_ids": insert_ids[:100],  # Return first 100 IDs
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusInsertError(
                message=f"Failed to insert vectors: {str(e)}",
                collection=collection_name,
                num_entities=len(data),
            )

    def upsert_vectors(
        self,
        collection_name: str,
        data: List[Dict[str, Any]],
        partition_name: Optional[str] = None,
        primary_key_field: str = "document_id",
        auto_embed: bool = True,
        embedding_field: str = "embedding",
        text_field: str = "content",
    ) -> Dict[str, Any]:
        """
        Upsert (insert or update) vectors

        Args:
            collection_name: Collection name
            data: List of dictionaries with data to upsert
            partition_name: Optional partition name
            primary_key_field: Field to use for identifying existing records
            auto_embed: Whether to auto-generate embeddings
            embedding_field: Name of the embedding field
            text_field: Name of the text field for embedding generation

        Returns:
            Upsert result with statistics
        """

        try:
            collection = Collection(collection_name)

            # Delete existing records
            deleted_count = 0
            primary_keys = [item.get(primary_key_field) for item in data if primary_key_field in item]

            if primary_keys:
                expr = f"{primary_key_field} in {primary_keys}"
                result = collection.delete(expr)
                deleted_count = result.delete_count if hasattr(result, "delete_count") else len(primary_keys)

            # Insert new records
            insert_result = self.insert_vectors(
                collection_name=collection_name,
                data=data,
                partition_name=partition_name,
                auto_embed=auto_embed,
                embedding_field=embedding_field,
                text_field=text_field,
            )

            return {
                **insert_result,
                "operation": "upsert",
                "deleted_entities": deleted_count,
            }

        except Exception as e:
            raise MilvusInsertError(
                message=f"Failed to upsert vectors: {str(e)}",
                collection=collection_name,
                num_entities=len(data),
            )

    def bulk_import(
        self,
        collection_name: str,
        file_path: str,
        file_type: str = "json",
        partition_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Bulk import from file

        Args:
            collection_name: Collection name
            file_path: Path to the file
            file_type: File type (json, numpy, parquet)
            partition_name: Optional partition name

        Returns:
            Import result
        """

        try:
            import json
            import pandas as pd

            # Load data based on file type
            if file_type == "json":
                with open(file_path, "r") as f:
                    data = json.load(f)
            elif file_type == "parquet":
                df = pd.read_parquet(file_path)
                data = df.to_dict("records")
            elif file_type == "numpy":
                data = np.load(file_path, allow_pickle=True)
                if isinstance(data, np.ndarray):
                    data = data.tolist()
            else:
                raise ValidationError(
                    message=f"Unsupported file type: {file_type}",
                    details={"file_type": file_type},
                )

            # Import data
            return self.insert_vectors(
                collection_name=collection_name,
                data=data,
                partition_name=partition_name,
            )

        except Exception as e:
            raise MilvusInsertError(
                message=f"Failed to bulk import: {str(e)}",
                collection=collection_name,
            )

    # ==================== Delete Operations ====================

    def delete_by_expression(
        self,
        collection_name: str,
        expression: str,
        partition_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete entities by expression

        Args:
            collection_name: Collection name
            expression: Delete expression
            partition_name: Optional partition name

        Returns:
            Delete result
        """

        try:
            collection = Collection(collection_name)

            if partition_name:
                partition = collection.partition(partition_name)
                result = partition.delete(expression)
            else:
                result = collection.delete(expression)

            return {
                "success": True,
                "collection_name": collection_name,
                "partition_name": partition_name,
                "expression": expression,
                "deleted_count": result.delete_count if hasattr(result, "delete_count") else 0,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusInsertError(
                message=f"Failed to delete entities: {str(e)}",
                collection=collection_name,
            )

    def delete_by_ids(
        self,
        collection_name: str,
        ids: List[Union[int, str]],
        partition_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete entities by primary keys

        Args:
            collection_name: Collection name
            ids: List of primary keys
            partition_name: Optional partition name

        Returns:
            Delete result
        """

        try:
            collection = Collection(collection_name)

            # Find primary key field
            primary_field = None
            for field in collection.schema.fields:
                if field.is_primary:
                    primary_field = field.name
                    break

            if not primary_field:
                raise ValidationError(
                    message="No primary key field found",
                    details={"collection_name": collection_name},
                )

            # Build expression
            if isinstance(ids[0], str):
                ids_str = ", ".join([f"'{id}'" for id in ids])
            else:
                ids_str = ", ".join([str(id) for id in ids])

            expression = f"{primary_field} in [{ids_str}]"

            return self.delete_by_expression(
                collection_name=collection_name,
                expression=expression,
                partition_name=partition_name,
            )

        except Exception as e:
            raise MilvusInsertError(
                message=f"Failed to delete by IDs: {str(e)}",
                collection=collection_name,
            )

    # ==================== Query Operations ====================

    def query_by_expression(
        self,
        collection_name: str,
        expression: str,
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Query entities by expression

        Args:
            collection_name: Collection name
            expression: Query expression
            output_fields: Fields to return
            partition_names: Partition names to query
            limit: Maximum results
            offset: Result offset

        Returns:
            Query results
        """

        try:
            collection = Collection(collection_name)

            # Ensure collection is loaded
            if utility.load_state(collection_name) != "Loaded":
                collection.load()

            # Default output fields
            if output_fields is None:
                output_fields = ["*"]

            # Query
            results = collection.query(
                expr=expression,
                output_fields=output_fields,
                partition_names=partition_names,
                limit=limit,
                offset=offset,
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "expression": expression,
                "count": len(results),
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Failed to query: {str(e)}",
                collection=collection_name,
                query={"expression": expression},
            )

    def get_by_ids(
        self,
        collection_name: str,
        ids: List[Union[int, str]],
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get entities by primary keys

        Args:
            collection_name: Collection name
            ids: List of primary keys
            output_fields: Fields to return
            partition_names: Partition names to query

        Returns:
            Query results
        """

        try:
            collection = Collection(collection_name)

            # Find primary key field
            primary_field = None
            for field in collection.schema.fields:
                if field.is_primary:
                    primary_field = field.name
                    break

            if not primary_field:
                raise ValidationError(
                    message="No primary key field found",
                    details={"collection_name": collection_name},
                )

            # Build expression
            if isinstance(ids[0], str):
                ids_str = ", ".join([f"'{id}'" for id in ids])
            else:
                ids_str = ", ".join([str(id) for id in ids])

            expression = f"{primary_field} in [{ids_str}]"

            return self.query_by_expression(
                collection_name=collection_name,
                expression=expression,
                output_fields=output_fields,
                partition_names=partition_names,
                limit=len(ids),
            )

        except Exception as e:
            raise MilvusSearchError(
                message=f"Failed to get by IDs: {str(e)}",
                collection=collection_name,
                query={"ids": ids},
            )

    # ==================== Batch Processing ====================

    def process_in_batches(
        self,
        collection_name: str,
        processor_func: callable,
        batch_size: int = 1000,
        expression: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Process collection data in batches

        Args:
            collection_name: Collection name
            processor_func: Function to process each batch
            batch_size: Batch size
            expression: Query expression
            output_fields: Fields to retrieve
            partition_names: Partition names

        Returns:
            Processing result
        """

        try:
            collection = Collection(collection_name)
            total_entities = collection.num_entities
            processed = 0
            results = []

            # Process in batches
            for offset in range(0, total_entities, batch_size):
                # Query batch
                batch = self.query_by_expression(
                    collection_name=collection_name,
                    expression=expression or "",
                    output_fields=output_fields,
                    partition_names=partition_names,
                    limit=batch_size,
                    offset=offset,
                )

                if not batch["results"]:
                    break

                # Process batch
                try:
                    result = processor_func(batch["results"])
                    results.append(result)
                    processed += len(batch["results"])
                except Exception as e:
                    logger.error(f"Failed to process batch at offset {offset}: {str(e)}")

            return {
                "success": True,
                "collection_name": collection_name,
                "total_entities": total_entities,
                "processed_entities": processed,
                "batch_size": batch_size,
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Failed to process in batches: {str(e)}",
                collection=collection_name,
            )

    def export_collection(
        self,
        collection_name: str,
        output_path: str,
        file_type: str = "json",
        expression: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        partition_names: Optional[List[str]] = None,
        batch_size: int = 1000,
    ) -> Dict[str, Any]:
        """
        Export collection data to file

        Args:
            collection_name: Collection name
            output_path: Output file path
            file_type: File type (json, parquet, csv)
            expression: Query expression
            output_fields: Fields to export
            partition_names: Partition names
            batch_size: Batch size

        Returns:
            Export result
        """

        try:
            import json
            import pandas as pd

            # Collect all data
            all_data = []

            def collect_batch(batch):
                all_data.extend(batch)

            # Process collection
            result = self.process_in_batches(
                collection_name=collection_name,
                processor_func=collect_batch,
                batch_size=batch_size,
                expression=expression,
                output_fields=output_fields,
                partition_names=partition_names,
            )

            # Save to file
            if file_type == "json":
                with open(output_path, "w") as f:
                    json.dump(all_data, f, indent=2, default=str)
            elif file_type == "parquet":
                df = pd.DataFrame(all_data)
                df.to_parquet(output_path)
            elif file_type == "csv":
                df = pd.DataFrame(all_data)
                df.to_csv(output_path, index=False)
            else:
                raise ValidationError(
                    message=f"Unsupported file type: {file_type}",
                    details={"file_type": file_type},
                )

            return {
                "success": True,
                "collection_name": collection_name,
                "output_path": output_path,
                "file_type": file_type,
                "exported_entities": len(all_data),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise MilvusSearchError(
                message=f"Failed to export collection: {str(e)}",
                collection=collection_name,
            )