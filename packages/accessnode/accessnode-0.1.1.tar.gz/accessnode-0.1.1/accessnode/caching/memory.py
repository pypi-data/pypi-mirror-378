from typing import Any, Dict, List, Optional, Pattern
import re
from datetime import datetime, timedelta
from ..core.exceptions import CacheError

class MemoryCache:
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[str]:
        """Get value from memory cache."""
        try:
            data = self._storage.get(key)
            if not data:
                return None

            if self._is_expired(data):
                await self.delete(key)
                return None

            return data['value']
        except Exception as e:
            raise CacheError(f"Memory cache get error: {str(e)}")

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> None:
        """Set value in memory cache."""
        try:
            self._storage[key] = {
                'value': value,
                'created_at': datetime.utcnow(),
                'ttl': expire
            }
        except Exception as e:
            raise CacheError(f"Memory cache set error: {str(e)}")

    async def delete(self, *keys: str) -> None:
        """Delete keys from memory cache."""
        try:
            for key in keys:
                self._storage.pop(key, None)
        except Exception as e:
            raise CacheError(f"Memory cache delete error: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        try:
            data = self._storage.get(key)
            if not data:
                return False
            
            if self._is_expired(data):
                await self.delete(key)
                return False
                
            return True
        except Exception as e:
            raise CacheError(f"Memory cache exists error: {str(e)}")

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            regex = self._pattern_to_regex(pattern)
            return [
                key for key in self._storage.keys()
                if regex.match(key)
            ]
        except Exception as e:
            raise CacheError(f"Memory cache keys error: {str(e)}")

    async def flushdb(self) -> None:
        """Clear all keys in memory cache."""
        try:
            self._storage.clear()
        except Exception as e:
            raise CacheError(f"Memory cache flushdb error: {str(e)}")

    def _is_expired(self, data: Dict[str, Any]) -> bool:
        """Check if cached data is expired."""
        if 'ttl' not in data or data['ttl'] is None:
            return False

        expiration = data['created_at'] + timedelta(seconds=data['ttl'])
        return datetime.utcnow() > expiration

    def _pattern_to_regex(self, pattern: str) -> Pattern:
        """Convert Redis-style pattern to regex pattern."""
        regex = pattern.replace('*', '.*').replace('?', '.')
        return re.compile(f"^{regex}$")