# cache manager
from typing import Any, Dict, Optional
from datetime import datetime
from .cache_strategy import CacheStrategy

class CacheManager:
    """Manages cache operations."""
    
    def __init__(self, cache_backend: Any, strategy: CacheStrategy):
        self.backend = cache_backend
        self.strategy = strategy
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cached = await self.backend.get(key)
        if not cached:
            return None
            
        if self.strategy.is_expired(cached['timestamp']):
            await self.backend.delete(key)
            return None
            
        return cached['data']
        
    async def set(self, key: str, value: Any, expiration: Optional[float] = None) -> None:
        """Set value in cache."""
        await self.backend.set(key, {
            'data': value,
            'timestamp': datetime.now().timestamp()
        }, expiration or self.strategy.expiration)
        
    async def invalidate(self, key: str) -> None:
        """Invalidate cache entry."""
        await self.backend.delete(key)
        
    async def clear(self) -> None:
        """Clear all cache entries."""
        await self.backend.clear()
    
        def generate_cache_key(self, table_name: str, filter_data: Dict[str, Any]) -> str:
            """Generate cache key using CacheStrategy"""
            return self.cache_strategy.generate_key(table_name, filter_data)
