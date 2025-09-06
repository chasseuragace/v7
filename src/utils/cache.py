"""
Caching utilities for the Statement-to-Reality System.
"""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import pickle
import os

from src.core.logging import LoggerMixin
from src.interfaces.base import CacheProvider


class MemoryCache(CacheProvider, LoggerMixin):
    """In-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if self._is_expired(entry):
                del self.cache[key]
                return None
            return entry['value']
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > entry['expiry']


class FileCache(CacheProvider, LoggerMixin):
    """File-based cache implementation."""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                if self._is_expired(entry):
                    os.remove(file_path)
                    return None
                return entry['value']
            except Exception as e:
                self.logger.warning(f"Failed to read cache file {file_path}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        entry = {
            'value': value,
            'expiry': expiry
        }
        
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            self.logger.warning(f"Failed to write cache file {file_path}: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key."""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > entry['expiry']


def create_cache_key(*args, **kwargs) -> str:
    """Create a cache key from arguments."""
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode()).hexdigest()


def cached(cache_provider: CacheProvider, ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}_{create_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache_provider.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_provider.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
