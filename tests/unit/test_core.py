"""
Unit Tests for Core Modules

Tests the core functionality including config, logging, security, and exceptions.
"""

import pytest
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import (
    JobBotException,
    ValidationException,
    NotFoundException,
    ExternalAPIException,
    DatabaseException,
    ConfigurationException,
    AuthenticationException,
    AuthorizationException,
    RateLimitException,
)


class TestConfig:
    """Tests for configuration module."""

    def test_settings_has_required_fields(self):
        """Test that settings has required configuration fields."""
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "environment")
        assert hasattr(settings, "database_url")

    def test_settings_environment(self):
        """Test environment setting."""
        assert settings.environment in ["development", "testing", "production"]


class TestSecurity:
    """Tests for security module."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2


class TestExceptions:
    """Tests for custom exceptions."""

    def test_job_bot_exception(self):
        """Test base JobBotException."""
        exc = JobBotException("Test error")

        assert exc.message == "Test error"
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_job_bot_exception_with_details(self):
        """Test JobBotException with details."""
        details = {"field": "value"}
        exc = JobBotException("Test error", details)

        assert exc.message == "Test error"
        assert exc.details == details

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Validation failed")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Validation failed"

    def test_not_found_exception(self):
        """Test NotFoundException."""
        exc = NotFoundException("Resource not found")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Resource not found"

    def test_external_api_exception(self):
        """Test ExternalAPIException."""
        exc = ExternalAPIException(
            "API call failed",
            service="GitHub",
            status_code=500,
            details={"error": "Internal server error"}
        )

        assert isinstance(exc, JobBotException)
        assert exc.service == "GitHub"
        assert exc.status_code == 500
        assert exc.details == {"error": "Internal server error"}

    def test_database_exception(self):
        """Test DatabaseException."""
        exc = DatabaseException("Database error")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Database error"

    def test_configuration_exception(self):
        """Test ConfigurationException."""
        exc = ConfigurationException("Configuration error")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Configuration error"

    def test_authentication_exception(self):
        """Test AuthenticationException."""
        exc = AuthenticationException("Authentication failed")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Authentication failed"

    def test_authorization_exception(self):
        """Test AuthorizationException."""
        exc = AuthorizationException("Authorization failed")

        assert isinstance(exc, JobBotException)
        assert exc.message == "Authorization failed"

    def test_rate_limit_exception(self):
        """Test RateLimitException."""
        exc = RateLimitException("Rate limit exceeded", retry_after=60)

        assert isinstance(exc, JobBotException)
        assert exc.message == "Rate limit exceeded"
        assert exc.retry_after == 60

    def test_rate_limit_exception_defaults(self):
        """Test RateLimitException with default values."""
        exc = RateLimitException()

        assert exc.message == "Rate limit exceeded"
        assert exc.retry_after is None
