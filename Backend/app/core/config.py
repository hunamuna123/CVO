"""
Application configuration module.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = Field(default="Real Estate API", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    secret_key: str = Field(description="Application secret key")

    # Database settings
    database_url: PostgresDsn = Field(
        description="PostgreSQL database URL",
        examples=["postgresql://user:pass@localhost:5432/db"],
    )
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Redis settings
    redis_url: RedisDsn = Field(
        description="Redis URL", examples=["redis://localhost:6379/0"]
    )
    redis_password: Optional[str] = Field(default=None, description="Redis password")

    # JWT settings
    jwt_secret_key: str = Field(description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=15, description="Access token expiration (minutes)"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration (days)"
    )

    # SMS service settings
    sms_api_key: str = Field(description="SMS service API key")
    sms_sender: str = Field(default="YourApp", description="SMS sender name")
    sms_provider: str = Field(default="sms_ru", description="SMS provider")

    # File upload settings
    media_url: str = Field(default="/media/", description="Media URL path")
    media_root: str = Field(default="/app/media/", description="Media root directory")
    max_upload_size: int = Field(
        default=52428800, description="Max upload size (bytes)"
    )
    allowed_image_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "webp"], description="Allowed image extensions"
    )
    allowed_document_extensions: List[str] = Field(
        default=["pdf", "doc", "docx"], description="Allowed document extensions"
    )

    # Image processing settings
    image_quality: int = Field(
        default=85, ge=1, le=100, description="Image quality for compression (1-100)"
    )

    # Rate limiting settings
    rate_limit_authenticated: str = Field(
        default="100/minute", description="Rate limit for authenticated users"
    )
    rate_limit_anonymous: str = Field(
        default="20/minute", description="Rate limit for anonymous users"
    )

    # CORS settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins (comma-separated)",
    )
    allowed_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS,PATCH,HEAD,TRACE,CONNECT",
        description="Allowed CORS methods (comma-separated)",
    )
    allowed_headers: str = Field(
        default="*", description="Allowed CORS headers (comma-separated)"
    )

    # Email settings (optional)
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: Optional[int] = Field(default=587, description="SMTP port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_tls: bool = Field(default=True, description="SMTP TLS enabled")

    # Celery settings
    celery_broker_url: Optional[str] = Field(
        default=None, description="Celery broker URL"
    )
    celery_result_backend: Optional[str] = Field(
        default=None, description="Celery result backend URL"
    )

    # Monitoring and logging
    log_level: str = Field(default="INFO", description="Logging level")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")

    # External APIs
    maps_api_key: Optional[str] = Field(default=None, description="Maps API key")
    weather_api_key: Optional[str] = Field(default=None, description="Weather API key")

    # Performance settings
    cache_ttl: int = Field(default=300, description="Cache TTL (seconds)")
    query_cache_ttl: int = Field(default=60, description="Query cache TTL (seconds)")

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        """Assemble database URL."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=v.get("user"),
            password=v.get("password"),
            host=v.get("host"),
            port=v.get("port"),
            path=v.get("path"),
        )

    @field_validator("redis_url", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str]) -> Any:
        """Assemble Redis URL."""
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=v.get("host"),
            port=v.get("port"),
            path=v.get("path"),
        )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> str:
        """Assemble CORS origins."""
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        return "*"

    @field_validator("allowed_methods", mode="before")
    @classmethod
    def assemble_cors_methods(cls, v: Union[str, List[str]]) -> str:
        """Assemble CORS methods."""
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        return "GET,POST,PUT,DELETE,OPTIONS"

    @field_validator("allowed_image_extensions", mode="before")
    @classmethod
    def assemble_image_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        """Assemble image extensions."""
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["jpg", "jpeg", "png", "webp"]  # Default values

    @field_validator("allowed_document_extensions", mode="before")
    @classmethod
    def assemble_document_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        """Assemble document extensions."""
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["pdf", "doc", "docx"]  # Default values

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment.lower() == "testing"

    def get_database_url(self) -> str:
        """Get database URL as string."""
        return str(self.database_url)

    def get_redis_url(self) -> str:
        """Get Redis URL as string."""
        return str(self.redis_url)


class TestSettings(Settings):
    """
    Test-specific settings configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = "testing"
    debug: bool = True

    # Use test databases
    database_url: PostgresDsn = Field(
        default="postgresql://postgres:password@localhost:5432/realestate_test"
    )
    redis_url: RedisDsn = Field(default="redis://localhost:6379/15")


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    """
    # Check if we're in test environment
    if os.getenv("TESTING") == "true":
        return TestSettings()

    return Settings()


# Export commonly used settings - removed to avoid import time loading
# Use get_settings() function instead
