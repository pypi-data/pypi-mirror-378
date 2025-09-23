"""
Document Processing Service with Real-time Status Updates
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import logging
from pathlib import Path
from ..websocket.manager import ws_manager
from ..milvus.operations import MilvusOperations
from ..services.embedding import get_embedding_service
from ...hybrid_processor import HybridProcessor


logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Processing status enum"""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    EXTRACTING_TEXT = "extracting_text"
    EXTRACTING_TABLES = "extracting_tables"
    EXTRACTING_DIAGRAMS = "extracting_diagrams"
    GENERATING_EMBEDDINGS = "generating_embeddings"
    STORING_VECTORS = "storing_vectors"
    BUILDING_KG = "building_kg"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingJob:
    """Represents a document processing job"""

    def __init__(
        self,
        job_id: str,
        document_id: str,
        file_path: str,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.job_id = job_id
        self.document_id = document_id
        self.file_path = file_path
        self.options = options or {}
        self.status = ProcessingStatus.QUEUED
        self.progress = 0
        self.current_page = 0
        self.total_pages = 0
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.results = {}
        self.metadata = {}
        self.subscribers: Set[str] = set()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "document_id": self.document_id,
            "status": self.status,
            "progress": self.progress,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "results": self.results,
            "metadata": self.metadata,
        }


class DocumentProcessingService:
    """Service for processing documents with real-time updates"""

    def __init__(self):
        self.jobs: Dict[str, ProcessingJob] = {}
        self.processing_queue = asyncio.Queue()
        self.workers = []
        self.milvus_ops = MilvusOperations()
        self.embedding_service = get_embedding_service()
        self._processing = False

    async def start_processing_workers(self, num_workers: int = 3):
        """Start processing workers"""
        if not self._processing:
            self._processing = True
            for i in range(num_workers):
                worker = asyncio.create_task(self._process_worker(i))
                self.workers.append(worker)
            logger.info(f"Started {num_workers} processing workers")

    async def stop_processing_workers(self):
        """Stop processing workers"""
        self._processing = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        logger.info("Stopped processing workers")

    async def _process_worker(self, worker_id: int):
        """Worker to process documents from queue"""
        logger.info(f"Processing worker {worker_id} started")

        while self._processing:
            try:
                # Get job from queue
                job = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=1.0
                )

                # Process the job
                await self._process_document(job)

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")

        logger.info(f"Processing worker {worker_id} stopped")

    async def submit_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        client_id: Optional[str] = None,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Submit a document for processing"""

        # Generate IDs
        job_id = str(uuid.uuid4())
        if not document_id:
            document_id = str(uuid.uuid4())

        # Create job
        job = ProcessingJob(
            job_id=job_id,
            document_id=document_id,
            file_path=file_path,
            options=options,
        )

        # Add client as subscriber
        if client_id:
            job.subscribers.add(client_id)

        # Store job
        self.jobs[job_id] = job

        # Add to queue based on priority
        if priority == "high":
            # Put at front of queue (implement priority queue if needed)
            await self.processing_queue.put(job)
        else:
            await self.processing_queue.put(job)

        # Send initial notification
        await self._notify_status(job)

        logger.info(f"Submitted document {document_id} for processing (job: {job_id})")

        return {
            "job_id": job_id,
            "document_id": document_id,
            "status": job.status,
            "queue_position": self.processing_queue.qsize(),
            "submitted_at": job.created_at.isoformat(),
        }

    async def _process_document(self, job: ProcessingJob):
        """Process a document with status updates"""

        try:
            # Update status to initializing
            await self._update_status(job, ProcessingStatus.INITIALIZING)
            job.started_at = datetime.utcnow()

            # Initialize processor
            processor = HybridProcessor(
                enable_ocr=job.options.get("ocr_enabled", True),
                enable_diagram_detection=job.options.get("extract_diagrams", True),
                enable_table_extraction=job.options.get("extract_tables", True),
                enable_knowledge_graph=job.options.get("extract_knowledge_graph", False),
            )

            # Process document in stages
            await self._process_stages(job, processor)

            # Mark as completed
            job.completed_at = datetime.utcnow()
            await self._update_status(job, ProcessingStatus.COMPLETED, progress=100)

            # Send completion notification
            await ws_manager.notify_processing_complete(
                document_id=job.document_id,
                success=True,
                results=job.results,
            )

        except asyncio.CancelledError:
            await self._update_status(job, ProcessingStatus.CANCELLED)
            raise
        except Exception as e:
            logger.error(f"Processing failed for job {job.job_id}: {str(e)}")
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            await self._update_status(job, ProcessingStatus.FAILED)

            # Send error notification
            await ws_manager.notify_processing_complete(
                document_id=job.document_id,
                success=False,
                error=str(e),
            )

    async def _process_stages(self, job: ProcessingJob, processor: HybridProcessor):
        """Process document through various stages"""

        # Stage 1: Extract text
        await self._update_status(job, ProcessingStatus.EXTRACTING_TEXT, progress=10)
        text_results = await self._extract_text(job, processor)
        job.results["text"] = text_results

        # Stage 2: Extract tables
        if job.options.get("extract_tables", True):
            await self._update_status(job, ProcessingStatus.EXTRACTING_TABLES, progress=30)
            table_results = await self._extract_tables(job, processor)
            job.results["tables"] = table_results

        # Stage 3: Extract diagrams
        if job.options.get("extract_diagrams", True):
            await self._update_status(job, ProcessingStatus.EXTRACTING_DIAGRAMS, progress=50)
            diagram_results = await self._extract_diagrams(job, processor)
            job.results["diagrams"] = diagram_results

        # Stage 4: Generate embeddings
        await self._update_status(job, ProcessingStatus.GENERATING_EMBEDDINGS, progress=70)
        embeddings = await self._generate_embeddings(job)
        job.results["embeddings"] = {
            "count": len(embeddings),
            "dimension": embeddings[0].shape[0] if embeddings else 0,
        }

        # Stage 5: Store in Milvus
        await self._update_status(job, ProcessingStatus.STORING_VECTORS, progress=85)
        storage_result = await self._store_vectors(job, embeddings)
        job.results["storage"] = storage_result

        # Stage 6: Build knowledge graph (if enabled)
        if job.options.get("extract_knowledge_graph", False):
            await self._update_status(job, ProcessingStatus.BUILDING_KG, progress=95)
            kg_result = await self._build_knowledge_graph(job, processor)
            job.results["knowledge_graph"] = kg_result

    async def _extract_text(self, job: ProcessingJob, processor: HybridProcessor) -> Dict[str, Any]:
        """Extract text from document"""
        # Simulate extraction (integrate with actual processor)
        await asyncio.sleep(1)

        return {
            "pages_processed": job.total_pages,
            "text_length": 10000,  # Placeholder
            "extraction_time": 1.5,
        }

    async def _extract_tables(self, job: ProcessingJob, processor: HybridProcessor) -> Dict[str, Any]:
        """Extract tables from document"""
        await asyncio.sleep(0.5)

        return {
            "tables_found": 5,  # Placeholder
            "extraction_time": 0.5,
        }

    async def _extract_diagrams(self, job: ProcessingJob, processor: HybridProcessor) -> Dict[str, Any]:
        """Extract diagrams from document"""
        await asyncio.sleep(0.5)

        return {
            "diagrams_found": 3,  # Placeholder
            "extraction_time": 0.5,
        }

    async def _generate_embeddings(self, job: ProcessingJob) -> List[Any]:
        """Generate embeddings for document content"""

        # Get text content from results
        text_chunks = ["Sample text chunk 1", "Sample text chunk 2"]  # Placeholder

        # Generate embeddings
        embeddings = self.embedding_service.encode_batch(text_chunks)

        return embeddings

    async def _store_vectors(self, job: ProcessingJob, embeddings: List[Any]) -> Dict[str, Any]:
        """Store vectors in Milvus"""

        # Prepare data for insertion
        data = []
        for i, embedding in enumerate(embeddings):
            data.append({
                "document_id": job.document_id,
                "page_number": i + 1,
                "content_type": "text",
                "content": f"Content chunk {i + 1}",
                "embedding": embedding.tolist(),
                "metadata": {
                    "job_id": job.job_id,
                    "processed_at": datetime.utcnow().isoformat(),
                },
            })

        # Insert into Milvus
        result = await asyncio.to_thread(
            self.milvus_ops.insert_vectors,
            collection_name="netintel_documents",
            data=data,
            auto_embed=False,
        )

        return result

    async def _build_knowledge_graph(self, job: ProcessingJob, processor: HybridProcessor) -> Dict[str, Any]:
        """Build knowledge graph from document"""
        await asyncio.sleep(1)

        return {
            "entities_extracted": 20,  # Placeholder
            "relationships_found": 15,
            "build_time": 1.0,
        }

    async def _update_status(
        self,
        job: ProcessingJob,
        status: ProcessingStatus,
        progress: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update job status and send notifications"""

        job.status = status
        if progress is not None:
            job.progress = progress
        if metadata:
            job.metadata.update(metadata)

        await self._notify_status(job)

    async def _notify_status(self, job: ProcessingJob):
        """Send status notification to subscribers"""

        await ws_manager.notify_processing_status(
            document_id=job.document_id,
            status=job.status,
            progress=job.progress,
            current_page=job.current_page,
            total_pages=job.total_pages,
            metadata=job.metadata,
        )

        # Also notify specific subscribers
        for client_id in job.subscribers:
            await ws_manager.send_personal_message(
                client_id,
                {
                    "type": "job_status",
                    "job_id": job.job_id,
                    **job.to_dict(),
                },
            )

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing job"""

        job = self.jobs.get(job_id)
        if not job:
            return None

        return job.to_dict()

    def get_document_jobs(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a document"""

        jobs = []
        for job in self.jobs.values():
            if job.document_id == document_id:
                jobs.append(job.to_dict())

        return sorted(jobs, key=lambda x: x["created_at"], reverse=True)

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a processing job"""

        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED]:
            return {
                "job_id": job_id,
                "status": job.status,
                "message": "Job already finished",
            }

        # Update status
        await self._update_status(job, ProcessingStatus.CANCELLED)

        return {
            "job_id": job_id,
            "status": ProcessingStatus.CANCELLED,
            "cancelled_at": datetime.utcnow().isoformat(),
        }


# Global processing service instance
processing_service = DocumentProcessingService()