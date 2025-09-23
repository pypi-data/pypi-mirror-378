"""
Monitoring and Metrics Service
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import time
import psutil
import asyncio
from collections import deque, defaultdict
from enum import Enum
from pydantic import BaseModel, Field
import prometheus_client
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class SystemMetrics(BaseModel):
    """System resource metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_usage: float
    network_io_sent: int
    network_io_recv: int
    open_connections: int
    process_count: int
    thread_count: int


class RequestMetrics(BaseModel):
    """HTTP request metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    method: str
    path: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    user_id: Optional[str] = None
    ip_address: Optional[str] = None


class BusinessMetrics(BaseModel):
    """Business/application metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_name: str
    value: float
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricsService:
    """Centralized metrics collection and reporting"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics service
        
        Args:
            registry: Prometheus collector registry
        """
        
        self.registry = registry or CollectorRegistry()
        
        # System metrics storage
        self.system_metrics_history = deque(maxlen=1000)
        self.request_metrics_history = deque(maxlen=10000)
        self.business_metrics_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        
        # HTTP metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )
        
        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )
        
        self.http_request_size_bytes = Summary(
            "http_request_size_bytes",
            "HTTP request size in bytes",
            ["method", "endpoint"],
            registry=self.registry,
        )
        
        self.http_response_size_bytes = Summary(
            "http_response_size_bytes",
            "HTTP response size in bytes",
            ["method", "endpoint"],
            registry=self.registry,
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )
        
        self.system_memory_usage = Gauge(
            "system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )
        
        self.system_disk_usage = Gauge(
            "system_disk_usage_percent",
            "System disk usage percentage",
            registry=self.registry,
        )
        
        # Application metrics
        self.active_connections = Gauge(
            "active_connections",
            "Number of active connections",
            registry=self.registry,
        )
        
        self.documents_processed_total = Counter(
            "documents_processed_total",
            "Total documents processed",
            ["type", "status"],
            registry=self.registry,
        )
        
        self.search_queries_total = Counter(
            "search_queries_total",
            "Total search queries",
            ["type"],
            registry=self.registry,
        )
        
        self.search_latency_seconds = Histogram(
            "search_latency_seconds",
            "Search query latency in seconds",
            ["type"],
            registry=self.registry,
        )
        
        self.milvus_operations_total = Counter(
            "milvus_operations_total",
            "Total Milvus operations",
            ["operation", "status"],
            registry=self.registry,
        )
        
        self.kg_queries_total = Counter(
            "kg_queries_total",
            "Total knowledge graph queries",
            ["type"],
            registry=self.registry,
        )
        
        self.cache_operations_total = Counter(
            "cache_operations_total",
            "Total cache operations",
            ["operation", "result"],
            registry=self.registry,
        )
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._collect_system_metrics())
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # Collect CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_cpu_usage.set(cpu_percent)
                
                # Collect memory usage
                memory = psutil.virtual_memory()
                self.system_memory_usage.set(memory.percent)
                
                # Collect disk usage
                disk = psutil.disk_usage("/")
                self.system_disk_usage.set(disk.percent)
                
                # Collect network I/O
                net_io = psutil.net_io_counters()
                
                # Collect connection count
                connections = len(psutil.net_connections())
                self.active_connections.set(connections)
                
                # Store system metrics
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used=memory.used,
                    memory_available=memory.available,
                    disk_usage=disk.percent,
                    network_io_sent=net_io.bytes_sent,
                    network_io_recv=net_io.bytes_recv,
                    open_connections=connections,
                    process_count=len(psutil.pids()),
                    thread_count=psutil.Process().num_threads(),
                )
                
                self.system_metrics_history.append(metrics)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            # Collect every 30 seconds
            await asyncio.sleep(30)
    
    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        request_size: int = 0,
        response_size: int = 0,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Record HTTP request metrics"""
        
        # Update Prometheus metrics
        self.http_requests_total.labels(
            method=method,
            endpoint=path,
            status=str(status_code),
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=path,
        ).observe(response_time)
        
        if request_size > 0:
            self.http_request_size_bytes.labels(
                method=method,
                endpoint=path,
            ).observe(request_size)
        
        if response_size > 0:
            self.http_response_size_bytes.labels(
                method=method,
                endpoint=path,
            ).observe(response_size)
        
        # Store request metrics
        metrics = RequestMetrics(
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            user_id=user_id,
            ip_address=ip_address,
        )
        
        self.request_metrics_history.append(metrics)
    
    def record_document_processed(
        self,
        doc_type: str,
        status: str = "success",
    ):
        """Record document processing metrics"""
        
        self.documents_processed_total.labels(
            type=doc_type,
            status=status,
        ).inc()
    
    def record_search_query(
        self,
        query_type: str,
        latency: float,
    ):
        """Record search query metrics"""
        
        self.search_queries_total.labels(type=query_type).inc()
        self.search_latency_seconds.labels(type=query_type).observe(latency)
    
    def record_milvus_operation(
        self,
        operation: str,
        status: str = "success",
    ):
        """Record Milvus operation metrics"""
        
        self.milvus_operations_total.labels(
            operation=operation,
            status=status,
        ).inc()
    
    def record_kg_query(
        self,
        query_type: str,
    ):
        """Record knowledge graph query metrics"""
        
        self.kg_queries_total.labels(type=query_type).inc()
    
    def record_cache_operation(
        self,
        operation: str,
        result: str,
    ):
        """Record cache operation metrics"""
        
        self.cache_operations_total.labels(
            operation=operation,
            result=result,
        ).inc()
    
    def record_business_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record custom business metrics"""
        
        metric = BusinessMetrics(
            metric_name=name,
            value=value,
            tags=tags or {},
            metadata=metadata or {},
        )
        
        self.business_metrics_history[name].append(metric)
    
    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry)
    
    def get_system_metrics(
        self,
        minutes: int = 30,
    ) -> List[SystemMetrics]:
        """Get recent system metrics"""
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            m for m in self.system_metrics_history
            if m.timestamp >= cutoff
        ]
    
    def get_request_metrics(
        self,
        minutes: int = 30,
    ) -> List[RequestMetrics]:
        """Get recent request metrics"""
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            m for m in self.request_metrics_history
            if m.timestamp >= cutoff
        ]
    
    def get_business_metrics(
        self,
        name: str,
        minutes: int = 30,
    ) -> List[BusinessMetrics]:
        """Get recent business metrics by name"""
        
        if name not in self.business_metrics_history:
            return []
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            m for m in self.business_metrics_history[name]
            if m.timestamp >= cutoff
        ]
    
    def get_summary(
        self,
        minutes: int = 30,
    ) -> Dict[str, Any]:
        """Get metrics summary"""
        
        # Get recent metrics
        system_metrics = self.get_system_metrics(minutes)
        request_metrics = self.get_request_metrics(minutes)
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in system_metrics) / len(system_metrics) if system_metrics else 0
        avg_memory = sum(m.memory_percent for m in system_metrics) / len(system_metrics) if system_metrics else 0
        
        # Calculate request stats
        total_requests = len(request_metrics)
        if request_metrics:
            avg_response_time = sum(m.response_time for m in request_metrics) / total_requests
            success_rate = len([m for m in request_metrics if 200 <= m.status_code < 400]) / total_requests
        else:
            avg_response_time = 0
            success_rate = 0
        
        return {
            "period_minutes": minutes,
            "system": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory,
                "current_connections": self.active_connections._value.get() if hasattr(self.active_connections, '_value') else 0,
            },
            "requests": {
                "total": total_requests,
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP metrics"""
    
    def __init__(self, app, metrics_service: MetricsService):
        super().__init__(app)
        self.metrics_service = metrics_service
    
    async def dispatch(self, request: Request, call_next):
        """Process request with metrics collection"""
        
        # Skip metrics for certain endpoints
        if request.url.path in ["/metrics", "/health"]:
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Get request size
        request_size = int(request.headers.get("content-length", 0))
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_id = getattr(request.state, "user_id", None)
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get response size
        response_size = int(response.headers.get("content-length", 0))
        
        # Record metrics
        self.metrics_service.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            user_id=user_id,
            ip_address=ip_address,
        )
        
        return response


# Global metrics service
metrics_service = MetricsService()


# Context manager for timing operations
class Timer:
    """Context manager for timing operations"""
    
    def __init__(
        self,
        metrics_service: MetricsService,
        metric_name: str,
        tags: Optional[Dict[str, str]] = None,
    ):
        self.metrics_service = metrics_service
        self.metric_name = metric_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        self.metrics_service.record_business_metric(
            name=f"{self.metric_name}_duration",
            value=elapsed,
            tags=self.tags,
        )
        return False