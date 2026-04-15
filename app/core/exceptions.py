"""
Custom Exceptions Module

Defines application-specific exceptions for better error handling.
"""


class JobBotException(Exception):
    """Base exception for Job Bot application."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(JobBotException):
    """Exception raised for validation errors."""

    pass


class NotFoundException(JobBotException):
    """Exception raised when a resource is not found."""

    pass


class ExternalAPIException(JobBotException):
    """Exception raised when external API calls fail."""

    def __init__(self, message: str, service: str, status_code: int = None, details: dict = None):
        """
        Initialize external API exception.

        Args:
            message: Error message
            service: Name of the external service
            status_code: HTTP status code from external service
            details: Additional error details
        """
        self.service = service
        self.status_code = status_code
        super().__init__(message, details)


class DatabaseException(JobBotException):
    """Exception raised for database-related errors."""

    pass


class ConfigurationException(JobBotException):
    """Exception raised for configuration errors."""

    pass


class AuthenticationException(JobBotException):
    """Exception raised for authentication errors."""

    pass


class AuthorizationException(JobBotException):
    """Exception raised for authorization errors."""

    pass


class RateLimitException(JobBotException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(message)