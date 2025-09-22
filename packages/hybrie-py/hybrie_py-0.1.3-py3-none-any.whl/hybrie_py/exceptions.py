"""
HybrIE Python SDK Exceptions

Custom exception classes for error handling.
"""


class HybrieError(Exception):
    """Base exception for all HybrIE SDK errors."""
    
    def __init__(self, message: str, code: str = None, details: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class ConnectionError(HybrieError):
    """Raised when connection to HybrIE server fails."""
    pass


class ModelNotFoundError(HybrieError):
    """Raised when requested model is not found or not loaded."""
    pass


class GenerationError(HybrieError):
    """Raised when image generation fails."""
    pass


class ValidationError(HybrieError):
    """Raised when request parameters are invalid."""
    pass


class ServerError(HybrieError):
    """Raised when server encounters an internal error."""
    pass


class TimeoutError(HybrieError):
    """Raised when request times out."""
    pass