"""
Fetcher Utilities Module

Provides shared utilities for job fetchers including retry logic,
response validation, and error handling.
"""

import asyncio
import time
from typing import Callable, Any, Optional
from app.core.logging import get_logger
from app.core.exceptions import ExternalAPIException, RateLimitException

logger = get_logger(__name__)


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
) -> Any:
    """
    Execute a function with exponential backoff retry logic.

    Args:
        func: Async function to execute
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_multiplier: Multiplier for exponential backoff
        retryable_exceptions: Tuple of exceptions that trigger retry

    Returns:
        Result of the function execution

    Raises:
        Exception: The last exception if all retries are exhausted
    """
    last_exception = None
    current_backoff = initial_backoff

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(f"Max retries ({max_retries}) exhausted for {func.__name__}")
                raise

            backoff_time = min(current_backoff, max_backoff)
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}. "
                f"Retrying in {backoff_time:.2f}s. Error: {str(e)}"
            )

            await asyncio.sleep(backoff_time)
            current_backoff *= backoff_multiplier

    raise last_exception


def validate_response_structure(
    data: dict,
    required_fields: list,
    optional_fields: list = None,
) -> bool:
    """
    Validate API response structure.

    Args:
        data: Response data to validate
        required_fields: List of required field names
        optional_fields: List of optional field names

    Returns:
        True if validation passes, False otherwise
    """
    if not isinstance(data, dict):
        logger.error("Response data is not a dictionary")
        return False

    missing_required = [field for field in required_fields if field not in data]
    if missing_required:
        logger.error(f"Missing required fields: {missing_required}")
        return False

    if optional_fields:
        missing_optional = [field for field in optional_fields if field not in data]
        if missing_optional:
            logger.warning(f"Missing optional fields: {missing_optional}")

    return True


def handle_rate_limit_response(
    status_code: int,
    headers: dict,
    service: str,
) -> Optional[RateLimitException]:
    """
    Check if response indicates rate limiting and raise appropriate exception.

    Args:
        status_code: HTTP status code
        headers: Response headers
        service: Service name for error message

    Returns:
        RateLimitException if rate limited, None otherwise

    Raises:
        RateLimitException: If rate limit is detected
    """
    if status_code == 429:
        retry_after = None

        if "Retry-After" in headers:
            try:
                retry_after = int(headers["Retry-After"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid Retry-After header: {headers['Retry-After']}")

        logger.warning(f"Rate limit exceeded for {service}. Retry after: {retry_after}s")
        return RateLimitException(
            f"Rate limit exceeded for {service}",
            retry_after=retry_after
        )

    return None


def extract_company_name_from_url(url: str) -> Optional[str]:
    """
    Extract company name from careers URL.

    Args:
        url: Careers page URL

    Returns:
        Company name if found, None otherwise
    """
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        parts = parsed.netloc.split(".")

        # Handle different URL formats:
        # - example.com -> example
        # - jobs.example.com -> example
        # - www.example.com -> example
        if len(parts) >= 2:
            # Remove common prefixes and suffixes
            if parts[0] in ["www", "jobs", "careers"]:
                if len(parts) >= 3:
                    return parts[1]
            # Get the second-to-last part (domain name)
            return parts[-2] if len(parts) >= 2 else parts[0]

        return None
    except Exception:
        logger.warning(f"Failed to extract company name from URL: {url}")
        return None


def sanitize_job_data(job_data: dict) -> dict:
    """
    Sanitize job data by removing None values and trimming strings.

    Args:
        job_data: Raw job data

    Returns:
        Sanitized job data
    """
    sanitized = {}

    for key, value in job_data.items():
        if value is None:
            continue

        if isinstance(value, str):
            sanitized[key] = value.strip()
        elif isinstance(value, (list, dict)):
            sanitized[key] = value
        else:
            sanitized[key] = value

    return sanitized


def calculate_fetch_priority(
    company_priority: int,
    freshness_hours: int,
    location_match: bool = False,
) -> float:
    """
    Calculate fetch priority score for a job.

    Args:
        company_priority: Company priority (1-5)
        freshness_hours: Hours since job was posted
        location_match: Whether location matches preferences

    Returns:
        Priority score (higher is better)
    """
    base_score = company_priority * 10

    freshness_score = max(0, 10 - (freshness_hours / 24))
    location_bonus = 5 if location_match else 0

    total_score = base_score + freshness_score + location_bonus

    return round(total_score, 2)
