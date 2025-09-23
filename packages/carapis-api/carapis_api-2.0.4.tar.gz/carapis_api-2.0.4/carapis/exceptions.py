"""
Exception classes for the Vehicles API client
"""

from typing import Optional, Dict, Any


class VehiclesAPIError(Exception):
    """Base exception for all Vehicles API errors"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        self.response_data = response_data
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(VehiclesAPIError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", status_code: Optional[int] = None):
        super().__init__(message, status_code=status_code or 401, error_type="authentication_error")


class AuthorizationError(VehiclesAPIError):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_type="authorization_error")


class NotFoundError(VehiclesAPIError):
    """Raised when resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_type="not_found_error")


class ValidationError(VehiclesAPIError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str = "Invalid parameters", details: Optional[Dict[str, Any]] = None, field_errors: Optional[Dict[str, str]] = None, status_code: Optional[int] = None):
        super().__init__(message, status_code=status_code or 400, error_type="validation_error", details=details)
        self.field_errors = field_errors or {}


class RateLimitError(VehiclesAPIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, error_type="rate_limit_error")


class ServerError(VehiclesAPIError):
    """Raised when server returns 5xx error"""
    
    def __init__(self, message: str = "Internal server error", status_code: int = 500):
        super().__init__(message, status_code=status_code, error_type="server_error")


class NetworkError(VehiclesAPIError):
    """Raised when network error occurs"""
    
    def __init__(self, message: str = "Network error occurred", original_exception: Optional[Exception] = None):
        super().__init__(message, error_type="network_error")
        self.original_exception = original_exception


class TimeoutError(VehiclesAPIError):
    """Raised when request times out"""
    
    def __init__(self, message: str = "Request timed out", timeout: Optional[float] = None):
        super().__init__(message, error_type="timeout_error")
        self.timeout = timeout


def handle_api_error(status_code: int, response_data: Any) -> VehiclesAPIError:
    """Convert HTTP status code and response to appropriate exception"""
    
    if isinstance(response_data, dict):
        message = response_data.get("message") or response_data.get("detail") or "API error"
        details = response_data.get("details") or response_data
    else:
        message = str(response_data) if response_data else "Unknown API error"
        details = {}
    
    if status_code == 401:
        return AuthenticationError(message)
    elif status_code == 403:
        return AuthorizationError(message)
    elif status_code == 404:
        return NotFoundError(message)
    elif status_code == 400:
        return ValidationError(message, details)
    elif status_code == 429:
        return RateLimitError(message)
    elif 500 <= status_code < 600:
        return ServerError(message, status_code)
    else:
        return VehiclesAPIError(message, status_code, "api_error", details)
