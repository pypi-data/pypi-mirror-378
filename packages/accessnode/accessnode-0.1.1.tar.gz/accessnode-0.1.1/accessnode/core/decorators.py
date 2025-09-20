from functools import wraps
from typing import Any, Callable, Type, TypeVar, Optional
from datetime import datetime
import inspect
import logging
from ..models.base import BaseModel

T = TypeVar('T', bound=BaseModel)

def transactional(func: Callable) -> Callable:
    """
    Decorator to handle database transactions.
    Automatically rolls back on exception.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the model instance if this is a method
        model_instance = args[0] if args and isinstance(args[0], BaseModel) else None
        
        # Get the database connection from the model or passed kwargs
        db = getattr(model_instance, '_db', None) if model_instance else kwargs.get('db')
        if not db:
            raise ValueError("No database connection available")

        async with db.transaction() as txn:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                await txn.rollback()
                logging.error(f"Transaction failed: {str(e)}")
                raise

    return wrapper

def cached(
    ttl: int = 3600,
    key_prefix: Optional[str] = None,
    invalidate_on_update: bool = True
) -> Callable:
    """
    Decorator for caching method results.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance from model or kwargs
            model_instance = args[0] if args and isinstance(args[0], BaseModel) else None
            cache = getattr(model_instance, '_cache', None) if model_instance else kwargs.get('cache')
            
            if not cache:
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = f"{key_prefix or func.__name__}:"
            cache_key += ":".join([str(arg) for arg in args[1:]])
            cache_key += ":".join([f"{k}={v}" for k, v in kwargs.items()])

            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator

def validate_input(model: Type[T]) -> Callable:
    """
    Decorator to validate input data against a model.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the input data from args or kwargs
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate input data against model
            data = bound_args.arguments.get('data', {})
            if data:
                validated_data = model(**data)
                bound_args.arguments['data'] = validated_data.dict()

            return await func(*bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator

def log_operation(operation: str) -> Callable:
    """
    Decorator to log database operations.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logging.info(
                    f"{operation} operation completed in {duration:.2f}s: "
                    f"func={func.__name__}, args={args}, kwargs={kwargs}"
                )
                return result
            except Exception as e:
                logging.error(
                    f"{operation} operation failed: func={func.__name__}, "
                    f"error={str(e)}, args={args}, kwargs={kwargs}"
                )
                raise
        return wrapper
    return decorator

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry failed operations with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise

                    logging.warning(
                        f"Operation failed (attempt {attempt}/{max_attempts}): {str(e)}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1

        return wrapper
    return decorator