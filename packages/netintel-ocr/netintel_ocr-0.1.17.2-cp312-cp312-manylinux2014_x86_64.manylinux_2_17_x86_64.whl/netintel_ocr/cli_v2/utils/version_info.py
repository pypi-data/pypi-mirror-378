"""Version information and capability detection for NetIntel-OCR."""

import os
import sys
import platform
import importlib
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

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
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        pyproject_path = project_root / 'pyproject.toml'

        if pyproject_path.exists():
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                return data.get('project', {}).get('version')
    except Exception:
        pass
    return None

__version__ = _get_version_from_pyproject() or "0.1.17.1"


class VersionInfo:
    """Comprehensive version and capability information."""

    # Define all available modules and their details
    MODULES = {
        'base': {
            'name': 'Core OCR',
            'always_installed': True,
            'check_packages': [],
            'display_packages': [],
            'size': '500MB',
            'description': 'Core OCR functionality with network diagram detection'
        },
        'kg': {
            'name': 'Knowledge Graph',
            'always_installed': False,
            'check_packages': ['pykeen', 'falkordb', 'torch'],
            'display_packages': ['PyKEEN', 'torch', 'FalkorDB'],
            'size': '1.5GB',
            'description': 'Knowledge Graph construction with PyKEEN embeddings'
        },
        'vector': {
            'name': 'Vector Store',
            'always_installed': False,
            'check_packages': ['pymilvus'],
            'display_packages': ['pymilvus', 'qdrant-client', 'chromadb'],
            'size': '300MB',
            'description': 'Vector database support for similarity search'
        },
        'api': {
            'name': 'API Server',
            'always_installed': False,
            'check_packages': ['fastapi', 'uvicorn'],
            'display_packages': ['fastapi', 'uvicorn'],
            'size': '50MB',
            'description': 'REST API server for programmatic access'
        },
        'mcp': {
            'name': 'MCP Server',
            'always_installed': False,
            'check_packages': ['fastmcp'],
            'display_packages': ['fastmcp', 'websockets'],
            'size': '30MB',
            'description': 'Model Context Protocol server for LLM integration'
        },
        'performance': {
            'name': 'C++ Optimizations',
            'always_installed': False,
            'check_packages': [],  # Check via C++ core detection
            'display_packages': ['numpy[mkl]', 'numba'],
            'size': '200MB',
            'description': 'High-performance C++ core with SIMD optimizations'
        },
        'dev': {
            'name': 'Development Tools',
            'always_installed': False,
            'check_packages': ['pytest', 'black', 'ruff'],
            'display_packages': ['pytest', 'black', 'ruff', 'mypy'],
            'size': '100MB',
            'description': 'Testing and code quality tools'
        }
    }

    @classmethod
    def get_version_details(cls) -> Dict[str, Any]:
        """Gather all version and capability information."""
        return {
            'version': __version__,
            'core': cls._get_core_info(),
            'modules': {
                'installed': cls._get_installed_modules(),
                'available': cls._get_available_modules()
            },
            'active_features': cls._get_active_features()
        }

    @classmethod
    def _get_core_info(cls) -> Dict[str, Any]:
        """Get core component information."""
        return {
            'cpp_enabled': cls._check_cpp_core(),
            'cpp_version': cls._get_cpp_version(),
            'avx2': cls._check_avx2_support(),
            'openmp': cls._check_openmp_support(),
            'platform': cls._get_platform_info()
        }

    @classmethod
    def _check_cpp_core(cls) -> bool:
        """Check if C++ core is available and functional."""
        try:
            from netintel_ocr.text_dedup import simhash_compute
            return True
        except ImportError:
            try:
                from netintel_ocr._cpp_core import simhash_compute
                return True
            except ImportError:
                return False

    @classmethod
    def _get_cpp_version(cls) -> str:
        """Get C++ core version if available."""
        try:
            from netintel_ocr.text_dedup import __cpp_version__
            return __cpp_version__
        except ImportError:
            try:
                from netintel_ocr._cpp_core import __version__
                return __version__
            except ImportError:
                return "N/A"

    @classmethod
    def _check_avx2_support(cls) -> bool:
        """Check if CPU supports AVX2 instructions."""
        try:
            # Try to get CPU flags
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    return "avx2" in cpuinfo.lower()
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.features"],
                    capture_output=True,
                    text=True
                )
                return "AVX2" in result.stdout
        except Exception:
            pass

        # Fallback: try to import and use cpuinfo package if available
        try:
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            return 'avx2' in info.get('flags', [])
        except ImportError:
            pass

        # If C++ core is working, assume AVX2 is available
        return cls._check_cpp_core()

    @classmethod
    def _check_openmp_support(cls) -> bool:
        """Check if OpenMP is available."""
        try:
            from netintel_ocr.text_dedup import get_openmp_threads
            return get_openmp_threads() > 0
        except ImportError:
            try:
                from netintel_ocr._cpp_core import get_openmp_threads
                return get_openmp_threads() > 0
            except ImportError:
                # Check if OpenMP is likely available based on platform
                if platform.system() == "Linux":
                    return os.path.exists("/usr/lib/x86_64-linux-gnu/libgomp.so.1") or \
                           os.path.exists("/usr/lib64/libgomp.so.1")
                return False

    @classmethod
    def _get_platform_info(cls) -> str:
        """Get platform information."""
        return f"{platform.system()} {platform.machine()}"

    @classmethod
    def _check_module_installed(cls, module_key: str) -> tuple[bool, Optional[str]]:
        """Check if a module is installed and get its version."""
        module_info = cls.MODULES.get(module_key, {})

        if module_info.get('always_installed'):
            return True, __version__

        # Special handling for performance module
        if module_key == 'performance':
            installed = cls._check_cpp_core()
            version = cls._get_cpp_version() if installed else None
            return installed, version

        # Check if all required packages are installed
        check_packages = module_info.get('check_packages', [])
        if not check_packages:
            return False, None

        all_installed = True
        version = None

        for package in check_packages:
            try:
                mod = importlib.import_module(package)
                if version is None and hasattr(mod, '__version__'):
                    version = mod.__version__
            except ImportError:
                all_installed = False
                break

        return all_installed, version

    @classmethod
    def _get_installed_modules(cls) -> Dict[str, Dict[str, Any]]:
        """Get list of installed modules with version info."""
        installed = {}

        for module_key, module_info in cls.MODULES.items():
            is_installed, version = cls._check_module_installed(module_key)

            installed[module_key] = {
                'name': module_info['name'],
                'installed': is_installed,
                'version': version,
                'always_installed': module_info.get('always_installed', False)
            }

        return installed

    @classmethod
    def _get_available_modules(cls) -> List[Dict[str, Any]]:
        """Get list of modules available for installation."""
        available = []

        for module_key, module_info in cls.MODULES.items():
            is_installed, _ = cls._check_module_installed(module_key)

            if not module_info.get('always_installed') and not is_installed:
                available.append({
                    'key': module_key,
                    'name': module_info['name'],
                    'command': f'pip install netintel-ocr[{module_key}]',
                    'packages': module_info.get('display_packages', []),
                    'size': module_info.get('size', 'Unknown'),
                    'description': module_info.get('description', '')
                })

        return available

    @classmethod
    def _get_active_features(cls) -> Dict[str, Any]:
        """Get status of active features."""
        features = {}

        # Check FalkorDB
        features['falkordb'] = cls._check_falkordb_connection()

        # Check Milvus
        features['milvus'] = cls._check_milvus_connection()

        # Check Ollama
        features['ollama'] = cls._check_ollama_connection()

        # Check GPU
        features['gpu'] = cls._check_gpu_support()

        # Check API Server readiness
        features['api'] = cls._check_api_ready()

        # Check MCP Server readiness
        features['mcp'] = cls._check_mcp_ready()

        return features

    @classmethod
    def _check_falkordb_connection(cls) -> Dict[str, Any]:
        """Check FalkorDB connection status."""
        try:
            import falkordb
            import redis

            host = os.environ.get('FALKORDB_HOST', 'localhost')
            port = int(os.environ.get('FALKORDB_PORT', '6379'))

            # Try to connect
            client = redis.Redis(host=host, port=port, decode_responses=True)
            client.ping()

            return {
                'connected': True,
                'host': f"{host}:{port}"
            }
        except ImportError:
            return {
                'connected': False,
                'error': 'kg module not installed'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)[:30]  # Truncate error message
            }

    @classmethod
    def _check_milvus_connection(cls) -> Dict[str, Any]:
        """Check Milvus connection status."""
        try:
            from pymilvus import connections, utility

            host = os.environ.get('MILVUS_HOST', 'localhost')
            port = os.environ.get('MILVUS_PORT', '19530')

            # Try to connect
            connections.connect(
                alias="default",
                host=host,
                port=port,
                timeout=2
            )

            # Check if connected
            if utility.get_connection("default") is not None:
                return {
                    'connected': True,
                    'host': f"{host}:{port}"
                }
            else:
                return {
                    'connected': False,
                    'error': 'connection failed'
                }
        except ImportError:
            return {
                'connected': False,
                'error': 'vector module not installed'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)[:30]
            }

    @classmethod
    def _check_ollama_connection(cls) -> Dict[str, Any]:
        """Check Ollama connection status."""
        try:
            import requests

            host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            if not host.startswith('http'):
                host = f'http://{host}'

            # Try to connect to Ollama API
            response = requests.get(f"{host}/api/tags", timeout=2)

            if response.status_code == 200:
                return {
                    'connected': True,
                    'host': host.replace('http://', '').replace('https://', '')
                }
            else:
                return {
                    'connected': False,
                    'error': f'status {response.status_code}'
                }
        except requests.exceptions.ConnectionError:
            return {
                'connected': False,
                'error': 'connection refused'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)[:30]
            }

    @classmethod
    def _check_gpu_support(cls) -> Dict[str, Any]:
        """Check GPU support and details."""
        try:
            import torch

            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3

                return {
                    'available': True,
                    'cuda_version': torch.version.cuda,
                    'device': device_name,
                    'memory': f"{memory_gb:.1f}GB",
                    'count': device_count
                }
            else:
                return {
                    'available': False,
                    'reason': 'CPU only'
                }
        except ImportError:
            return {
                'available': False,
                'reason': 'torch not installed'
            }
        except Exception:
            return {
                'available': False,
                'reason': 'detection failed'
            }

    @classmethod
    def _check_api_ready(cls) -> Dict[str, Any]:
        """Check if API server is ready."""
        try:
            import fastapi
            import uvicorn

            # Check if API server is likely running
            import requests
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    return {
                        'ready': True,
                        'port': 8000
                    }
            except:
                pass

            return {
                'ready': False,
                'installed': True
            }
        except ImportError:
            return {
                'ready': False,
                'installed': False
            }

    @classmethod
    def _check_mcp_ready(cls) -> Dict[str, Any]:
        """Check if MCP server is ready."""
        try:
            import fastmcp

            # Check if MCP server is likely running
            import requests
            try:
                response = requests.get("http://localhost:8001/health", timeout=1)
                if response.status_code == 200:
                    return {
                        'ready': True,
                        'port': 8001
                    }
            except:
                pass

            return {
                'ready': False,
                'installed': True
            }
        except ImportError:
            return {
                'ready': False,
                'installed': False
            }

    @classmethod
    def format_as_json(cls, info: Dict[str, Any]) -> str:
        """Format version info as JSON."""
        return json.dumps(info, indent=2)

    @classmethod
    def format_as_text(cls, info: Dict[str, Any], detailed: bool = False) -> str:
        """Format version info as text tree."""
        lines = []
        lines.append(f"NetIntel-OCR v{info['version']}")

        # Core Components
        lines.append("├── Core Components:")
        core = info['core']
        cpp_status = "✓" if core['cpp_enabled'] else "✗ (fallback to Python)"
        lines.append(f"│   ├── C++ Core: {cpp_status}")
        if core['cpp_enabled']:
            lines.append(f"│   │   └── Version: {core['cpp_version']}")
        lines.append(f"│   ├── AVX2: {'✓' if core['avx2'] else '✗'}")
        lines.append(f"│   ├── OpenMP: {'✓' if core['openmp'] else '✗'}")
        lines.append(f"│   └── Platform: {core['platform']}")

        # Installed Modules
        lines.append("├── Installed Modules:")
        modules = info['modules']['installed']
        for key, module in modules.items():
            status = "✓" if module['installed'] else "✗"
            version_str = f" ({module['version']})" if module.get('version') and module['installed'] else ""
            note = " (always installed)" if module.get('always_installed') else " (not installed)" if not module['installed'] else ""
            lines.append(f"│   ├── [{key}] {module['name']}: {status}{version_str}{note}")

        # Available for Install
        available = info['modules']['available']
        if available:
            lines.append("├── Available for Install:")
            for i, module in enumerate(available):
                is_last = i == len(available) - 1
                prefix = "└──" if is_last else "├──"
                lines.append(f"│   {prefix} [{module['key']}] {module['name']}: {module['command']}")
                if module['packages']:
                    sub_prefix = "    " if is_last else "│   "
                    lines.append(f"│   {sub_prefix}└── Adds: {', '.join(module['packages'])} (+{module['size']})")

        # Active Features
        lines.append("├── Active Features:")
        features = info['active_features']

        # FalkorDB
        falkor = features.get('falkordb', {})
        if falkor.get('connected'):
            lines.append(f"│   ├── FalkorDB: ✓ (connected to {falkor['host']})")
        else:
            lines.append(f"│   ├── FalkorDB: ✗ ({falkor.get('error', 'not available')})")

        # Milvus
        milvus = features.get('milvus', {})
        if milvus.get('connected'):
            lines.append(f"│   ├── Milvus: ✓ (connected to {milvus['host']})")
        else:
            lines.append(f"│   ├── Milvus: ✗ ({milvus.get('error', 'not available')})")

        # Ollama
        ollama = features.get('ollama', {})
        if ollama.get('connected'):
            lines.append(f"│   ├── Ollama: ✓ (connected to {ollama['host']})")
        else:
            lines.append(f"│   ├── Ollama: ✗ ({ollama.get('error', 'not available')})")

        # GPU
        gpu = features.get('gpu', {})
        if gpu.get('available'):
            lines.append(f"│   ├── GPU Support: ✓ (CUDA {gpu['cuda_version']}, {gpu['memory']})")
        else:
            lines.append(f"│   ├── GPU Support: ✗ ({gpu.get('reason', 'not available')})")

        # API Server
        api = features.get('api', {})
        if api.get('ready'):
            lines.append(f"│   ├── API Server: ✓ (ready on port {api['port']})")
        elif api.get('installed'):
            lines.append(f"│   ├── API Server: ✗ (installed but not running)")
        else:
            lines.append(f"│   ├── API Server: ✗ (api module not installed)")

        # MCP Server
        mcp = features.get('mcp', {})
        if mcp.get('ready'):
            lines.append(f"│   └── MCP Server: ✓ (ready on port {mcp['port']})")
        elif mcp.get('installed'):
            lines.append(f"│   └── MCP Server: ✗ (installed but not running)")
        else:
            lines.append(f"│   └── MCP Server: ✗ (mcp module not installed)")

        # Quick Install hint
        if available:
            lines.append("└── Quick Install:")
            lines.append("    └── All features: pip install netintel-ocr[all]")
        else:
            lines.append("└── Status:")
            # Determine overall status
            all_installed = all(m['installed'] for m in modules.values() if not m.get('always_installed'))
            if all_installed:
                lines.append("    └── Full installation complete")
            else:
                lines.append("    └── Ready for production use")

        return "\n".join(lines)