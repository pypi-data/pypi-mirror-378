"""
Streaming Upload Service for Large Files
"""

import os
import hashlib
import uuid
import asyncio
import aiofiles
from typing import Dict, Any, Optional, BinaryIO, AsyncIterator
from datetime import datetime, timedelta
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from ..config import settings
from ..exceptions import ValidationError, DocumentProcessingError
from ..websocket.manager import ws_manager


logger = logging.getLogger(__name__)


class UploadSession:
    """Represents an upload session for chunked uploads"""

    def __init__(
        self,
        upload_id: str,
        filename: str,
        total_size: int,
        chunk_size: int = 5 * 1024 * 1024,  # 5MB chunks
    ):
        self.upload_id = upload_id
        self.filename = filename
        self.total_size = total_size
        self.chunk_size = chunk_size
        self.chunks_received = 0
        self.bytes_received = 0
        self.temp_path = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "uploading"
        self.checksum = hashlib.sha256()
        self.metadata = {}

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() - self.updated_at > timedelta(minutes=timeout_minutes)

    @property
    def progress(self) -> float:
        """Calculate upload progress"""
        if self.total_size == 0:
            return 0.0
        return (self.bytes_received / self.total_size) * 100

    @property
    def chunks_total(self) -> int:
        """Calculate total number of chunks"""
        return (self.total_size + self.chunk_size - 1) // self.chunk_size


class StreamingUploadService:
    """Service for handling streaming uploads"""

    def __init__(
        self,
        upload_dir: str = "/tmp/netintel_uploads",
        max_file_size: int = 5 * 1024 * 1024 * 1024,  # 5GB
        chunk_size: int = 5 * 1024 * 1024,  # 5MB
    ):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.chunk_size = chunk_size
        self.sessions: Dict[str, UploadSession] = {}
        self._cleanup_task = None

    async def start_cleanup_task(self):
        """Start background cleanup task for expired sessions"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())

    async def _cleanup_expired_sessions(self):
        """Clean up expired upload sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                expired_sessions = [
                    session_id
                    for session_id, session in self.sessions.items()
                    if session.is_expired()
                ]

                for session_id in expired_sessions:
                    await self.cancel_upload(session_id)
                    logger.info(f"Cleaned up expired session: {session_id}")

            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")

    async def create_upload_session(
        self,
        filename: str,
        file_size: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new upload session for chunked upload"""

        # Validate file size
        if file_size > self.max_file_size:
            raise ValidationError(
                message=f"File size exceeds maximum allowed size of {self.max_file_size} bytes",
                details={"file_size": file_size, "max_size": self.max_file_size},
            )

        # Generate upload ID
        upload_id = str(uuid.uuid4())

        # Create session
        session = UploadSession(
            upload_id=upload_id,
            filename=filename,
            total_size=file_size,
            chunk_size=self.chunk_size,
        )

        # Set temp path
        session.temp_path = self.upload_dir / f"{upload_id}.tmp"
        session.metadata = metadata or {}

        # Store session
        self.sessions[upload_id] = session

        # Create empty file
        async with aiofiles.open(session.temp_path, "wb") as f:
            pass

        logger.info(f"Created upload session {upload_id} for file {filename} ({file_size} bytes)")

        return {
            "upload_id": upload_id,
            "filename": filename,
            "file_size": file_size,
            "chunk_size": self.chunk_size,
            "chunks_total": session.chunks_total,
            "upload_url": f"/api/v2/documents/upload/chunk/{upload_id}",
            "expires_at": (session.created_at + timedelta(hours=1)).isoformat(),
        }

    async def upload_chunk(
        self,
        upload_id: str,
        chunk_number: int,
        chunk_data: bytes,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a chunk of data"""

        # Get session
        session = self.sessions.get(upload_id)
        if not session:
            raise ValidationError(
                message=f"Upload session {upload_id} not found",
                details={"upload_id": upload_id},
            )

        # Check if session is expired
        if session.is_expired():
            raise ValidationError(
                message=f"Upload session {upload_id} has expired",
                details={"upload_id": upload_id},
            )

        # Validate chunk number
        if chunk_number < 0 or chunk_number >= session.chunks_total:
            raise ValidationError(
                message=f"Invalid chunk number {chunk_number}",
                details={
                    "chunk_number": chunk_number,
                    "chunks_total": session.chunks_total,
                },
            )

        # Calculate offset
        offset = chunk_number * session.chunk_size

        # Write chunk to file
        async with aiofiles.open(session.temp_path, "r+b") as f:
            await f.seek(offset)
            await f.write(chunk_data)

        # Update session
        session.chunks_received += 1
        session.bytes_received += len(chunk_data)
        session.checksum.update(chunk_data)
        session.updated_at = datetime.utcnow()

        # Send progress notification via WebSocket
        if client_id:
            await ws_manager.notify_upload_progress(
                upload_id=upload_id,
                chunks_received=session.chunks_received,
                chunks_total=session.chunks_total,
                bytes_received=session.bytes_received,
                bytes_total=session.total_size,
            )

        # Check if upload is complete
        is_complete = session.bytes_received >= session.total_size

        if is_complete:
            session.status = "complete"
            logger.info(f"Upload {upload_id} completed")

        return {
            "upload_id": upload_id,
            "chunk_number": chunk_number,
            "chunks_received": session.chunks_received,
            "chunks_total": session.chunks_total,
            "bytes_received": session.bytes_received,
            "bytes_total": session.total_size,
            "progress": session.progress,
            "is_complete": is_complete,
            "checksum": session.checksum.hexdigest() if is_complete else None,
        }

    async def stream_upload(
        self,
        file: UploadFile,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        client_id: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream upload with progress updates"""

        upload_id = str(uuid.uuid4())
        temp_path = self.upload_dir / f"{upload_id}.tmp"
        bytes_received = 0
        chunk_count = 0

        try:
            async with aiofiles.open(temp_path, "wb") as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break

                    await f.write(chunk)
                    bytes_received += len(chunk)
                    chunk_count += 1

                    # Calculate progress
                    progress = {
                        "upload_id": upload_id,
                        "filename": file.filename,
                        "chunk_number": chunk_count,
                        "bytes_received": bytes_received,
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    # Send WebSocket notification
                    if client_id:
                        await ws_manager.send_personal_message(
                            client_id,
                            {
                                "type": "upload_progress",
                                **progress,
                            },
                        )

                    yield progress

            # Final result
            final_result = {
                "upload_id": upload_id,
                "filename": file.filename,
                "file_size": bytes_received,
                "temp_path": str(temp_path),
                "status": "complete",
                "timestamp": datetime.utcnow().isoformat(),
            }

            if client_id:
                await ws_manager.notify_upload_complete(
                    upload_id=upload_id,
                    document_id=upload_id,  # Will be replaced with actual document ID
                    success=True,
                )

            yield final_result

        except Exception as e:
            # Clean up on error
            if temp_path.exists():
                temp_path.unlink()

            error_result = {
                "upload_id": upload_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

            if client_id:
                await ws_manager.notify_upload_complete(
                    upload_id=upload_id,
                    document_id="",
                    success=False,
                    error=str(e),
                )

            yield error_result
            raise

    async def complete_upload(
        self,
        upload_id: str,
        expected_checksum: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Complete an upload session and prepare file for processing"""

        session = self.sessions.get(upload_id)
        if not session:
            raise ValidationError(
                message=f"Upload session {upload_id} not found",
                details={"upload_id": upload_id},
            )

        # Verify checksum if provided
        actual_checksum = session.checksum.hexdigest()
        if expected_checksum and actual_checksum != expected_checksum:
            raise ValidationError(
                message="Checksum mismatch",
                details={
                    "expected": expected_checksum,
                    "actual": actual_checksum,
                },
            )

        # Move file to final location
        final_path = self.upload_dir / f"{upload_id}_{session.filename}"
        session.temp_path.rename(final_path)

        # Update session
        session.status = "completed"

        # Clean up session
        del self.sessions[upload_id]

        logger.info(f"Completed upload {upload_id}, file saved to {final_path}")

        return {
            "upload_id": upload_id,
            "filename": session.filename,
            "file_path": str(final_path),
            "file_size": session.bytes_received,
            "checksum": actual_checksum,
            "metadata": session.metadata,
            "completed_at": datetime.utcnow().isoformat(),
        }

    async def cancel_upload(self, upload_id: str) -> Dict[str, Any]:
        """Cancel an upload session"""

        session = self.sessions.get(upload_id)
        if not session:
            raise ValidationError(
                message=f"Upload session {upload_id} not found",
                details={"upload_id": upload_id},
            )

        # Delete temp file
        if session.temp_path and session.temp_path.exists():
            session.temp_path.unlink()

        # Remove session
        del self.sessions[upload_id]

        logger.info(f"Cancelled upload {upload_id}")

        return {
            "upload_id": upload_id,
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat(),
        }

    async def resume_upload(self, upload_id: str) -> Dict[str, Any]:
        """Get information to resume an upload"""

        session = self.sessions.get(upload_id)
        if not session:
            raise ValidationError(
                message=f"Upload session {upload_id} not found",
                details={"upload_id": upload_id},
            )

        # Get file size to determine last byte received
        if session.temp_path and session.temp_path.exists():
            actual_size = session.temp_path.stat().st_size
            session.bytes_received = actual_size

        return {
            "upload_id": upload_id,
            "filename": session.filename,
            "bytes_received": session.bytes_received,
            "bytes_total": session.total_size,
            "chunks_received": session.chunks_received,
            "chunks_total": session.chunks_total,
            "next_chunk": session.chunks_received,
            "progress": session.progress,
            "can_resume": True,
        }

    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """Get status of an upload session"""

        session = self.sessions.get(upload_id)
        if not session:
            return {
                "upload_id": upload_id,
                "status": "not_found",
            }

        return {
            "upload_id": upload_id,
            "filename": session.filename,
            "status": session.status,
            "progress": session.progress,
            "bytes_received": session.bytes_received,
            "bytes_total": session.total_size,
            "chunks_received": session.chunks_received,
            "chunks_total": session.chunks_total,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "is_expired": session.is_expired(),
        }


# Global upload service instance
upload_service = StreamingUploadService()