"""
Distributed Caching Service
"""

from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
import json
import pickle
import hashlib
from enum import Enum
import asyncio
from redis import asyncio as aioredis
from cachetools import TTLCache, LRUCache, LFUCache
from pydantic import BaseModel
from ..config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class CacheBackend(str, Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"  # Memory + Redis


class CacheStrategy(str, Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live


class CacheStats(BaseModel):
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    hit_rate: float = 0.0
    total_keys: int = 0
    memory_usage: Optional[int] = None
    backend: str
    
    def calculate_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        if total > 0:
            self.hit_rate = self.hits / total
        return self.hit_rate


class CacheService:
    """Unified caching service with multiple backend support"""
    
    def __init__(
        self,
        backend: CacheBackend = CacheBackend.HYBRID,
        strategy: CacheStrategy = CacheStrategy.LRU,
        memory_max_size: int = 1000,
        memory_ttl: int = 300,  # 5 minutes
        redis_url: Optional[str] = None,
        redis_ttl: int = 3600,  # 1 hour
        key_prefix: str = "netintel:",
    ):
        """
        Initialize cache service
        
        Args:
            backend: Cache backend type
            strategy: Cache eviction strategy
            memory_max_size: Maximum items in memory cache
            memory_ttl: Memory cache TTL in seconds
            redis_url: Redis connection URL
            redis_ttl: Redis cache TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        
        self.backend = backend
        self.strategy = strategy
        self.memory_ttl = memory_ttl
        self.redis_ttl = redis_ttl
        self.key_prefix = key_prefix
        
        # Statistics
        self.stats = CacheStats(backend=backend.value)
        
        # Initialize memory cache based on strategy
        if backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
            if strategy == CacheStrategy.LRU:
                self.memory_cache = LRUCache(maxsize=memory_max_size)
            elif strategy == CacheStrategy.LFU:
                self.memory_cache = LFUCache(maxsize=memory_max_size)
            else:  # TTL
                self.memory_cache = TTLCache(maxsize=memory_max_size, ttl=memory_ttl)
        else:
            self.memory_cache = None
        
        # Initialize Redis connection
        self.redis_client = None
        if backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
            redis_url = redis_url or settings.REDIS_URL
            if redis_url:
                self._init_redis(redis_url)
    
    def _init_redis(self, redis_url: str):
        """Initialize Redis connection"""
        try:
            self.redis_client = aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=False,  # We'll handle decoding
            )
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _make_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Create namespaced cache key"""
        if namespace:
            return f"{self.key_prefix}{namespace}:{key}"
        return f"{self.key_prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first (more portable)
            return json.dumps(value).encode("utf-8")
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    async def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            namespace: Optional namespace
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        
        full_key = self._make_key(key, namespace)
        
        # Try memory cache first
        if self.memory_cache is not None:
            try:
                value = self.memory_cache.get(full_key)
                if value is not None:
                    self.stats.hits += 1
                    return value
            except KeyError:
                pass
        
        # Try Redis if available
        if self.redis_client:
            try:
                data = await self.redis_client.get(full_key)
                if data:
                    value = self._deserialize(data)
                    
                    # Populate memory cache
                    if self.memory_cache is not None:
                        self.memory_cache[full_key] = value
                    
                    self.stats.hits += 1
                    return value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        self.stats.misses += 1
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        
        full_key = self._make_key(key, namespace)
        
        # Set in memory cache
        if self.memory_cache is not None:
            try:
                self.memory_cache[full_key] = value
            except Exception as e:
                logger.warning(f"Memory cache set error: {e}")
        
        # Set in Redis
        if self.redis_client:
            try:
                data = self._serialize(value)
                ttl = ttl or self.redis_ttl
                await self.redis_client.setex(full_key, ttl, data)
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
                return False
        
        self.stats.sets += 1
        return True
    
    async def delete(
        self,
        key: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            namespace: Optional namespace
            
        Returns:
            True if deleted
        """
        
        full_key = self._make_key(key, namespace)
        deleted = False
        
        # Delete from memory cache
        if self.memory_cache is not None:
            try:
                del self.memory_cache[full_key]
                deleted = True
            except KeyError:
                pass
        
        # Delete from Redis
        if self.redis_client:
            try:
                result = await self.redis_client.delete(full_key)
                if result > 0:
                    deleted = True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        if deleted:
            self.stats.deletes += 1
        
        return deleted
    
    async def clear(
        self,
        namespace: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> int:
        """
        Clear cache
        
        Args:
            namespace: Clear specific namespace
            pattern: Clear keys matching pattern
            
        Returns:
            Number of keys cleared
        """
        
        count = 0
        
        # Clear memory cache
        if self.memory_cache is not None:
            if not namespace and not pattern:
                # Clear all
                count = len(self.memory_cache)
                self.memory_cache.clear()
            else:
                # Clear matching keys
                keys_to_delete = []
                for key in self.memory_cache.keys():
                    if namespace and not key.startswith(f"{self.key_prefix}{namespace}:"):
                        continue
                    if pattern and pattern not in key:
                        continue
                    keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    count += 1
        
        # Clear Redis
        if self.redis_client:
            try:
                if not namespace and not pattern:
                    # Clear all with prefix
                    pattern_str = f"{self.key_prefix}*"
                elif namespace:
                    pattern_str = f"{self.key_prefix}{namespace}:*"
                else:
                    pattern_str = f"{self.key_prefix}*{pattern}*"
                
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor, match=pattern_str, count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        return count
    
    async def exists(
        self,
        key: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            namespace: Optional namespace
            
        Returns:
            True if exists
        """
        
        full_key = self._make_key(key, namespace)
        
        # Check memory cache
        if self.memory_cache is not None and full_key in self.memory_cache:
            return True
        
        # Check Redis
        if self.redis_client:
            try:
                exists = await self.redis_client.exists(full_key)
                return bool(exists)
            except Exception as e:
                logger.warning(f"Redis exists error: {e}")
        
        return False
    
    async def get_many(
        self,
        keys: List[str],
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get multiple values from cache
        
        Args:
            keys: List of cache keys
            namespace: Optional namespace
            
        Returns:
            Dictionary of key-value pairs
        """
        
        result = {}
        redis_keys = []
        
        # Get from memory cache first
        for key in keys:
            full_key = self._make_key(key, namespace)
            
            if self.memory_cache is not None:
                try:
                    value = self.memory_cache.get(full_key)
                    if value is not None:
                        result[key] = value
                        self.stats.hits += 1
                    else:
                        redis_keys.append((key, full_key))
                except KeyError:
                    redis_keys.append((key, full_key))
            else:
                redis_keys.append((key, full_key))
        
        # Get remaining from Redis
        if self.redis_client and redis_keys:
            try:
                full_keys = [fk for _, fk in redis_keys]
                values = await self.redis_client.mget(full_keys)
                
                for (key, full_key), value in zip(redis_keys, values):
                    if value:
                        deserialized = self._deserialize(value)
                        result[key] = deserialized
                        self.stats.hits += 1
                        
                        # Populate memory cache
                        if self.memory_cache is not None:
                            self.memory_cache[full_key] = deserialized
                    else:
                        self.stats.misses += 1
            except Exception as e:
                logger.warning(f"Redis mget error: {e}")
                self.stats.misses += len(redis_keys)
        
        return result
    
    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Set multiple values in cache
        
        Args:
            items: Dictionary of key-value pairs
            ttl: Optional TTL in seconds
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        
        # Set in memory cache
        if self.memory_cache is not None:
            for key, value in items.items():
                full_key = self._make_key(key, namespace)
                try:
                    self.memory_cache[full_key] = value
                except Exception as e:
                    logger.warning(f"Memory cache set_many error: {e}")
        
        # Set in Redis
        if self.redis_client:
            try:
                pipeline = self.redis_client.pipeline()
                ttl = ttl or self.redis_ttl
                
                for key, value in items.items():
                    full_key = self._make_key(key, namespace)
                    data = self._serialize(value)
                    pipeline.setex(full_key, ttl, data)
                
                await pipeline.execute()
                self.stats.sets += len(items)
                return True
            except Exception as e:
                logger.warning(f"Redis set_many error: {e}")
                return False
        
        self.stats.sets += len(items)
        return True
    
    def cache_key(
        self,
        func_name: str,
        *args,
        **kwargs,
    ) -> str:
        """
        Generate cache key from function and arguments
        
        Args:
            func_name: Function name
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Cache key
        """
        
        # Create a stable hash from arguments
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": kwargs,
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"{func_name}:{key_hash}"
    
    def cached(
        self,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
        key_func: Optional[callable] = None,
    ):
        """
        Decorator for caching function results
        
        Args:
            ttl: Cache TTL in seconds
            namespace: Cache namespace
            key_func: Custom key generation function
            
        Returns:
            Decorator function
        """
        
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                result = await self.get(cache_key, namespace)
                if result is not None:
                    return result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl, namespace)
                
                return result
            
            return wrapper
        
        return decorator
    
    async def get_stats(self) -> CacheStats:
        """
        Get cache statistics
        
        Returns:
            Cache statistics
        """
        
        self.stats.calculate_hit_rate()
        
        # Get memory cache stats
        if self.memory_cache is not None:
            self.stats.total_keys = len(self.memory_cache)
            
            # Estimate memory usage
            try:
                import sys
                memory_usage = sum(
                    sys.getsizeof(k) + sys.getsizeof(v)
                    for k, v in self.memory_cache.items()
                )
                self.stats.memory_usage = memory_usage
            except:
                pass
        
        # Get Redis stats
        if self.redis_client:
            try:
                info = await self.redis_client.info("memory")
                if self.stats.memory_usage:
                    self.stats.memory_usage += info.get("used_memory", 0)
                else:
                    self.stats.memory_usage = info.get("used_memory", 0)
            except:
                pass
        
        return self.stats
    
    async def warmup(
        self,
        items: Dict[str, Any],
        namespace: Optional[str] = None,
    ):
        """
        Warm up cache with pre-computed values
        
        Args:
            items: Dictionary of key-value pairs
            namespace: Optional namespace
        """
        
        await self.set_many(items, namespace=namespace)
        logger.info(f"Warmed up cache with {len(items)} items")


# Global cache instances
memory_cache = CacheService(backend=CacheBackend.MEMORY)
redis_cache = CacheService(backend=CacheBackend.REDIS)
hybrid_cache = CacheService(backend=CacheBackend.HYBRID)

# Default cache
cache = hybrid_cache