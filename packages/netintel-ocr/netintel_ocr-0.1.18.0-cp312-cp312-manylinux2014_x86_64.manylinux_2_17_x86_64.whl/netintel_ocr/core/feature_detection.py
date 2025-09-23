"""Feature detection for modular installation support in NetIntel-OCR v0.1.17.1."""

import importlib
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class FeatureDetector:
    """Detect available features based on installed packages."""

    # Cache results for performance
    _cache: Dict[str, bool] = {}

    @classmethod
    @lru_cache(maxsize=None)
    def has_kg(cls) -> bool:
        """Check if Knowledge Graph support is installed."""
        if 'kg' in cls._cache:
            return cls._cache['kg']

        try:
            import pykeen
            import falkordb
            import torch
            cls._cache['kg'] = True
            return True
        except ImportError as e:
            logger.debug(f"KG dependencies not found: {e}")
            cls._cache['kg'] = False
            return False

    @classmethod
    @lru_cache(maxsize=None)
    def has_vector(cls) -> bool:
        """Check if vector store support is installed."""
        if 'vector' in cls._cache:
            return cls._cache['vector']

        try:
            import pymilvus
            cls._cache['vector'] = True
            return True
        except ImportError as e:
            logger.debug(f"Vector store dependencies not found: {e}")
            cls._cache['vector'] = False
            return False

    @classmethod
    @lru_cache(maxsize=None)
    def has_api(cls) -> bool:
        """Check if API server support is installed."""
        if 'api' in cls._cache:
            return cls._cache['api']

        try:
            import fastapi
            import uvicorn
            cls._cache['api'] = True
            return True
        except ImportError as e:
            logger.debug(f"API server dependencies not found: {e}")
            cls._cache['api'] = False
            return False

    @classmethod
    @lru_cache(maxsize=None)
    def has_mcp(cls) -> bool:
        """Check if MCP server support is installed."""
        if 'mcp' in cls._cache:
            return cls._cache['mcp']

        try:
            import fastmcp
            import websockets
            cls._cache['mcp'] = True
            return True
        except ImportError as e:
            logger.debug(f"MCP server dependencies not found: {e}")
            cls._cache['mcp'] = False
            return False

    @classmethod
    @lru_cache(maxsize=None)
    def has_performance(cls) -> bool:
        """Check if performance optimizations are installed."""
        if 'performance' in cls._cache:
            return cls._cache['performance']

        # Check for C++ core
        try:
            from netintel_ocr.text_dedup import simhash_compute
            cls._cache['performance'] = True
            return True
        except ImportError:
            try:
                from netintel_ocr._cpp_core import simhash_compute
                cls._cache['performance'] = True
                return True
            except ImportError:
                pass

        # Check for other performance libs
        try:
            import numba
            cls._cache['performance'] = True
            return True
        except ImportError:
            cls._cache['performance'] = False
            return False

    @classmethod
    @lru_cache(maxsize=None)
    def has_dev(cls) -> bool:
        """Check if development tools are installed."""
        if 'dev' in cls._cache:
            return cls._cache['dev']

        try:
            import pytest
            import black
            import ruff
            cls._cache['dev'] = True
            return True
        except ImportError as e:
            logger.debug(f"Dev tools not found: {e}")
            cls._cache['dev'] = False
            return False

    @classmethod
    def require_feature(cls, feature: str, message: Optional[str] = None) -> None:
        """Raise helpful error if feature not installed."""
        feature_map = {
            'kg': ('Knowledge Graph', 'pip install netintel-ocr[kg]'),
            'vector': ('Vector Store', 'pip install netintel-ocr[vector]'),
            'api': ('API Server', 'pip install netintel-ocr[api]'),
            'mcp': ('MCP Server', 'pip install netintel-ocr[mcp]'),
            'performance': ('Performance Optimizations', 'pip install netintel-ocr[performance]'),
            'dev': ('Development Tools', 'pip install netintel-ocr[dev]'),
        }

        # Check if feature is available
        check_method = getattr(cls, f'has_{feature}', None)
        if check_method and check_method():
            return

        # Feature not available, raise error
        if feature in feature_map:
            name, install_cmd = feature_map[feature]
            error_msg = (
                f"{name} features not installed.\n"
                f"Install with: {install_cmd}"
            )
            if message:
                error_msg = f"{message}\n{error_msg}"
        else:
            error_msg = f"Unknown feature: {feature}"

        raise ImportError(error_msg)

    @classmethod
    def get_available_features(cls) -> Dict[str, bool]:
        """Get dictionary of all available features."""
        return {
            'kg': cls.has_kg(),
            'vector': cls.has_vector(),
            'api': cls.has_api(),
            'mcp': cls.has_mcp(),
            'performance': cls.has_performance(),
            'dev': cls.has_dev(),
        }

    @classmethod
    def get_missing_features(cls) -> Dict[str, str]:
        """Get dictionary of missing features with install commands."""
        missing = {}

        if not cls.has_kg():
            missing['kg'] = 'pip install netintel-ocr[kg]'
        if not cls.has_vector():
            missing['vector'] = 'pip install netintel-ocr[vector]'
        if not cls.has_api():
            missing['api'] = 'pip install netintel-ocr[api]'
        if not cls.has_mcp():
            missing['mcp'] = 'pip install netintel-ocr[mcp]'
        if not cls.has_performance():
            missing['performance'] = 'pip install netintel-ocr[performance]'
        if not cls.has_dev():
            missing['dev'] = 'pip install netintel-ocr[dev]'

        return missing

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the feature detection cache."""
        cls._cache.clear()
        cls.has_kg.cache_clear()
        cls.has_vector.cache_clear()
        cls.has_api.cache_clear()
        cls.has_mcp.cache_clear()
        cls.has_performance.cache_clear()
        cls.has_dev.cache_clear()


def lazy_import(module_name: str, feature: Optional[str] = None):
    """Lazy import with feature detection.

    Args:
        module_name: Module to import
        feature: Optional feature name to check

    Returns:
        Module or None if not available

    Example:
        kg_module = lazy_import('netintel_ocr.kg', 'kg')
        if kg_module:
            kg_module.KnowledgeGraphBuilder()
    """
    if feature and not getattr(FeatureDetector, f'has_{feature}', lambda: False)():
        logger.debug(f"Feature '{feature}' not available, skipping import of {module_name}")
        return None

    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        logger.debug(f"Failed to import {module_name}: {e}")
        return None


def optional_import(module_name: str, attribute: Optional[str] = None, feature: Optional[str] = None):
    """Import with graceful fallback.

    Args:
        module_name: Module to import
        attribute: Optional attribute to get from module
        feature: Optional feature name to check

    Returns:
        Module, attribute, or None if not available

    Example:
        KGBuilder = optional_import('netintel_ocr.kg', 'KnowledgeGraphBuilder', 'kg')
        if KGBuilder:
            builder = KGBuilder()
    """
    module = lazy_import(module_name, feature)
    if module and attribute:
        return getattr(module, attribute, None)
    return module