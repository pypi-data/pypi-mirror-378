"""
NetIntel-OCR Version Information with C++ Core Detection
"""

import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional

# Try to read version from pyproject.toml
def _get_version_from_pyproject():
    """Read version from pyproject.toml if available."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return None

    try:
        # Find pyproject.toml relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        pyproject_path = os.path.join(project_root, 'pyproject.toml')

        if os.path.exists(pyproject_path):
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                return data.get('project', {}).get('version')
    except Exception:
        pass
    return None

# Get version from pyproject.toml or use fallback
__version__ = _get_version_from_pyproject() or "0.1.17.1"
__cpp_core_version__ = "1.0.1"

def check_cpp_core() -> bool:
    """Check if C++ deduplication core is available."""
    try:
        from netintel_ocr.text_dedup import SimHash, CDC, AVAILABLE
        return AVAILABLE
    except ImportError:
        try:
            # Fallback to text_dedup module
            from text_dedup import SimHash, CDC, AVAILABLE
            return AVAILABLE
        except ImportError:
            return False

def check_faiss() -> Optional[str]:
    """Check if Faiss is available and return version."""
    try:
        import faiss
        return faiss.__version__
    except ImportError:
        return None

def check_avx2() -> bool:
    """Check if AVX2 instructions are available."""
    try:
        import platform
        if platform.machine() in ['x86_64', 'AMD64']:
            # Check CPU flags on Linux
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'avx2' in cpuinfo.lower()
    except:
        pass
    return False

def check_openmp() -> bool:
    """Check if OpenMP is available."""
    try:
        # Try to import the C++ core which uses OpenMP
        from netintel_ocr.text_dedup import _openmp_available
        return _openmp_available()
    except:
        try:
            from text_dedup import _openmp_available
            return _openmp_available()
        except:
            return False

def check_kg_support() -> bool:
    """Check if Knowledge Graph support is available."""
    try:
        import falkordb
        import pykeen
        return True
    except ImportError:
        return False

def get_version_info() -> Dict[str, Any]:
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "cpp_core": check_cpp_core(),
        "cpp_core_version": __cpp_core_version__ if check_cpp_core() else None,
        "faiss": check_faiss(),
        "avx2": check_avx2(),
        "openmp": check_openmp(),
        "kg_support": check_kg_support(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

def format_version_string(json_format: bool = False) -> str:
    """Format version information for display."""
    info = get_version_info()
    
    if json_format:
        return json.dumps(info, indent=2)
    
    # Build human-readable string
    parts = [f"NetIntel-OCR v{info['version']}"]
    
    if info.get('kg_support'):
        parts.append("KG: ✓")
    
    if info['cpp_core']:
        parts.append(f"C++ Core: v{info['cpp_core_version']}")
    else:
        parts.append("C++ Core: Disabled (Python fallback)")
    
    if info['faiss']:
        parts.append(f"Faiss: {info['faiss']}")
    
    if info['avx2']:
        parts.append("AVX2: ✓")
    
    if info['openmp']:
        parts.append("OpenMP: ✓")
    
    return f"{parts[0]} ({', '.join(parts[1:])})"