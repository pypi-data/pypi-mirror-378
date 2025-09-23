"""
Document Management API Routes
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from fastapi import (
    APIRouter, HTTPException, status, Depends, 
    File, UploadFile, Form, Query, WebSocket
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
from ..services.upload import upload_service
from ..services.processing import processing_service
from ..services.versioning import versioning_service
from ..services.websocket import websocket_manager
from ..auth.oauth2 import get_current_user, require_permissions
from ..monitoring.metrics import metrics_service
from ..monitoring.audit import audit_logger, AuditEventType


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/documents", tags=["Documents"])


# ==================== Request Models ====================

class ProcessingOptions(BaseModel):
    """Document processing options"""
    ocr_model: str = "nanonets-ocr-s"  # nanonets-ocr-s|qwen2.5vl
    extract_diagrams: bool = True
    extract_tables: bool = True
    extract_knowledge_graph: bool = True
    page_range: Optional[List[int]] = None
    output_format: str = "markdown"  # markdown|json|xml
    language: str = "en"  # en|es|fr
    priority: str = "normal"  # low|normal|high


class VersionCreateRequest(BaseModel):
    """Version creation request"""
    description: Optional[str] = None
    reprocess: bool = False
    processing_options: Optional[ProcessingOptions] = None


# ==================== Upload Endpoints ====================

@router.post(
    "/upload",
    summary="Upload document",
    description="Upload a document for processing",
)
async def upload_document(
    file: UploadFile = File(...),
    options: str = Form(None),  # JSON string of ProcessingOptions
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Upload document for processing"""
    
    try:
        # Parse options if provided
        processing_options = None
        if options:
            processing_options = ProcessingOptions(**json.loads(options))
        
        # Create upload session for regular upload
        session_id = await upload_service.create_upload_session(
            filename=file.filename,
            file_size=file.size if hasattr(file, 'size') else 0,
            user_id=current_user.sub,
        )
        
        # Read file content
        content = await file.read()
        
        # Complete upload
        document = await upload_service.complete_upload(
            session_id,
            checksum=None,  # TODO: Calculate checksum
        )
        
        # Submit for processing
        job_id = await processing_service.submit_document(
            document_id=document["document_id"],
            file_path=document["file_path"],
            options=processing_options.dict() if processing_options else {},
        )
        
        # Audit log
        await audit_logger.log_event(
            event_type=AuditEventType.DOCUMENT_UPLOAD,
            user_id=current_user.sub,
            resource_type="document",
            resource_id=document["document_id"],
            message=f"Uploaded document {file.filename}",
        )
        
        # Record metrics
        metrics_service.record_document_processed("upload", "success")
        
        return {
            "document_id": document["document_id"],
            "job_id": job_id,
            "status": "processing",
            "upload_id": session_id,
        }
        
    except Exception as e:
        metrics_service.record_document_processed("upload", "failure")
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/upload/stream",
    summary="Stream upload document",
    description="Upload large documents using streaming with resume capability",
)
async def stream_upload_document(
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Initialize streaming upload session"""
    
    # This endpoint would be used with chunked upload
    # The actual implementation would handle multipart uploads
    
    return {
        "message": "Use /upload/stream/init to initialize streaming upload"
    }


@router.post(
    "/upload/stream/init",
    summary="Initialize stream upload",
    description="Initialize a streaming upload session",
)
async def init_stream_upload(
    filename: str = Form(...),
    file_size: int = Form(...),
    chunk_size: int = Form(1024 * 1024),  # 1MB default
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Initialize streaming upload session"""
    
    try:
        session_id = await upload_service.create_upload_session(
            filename=filename,
            file_size=file_size,
            chunk_size=chunk_size,
            user_id=current_user.sub,
        )
        
        session = upload_service.sessions.get(session_id)
        
        return {
            "upload_id": session_id,
            "chunk_size": chunk_size,
            "total_chunks": session.total_chunks if session else 0,
            "status": "initialized",
            "progress_url": f"ws://host/api/v2/ws/upload/{session_id}",
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize stream upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/upload/stream/{upload_id}/chunk",
    summary="Upload chunk",
    description="Upload a file chunk",
)
async def upload_chunk(
    upload_id: str,
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Upload a file chunk"""
    
    try:
        chunk_data = await chunk.read()
        
        result = await upload_service.upload_chunk(
            upload_id,
            chunk_index,
            chunk_data,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to upload chunk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/upload/stream/{upload_id}/complete",
    summary="Complete stream upload",
    description="Complete streaming upload and start processing",
)
async def complete_stream_upload(
    upload_id: str,
    checksum: Optional[str] = Form(None),
    processing_options: Optional[str] = Form(None),  # JSON string
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Complete streaming upload"""
    
    try:
        # Complete upload
        document = await upload_service.complete_upload(
            upload_id,
            checksum=checksum,
        )
        
        # Parse processing options
        options = {}
        if processing_options:
            options = json.loads(processing_options)
        
        # Submit for processing
        job_id = await processing_service.submit_document(
            document_id=document["document_id"],
            file_path=document["file_path"],
            options=options,
        )
        
        return {
            "document_id": document["document_id"],
            "job_id": job_id,
            "status": "processing",
        }
        
    except Exception as e:
        logger.error(f"Failed to complete stream upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/upload/stream/{upload_id}/resume",
    summary="Resume upload",
    description="Resume interrupted upload",
)
async def resume_upload(
    upload_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Resume interrupted upload"""
    
    try:
        result = await upload_service.resume_upload(upload_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to resume upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/batch",
    summary="Batch upload",
    description="Upload multiple documents",
)
async def batch_upload(
    files: List[UploadFile] = File(...),
    options: str = Form(None),  # JSON string of ProcessingOptions
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Batch upload documents"""
    
    try:
        # Parse options
        processing_options = None
        if options:
            processing_options = ProcessingOptions(**json.loads(options))
        
        batch_id = f"batch_{datetime.utcnow().timestamp()}"
        documents = []
        jobs = []
        
        for file in files:
            # Process each file
            content = await file.read()
            
            # Create session and upload
            session_id = await upload_service.create_upload_session(
                filename=file.filename,
                file_size=len(content),
                user_id=current_user.sub,
            )
            
            # Complete upload
            document = await upload_service.complete_upload(
                session_id,
                checksum=None,
            )
            
            # Submit for processing
            job_id = await processing_service.submit_document(
                document_id=document["document_id"],
                file_path=document["file_path"],
                options=processing_options.dict() if processing_options else {},
            )
            
            documents.append(document["document_id"])
            jobs.append(job_id)
        
        return {
            "batch_id": batch_id,
            "documents": documents,
            "jobs": jobs,
            "total": len(files),
            "status": "processing",
        }
        
    except Exception as e:
        logger.error(f"Failed batch upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== Document Management Endpoints ====================

@router.get(
    "/{document_id}",
    summary="Get document",
    description="Get document metadata and status",
)
async def get_document(
    document_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get document information"""
    
    try:
        # Get processing status
        job_status = processing_service.get_job_status(document_id)
        
        # Get current version
        current_version = versioning_service.get_current_version(document_id)
        
        return {
            "document_id": document_id,
            "status": job_status.get("status") if job_status else "unknown",
            "progress": job_status.get("progress") if job_status else 0,
            "current_version": current_version.version_id if current_version else None,
            "metadata": {
                "created_at": current_version.created_at if current_version else None,
                "updated_at": current_version.updated_at if current_version else None,
            },
        }
        
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{document_id}/content",
    summary="Get document content",
    description="Get extracted text content",
)
async def get_document_content(
    document_id: str,
    page: Optional[int] = Query(None, description="Specific page number"),
    format: str = Query("markdown", description="Output format"),
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get document content"""
    
    # TODO: Implement actual content retrieval
    return {
        "document_id": document_id,
        "content": "Document content here...",
        "format": format,
        "page": page,
    }


@router.get(
    "/{document_id}/diagrams",
    summary="Get diagrams",
    description="Get extracted network diagrams",
)
async def get_document_diagrams(
    document_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get document diagrams"""
    
    # TODO: Implement actual diagram retrieval
    return {
        "document_id": document_id,
        "diagrams": [],
    }


@router.get(
    "/{document_id}/tables",
    summary="Get tables",
    description="Get extracted tables",
)
async def get_document_tables(
    document_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get document tables"""
    
    # TODO: Implement actual table retrieval
    return {
        "document_id": document_id,
        "tables": [],
    }


@router.delete(
    "/{document_id}",
    summary="Delete document",
    description="Delete document and all versions",
)
async def delete_document(
    document_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Delete document"""
    
    try:
        # Cancel any processing jobs
        await processing_service.cancel_job(document_id)
        
        # Delete versions
        # TODO: Implement deletion
        
        # Audit log
        await audit_logger.log_event(
            event_type=AuditEventType.DOCUMENT_DELETE,
            user_id=current_user.sub,
            resource_type="document",
            resource_id=document_id,
            message=f"Deleted document {document_id}",
        )
        
        return {
            "document_id": document_id,
            "status": "deleted",
        }
        
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== Version Management Endpoints ====================

@router.post(
    "/{document_id}/versions",
    summary="Create version",
    description="Create new document version",
)
async def create_version(
    document_id: str,
    request: VersionCreateRequest,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create document version"""
    
    try:
        version = versioning_service.create_version(
            document_id,
            description=request.description,
            user_id=current_user.sub,
        )
        
        # If reprocess requested
        if request.reprocess:
            job_id = await processing_service.submit_document(
                document_id=document_id,
                file_path="",  # TODO: Get file path
                options=request.processing_options.dict() if request.processing_options else {},
            )
            
            return {
                "version_id": version.version_id,
                "job_id": job_id,
                "status": "processing",
            }
        
        return {
            "version_id": version.version_id,
            "status": "created",
        }
        
    except Exception as e:
        logger.error(f"Failed to create version: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{document_id}/versions",
    summary="List versions",
    description="List all document versions",
)
async def list_versions(
    document_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """List document versions"""
    
    try:
        history = versioning_service.get_version_history(document_id)
        
        return {
            "document_id": document_id,
            "versions": [
                {
                    "version_id": v.version_id,
                    "created_at": v.created_at,
                    "description": v.description,
                    "is_current": v.is_current,
                }
                for v in history
            ],
        }
        
    except Exception as e:
        logger.error(f"Failed to list versions: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{document_id}/versions/{version_id}",
    summary="Get version",
    description="Get specific version details",
)
async def get_version(
    document_id: str,
    version_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get version details"""
    
    try:
        version = versioning_service.get_version(document_id, version_id)
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found",
            )
        
        return version.dict()
        
    except Exception as e:
        logger.error(f"Failed to get version: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{document_id}/versions/{version_id}/rollback",
    summary="Rollback version",
    description="Rollback to specific version",
)
async def rollback_version(
    document_id: str,
    version_id: str,
    current_user = Depends(get_current_user),
) -> Dict[str, Any]:
    """Rollback to version"""
    
    try:
        result = versioning_service.rollback_version(
            document_id,
            version_id,
            user_id=current_user.sub,
        )
        
        # Audit log
        await audit_logger.log_event(
            event_type=AuditEventType.DOCUMENT_VERSION,
            user_id=current_user.sub,
            resource_type="document",
            resource_id=document_id,
            message=f"Rolled back to version {version_id}",
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to rollback version: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== WebSocket Endpoints ====================

@router.websocket("/ws/processing/{job_id}")
async def processing_websocket(
    websocket: WebSocket,
    job_id: str,
):
    """WebSocket for real-time processing updates"""
    
    await websocket_manager.connect(websocket, job_id)
    
    try:
        while True:
            # Send processing updates
            status = processing_service.get_job_status(job_id)
            
            if status:
                await websocket_manager.send_json(
                    job_id,
                    {
                        "event": "status_change",
                        "data": status,
                    },
                )
            
            # Check if processing complete
            if status and status.get("status") in ["completed", "failed"]:
                break
            
            # Wait before next update
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(job_id)


@router.websocket("/ws/upload/{upload_id}")
async def upload_websocket(
    websocket: WebSocket,
    upload_id: str,
):
    """WebSocket for upload progress updates"""
    
    await websocket_manager.connect(websocket, upload_id)
    
    try:
        while True:
            # Get upload session
            session = upload_service.sessions.get(upload_id)
            
            if session:
                progress = {
                    "event": "progress",
                    "data": {
                        "chunks_received": len(session.chunks_received),
                        "total_chunks": session.total_chunks,
                        "progress": (len(session.chunks_received) / session.total_chunks * 100)
                        if session.total_chunks > 0 else 0,
                        "status": session.status,
                    },
                }
                
                await websocket_manager.send_json(upload_id, progress)
                
                # Check if upload complete
                if session.status in ["completed", "failed"]:
                    break
            
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(upload_id)