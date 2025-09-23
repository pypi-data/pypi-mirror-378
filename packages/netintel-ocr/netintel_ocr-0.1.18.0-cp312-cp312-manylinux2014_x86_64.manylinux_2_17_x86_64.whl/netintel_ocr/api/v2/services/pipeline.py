"""
Automatic Embedding Generation and Vector Insertion Pipeline
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging
import numpy as np
from ..services.embedding import get_embedding_service
from ..milvus.manager import MilvusManager
from ..milvus.operations import MilvusOperations
from ..websocket.manager import ws_manager


logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk"""
    chunk_id: str
    document_id: str
    page_number: int
    chunk_number: int
    content_type: str
    start_char: int
    end_char: int
    tokens: int
    metadata: Dict[str, Any]


class EmbeddingPipeline:
    """Pipeline for automatic embedding generation and vector insertion"""

    def __init__(
        self,
        collection_name: str = "netintel_documents",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        batch_size: int = 32,
        enable_partitioning: bool = True,
    ):
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        self.enable_partitioning = enable_partitioning

        self.embedding_service = get_embedding_service()
        self.milvus_manager = MilvusManager()
        self.milvus_ops = MilvusOperations()

    async def process_document(
        self,
        document_id: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        auto_index: bool = True,
        notify_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a document through the embedding pipeline

        Args:
            document_id: Document identifier
            content: Document content (text, tables, diagrams)
            metadata: Document metadata
            auto_index: Whether to automatically index after insertion
            notify_progress: Whether to send progress notifications

        Returns:
            Processing results
        """

        try:
            start_time = datetime.utcnow()
            results = {
                "document_id": document_id,
                "chunks_processed": 0,
                "embeddings_generated": 0,
                "vectors_inserted": 0,
                "partitions_used": [],
                "processing_time": 0,
            }

            # Step 1: Chunk document content
            if notify_progress:
                await self._notify_progress(document_id, "chunking", 10)

            chunks = await self._chunk_document(document_id, content)
            results["chunks_processed"] = len(chunks)

            # Step 2: Generate embeddings
            if notify_progress:
                await self._notify_progress(document_id, "embedding", 30)

            embeddings = await self._generate_embeddings(chunks)
            results["embeddings_generated"] = len(embeddings)

            # Step 3: Prepare data for insertion
            if notify_progress:
                await self._notify_progress(document_id, "preparing", 50)

            insertion_data = self._prepare_insertion_data(
                chunks,
                embeddings,
                metadata,
            )

            # Step 4: Determine partitioning strategy
            if self.enable_partitioning:
                partitions = await self._determine_partitions(chunks)
                results["partitions_used"] = list(set(partitions))
            else:
                partitions = None

            # Step 5: Insert vectors into Milvus
            if notify_progress:
                await self._notify_progress(document_id, "inserting", 70)

            insert_results = await self._insert_vectors(
                insertion_data,
                partitions,
            )
            results["vectors_inserted"] = insert_results["inserted_entities"]

            # Step 6: Incremental indexing
            if auto_index:
                if notify_progress:
                    await self._notify_progress(document_id, "indexing", 90)

                await self._incremental_index()

            # Calculate processing time
            results["processing_time"] = (
                datetime.utcnow() - start_time
            ).total_seconds()

            if notify_progress:
                await self._notify_progress(document_id, "complete", 100)

            logger.info(
                f"Processed document {document_id}: "
                f"{results['chunks_processed']} chunks, "
                f"{results['vectors_inserted']} vectors inserted"
            )

            return results

        except Exception as e:
            logger.error(f"Pipeline error for document {document_id}: {str(e)}")
            raise

    async def _chunk_document(
        self,
        document_id: str,
        content: Dict[str, Any],
    ) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk document content into processable pieces"""

        chunks = []
        chunk_counter = 0

        # Process text content
        if "text" in content:
            text_chunks = self._chunk_text(
                content["text"],
                self.chunk_size,
                self.chunk_overlap,
            )

            for i, (text, start, end) in enumerate(text_chunks):
                chunk_id = f"{document_id}_chunk_{chunk_counter}"
                metadata = ChunkMetadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    page_number=content.get("page", 1),
                    chunk_number=chunk_counter,
                    content_type="text",
                    start_char=start,
                    end_char=end,
                    tokens=len(text.split()),
                    metadata={"source": "text_content"},
                )
                chunks.append((text, metadata))
                chunk_counter += 1

        # Process table content
        if "tables" in content:
            for i, table in enumerate(content["tables"]):
                table_text = self._table_to_text(table)
                chunk_id = f"{document_id}_table_{i}"
                metadata = ChunkMetadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    page_number=table.get("page", 1),
                    chunk_number=chunk_counter,
                    content_type="table",
                    start_char=0,
                    end_char=len(table_text),
                    tokens=len(table_text.split()),
                    metadata={
                        "source": "table",
                        "table_index": i,
                        "headers": table.get("headers", []),
                    },
                )
                chunks.append((table_text, metadata))
                chunk_counter += 1

        # Process diagram content
        if "diagrams" in content:
            for i, diagram in enumerate(content["diagrams"]):
                diagram_text = diagram.get("description", "") or diagram.get("mermaid", "")
                if diagram_text:
                    chunk_id = f"{document_id}_diagram_{i}"
                    metadata = ChunkMetadata(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        page_number=diagram.get("page", 1),
                        chunk_number=chunk_counter,
                        content_type="diagram",
                        start_char=0,
                        end_char=len(diagram_text),
                        tokens=len(diagram_text.split()),
                        metadata={
                            "source": "diagram",
                            "diagram_index": i,
                            "diagram_type": diagram.get("type", "unknown"),
                        },
                    )
                    chunks.append((diagram_text, metadata))
                    chunk_counter += 1

        return chunks

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[Tuple[str, int, int]]:
        """Split text into chunks with overlap"""

        chunks = []
        words = text.split()
        total_words = len(words)

        for i in range(0, total_words, chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)

            # Calculate character positions
            start_char = len(" ".join(words[:i]))
            end_char = start_char + len(chunk_text)

            chunks.append((chunk_text, start_char, end_char))

            if i + chunk_size >= total_words:
                break

        return chunks

    def _table_to_text(self, table: Dict[str, Any]) -> str:
        """Convert table to text representation"""

        text_parts = []

        # Add headers
        if "headers" in table:
            text_parts.append("Headers: " + ", ".join(table["headers"]))

        # Add rows
        if "rows" in table:
            for i, row in enumerate(table["rows"]):
                row_text = f"Row {i+1}: " + ", ".join(str(cell) for cell in row)
                text_parts.append(row_text)

        # Add summary if available
        if "summary" in table:
            text_parts.append(f"Summary: {table['summary']}")

        return " | ".join(text_parts)

    async def _generate_embeddings(
        self,
        chunks: List[Tuple[str, ChunkMetadata]],
    ) -> List[np.ndarray]:
        """Generate embeddings for chunks"""

        # Extract text from chunks
        texts = [chunk[0] for chunk in chunks]

        # Generate embeddings in batches
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self.embedding_service.encode_async(
                batch,
                normalize=True,
            )
            embeddings.extend(batch_embeddings)

        return embeddings

    def _prepare_insertion_data(
        self,
        chunks: List[Tuple[str, ChunkMetadata]],
        embeddings: List[np.ndarray],
        document_metadata: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Prepare data for Milvus insertion"""

        insertion_data = []
        timestamp = int(datetime.utcnow().timestamp())

        for (text, chunk_meta), embedding in zip(chunks, embeddings):
            data = {
                "document_id": chunk_meta.document_id,
                "page_number": chunk_meta.page_number,
                "content_type": chunk_meta.content_type,
                "content": text[:65535],  # Truncate if too long
                "embedding": embedding.tolist(),
                "metadata": {
                    **chunk_meta.metadata,
                    "chunk_id": chunk_meta.chunk_id,
                    "chunk_number": chunk_meta.chunk_number,
                    "start_char": chunk_meta.start_char,
                    "end_char": chunk_meta.end_char,
                    "tokens": chunk_meta.tokens,
                    **(document_metadata or {}),
                },
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            insertion_data.append(data)

        return insertion_data

    async def _determine_partitions(
        self,
        chunks: List[Tuple[str, ChunkMetadata]],
    ) -> List[str]:
        """Determine partition strategy for chunks"""

        partitions = []

        for _, metadata in chunks:
            # Partition by content type
            partition_name = f"{metadata.content_type}_content"

            # Ensure partition exists
            await self._ensure_partition(partition_name)

            partitions.append(partition_name)

        return partitions

    async def _ensure_partition(self, partition_name: str):
        """Ensure a partition exists"""

        try:
            partitions = self.milvus_manager.list_partitions(self.collection_name)
            partition_names = [p["name"] for p in partitions]

            if partition_name not in partition_names:
                self.milvus_manager.create_partition(
                    collection_name=self.collection_name,
                    partition_name=partition_name,
                    description=f"Partition for {partition_name}",
                )
                logger.info(f"Created partition: {partition_name}")
        except Exception as e:
            logger.warning(f"Could not ensure partition {partition_name}: {str(e)}")

    async def _insert_vectors(
        self,
        data: List[Dict[str, Any]],
        partitions: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Insert vectors into Milvus"""

        if not partitions:
            # Insert all data into default partition
            return await asyncio.to_thread(
                self.milvus_ops.insert_vectors,
                collection_name=self.collection_name,
                data=data,
                auto_embed=False,
            )

        # Group data by partition
        partition_data = {}
        for item, partition in zip(data, partitions):
            if partition not in partition_data:
                partition_data[partition] = []
            partition_data[partition].append(item)

        # Insert into each partition
        total_inserted = 0
        for partition_name, partition_items in partition_data.items():
            result = await asyncio.to_thread(
                self.milvus_ops.insert_vectors,
                collection_name=self.collection_name,
                data=partition_items,
                partition_name=partition_name,
                auto_embed=False,
            )
            total_inserted += result.get("inserted_entities", 0)

        return {
            "inserted_entities": total_inserted,
            "partitions": list(partition_data.keys()),
        }

    async def _incremental_index(self):
        """Perform incremental indexing"""

        try:
            # Get collection info
            collection_info = self.milvus_manager.get_collection_details(
                self.collection_name
            )

            # Check if index needs updating
            num_entities = collection_info.get("num_entities", 0)
            indexes = collection_info.get("indexes", [])

            # Only reindex if there are significant new entities
            if num_entities > 0 and num_entities % 10000 == 0:
                for index in indexes:
                    field_name = index["field_name"]
                    logger.info(f"Triggering incremental index for {field_name}")

                    # This would trigger index rebuild in production
                    # For now, just flush the collection
                    self.milvus_manager.flush_collection(self.collection_name)

        except Exception as e:
            logger.warning(f"Incremental indexing failed: {str(e)}")

    async def _notify_progress(
        self,
        document_id: str,
        stage: str,
        progress: int,
    ):
        """Send progress notification"""

        await ws_manager.send_to_topic(
            f"document:{document_id}",
            {
                "type": "pipeline_progress",
                "document_id": document_id,
                "stage": stage,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def batch_process_documents(
        self,
        documents: List[Dict[str, Any]],
        parallel_workers: int = 3,
    ) -> Dict[str, Any]:
        """Process multiple documents in parallel"""

        semaphore = asyncio.Semaphore(parallel_workers)
        results = []

        async def process_with_limit(doc):
            async with semaphore:
                return await self.process_document(
                    document_id=doc["document_id"],
                    content=doc["content"],
                    metadata=doc.get("metadata"),
                )

        tasks = [process_with_limit(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        return {
            "total_documents": len(documents),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": [str(e) for e in failed],
        }


# Global pipeline instance
embedding_pipeline = EmbeddingPipeline()