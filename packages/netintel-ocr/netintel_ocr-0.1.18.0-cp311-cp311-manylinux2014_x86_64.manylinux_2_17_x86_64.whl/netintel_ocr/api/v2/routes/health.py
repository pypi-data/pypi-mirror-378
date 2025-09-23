"""
Health Check and Readiness Endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
import psutil
from ..milvus.connection import MilvusConnection
from ..config import get_settings
from ..monitoring.metrics import metrics_service


logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/health", tags=["Health"])


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Individual component health"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Overall system health"""
    status: HealthStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float
    version: str
    components: List[ComponentHealth]
    system: Dict[str, Any]


class ReadinessCheck(BaseModel):
    """Readiness check result"""
    ready: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, bool]
    message: Optional[str] = None


class LivenessCheck(BaseModel):
    """Liveness check result"""
    alive: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Application start time
APP_START_TIME = datetime.utcnow()


@router.get(
    "/",
    response_model=SystemHealth,
    summary="System health check",
    description="Comprehensive health check of all system components",
)
async def health_check() -> SystemHealth:
    """Perform comprehensive system health check"""
    
    components = []
    overall_status = HealthStatus.HEALTHY
    
    # Check Milvus
    milvus_health = await check_milvus_health()
    components.append(milvus_health)
    if milvus_health.status == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.UNHEALTHY
    elif milvus_health.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
        overall_status = HealthStatus.DEGRADED
    
    # Check Redis (if configured)
    if settings.REDIS_URL:
        redis_health = await check_redis_health()
        components.append(redis_health)
        if redis_health.status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
    
    # Check disk space
    disk_health = check_disk_health()
    components.append(disk_health)
    if disk_health.status == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.DEGRADED
    
    # Check memory
    memory_health = check_memory_health()
    components.append(memory_health)
    if memory_health.status == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.DEGRADED
    
    # Check CPU
    cpu_health = check_cpu_health()
    components.append(cpu_health)
    if cpu_health.status == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.DEGRADED
    
    # Calculate uptime
    uptime = (datetime.utcnow() - APP_START_TIME).total_seconds()
    
    # Get system info
    system_info = {
        "cpu_count": psutil.cpu_count(),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "python_version": "3.9",
        "platform": "linux",
    }
    
    return SystemHealth(
        status=overall_status,
        uptime_seconds=uptime,
        version=settings.API_VERSION or "0.1.18.0",
        components=components,
        system=system_info,
    )


@router.get(
    "/ready",
    response_model=ReadinessCheck,
    summary="Readiness check",
    description="Check if the service is ready to handle requests",
)
async def readiness_check(response: Response) -> ReadinessCheck:
    """Check if service is ready to handle requests"""
    
    checks = {}
    all_ready = True
    
    # Check Milvus connection
    try:
        milvus_conn = MilvusConnection()
        if milvus_conn.is_connected():
            checks["milvus"] = True
        else:
            checks["milvus"] = False
            all_ready = False
    except Exception as e:
        logger.error(f"Milvus readiness check failed: {e}")
        checks["milvus"] = False
        all_ready = False
    
    # Check if embeddings service is available
    try:
        from ..services.embedding import get_embedding_service
        embedding_service = get_embedding_service()
        if embedding_service:
            checks["embeddings"] = True
        else:
            checks["embeddings"] = False
            all_ready = False
    except Exception as e:
        logger.error(f"Embeddings readiness check failed: {e}")
        checks["embeddings"] = False
        all_ready = False
    
    # Check disk space (must have at least 1GB free)
    disk = psutil.disk_usage("/")
    if disk.free > 1024 * 1024 * 1024:  # 1GB
        checks["disk_space"] = True
    else:
        checks["disk_space"] = False
        all_ready = False
    
    # Check memory (must have at least 10% free)
    memory = psutil.virtual_memory()
    if memory.percent < 90:
        checks["memory"] = True
    else:
        checks["memory"] = False
        all_ready = False
    
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Service not ready: " + ", ".join(
            [k for k, v in checks.items() if not v]
        )
    else:
        message = "Service ready"
    
    return ReadinessCheck(
        ready=all_ready,
        checks=checks,
        message=message,
    )


@router.get(
    "/live",
    response_model=LivenessCheck,
    summary="Liveness check",
    description="Simple liveness probe",
)
async def liveness_check() -> LivenessCheck:
    """Simple liveness check"""
    
    return LivenessCheck(alive=True)


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Get metrics in Prometheus format",
    response_class=Response,
)
async def get_metrics():
    """Get Prometheus metrics"""
    
    metrics = metrics_service.get_prometheus_metrics()
    return Response(
        content=metrics,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get(
    "/metrics/summary",
    summary="Metrics summary",
    description="Get human-readable metrics summary",
)
async def get_metrics_summary(
    minutes: int = 30,
) -> Dict[str, Any]:
    """Get metrics summary"""
    
    return metrics_service.get_summary(minutes=minutes)


# Helper functions

async def check_milvus_health() -> ComponentHealth:
    """Check Milvus health"""
    
    start_time = datetime.utcnow()
    
    try:
        milvus_conn = MilvusConnection()
        
        if not milvus_conn.is_connected():
            await milvus_conn.connect()
        
        # Try a simple operation
        collections = await milvus_conn.client.list_collections()
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ComponentHealth(
            name="milvus",
            status=HealthStatus.HEALTHY,
            message=f"Connected, {len(collections)} collections",
            latency_ms=latency,
            metadata={"collections": len(collections)},
        )
    
    except Exception as e:
        logger.error(f"Milvus health check failed: {e}")
        return ComponentHealth(
            name="milvus",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_redis_health() -> ComponentHealth:
    """Check Redis health"""
    
    start_time = datetime.utcnow()
    
    try:
        from redis import asyncio as aioredis
        
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Connected",
            latency_ms=latency,
        )
    
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return ComponentHealth(
            name="redis",
            status=HealthStatus.DEGRADED,
            message=str(e),
        )


def check_disk_health() -> ComponentHealth:
    """Check disk space health"""
    
    try:
        disk = psutil.disk_usage("/")
        percent_used = disk.percent
        
        if percent_used > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Critical: {percent_used:.1f}% disk used"
        elif percent_used > 85:
            status = HealthStatus.DEGRADED
            message = f"Warning: {percent_used:.1f}% disk used"
        else:
            status = HealthStatus.HEALTHY
            message = f"{percent_used:.1f}% disk used"
        
        return ComponentHealth(
            name="disk",
            status=status,
            message=message,
            metadata={
                "percent_used": percent_used,
                "free_gb": round(disk.free / (1024**3), 2),
            },
        )
    
    except Exception as e:
        return ComponentHealth(
            name="disk",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


def check_memory_health() -> ComponentHealth:
    """Check memory health"""
    
    try:
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        
        if percent_used > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Critical: {percent_used:.1f}% memory used"
        elif percent_used > 85:
            status = HealthStatus.DEGRADED
            message = f"Warning: {percent_used:.1f}% memory used"
        else:
            status = HealthStatus.HEALTHY
            message = f"{percent_used:.1f}% memory used"
        
        return ComponentHealth(
            name="memory",
            status=status,
            message=message,
            metadata={
                "percent_used": percent_used,
                "available_gb": round(memory.available / (1024**3), 2),
            },
        )
    
    except Exception as e:
        return ComponentHealth(
            name="memory",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


def check_cpu_health() -> ComponentHealth:
    """Check CPU health"""
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Critical: {cpu_percent:.1f}% CPU usage"
        elif cpu_percent > 75:
            status = HealthStatus.DEGRADED
            message = f"Warning: {cpu_percent:.1f}% CPU usage"
        else:
            status = HealthStatus.HEALTHY
            message = f"{cpu_percent:.1f}% CPU usage"
        
        return ComponentHealth(
            name="cpu",
            status=status,
            message=message,
            metadata={
                "percent_used": cpu_percent,
                "cpu_count": psutil.cpu_count(),
            },
        )
    
    except Exception as e:
        return ComponentHealth(
            name="cpu",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


@router.get(
    "/dependencies",
    summary="Dependency health",
    description="Check health of all external dependencies",
)
async def check_dependencies() -> Dict[str, Any]:
    """Check all external dependencies"""
    
    dependencies = {}
    
    # Check Milvus
    milvus_health = await check_milvus_health()
    dependencies["milvus"] = {
        "status": milvus_health.status,
        "message": milvus_health.message,
        "latency_ms": milvus_health.latency_ms,
    }
    
    # Check Redis if configured
    if settings.REDIS_URL:
        redis_health = await check_redis_health()
        dependencies["redis"] = {
            "status": redis_health.status,
            "message": redis_health.message,
            "latency_ms": redis_health.latency_ms,
        }
    
    # Check OIDC provider if configured
    if settings.OIDC_ISSUER:
        dependencies["oidc"] = {
            "status": "configured",
            "issuer": settings.OIDC_ISSUER,
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies,
    }