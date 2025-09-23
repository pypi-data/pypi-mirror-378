"""
Utility functions for the SmartDecision SDK.

This module contains helper functions and utilities used throughout the SDK.
"""

import os
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse


def get_api_key_from_env() -> Optional[str]:
    """
    Get the API key from environment variables.
    
    Checks for the following environment variables in order:
    - SMARTDECISION_API_KEY
    - SMARTDECISION_SDK_API_KEY
    - SD_API_KEY
    
    Returns:
        API key if found, None otherwise
    """
    env_vars = [
        "SMARTDECISION_API_KEY",
        "SMARTDECISION_SDK_API_KEY", 
        "SD_API_KEY"
    ]
    
    for env_var in env_vars:
        api_key = os.getenv(env_var)
        if api_key and api_key.strip():
            return api_key.strip()
    
    return None


def validate_api_key(api_key: str) -> bool:
    """
    Validate the format of an API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the API key format is valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    api_key = api_key.strip()
    if not api_key:
        return False
    
    # Basic format validation - should start with smartdec-api- and contain alphanumeric characters
    pattern = r'^smartdec-api-[a-zA-Z0-9]+-[a-zA-Z0-9]+$'
    return bool(re.match(pattern, api_key))


def validate_base_url(base_url: str) -> bool:
    """
    Validate the format of a base URL.
    
    Args:
        base_url: The base URL to validate
        
    Returns:
        True if the URL format is valid, False otherwise
    """
    if not base_url or not isinstance(base_url, str):
        return False
    
    try:
        parsed = urlparse(base_url.strip())
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def clean_categories(categories: List[str]) -> List[str]:
    """
    Clean and validate a list of categories.
    
    Args:
        categories: List of category strings
        
    Returns:
        Cleaned list of unique, non-empty categories
        
    Raises:
        ValueError: If insufficient valid categories remain after cleaning
    """
    if not categories or not isinstance(categories, list):
        raise ValueError("Categories must be a non-empty list")
    
    # Remove duplicates and empty strings, strip whitespace
    cleaned = list(dict.fromkeys([
        cat.strip() for cat in categories 
        if cat and isinstance(cat, str) and cat.strip()
    ]))
    
    if len(cleaned) < 2:
        raise ValueError("At least 2 unique, non-empty categories are required")
    
    return cleaned


def format_confidence(confidence: float, decimal_places: int = 2) -> str:
    """
    Format a confidence score as a percentage string.
    
    Args:
        confidence: Confidence score (0.0 to 1.0)
        decimal_places: Number of decimal places to show
        
    Returns:
        Formatted percentage string
    """
    if not isinstance(confidence, (int, float)):
        return "0.00%"
    
    # Clamp to valid range
    confidence = max(0.0, min(1.0, float(confidence)))
    
    percentage = confidence * 100
    return f"{percentage:.{decimal_places}f}%"


def format_response_time(seconds: float, decimal_places: int = 2) -> str:
    """
    Format a response time in a human-readable format.
    
    Args:
        seconds: Response time in seconds
        decimal_places: Number of decimal places to show
        
    Returns:
        Formatted time string
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "0.00s"
    
    if seconds < 1:
        # Show in milliseconds for very fast responses
        ms = seconds * 1000
        return f"{ms:.0f}ms"
    else:
        # Show in seconds with decimal places
        return f"{seconds:.{decimal_places}f}s"


def create_user_agent(package_name: str = "smartdecision-sdk", version: str = "1.0.0") -> str:
    """
    Create a user agent string for HTTP requests.
    
    Args:
        package_name: Name of the package
        version: Version of the package
        
    Returns:
        User agent string
    """
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return f"{package_name}/{version} (Python {python_version})"


def merge_headers(default_headers: Dict[str, str], custom_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge default headers with custom headers.
    
    Args:
        default_headers: Default headers dictionary
        custom_headers: Optional custom headers dictionary
        
    Returns:
        Merged headers dictionary
    """
    if not custom_headers:
        return default_headers.copy()
    
    merged = default_headers.copy()
    merged.update(custom_headers)
    return merged


def extract_error_message(error_data: Dict[str, Any]) -> str:
    """
    Extract error message from API error response data.
    
    Args:
        error_data: Error response data dictionary
        
    Returns:
        Extracted error message
    """
    if not isinstance(error_data, dict):
        return "Unknown error occurred"
    
    # Try common error message fields
    message_fields = ["detail", "message", "error", "error_message", "description"]
    
    for field in message_fields:
        if field in error_data and error_data[field]:
            return str(error_data[field])
    
    # Fallback to first string value
    for key, value in error_data.items():
        if isinstance(value, str) and value.strip():
            return value
    
    return "Unknown error occurred"


def is_retryable_status_code(status_code: int) -> bool:
    """
    Check if an HTTP status code indicates a retryable error.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if the error is retryable, False otherwise
    """
    retryable_codes = {
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }
    
    return status_code in retryable_codes


def calculate_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay for retries.
    
    Args:
        attempt: Attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Calculated delay in seconds
    """
    if attempt < 0:
        attempt = 0
    
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def sanitize_log_data(data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitize data for logging by masking sensitive information.
    
    Args:
        data: Data dictionary to sanitize
        sensitive_keys: List of keys to mask (defaults to common sensitive keys)
        
    Returns:
        Sanitized data dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = [
            "api_key", "password", "token", "secret", "key",
            "authorization", "auth", "credential"
        ]
    
    sanitized = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if this key should be masked
        should_mask = any(sensitive in key_lower for sensitive in sensitive_keys)
        
        if should_mask and isinstance(value, str) and len(value) > 8:
            # Mask the value, keeping first 4 and last 4 characters
            masked_value = f"{value[:4]}...{value[-4:]}"
            sanitized[key] = masked_value
        else:
            sanitized[key] = value
    
    return sanitized


class RateLimiter:
    """
    Simple rate limiter for tracking request rates.
    """
    
    def __init__(self, max_requests: int = 100, time_window: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """
        Check if a request is allowed based on current rate.
        
        Returns:
            True if request is allowed, False otherwise
        """
        import time
        
        current_time = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Check if we're under the limit
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a request timestamp."""
        import time
        self.requests.append(time.time())
    
    def reset(self):
        """Reset the rate limiter."""
        self.requests.clear()
