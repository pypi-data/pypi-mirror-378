"""
API v2 Configuration
"""

from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
import os


class APIv2Settings(BaseSettings):
    """API v2 Configuration Settings"""

    # API Settings
    api_version: str = Field(default="2.0.0", description="API Version")
    api_prefix: str = Field(default="/api/v2", description="API URL Prefix")
    enable_docs: bool = Field(default=True, description="Enable OpenAPI documentation")
    docs_url: str = Field(default="/api/v2/docs", description="Documentation URL")
    redoc_url: str = Field(default="/api/v2/redoc", description="ReDoc URL")

    # WebSocket Settings
    ws_enabled: bool = Field(default=True, description="Enable WebSocket support")
    ws_ping_interval: int = Field(default=30, description="WebSocket ping interval (seconds)")
    ws_max_connections: int = Field(default=100, description="Maximum WebSocket connections")

    # Milvus Settings
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_user: Optional[str] = Field(default=None, env="MILVUS_USER")
    milvus_password: Optional[str] = Field(default=None, env="MILVUS_PASSWORD")
    milvus_database: str = Field(default="default", env="MILVUS_DATABASE")
    milvus_secure: bool = Field(default=False, env="MILVUS_SECURE")

    # Collection Settings
    default_collection: str = Field(default="netintel_documents", description="Default collection name")
    entity_collection: str = Field(default="netintel_entities", description="Entity collection name")
    query_collection: str = Field(default="netintel_queries", description="Query cache collection")

    # Vector Settings
    embedding_dimension: int = Field(default=768, description="Default embedding dimension")
    default_metric_type: str = Field(default="IP", description="Default metric type (IP, L2, COSINE)")
    default_index_type: str = Field(default="IVF_FLAT", description="Default index type")

    # Performance Settings
    batch_size: int = Field(default=1000, description="Default batch size for operations")
    search_limit: int = Field(default=20, description="Default search result limit")
    search_timeout: int = Field(default=30, description="Search timeout in seconds")

    # Cache Settings
    enable_cache: bool = Field(default=True, description="Enable result caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_backend: str = Field(default="redis", description="Cache backend (redis, memory)")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_default: int = Field(default=100, description="Default requests per minute")
    rate_limit_search: int = Field(default=20, description="Search requests per minute")
    rate_limit_upload: int = Field(default=10, description="Upload requests per hour")

    # Security
    require_auth: bool = Field(default=True, description="Require authentication")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: list = Field(default=["*"], description="Allowed CORS origins")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_endpoint: str = Field(default="/api/v2/metrics", description="Metrics endpoint")
    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")

    class Config:
        env_file = ".env"
        env_prefix = "NETINTEL_API_V2_"


# Global settings instance
settings = APIv2Settings()