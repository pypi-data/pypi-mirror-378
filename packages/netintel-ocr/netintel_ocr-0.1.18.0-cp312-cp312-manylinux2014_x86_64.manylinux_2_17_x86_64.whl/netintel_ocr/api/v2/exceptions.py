"""
Enhanced Error Handling Framework for API v2
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import traceback
import logging
from fastapi import HTTPException, status
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes"""

    # General errors (1000-1999)
    INTERNAL_ERROR = "ERR_1000"
    VALIDATION_ERROR = "ERR_1001"
    NOT_FOUND = "ERR_1002"
    UNAUTHORIZED = "ERR_1003"
    FORBIDDEN = "ERR_1004"
    RATE_LIMITED = "ERR_1005"
    SERVICE_UNAVAILABLE = "ERR_1006"

    # Document errors (2000-2999)
    DOCUMENT_NOT_FOUND = "ERR_2000"
    DOCUMENT_PROCESSING_FAILED = "ERR_2001"
    DOCUMENT_INVALID_FORMAT = "ERR_2002"
    DOCUMENT_TOO_LARGE = "ERR_2003"
    DOCUMENT_ALREADY_EXISTS = "ERR_2004"

    # Milvus errors (3000-3999)
    MILVUS_CONNECTION_ERROR = "ERR_3000"
    MILVUS_COLLECTION_NOT_FOUND = "ERR_3001"
    MILVUS_INDEX_ERROR = "ERR_3002"
    MILVUS_SEARCH_ERROR = "ERR_3003"
    MILVUS_INSERT_ERROR = "ERR_3004"
    MILVUS_SCHEMA_ERROR = "ERR_3005"
    MILVUS_PARTITION_ERROR = "ERR_3006"
    MILVUS_ALIAS_ERROR = "ERR_3007"

    # Vector/Embedding errors (4000-4999)
    EMBEDDING_GENERATION_ERROR = "ERR_4000"
    EMBEDDING_DIMENSION_MISMATCH = "ERR_4001"
    VECTOR_SEARCH_ERROR = "ERR_4002"

    # Knowledge Graph errors (5000-5999)
    KG_CONNECTION_ERROR = "ERR_5000"
    KG_QUERY_ERROR = "ERR_5001"
    KG_EXTRACTION_ERROR = "ERR_5002"

    # WebSocket errors (6000-6999)
    WS_CONNECTION_ERROR = "ERR_6000"
    WS_MESSAGE_ERROR = "ERR_6001"
    WS_TIMEOUT_ERROR = "ERR_6002"


class ErrorResponse(BaseModel):
    """Standardized error response model"""

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    path: Optional[str] = None
    suggestion: Optional[str] = None


class BaseAPIException(HTTPException):
    """Base exception class for API v2"""

    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion

        super().__init__(
            status_code=status_code,
            detail=ErrorResponse(
                error_code=error_code.value,
                message=message,
                details=details,
                suggestion=suggestion,
            ).dict(),
        )


# Specific Exception Classes

class ValidationError(BaseAPIException):
    """Raised when request validation fails"""

    def __init__(
        self,
        message: str = "Invalid request parameters",
        details: Optional[Dict[str, Any]] = None,
        field_errors: Optional[List[Dict[str, str]]] = None,
    ):
        if field_errors:
            details = details or {}
            details["field_errors"] = field_errors

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            suggestion="Check the request parameters and try again",
        )


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found"""

    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if not message:
            message = f"{resource_type} not found"
            if resource_id:
                message = f"{resource_type} with ID '{resource_id}' not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            message=message,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class UnauthorizedError(BaseAPIException):
    """Raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
            suggestion="Provide valid authentication credentials",
        )


class ForbiddenError(BaseAPIException):
    """Raised when user lacks permissions"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.FORBIDDEN,
            message=message,
            details=details,
            suggestion="Contact administrator for required permissions",
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        if limit:
            details["rate_limit"] = limit

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMITED,
            message=message,
            details=details,
            suggestion=f"Wait {retry_after} seconds before retrying" if retry_after else "Reduce request frequency",
        )


# Milvus-specific Exceptions

class MilvusConnectionError(BaseAPIException):
    """Raised when Milvus connection fails"""

    def __init__(
        self,
        message: str = "Failed to connect to Milvus",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        details = {}
        if host:
            details["host"] = host
        if port:
            details["port"] = port

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.MILVUS_CONNECTION_ERROR,
            message=message,
            details=details,
            suggestion="Check Milvus server status and connection parameters",
        )


class MilvusCollectionError(BaseAPIException):
    """Raised for Milvus collection operations errors"""

    def __init__(
        self,
        message: str,
        collection_name: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        details = {}
        if collection_name:
            details["collection"] = collection_name
        if operation:
            details["operation"] = operation

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.MILVUS_COLLECTION_NOT_FOUND,
            message=message,
            details=details,
        )


class MilvusSearchError(BaseAPIException):
    """Raised when Milvus search fails"""

    def __init__(
        self,
        message: str = "Search operation failed",
        collection: Optional[str] = None,
        query: Optional[Dict] = None,
    ):
        details = {}
        if collection:
            details["collection"] = collection
        if query:
            details["query"] = query

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.MILVUS_SEARCH_ERROR,
            message=message,
            details=details,
            suggestion="Check search parameters and collection status",
        )


class MilvusInsertError(BaseAPIException):
    """Raised when Milvus insert operation fails"""

    def __init__(
        self,
        message: str = "Failed to insert data",
        collection: Optional[str] = None,
        num_entities: Optional[int] = None,
    ):
        details = {}
        if collection:
            details["collection"] = collection
        if num_entities:
            details["num_entities"] = num_entities

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.MILVUS_INSERT_ERROR,
            message=message,
            details=details,
        )


# Document-specific Exceptions

class DocumentNotFoundError(NotFoundError):
    """Raised when a document is not found"""

    def __init__(self, document_id: str):
        super().__init__(
            resource_type="Document",
            resource_id=document_id,
        )


class DocumentProcessingError(BaseAPIException):
    """Raised when document processing fails"""

    def __init__(
        self,
        message: str = "Document processing failed",
        document_id: Optional[str] = None,
        stage: Optional[str] = None,
        error_detail: Optional[str] = None,
    ):
        details = {}
        if document_id:
            details["document_id"] = document_id
        if stage:
            details["processing_stage"] = stage
        if error_detail:
            details["error"] = error_detail

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DOCUMENT_PROCESSING_FAILED,
            message=message,
            details=details,
        )


# Error Handler Utility

class ErrorHandler:
    """Centralized error handler"""

    @staticmethod
    def handle_exception(
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> BaseAPIException:
        """Convert any exception to API exception"""

        # If it's already an API exception, return it
        if isinstance(exception, BaseAPIException):
            return exception

        # Log the full exception
        logger.error(
            f"Unhandled exception: {str(exception)}",
            exc_info=True,
            extra={"context": context},
        )

        # Convert to internal error
        return BaseAPIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An internal error occurred",
            details={
                "error": str(exception),
                "type": type(exception).__name__,
                "context": context,
            },
            suggestion="Please try again later or contact support",
        )

    @staticmethod
    def log_error(
        error: BaseAPIException,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Log error with context"""

        logger.error(
            f"API Error: {error.error_code.value} - {error.message}",
            extra={
                "error_code": error.error_code.value,
                "status_code": error.status_code,
                "details": error.details,
                "request_id": request_id,
                "user_id": user_id,
            },
        )