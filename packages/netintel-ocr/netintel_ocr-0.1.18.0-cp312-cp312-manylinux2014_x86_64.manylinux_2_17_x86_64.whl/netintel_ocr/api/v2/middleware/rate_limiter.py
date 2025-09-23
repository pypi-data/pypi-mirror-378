"""
Rate Limiting Middleware
"""

from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
import hashlib
from enum import Enum
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from collections import defaultdict
import time
from ..cache.cache_service import CacheService, CacheBackend
from ..config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(str, Enum):
    """Rate limit scopes"""
    GLOBAL = "global"  # Global rate limit
    USER = "user"  # Per-user rate limit
    IP = "ip"  # Per-IP rate limit
    ENDPOINT = "endpoint"  # Per-endpoint rate limit
    COMBINED = "combined"  # Combined user+endpoint


class RateLimiter:
    """Rate limiter implementation"""
    
    def __init__(
        self,
        requests: int = 100,
        window: int = 60,  # seconds
        strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW,
        scope: RateLimitScope = RateLimitScope.IP,
        cache_backend: Optional[CacheService] = None,
    ):
        """
        Initialize rate limiter
        
        Args:
            requests: Maximum number of requests
            window: Time window in seconds
            strategy: Rate limiting strategy
            scope: Rate limit scope
            cache_backend: Cache service for distributed rate limiting
        """
        
        self.requests = requests
        self.window = window
        self.strategy = strategy
        self.scope = scope
        
        # Use cache for distributed rate limiting
        if cache_backend:
            self.cache = cache_backend
        else:
            # Create a memory-only cache for single-instance
            self.cache = CacheService(backend=CacheBackend.MEMORY)
        
        # Local storage for non-cached strategies
        self.buckets: Dict[str, Any] = {}
        self.locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    
    def get_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier based on scope
        
        Args:
            request: FastAPI request
            
        Returns:
            Identifier string
        """
        
        identifiers = []
        
        if self.scope in [RateLimitScope.IP, RateLimitScope.GLOBAL]:
            # Get client IP
            ip = request.client.host if request.client else "unknown"
            # Check for proxy headers
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            identifiers.append(f"ip:{ip}")
        
        if self.scope in [RateLimitScope.USER, RateLimitScope.COMBINED]:
            # Get user ID from request state or headers
            user_id = getattr(request.state, "user_id", None)
            if not user_id:
                # Try to get from authorization header
                auth = request.headers.get("Authorization")
                if auth:
                    user_id = hashlib.md5(auth.encode()).hexdigest()[:8]
            if user_id:
                identifiers.append(f"user:{user_id}")
        
        if self.scope in [RateLimitScope.ENDPOINT, RateLimitScope.COMBINED]:
            # Get endpoint path
            path = request.url.path
            method = request.method
            identifiers.append(f"endpoint:{method}:{path}")
        
        if self.scope == RateLimitScope.GLOBAL:
            identifiers = ["global"]
        
        return ":".join(identifiers) if identifiers else "unknown"
    
    async def check_rate_limit(
        self,
        identifier: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Rate limit identifier
            
        Returns:
            Tuple of (allowed, info)
        """
        
        if self.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(identifier)
        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(identifier)
        elif self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(identifier)
        elif self.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return await self._check_leaky_bucket(identifier)
        else:
            return True, {"requests_remaining": self.requests}
    
    async def _check_fixed_window(
        self,
        identifier: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Fixed window rate limiting
        """
        
        now = time.time()
        window_start = int(now / self.window) * self.window
        cache_key = f"ratelimit:fixed:{identifier}:{window_start}"
        
        # Get current count
        count = await self.cache.get(cache_key, default=0)
        
        if count >= self.requests:
            return False, {
                "requests_remaining": 0,
                "reset_at": window_start + self.window,
                "retry_after": int(window_start + self.window - now),
            }
        
        # Increment count
        await self.cache.set(cache_key, count + 1, ttl=self.window)
        
        return True, {
            "requests_remaining": self.requests - count - 1,
            "reset_at": window_start + self.window,
        }
    
    async def _check_sliding_window(
        self,
        identifier: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Sliding window rate limiting using timestamps
        """
        
        now = time.time()
        window_start = now - self.window
        cache_key = f"ratelimit:sliding:{identifier}"
        
        async with self.locks[identifier]:
            # Get timestamps of recent requests
            timestamps = await self.cache.get(cache_key, default=[])
            
            # Remove old timestamps
            timestamps = [ts for ts in timestamps if ts > window_start]
            
            if len(timestamps) >= self.requests:
                oldest = min(timestamps)
                retry_after = int(oldest + self.window - now)
                return False, {
                    "requests_remaining": 0,
                    "retry_after": retry_after,
                }
            
            # Add current timestamp
            timestamps.append(now)
            await self.cache.set(cache_key, timestamps, ttl=self.window)
            
            return True, {
                "requests_remaining": self.requests - len(timestamps),
            }
    
    async def _check_token_bucket(
        self,
        identifier: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Token bucket rate limiting
        """
        
        now = time.time()
        cache_key = f"ratelimit:token:{identifier}"
        refill_rate = self.requests / self.window  # tokens per second
        
        async with self.locks[identifier]:
            # Get bucket state
            bucket = await self.cache.get(cache_key, default=None)
            
            if bucket is None:
                # Initialize bucket
                bucket = {
                    "tokens": self.requests,
                    "last_refill": now,
                }
            else:
                # Refill tokens
                time_passed = now - bucket["last_refill"]
                tokens_to_add = time_passed * refill_rate
                bucket["tokens"] = min(
                    self.requests,
                    bucket["tokens"] + tokens_to_add
                )
                bucket["last_refill"] = now
            
            if bucket["tokens"] < 1:
                # Calculate when next token will be available
                retry_after = int((1 - bucket["tokens"]) / refill_rate)
                return False, {
                    "requests_remaining": 0,
                    "retry_after": retry_after,
                }
            
            # Consume a token
            bucket["tokens"] -= 1
            await self.cache.set(cache_key, bucket, ttl=self.window * 2)
            
            return True, {
                "requests_remaining": int(bucket["tokens"]),
            }
    
    async def _check_leaky_bucket(
        self,
        identifier: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Leaky bucket rate limiting
        """
        
        now = time.time()
        cache_key = f"ratelimit:leaky:{identifier}"
        leak_rate = self.requests / self.window  # requests per second
        
        async with self.locks[identifier]:
            # Get bucket state
            bucket = await self.cache.get(cache_key, default=None)
            
            if bucket is None:
                # Initialize bucket
                bucket = {
                    "volume": 0,
                    "last_leak": now,
                }
            else:
                # Leak water
                time_passed = now - bucket["last_leak"]
                leaked = time_passed * leak_rate
                bucket["volume"] = max(0, bucket["volume"] - leaked)
                bucket["last_leak"] = now
            
            if bucket["volume"] >= self.requests:
                # Bucket is full
                overflow = bucket["volume"] - self.requests + 1
                retry_after = int(overflow / leak_rate)
                return False, {
                    "requests_remaining": 0,
                    "retry_after": retry_after,
                }
            
            # Add water
            bucket["volume"] += 1
            await self.cache.set(cache_key, bucket, ttl=self.window * 2)
            
            return True, {
                "requests_remaining": int(self.requests - bucket["volume"]),
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI"""
    
    def __init__(
        self,
        app,
        default_limits: Dict[str, Any] = None,
        endpoint_limits: Dict[str, Dict[str, Any]] = None,
        cache_backend: Optional[CacheService] = None,
    ):
        """
        Initialize rate limit middleware
        
        Args:
            app: FastAPI application
            default_limits: Default rate limit configuration
            endpoint_limits: Per-endpoint rate limit configuration
            cache_backend: Cache service for distributed rate limiting
        """
        
        super().__init__(app)
        
        # Default configuration
        if default_limits is None:
            default_limits = {
                "requests": 100,
                "window": 60,
                "strategy": RateLimitStrategy.SLIDING_WINDOW,
                "scope": RateLimitScope.IP,
            }
        
        self.default_limiter = RateLimiter(
            cache_backend=cache_backend,
            **default_limits
        )
        
        # Per-endpoint limiters
        self.endpoint_limiters = {}
        if endpoint_limits:
            for endpoint, config in endpoint_limits.items():
                self.endpoint_limiters[endpoint] = RateLimiter(
                    cache_backend=cache_backend,
                    **config
                )
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting
        """
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get appropriate limiter
        limiter = self.endpoint_limiters.get(
            request.url.path,
            self.default_limiter
        )
        
        # Get identifier
        identifier = limiter.get_identifier(request)
        
        # Check rate limit
        allowed, info = await limiter.check_rate_limit(identifier)
        
        if not allowed:
            # Rate limit exceeded
            retry_after = info.get("retry_after", 60)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limiter.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info.get("reset_at", 0)),
                },
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limiter.requests)
        response.headers["X-RateLimit-Remaining"] = str(
            info.get("requests_remaining", 0)
        )
        if "reset_at" in info:
            response.headers["X-RateLimit-Reset"] = str(info["reset_at"])
        
        return response


def create_rate_limiter(
    requests: int = 100,
    window: int = 60,
    strategy: str = "sliding_window",
    scope: str = "ip",
):
    """
    Factory function to create rate limiter decorator
    
    Args:
        requests: Maximum number of requests
        window: Time window in seconds
        strategy: Rate limiting strategy
        scope: Rate limit scope
        
    Returns:
        Rate limiter decorator
    """
    
    limiter = RateLimiter(
        requests=requests,
        window=window,
        strategy=RateLimitStrategy(strategy),
        scope=RateLimitScope(scope),
    )
    
    async def check_limit(request: Request):
        """FastAPI dependency for rate limiting"""
        
        identifier = limiter.get_identifier(request)
        allowed, info = await limiter.check_rate_limit(identifier)
        
        if not allowed:
            retry_after = info.get("retry_after", 60)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limiter.requests),
                    "X-RateLimit-Remaining": "0",
                },
            )
        
        # Add rate limit info to request state
        request.state.rate_limit_info = info
        
        return info
    
    return check_limit