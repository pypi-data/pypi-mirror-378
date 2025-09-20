from typing import Any, Dict, Optional
from functools import wraps

class AccessNodeError(Exception):
    """Base exception for AccessNode."""
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class DatabaseError(AccessNodeError):
    """Database-related errors."""
    pass

class ValidationError(AccessNodeError):
    """Data validation errors."""
    pass

class SchemaError(AccessNodeError):
    """Schema-related errors."""
    pass

class CacheError(AccessNodeError):
    """Cache-related errors."""
    pass

class ConfigurationError(AccessNodeError):
    """Configuration-related errors."""
    pass

class AuthenticationError(AccessNodeError):
    """Authentication-related errors."""
    pass

class AuthorizationError(AccessNodeError):
    """Authorization-related errors."""
    pass

class QueryError(AccessNodeError):
    """Query-related errors."""
    pass

class ConnectionError(AccessNodeError):
    """Connection-related errors."""
    pass

class MigrationError(AccessNodeError):
    """Migration-related errors."""
    pass

class EncryptionError(AccessNodeError):
    """Encryption-related errors."""
    pass

def handle_exception(exc: Exception) -> AccessNodeError:
    """Convert various exceptions to AccessNode exceptions."""
    if isinstance(exc, AccessNodeError):
        return exc
        
    # Map common database exceptions
    if isinstance(exc, (
        ImportError,
        ModuleNotFoundError,
        ConnectionRefusedError,
        TimeoutError
    )):
        return ConnectionError(
            message=f"Database connection failed: {str(exc)}",
            code="DB_CONNECTION_ERROR"
        )
        
    # Map validation exceptions
    if isinstance(exc, (ValueError, TypeError, AttributeError)):
        return ValidationError(
            message=f"Validation failed: {str(exc)}",
            code="VALIDATION_ERROR"
        )
        
    # Default to generic error
    return AccessNodeError(
        message=f"An unexpected error occurred: {str(exc)}",
        code="INTERNAL_ERROR",
        details={"original_error": str(exc)}
    )

def safe_db_operation(func):
    """Decorator for safely handling database operations"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            raise AccessNodeError(f"Database operation failed: {str(e)}") from e
    return wrapper