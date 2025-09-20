from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, RedisDsn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseSettings(BaseSettings):
    TYPE: str = "postgresql"
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "postgres"
    PASSWORD: str
    NAME: str
    MIN_CONNECTIONS: int = 1
    MAX_CONNECTIONS: int = 10
    SSL_MODE: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Generate database URL."""
        return PostgresDsn.build(
            scheme=self.TYPE,
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            path=f"/{self.NAME}"
        )

class CacheSettings(BaseSettings):
    ENABLED: bool = True
    TYPE: str = "redis"
    HOST: str = "localhost"
    PORT: int = 6379
    PASSWORD: Optional[str] = None
    DB: int = 0
    TTL: int = 3600
    
    @property
    def url(self) -> str:
        """Generate cache URL."""
        return RedisDsn.build(
            scheme=self.TYPE,
            host=self.HOST,
            port=self.PORT,
            password=self.PASSWORD,
            path=f"/{self.DB}"
        )

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AccessNode"
    DEBUG: bool = False
    SECRET_KEY: str
    API_VERSION: str = "v1"
    
    # Database settings
    DB: DatabaseSettings = DatabaseSettings()
    
    # Cache settings
    CACHE: CacheSettings = CacheSettings()
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Schema settings
    SCHEMA_AUTO_UPDATE: bool = True
    SCHEMA_BACKUP: bool = True
    
    # Query settings
    MAX_QUERY_DEPTH: int = 3
    QUERY_TIMEOUT: int = 30
    
    # Security settings
    ENABLE_FIELD_ENCRYPTION: bool = False
    ENCRYPTION_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings

def update_settings(**kwargs: Dict[str, Any]) -> None:
    """Update settings dynamically."""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

def init_logging() -> None:
    """Initialize logging configuration."""
    import logging
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT
    )

def validate_settings() -> None:
    """Validate critical settings."""
    if settings.ENABLE_FIELD_ENCRYPTION and not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY must be set when ENABLE_FIELD_ENCRYPTION is True")