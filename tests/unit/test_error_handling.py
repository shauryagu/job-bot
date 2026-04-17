"""
Unit Tests for Error Handling

Tests error handling utilities and exception classes.
"""

import pytest
import asyncio
from app.core.exceptions import (
    JobBotException,
    ValidationException,
    NotFoundException,
    ExternalAPIException,
    DatabaseException,
    ConfigurationException,
    AuthenticationException,
    AuthorizationException,
    RateLimitException
)
from app.services.fetchers.utils import (
    retry_with_backoff,
    validate_response_structure,
    handle_rate_limit_response,
    extract_company_name_from_url,
    sanitize_job_data,
    calculate_fetch_priority
)


class TestExceptions:
    """Tests for custom exception classes."""

    def test_job_bot_exception(self):
        """Test base JobBotException."""
        exc = JobBotException("Test error", {"key": "value"})

        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.details == {"key": "value"}

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid input")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Invalid input"

    def test_not_found_exception(self):
        """Test NotFoundException."""
        exc = NotFoundException("Resource not found")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Resource not found"

    def test_external_api_exception(self):
        """Test ExternalAPIException."""
        exc = ExternalAPIException(
            "API error",
            service="test_service",
            status_code=500,
            details={"error": "Internal server error"}
        )

        assert isinstance(exc, JobBotException)
        assert exc.service == "test_service"
        assert exc.status_code == 500
        assert exc.details == {"error": "Internal server error"}

    def test_database_exception(self):
        """Test DatabaseException."""
        exc = DatabaseException("Database error")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Database error"

    def test_configuration_exception(self):
        """Test ConfigurationException."""
        exc = ConfigurationException("Config error")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Config error"

    def test_authentication_exception(self):
        """Test AuthenticationException."""
        exc = AuthenticationException("Auth error")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Auth error"

    def test_authorization_exception(self):
        """Test AuthorizationException."""
        exc = AuthorizationException("Authz error")

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Authz error"

    def test_rate_limit_exception(self):
        """Test RateLimitException."""
        exc = RateLimitException("Rate limit exceeded", retry_after=60)

        assert isinstance(exc, JobBotException)
        assert str(exc) == "Rate limit exceeded"
        assert exc.retry_after == 60

    def test_rate_limit_exception_default_retry_after(self):
        """Test RateLimitException with default retry_after."""
        exc = RateLimitException()

        assert exc.retry_after is None


class TestRetryWithBackoff:
    """Tests for retry_with_backoff function."""

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self):
        """Test successful execution without retries."""
        call_count = 0

        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_with_backoff(test_func, max_retries=3)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_with_backoff_max_retries(self):
        """Test that max retries are respected."""
        call_count = 0

        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await retry_with_backoff(test_func, max_retries=2)

        assert call_count == 3  # Initial attempt + 2 retries

    @pytest.mark.asyncio
    async def test_retry_with_backoff_specific_exception(self):
        """Test retrying only for specific exceptions."""
        call_count = 0

        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"

        result = await retry_with_backoff(
            test_func,
            max_retries=3,
            retryable_exceptions=(ValueError,)
        )

        assert result == "success"
        assert call_count == 2


class TestValidateResponseStructure:
    """Tests for validate_response_structure function."""

    def test_validate_response_structure_valid(self):
        """Test validation of valid response."""
        data = {
            "id": 123,
            "title": "Test Job",
            "description": "Test description"
        }

        result = validate_response_structure(
            data,
            required_fields=["id", "title"],
            optional_fields=["description"]
        )

        assert result is True

    def test_validate_response_structure_missing_required(self):
        """Test validation with missing required fields."""
        data = {
            "id": 123
        }

        result = validate_response_structure(
            data,
            required_fields=["id", "title"]
        )

        assert result is False

    def test_validate_response_structure_missing_optional(self):
        """Test validation with missing optional fields."""
        data = {
            "id": 123,
            "title": "Test Job"
        }

        result = validate_response_structure(
            data,
            required_fields=["id"],
            optional_fields=["description"]
        )

        assert result is True  # Should still pass with missing optional fields

    def test_validate_response_structure_invalid_type(self):
        """Test validation with invalid data type."""
        data = "not a dict"

        result = validate_response_structure(
            data,
            required_fields=["id"]
        )

        assert result is False


class TestHandleRateLimitResponse:
    """Tests for handle_rate_limit_response function."""

    def test_handle_rate_limit_response_429(self):
        """Test handling of 429 rate limit response."""
        headers = {"Retry-After": "60"}

        exc = handle_rate_limit_response(429, headers, "test_service")

        assert isinstance(exc, RateLimitException)
        assert exc.retry_after == 60

    def test_handle_rate_limit_response_429_no_retry_after(self):
        """Test handling of 429 response without Retry-After header."""
        headers = {}

        exc = handle_rate_limit_response(429, headers, "test_service")

        assert isinstance(exc, RateLimitException)
        assert exc.retry_after is None

    def test_handle_rate_limit_response_not_rate_limited(self):
        """Test handling of non-rate-limited response."""
        headers = {}

        exc = handle_rate_limit_response(200, headers, "test_service")

        assert exc is None


class TestExtractCompanyNameFromUrl:
    """Tests for extract_company_name_from_url function."""

    def test_extract_company_name_from_url_valid(self):
        """Test extracting company name from valid URL."""
        url = "https://example.com/careers"

        company = extract_company_name_from_url(url)

        assert company == "example"

    def test_extract_company_name_from_url_subdomain(self):
        """Test extracting company name from subdomain URL."""
        url = "https://jobs.example.com/careers"

        company = extract_company_name_from_url(url)

        assert company == "example"

    def test_extract_company_name_from_url_invalid(self):
        """Test extracting company name from invalid URL."""
        url = "not-a-url"

        company = extract_company_name_from_url(url)

        assert company is None


class TestSanitizeJobData:
    """Tests for sanitize_job_data function."""

    def test_sanitize_job_data_removes_none(self):
        """Test that None values are removed."""
        data = {
            "title": "Software Engineer",
            "description": None,
            "location": "New York"
        }

        sanitized = sanitize_job_data(data)

        assert "title" in sanitized
        assert "description" not in sanitized
        assert "location" in sanitized

    def test_sanitize_job_data_trims_strings(self):
        """Test that strings are trimmed."""
        data = {
            "title": "  Software Engineer  ",
            "location": "  New York  "
        }

        sanitized = sanitize_job_data(data)

        assert sanitized["title"] == "Software Engineer"
        assert sanitized["location"] == "New York"

    def test_sanitize_job_data_preserves_lists(self):
        """Test that lists are preserved."""
        data = {
            "title": "Software Engineer",
            "skills": ["Python", "JavaScript"]
        }

        sanitized = sanitize_job_data(data)

        assert sanitized["skills"] == ["Python", "JavaScript"]

    def test_sanitize_job_data_preserves_dicts(self):
        """Test that dicts are preserved."""
        data = {
            "title": "Software Engineer",
            "metadata": {"key": "value"}
        }

        sanitized = sanitize_job_data(data)

        assert sanitized["metadata"] == {"key": "value"}


class TestCalculateFetchPriority:
    """Tests for calculate_fetch_priority function."""

    def test_calculate_fetch_priority_high_priority(self):
        """Test priority calculation for high priority company."""
        priority = calculate_fetch_priority(
            company_priority=5,
            freshness_hours=1,
            location_match=True
        )

        assert priority > 50  # Should be high

    def test_calculate_fetch_priority_low_priority(self):
        """Test priority calculation for low priority company."""
        priority = calculate_fetch_priority(
            company_priority=1,
            freshness_hours=100,
            location_match=False
        )

        assert priority < 20  # Should be low

    def test_calculate_fetch_priority_location_bonus(self):
        """Test that location match adds bonus."""
        priority_with_match = calculate_fetch_priority(
            company_priority=3,
            freshness_hours=10,
            location_match=True
        )

        priority_without_match = calculate_fetch_priority(
            company_priority=3,
            freshness_hours=10,
            location_match=False
        )

        assert priority_with_match > priority_without_match

    def test_calculate_fetch_priority_freshness(self):
        """Test that freshness affects priority."""
        priority_fresh = calculate_fetch_priority(
            company_priority=3,
            freshness_hours=1,
            location_match=False
        )

        priority_old = calculate_fetch_priority(
            company_priority=3,
            freshness_hours=100,
            location_match=False
        )

        assert priority_fresh > priority_old
