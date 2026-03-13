"""ApiTwitter SDK exceptions."""


class ApiTwitterError(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str, status_code: int = 0, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(ApiTwitterError):
    """Raised when the API key is invalid or missing."""


class InsufficientCreditsError(ApiTwitterError):
    """Raised when the user doesn't have enough credits."""


class RateLimitError(ApiTwitterError):
    """Raised when the rate limit is exceeded."""

    def __init__(self, message: str, retry_after: float = 0, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class NotFoundError(ApiTwitterError):
    """Raised when a resource is not found."""


class ValidationError(ApiTwitterError):
    """Raised when request parameters are invalid."""
