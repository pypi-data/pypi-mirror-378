# accessnode/caching/cache_database_handler.py

# cache database handler
from typing import Dict, Any, List, Union

class CacheDatabaseHandler:
    def __init__(self, cache, db_handler):
        """Initialize with cache and db_handler."""
        self.cache = cache  # cache instance (e.g., Redis, in-memory cache)
        self.db_handler = db_handler  # database handler instance (e.g., MongoDB, SQL)

    def _cache_key(self, table_name: str, filter_data: Dict[str, Any]) -> str:
        """Helper to generate cache keys."""
        filter_key = '_'.join(f"{k}:{v}" for k, v in filter_data.items())
        return f"{table_name}_{filter_key}"

    def get(self, table_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """Retrieve a single record with caching."""
        if self.cache:
            cache_key = self._cache_key(table_name, filter_data)
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

        # Retrieve from the database if not in cache
        result = self.db_handler.get(table_name, filter_data)
        if result and self.cache:
            self.cache.set(cache_key, result)  # Store in cache

        return result

    def get_all(self, table_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve all records with caching."""
        if self.cache:
            cache_key = self._cache_key(table_name, filter_data or {})
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

        # Retrieve from the database if not in cache
        result = self.db_handler.get_all(table_name, filter_data)
        if result and self.cache:
            self.cache.set(cache_key, result)  # Store in cache

        return result

    def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update records and invalidate cache."""
        if self.cache:
            cache_key = self._cache_key(table_name, filter_data)
            self.cache.invalidate(cache_key)

        return self.db_handler.update(table_name, filter_data, update_data)

    def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        """Delete records and invalidate cache."""
        if self.cache:
            cache_key = self._cache_key(table_name, filter_data)
            self.cache.invalidate(cache_key)

        return self.db_handler.delete(table_name, filter_data)
