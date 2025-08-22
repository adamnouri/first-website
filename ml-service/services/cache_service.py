"""
Caching Service for NBA Playoff Predictions
==========================================

Implements intelligent caching to dramatically improve response times
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PredictionCacheService:
    """In-memory cache for playoff predictions with intelligent invalidation"""
    
    def __init__(self, default_ttl_minutes: int = 30):
        self.cache = {}
        self.default_ttl = default_ttl_minutes * 60  # Convert to seconds
        
    def _generate_key(self, operation: str, **params) -> str:
        """Generate cache key from operation and parameters"""
        # Create deterministic key from parameters
        param_str = json.dumps(params, sort_keys=True)
        key_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{operation}_{key_hash}"
    
    def get(self, operation: str, **params) -> Optional[Dict]:
        """Get cached result if valid"""
        key = self._generate_key(operation, **params)
        
        if key not in self.cache:
            return None
            
        cached_item = self.cache[key]
        
        # Check if expired
        if time.time() > cached_item['expires_at']:
            del self.cache[key]
            logger.info(f"Cache expired for {operation}")
            return None
            
        logger.info(f"Cache hit for {operation} (saved {time.time() - cached_item['created_at']:.1f}s)")
        return cached_item['data']
    
    def set(self, operation: str, data: Dict, ttl_minutes: Optional[int] = None, **params):
        """Cache result with TTL"""
        key = self._generate_key(operation, **params)
        ttl = (ttl_minutes or self.default_ttl // 60) * 60
        
        self.cache[key] = {
            'data': data,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'operation': operation,
            'params': params
        }
        
        logger.info(f"Cached {operation} for {ttl//60} minutes")
    
    def invalidate(self, operation: str = None):
        """Invalidate cache entries"""
        if operation:
            # Invalidate specific operation
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(operation)]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for {operation}")
        else:
            # Clear all cache
            self.cache.clear()
            logger.info("Cleared all cache")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        operations = {}
        
        for key, item in self.cache.items():
            op = item['operation']
            if op not in operations:
                operations[op] = {'count': 0, 'oldest': None, 'newest': None}
            
            operations[op]['count'] += 1
            created_at = item['created_at']
            
            if operations[op]['oldest'] is None or created_at < operations[op]['oldest']:
                operations[op]['oldest'] = created_at
            if operations[op]['newest'] is None or created_at > operations[op]['newest']:
                operations[op]['newest'] = created_at
        
        return {
            'total_entries': total_entries,
            'operations': operations,
            'cache_size_mb': self._estimate_size_mb()
        }
    
    def _estimate_size_mb(self) -> float:
        """Estimate cache size in MB"""
        try:
            total_chars = sum(len(json.dumps(item)) for item in self.cache.values())
            return total_chars / 1024 / 1024  # Convert to MB
        except:
            return 0.0

# Global cache instance
prediction_cache = PredictionCacheService()

def cached_prediction(operation: str, ttl_minutes: int = 30):
    """Decorator for caching prediction operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check cache first
            cached_result = prediction_cache.get(operation, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache result
            prediction_cache.set(operation, result, ttl_minutes, **kwargs)
            
            logger.info(f"{operation} executed in {execution_time:.1f}s and cached")
            return result
            
        return wrapper
    return decorator