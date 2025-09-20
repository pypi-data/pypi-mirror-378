# # redis cache
# from typing import Any, Optional
# import redis.asyncio as redis
# import json

# class RedisCache:
#     def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs):
#         """Initialize Redis cache connection."""
#         self.redis = redis.Redis(
#             host=host,
#             port=port,
#             db=db,
#             decode_responses=True,
#             **kwargs
#         )

#     async def get(self, key: str) -> Optional[Any]:
#         """Get value from cache."""
#         value = await self.redis.get(key)
#         if value:
#             return json.loads(value)
#         return None

#     async def set(self, key: str, value: Any, expiration: int = None) -> bool:
#         """Set value in cache with optional expiration in seconds."""
#         try:
#             serialized = json.dumps(value)
#             await self.redis.set(key, serialized, ex=expiration)
#             return True
#         except Exception:
#             return False

#     async def delete(self, key: str) -> bool:
#         """Delete key from cache."""
#         return await self.redis.delete(key) > 0

#     async def invalidate(self, pattern: str) -> bool:
#         """Invalidate all keys matching pattern."""
#         try:
#             keys = await self.redis.keys(pattern)
#             if keys:
#                 await self.redis.delete(*keys)
#             return True
#         except Exception:
#             return False

#     async def close(self) -> None:
#         """Close Redis connection."""
#         await self.redis.close()

#     async def __aenter__(self):
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self.close()


from typing import Any, Dict, List, Optional, Union
import json
from redis.asyncio import Redis
from ..core.exceptions import CacheError

class RedisCache:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ):
        self.client = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            **kwargs
        )

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            return await self.client.get(key)
        except Exception as e:
            raise CacheError(f"Redis get error: {str(e)}")

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> None:
        """Set value in Redis."""
        try:
            if expire:
                await self.client.setex(key, expire, value)
            else:
                await self.client.set(key, value)
        except Exception as e:
            raise CacheError(f"Redis set error: {str(e)}")

    async def delete(self, *keys: str) -> None:
        """Delete keys from Redis."""
        try:
            if keys:
                await self.client.delete(*keys)
        except Exception as e:
            raise CacheError(f"Redis delete error: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            raise CacheError(f"Redis exists error: {str(e)}")

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            return await self.client.keys(pattern)
        except Exception as e:
            raise CacheError(f"Redis keys error: {str(e)}")

    async def flushdb(self) -> None:
        """Clear all keys in current database."""
        try:
            await self.client.flushdb()
        except Exception as e:
            raise CacheError(f"Redis flushdb error: {str(e)}")

    async def close(self) -> None:
        """Close Redis connection."""
        try:
            await self.client.close()
        except Exception as e:
            raise CacheError(f"Redis close error: {str(e)}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()