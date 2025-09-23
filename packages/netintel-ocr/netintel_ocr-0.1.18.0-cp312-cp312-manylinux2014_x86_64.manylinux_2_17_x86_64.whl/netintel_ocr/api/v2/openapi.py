"""
OpenAPI Documentation Configuration for API v2
"""

from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema"""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="NetIntel-OCR API v2",
        version="2.0.0 (v0.1.18.0)",
        description="""
        ## NetIntel-OCR API v2 - Enhanced Document Intelligence Platform

        ### Key Features
        - **Document Processing**: Advanced PDF processing with OCR, table extraction, and diagram detection
        - **Vector Search**: Milvus-powered similarity search with 20-60x performance improvement
        - **Knowledge Graph**: FalkorDB integration with PyKEEN embeddings for intelligent querying
        - **Real-time Updates**: WebSocket support for processing status and notifications
        - **Hybrid Retrieval**: Combined vector and graph search with 94% accuracy

        ### New in v2.0.0
        - Milvus vector database integration
        - Streaming upload support for large files
        - Document versioning
        - Enhanced error handling with standardized error codes
        - WebSocket support for real-time updates
        - GraphQL endpoint for flexible queries
        - Comprehensive metrics and monitoring

        ### Collections
        - `netintel_documents`: Main document embeddings and content
        - `netintel_entities`: Named entities and their relationships
        - `netintel_queries`: Query cache for improved performance

        ### Authentication
        All endpoints require API key authentication via the `X-API-Key` header.

        ### Rate Limiting
        - Default: 100 requests/minute
        - Search: 20 requests/minute
        - Upload: 10 documents/hour

        ### Error Codes
        - `1xxx`: General errors
        - `2xxx`: Document-related errors
        - `3xxx`: Milvus-related errors
        - `4xxx`: Vector/Embedding errors
        - `5xxx`: Knowledge Graph errors
        - `6xxx`: WebSocket errors
        """,
        routes=app.routes,
        tags=[
            {
                "name": "Documents",
                "description": "Document upload, processing, and management",
            },
            {
                "name": "Search",
                "description": "Vector and hybrid search operations",
            },
            {
                "name": "Milvus Collections",
                "description": "Milvus collection management operations",
            },
            {
                "name": "Milvus Vectors",
                "description": "Vector insertion and search operations",
            },
            {
                "name": "Milvus Index",
                "description": "Index management operations",
            },
            {
                "name": "Milvus Partitions",
                "description": "Partition management operations",
            },
            {
                "name": "Knowledge Graph",
                "description": "Knowledge graph operations and queries",
            },
            {
                "name": "WebSocket",
                "description": "Real-time WebSocket connections",
            },
            {
                "name": "Analytics",
                "description": "Analytics and insights",
            },
            {
                "name": "Health",
                "description": "Health checks and monitoring",
            },
        ],
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server",
            },
            {
                "url": "https://api.netintel-ocr.com",
                "description": "Production server",
            },
        ],
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication",
        },
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/api/v2/auth/oauth/authorize",
                    "tokenUrl": "/api/v2/auth/oauth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access",
                    },
                }
            },
        },
    }

    # Add global security requirement
    openapi_schema["security"] = [{"ApiKeyAuth": []}]

    # Add example responses
    openapi_schema["components"]["responses"] = {
        "ValidationError": {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error_code": "ERR_1001",
                        "message": "Invalid request parameters",
                        "details": {
                            "field_errors": [
                                {"field": "page_size", "message": "Must be between 1 and 100"}
                            ]
                        },
                        "suggestion": "Check the request parameters and try again",
                    },
                }
            },
        },
        "UnauthorizedError": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error_code": "ERR_1003",
                        "message": "Authentication required",
                        "suggestion": "Provide valid authentication credentials",
                    },
                }
            },
        },
        "NotFoundError": {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error_code": "ERR_1002",
                        "message": "Document with ID 'doc_123' not found",
                        "details": {
                            "resource_type": "Document",
                            "resource_id": "doc_123",
                        },
                    },
                }
            },
        },
        "RateLimitError": {
            "description": "Rate Limit Exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error_code": "ERR_1005",
                        "message": "Rate limit exceeded",
                        "details": {
                            "retry_after_seconds": 60,
                            "rate_limit": 100,
                        },
                        "suggestion": "Wait 60 seconds before retrying",
                    },
                }
            },
        },
        "InternalError": {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "error_code": "ERR_1000",
                        "message": "An internal error occurred",
                        "suggestion": "Please try again later or contact support",
                    },
                }
            },
        },
    }

    # Add webhooks
    openapi_schema["webhooks"] = {
        "documentProcessed": {
            "post": {
                "summary": "Document Processing Complete",
                "description": "Webhook called when document processing is complete",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "event": {"type": "string", "enum": ["document.processed"]},
                                    "document_id": {"type": "string"},
                                    "status": {"type": "string", "enum": ["success", "failed"]},
                                    "timestamp": {"type": "string", "format": "date-time"},
                                    "metadata": {"type": "object"},
                                },
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Webhook received successfully"}
                },
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_openapi(app: FastAPI):
    """Setup OpenAPI documentation"""

    # Override the OpenAPI function
    app.openapi = lambda: custom_openapi(app)

    # Add additional metadata
    app.title = "NetIntel-OCR API v2"
    app.version = "2.0.0"
    app.contact = {
        "name": "NetIntel-OCR Support",
        "url": "https://github.com/netintel-ocr/support",
        "email": "support@netintel-ocr.com",
    }
    app.license_info = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }