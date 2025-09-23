"""
Audit Logging Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import json
import asyncio
from enum import Enum
from pathlib import Path
import hashlib
from pydantic import BaseModel, Field
from collections import deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_REFRESH = "auth.token_refresh"
    
    # Authorization events
    ACCESS_GRANTED = "authz.access_granted"
    ACCESS_DENIED = "authz.access_denied"
    PERMISSION_CHANGED = "authz.permission_changed"
    ROLE_CHANGED = "authz.role_changed"
    
    # Data events
    DATA_CREATE = "data.create"
    DATA_READ = "data.read"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    
    # Document events
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_PROCESS = "document.process"
    DOCUMENT_DELETE = "document.delete"
    DOCUMENT_VERSION = "document.version"
    
    # Search events
    SEARCH_QUERY = "search.query"
    SEARCH_EXPORT = "search.export"
    
    # System events
    CONFIG_CHANGE = "system.config_change"
    SERVICE_START = "system.service_start"
    SERVICE_STOP = "system.service_stop"
    ERROR = "system.error"
    
    # Admin events
    USER_CREATE = "admin.user_create"
    USER_UPDATE = "admin.user_update"
    USER_DELETE = "admin.user_delete"
    ROLE_CREATE = "admin.role_create"
    ROLE_UPDATE = "admin.role_update"
    ROLE_DELETE = "admin.role_delete"


class AuditSeverity(str, Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """Audit event record"""
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = self.dict()
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, default=str)
    
    def to_log_format(self) -> str:
        """Convert to structured log format"""
        return (
            f"[{self.timestamp.isoformat()}] "
            f"EVENT={self.event_type} "
            f"USER={self.user_id or 'anonymous'} "
            f"IP={self.ip_address or 'unknown'} "
            f"RESOURCE={self.resource_type}:{self.resource_id} "
            f"RESULT={self.result} "
            f"MSG='{self.message}'"
        )


class AuditLogger:
    """Audit logging service"""
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        max_memory_events: int = 10000,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_remote: bool = False,
        remote_endpoint: Optional[str] = None,
    ):
        """
        Initialize audit logger
        
        Args:
            log_file: Path to audit log file
            max_memory_events: Maximum events to keep in memory
            enable_console: Log to console
            enable_file: Log to file
            enable_remote: Send logs to remote endpoint
            remote_endpoint: Remote logging endpoint URL
        """
        
        self.log_file = log_file or Path("/var/log/netintel/audit.log")
        self.max_memory_events = max_memory_events
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_remote = enable_remote
        self.remote_endpoint = remote_endpoint
        
        # In-memory event storage
        self.events = deque(maxlen=max_memory_events)
        
        # Event counters
        self.event_counts = {event_type: 0 for event_type in AuditEventType}
        
        # Setup file logging if enabled
        if self.enable_file:
            self._setup_file_logging()
        
        # Start background tasks
        if self.enable_remote:
            asyncio.create_task(self._remote_log_sender())
    
    def _setup_file_logging(self):
        """Setup file-based audit logging"""
        
        try:
            # Ensure log directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            self.file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=10,
            )
            
            # Set formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.file_handler.setFormatter(formatter)
            
            # Create audit logger
            self.audit_file_logger = logging.getLogger("audit")
            self.audit_file_logger.addHandler(self.file_handler)
            self.audit_file_logger.setLevel(logging.INFO)
            
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
            self.enable_file = False
    
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        
        timestamp = datetime.utcnow().isoformat()
        random_part = hashlib.md5(
            f"{timestamp}{id(self)}".encode()
        ).hexdigest()[:8]
        return f"evt_{random_part}"
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = "success",
        message: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditEvent:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            user_id: User ID
            resource_type: Type of resource
            resource_id: Resource identifier
            action: Action performed
            result: Result of action
            message: Human-readable message
            severity: Event severity
            metadata: Additional metadata
            request: FastAPI request object
            
        Returns:
            Created audit event
        """
        
        # Extract request information if available
        ip_address = None
        user_agent = None
        request_id = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent")
            request_id = getattr(request.state, "request_id", None)
            
            # Override user_id if available in request
            if hasattr(request.state, "user_id"):
                user_id = request.state.user_id
        
        # Create event
        event = AuditEvent(
            event_id=self.generate_event_id(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            message=message,
            metadata=metadata or {},
            request_id=request_id,
        )
        
        # Store in memory
        self.events.append(event)
        
        # Update counters
        self.event_counts[event_type] += 1
        
        # Log to various outputs
        await self._write_event(event)
        
        return event
    
    async def _write_event(self, event: AuditEvent):
        """Write event to configured outputs"""
        
        # Console logging
        if self.enable_console:
            if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
                logger.error(event.to_log_format())
            elif event.severity == AuditSeverity.WARNING:
                logger.warning(event.to_log_format())
            else:
                logger.info(event.to_log_format())
        
        # File logging
        if self.enable_file and hasattr(self, "audit_file_logger"):
            self.audit_file_logger.info(event.to_json())
        
        # Remote logging (queued for batch sending)
        if self.enable_remote:
            # Events are already in memory queue
            pass
    
    async def _remote_log_sender(self):
        """Background task to send logs to remote endpoint"""
        
        import httpx
        
        while True:
            try:
                # Wait for events to accumulate
                await asyncio.sleep(10)
                
                if not self.events:
                    continue
                
                # Get batch of events
                batch_size = min(100, len(self.events))
                batch = []
                
                for _ in range(batch_size):
                    if self.events:
                        batch.append(self.events.popleft())
                
                if batch:
                    # Send to remote endpoint
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            self.remote_endpoint,
                            json={"events": [e.dict() for e in batch]},
                            timeout=30,
                        )
                
            except Exception as e:
                logger.error(f"Failed to send audit logs to remote: {e}")
                # Re-add events to queue
                if 'batch' in locals():
                    for event in batch:
                        self.events.appendleft(event)
    
    def search_events(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Search audit events
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            resource_type: Filter by resource type
            start_time: Start time filter
            end_time: End time filter
            severity: Filter by severity
            limit: Maximum results
            
        Returns:
            List of matching events
        """
        
        results = []
        
        for event in reversed(self.events):
            # Apply filters
            if event_type and event.event_type != event_type:
                continue
            if user_id and event.user_id != user_id:
                continue
            if resource_type and event.resource_type != resource_type:
                continue
            if severity and event.severity != severity:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            
            results.append(event)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get audit statistics
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Audit statistics
        """
        
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Filter events in time range
        filtered_events = [
            e for e in self.events
            if start_time <= e.timestamp <= end_time
        ]
        
        # Calculate statistics
        stats = {
            "total_events": len(filtered_events),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "events_by_type": {},
            "events_by_severity": {},
            "top_users": {},
            "failed_operations": 0,
            "unique_users": set(),
        }
        
        for event in filtered_events:
            # Count by type
            event_type = event.event_type
            stats["events_by_type"][event_type] = \
                stats["events_by_type"].get(event_type, 0) + 1
            
            # Count by severity
            severity = event.severity
            stats["events_by_severity"][severity] = \
                stats["events_by_severity"].get(severity, 0) + 1
            
            # Count by user
            if event.user_id:
                stats["top_users"][event.user_id] = \
                    stats["top_users"].get(event.user_id, 0) + 1
                stats["unique_users"].add(event.user_id)
            
            # Count failures
            if event.result and event.result != "success":
                stats["failed_operations"] += 1
        
        # Convert sets to counts
        stats["unique_users"] = len(stats["unique_users"])
        
        # Get top 10 users
        stats["top_users"] = dict(
            sorted(
                stats["top_users"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
        )
        
        return stats


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic audit logging"""
    
    def __init__(self, app, audit_logger: AuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger
    
    async def dispatch(self, request: Request, call_next):
        """Process request with audit logging"""
        
        # Skip audit for certain endpoints
        if request.url.path in ["/health", "/metrics", "/docs"]:
            return await call_next(request)
        
        # Get user information
        user_id = getattr(request.state, "user_id", None)
        
        # Map HTTP methods to audit actions
        action_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        
        action = action_map.get(request.method, "unknown")
        
        # Process request
        response = await call_next(request)
        
        # Determine event type based on path and method
        event_type = self._determine_event_type(request.url.path, request.method)
        
        # Determine result
        if 200 <= response.status_code < 400:
            result = "success"
            severity = AuditSeverity.INFO
        elif 400 <= response.status_code < 500:
            result = "client_error"
            severity = AuditSeverity.WARNING
        else:
            result = "server_error"
            severity = AuditSeverity.ERROR
        
        # Log audit event
        await self.audit_logger.log_event(
            event_type=event_type,
            user_id=user_id,
            resource_type=self._extract_resource_type(request.url.path),
            action=action,
            result=result,
            severity=severity,
            message=f"{request.method} {request.url.path}",
            metadata={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
            request=request,
        )
        
        return response
    
    def _determine_event_type(self, path: str, method: str) -> AuditEventType:
        """Determine audit event type from path and method"""
        
        if "/auth/" in path:
            if "login" in path:
                return AuditEventType.LOGIN
            elif "logout" in path:
                return AuditEventType.LOGOUT
            else:
                return AuditEventType.TOKEN_REFRESH
        
        elif "/documents/" in path:
            if method == "POST":
                return AuditEventType.DOCUMENT_UPLOAD
            elif method == "DELETE":
                return AuditEventType.DOCUMENT_DELETE
            else:
                return AuditEventType.DATA_READ
        
        elif "/search/" in path:
            return AuditEventType.SEARCH_QUERY
        
        elif "/admin/" in path:
            if "user" in path:
                if method == "POST":
                    return AuditEventType.USER_CREATE
                elif method in ["PUT", "PATCH"]:
                    return AuditEventType.USER_UPDATE
                elif method == "DELETE":
                    return AuditEventType.USER_DELETE
            elif "role" in path:
                if method == "POST":
                    return AuditEventType.ROLE_CREATE
                elif method in ["PUT", "PATCH"]:
                    return AuditEventType.ROLE_UPDATE
                elif method == "DELETE":
                    return AuditEventType.ROLE_DELETE
        
        # Default based on method
        method_map = {
            "GET": AuditEventType.DATA_READ,
            "POST": AuditEventType.DATA_CREATE,
            "PUT": AuditEventType.DATA_UPDATE,
            "PATCH": AuditEventType.DATA_UPDATE,
            "DELETE": AuditEventType.DATA_DELETE,
        }
        
        return method_map.get(method, AuditEventType.DATA_READ)
    
    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path"""
        
        parts = path.strip("/").split("/")
        if parts:
            return parts[0]
        return "unknown"


# Global audit logger
audit_logger = AuditLogger()