"""
Application Settings Configuration

Centralized configuration management using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="JobBot", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/database/job_bot.db",
        description="Database connection URL (SQLite for development)"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # PostgreSQL Configuration
    # All credentials loaded from environment variables for security
    postgres_host: str = Field(default="localhost", description="PostgreSQL server hostname")
    postgres_port: int = Field(default=5432, description="PostgreSQL server port")
    postgres_user: str = Field(default="jobbot", description="PostgreSQL username")
    postgres_password: str = Field(default="", description="PostgreSQL password (REQUIRED for production)")
    postgres_database: str = Field(default="jobbot", description="PostgreSQL database name")

    # PostgreSQL SSL Configuration
    postgres_ssl_mode: str = Field(default="prefer", description="SSL mode for PostgreSQL connection")
    postgres_ssl_cert: str = Field(default="", description="Path to SSL client certificate")
    postgres_ssl_key: str = Field(default="", description="Path to SSL client key")
    postgres_ssl_root_cert: str = Field(default="", description="Path to SSL root certificate")

    # PostgreSQL Connection Pooling
    postgres_pool_size: int = Field(default=20, description="Connection pool size")
    postgres_max_overflow: int = Field(default=30, description="Max overflow connections")
    postgres_pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    postgres_pool_recycle: int = Field(default=3600, description="Recycle connections after N seconds")
    postgres_pool_pre_ping: bool = Field(default=True, description="Test connections before use")

    # PostgreSQL Timeouts
    postgres_connect_timeout: int = Field(default=10, description="Connection timeout in seconds")
    postgres_statement_timeout: int = Field(default=30000, description="Statement timeout in milliseconds")

    # Security
    secret_key: str = Field(default="change-me-in-production", description="Secret key for JWT")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )

    # Google Sheets
    google_sheets_credentials_path: str = Field(
        default="config/credentials.json",
        description="Path to Google Sheets credentials"
    )
    google_sheets_spreadsheet_id: str = Field(default="", description="Google Sheets spreadsheet ID")
    google_sheets_token_path: str = Field(
        default="config/token.json",
        description="Path to Google Sheets token"
    )

    # ATS APIs
    greenhouse_api_key: str = Field(default="", description="Greenhouse API key")
    greenhouse_api_version: str = Field(default="v1", description="Greenhouse API version")
    lever_api_key: str = Field(default="", description="Lever API key")
    ashby_api_key: str = Field(default="", description="Ashby API key")

    # LLM
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    llm_provider: str = Field(default="anthropic", description="LLM provider")
    llm_model: str = Field(default="claude-3-sonnet-20240229", description="LLM model")

    # Playwright
    playwright_headless: bool = Field(default=True, description="Run Playwright in headless mode")
    playwright_timeout: int = Field(default=30000, description="Playwright timeout in ms")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="logs/job_bot.log", description="Log file path")

    # Cache
    cache_ttl: int = Field(default=3600, description="Cache time-to-live in seconds")
    enable_cache: bool = Field(default=True, description="Enable caching")

    # Job Fetching
    fetch_interval_hours: int = Field(default=6, description="Job fetch interval in hours")
    max_jobs_per_source: int = Field(default=100, description="Maximum jobs per source")
    fetch_timeout_seconds: int = Field(default=30, description="Timeout for fetch requests")
    fetch_max_retries: int = Field(default=3, description="Max retries for failed requests")
    deduplication_enabled: bool = Field(default=True, description="Enable/disable deduplication")
    deduplication_window_days: int = Field(default=30, description="Time window for duplicate detection")

    # User Preferences
    default_location: str = Field(default="New York", description="Default location")
    default_remote: bool = Field(default=True, description="Default remote preference")
    target_roles: str = Field(
        default="backend,infrastructure,platform,ml_infra",
        description="Target role types"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests")
    rate_limit_period: int = Field(default=60, description="Rate limit period in seconds")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()