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
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

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