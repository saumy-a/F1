"""
Configuration management using Pydantic Settings.
All configuration values are loaded from environment variables.
"""
import logging
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "F1 Dashboard API"
    APP_VERSION: str = "2.0"
    DEBUG: bool = False
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]
    
    # External APIs
    JOLPICA_BASE_URL: str = "https://ergast.com/api/f1"
    OPENF1_BASE_URL: str = "https://api.openf1.org/v1"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Configure logging with request ID support
class RequestIDFilter(logging.Filter):
    """Add default request_id for logs outside request context."""
    
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'system'
        return True


def configure_logging():
    """Configure application logging with request ID support."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add request ID filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(RequestIDFilter())
