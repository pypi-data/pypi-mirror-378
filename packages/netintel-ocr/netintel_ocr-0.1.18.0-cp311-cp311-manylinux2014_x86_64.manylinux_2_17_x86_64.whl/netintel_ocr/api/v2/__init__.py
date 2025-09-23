"""
NetIntel-OCR API v2 - Enhanced API with Milvus Integration

Version: 0.1.18.0
Focus: API & MCP Enhancement with Vector Database Support
"""

from .routes import router as v2_router
from .models import *
from .services import *
from .milvus import MilvusManager

__version__ = "2.0.0"
__all__ = ["v2_router", "MilvusManager"]