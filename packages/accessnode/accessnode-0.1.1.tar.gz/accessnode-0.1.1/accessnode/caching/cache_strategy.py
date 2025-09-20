# accessnode/caching/cache_stategy.py
import hashlib
from typing import Dict, Any
import json
from datetime import datetime, timedelta


class CacheStrategy:
    def __init__(self, expiration_seconds: int = 3600):
        """
        Initialize cache strategy with expiration time in seconds.
        
        :param expiration_seconds: Time in seconds before cache entries expire
        """
        self._expiration_seconds = expiration_seconds

    def generate_key(self, table_name: str, filter_data: Dict[str, Any]) -> str:
        """
        Generate a deterministic cache key.
        
        :param table_name: Name of the table/collection
        :param filter_data: Dictionary of filter criteria
        :return: Generated cache key as string
        """
        sorted_items = sorted(filter_data.items())
        filter_string = "_".join(
            f"{k}:{self._serialize_value(v)}" 
            for k, v in sorted_items
        )
        return f"{table_name}_{hashlib.md5(filter_string.encode()).hexdigest()}"

    def is_expired(self, timestamp: float) -> bool:
        """
        Check if cache entry is expired.
        
        :param timestamp: Timestamp to check
        :return: True if expired, False otherwise
        """
        age = datetime.now().timestamp() - timestamp
        return age > self._expiration_seconds
        
    @property
    def expiration_time(self) -> float:
        """
        Get expiration timestamp for new cache entries.
        
        :return: Timestamp when cache entries should expire
        """
        return datetime.now().timestamp() + self._expiration_seconds
    
    def _serialize_value(self, value: Any) -> str:
        """
        Serialize complex values for cache key generation.
        
        :param value: Value to serialize
        :return: Serialized string representation
        """
        if isinstance(value, (dict, list)):
            return hashlib.md5(json.dumps(value, sort_keys=True).encode()).hexdigest()
        return str(value)