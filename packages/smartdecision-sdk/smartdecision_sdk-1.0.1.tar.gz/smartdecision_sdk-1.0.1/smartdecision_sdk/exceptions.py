"""
Exception classes for the SmartDecision SDK.

This module contains custom exception classes for different types of errors
that can occur when using the SmartDecision API.
"""

from typing import Optional, Dict, Any


class SmartDecisionError(Exception):
    """Base exception class for all SmartDecision SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(SmartDecisionError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed. Please check your API key.", status_code: Optional[int] = 401, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response_data)


class APIError(SmartDecisionError):
    """Raised when the API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response_data)


class ValidationError(SmartDecisionError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str = "Request validation failed.", status_code: Optional[int] = 400, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response_data)


class RateLimitError(SmartDecisionError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", status_code: Optional[int] = 429, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response_data)


class ConnectionError(SmartDecisionError):
    """Raised when connection to the API fails."""
    
    def __init__(self, message: str = "Failed to connect to the API. Please check your internet connection.", status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response_data)
