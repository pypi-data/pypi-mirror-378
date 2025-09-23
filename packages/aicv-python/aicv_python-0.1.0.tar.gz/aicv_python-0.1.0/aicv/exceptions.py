"""
AiCV Python SDK Exceptions

Custom exceptions for the AiCV SDK.
"""


class AiCVError(Exception):
    """Base exception for AiCV SDK errors."""
    pass


class AuthenticationError(AiCVError):
    """Raised when authentication fails."""
    pass


class APIError(AiCVError):
    """Raised when API returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(AiCVError):
    """Raised when input validation fails."""
    pass


class RateLimitError(AiCVError):
    """Raised when rate limit is exceeded."""
    pass


class NetworkError(AiCVError):
    """Raised when network-related errors occur."""
    pass
