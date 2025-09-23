"""
Tests for the SmartDecision SDK exceptions.
"""

import pytest
from smartdecision_sdk.exceptions import (
    SmartDecisionError,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
)


class TestSmartDecisionError:
    """Test cases for SmartDecisionError base class."""
    
    def test_base_error_creation(self):
        """Test creating a base error with message only."""
        error = SmartDecisionError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_data == {}
    
    def test_base_error_creation_with_status_code(self):
        """Test creating a base error with status code."""
        error = SmartDecisionError("Test error message", status_code=500)
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code == 500
        assert error.response_data == {}
    
    def test_base_error_creation_with_response_data(self):
        """Test creating a base error with response data."""
        response_data = {"detail": "Additional error info"}
        error = SmartDecisionError("Test error message", status_code=400, response_data=response_data)
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code == 400
        assert error.response_data == response_data
    
    def test_base_error_inheritance(self):
        """Test that base error is properly inherited."""
        error = SmartDecisionError("Test message")
        assert isinstance(error, Exception)


class TestAuthenticationError:
    """Test cases for AuthenticationError."""
    
    def test_authentication_error_default_message(self):
        """Test authentication error with default message."""
        error = AuthenticationError()
        
        assert error.message == "Authentication failed. Please check your API key."
        assert error.status_code == 401
        assert error.response_data == {}
    
    def test_authentication_error_custom_message(self):
        """Test authentication error with custom message."""
        error = AuthenticationError("Invalid API key provided")
        
        assert error.message == "Invalid API key provided"
        assert error.status_code == 401
        assert error.response_data == {}
    
    def test_authentication_error_with_response_data(self):
        """Test authentication error with response data."""
        response_data = {"error": "invalid_token"}
        error = AuthenticationError("Token expired", response_data=response_data)
        
        assert error.message == "Token expired"
        assert error.status_code == 401
        assert error.response_data == response_data
    
    def test_authentication_error_inheritance(self):
        """Test that authentication error inherits from base."""
        error = AuthenticationError()
        assert isinstance(error, SmartDecisionError)
        assert isinstance(error, Exception)


class TestAPIError:
    """Test cases for APIError."""
    
    def test_api_error_creation(self):
        """Test creating an API error."""
        error = APIError("Server error occurred")
        
        assert error.message == "Server error occurred"
        assert error.status_code is None
        assert error.response_data == {}
    
    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = APIError("Server error occurred", status_code=500)
        
        assert error.message == "Server error occurred"
        assert error.status_code == 500
        assert error.response_data == {}
    
    def test_api_error_with_response_data(self):
        """Test API error with response data."""
        response_data = {"error": "internal_server_error", "trace_id": "abc123"}
        error = APIError("Server error occurred", status_code=500, response_data=response_data)
        
        assert error.message == "Server error occurred"
        assert error.status_code == 500
        assert error.response_data == response_data
    
    def test_api_error_inheritance(self):
        """Test that API error inherits from base."""
        error = APIError("Test message")
        assert isinstance(error, SmartDecisionError)
        assert isinstance(error, Exception)


class TestValidationError:
    """Test cases for ValidationError."""
    
    def test_validation_error_default_message(self):
        """Test validation error with default message."""
        error = ValidationError()
        
        assert error.message == "Request validation failed."
        assert error.status_code == 400
        assert error.response_data == {}
    
    def test_validation_error_custom_message(self):
        """Test validation error with custom message."""
        error = ValidationError("Invalid request parameters")
        
        assert error.message == "Invalid request parameters"
        assert error.status_code == 400
        assert error.response_data == {}
    
    def test_validation_error_with_response_data(self):
        """Test validation error with response data."""
        response_data = {"field_errors": {"prompt": "required"}}
        error = ValidationError("Validation failed", response_data=response_data)
        
        assert error.message == "Validation failed"
        assert error.status_code == 400
        assert error.response_data == response_data
    
    def test_validation_error_inheritance(self):
        """Test that validation error inherits from base."""
        error = ValidationError()
        assert isinstance(error, SmartDecisionError)
        assert isinstance(error, Exception)


class TestRateLimitError:
    """Test cases for RateLimitError."""
    
    def test_rate_limit_error_default_message(self):
        """Test rate limit error with default message."""
        error = RateLimitError()
        
        assert error.message == "Rate limit exceeded. Please try again later."
        assert error.status_code == 429
        assert error.response_data == {}
    
    def test_rate_limit_error_custom_message(self):
        """Test rate limit error with custom message."""
        error = RateLimitError("Too many requests per minute")
        
        assert error.message == "Too many requests per minute"
        assert error.status_code == 429
        assert error.response_data == {}
    
    def test_rate_limit_error_with_response_data(self):
        """Test rate limit error with response data."""
        response_data = {"retry_after": 60, "limit": 100}
        error = RateLimitError("Rate limit exceeded", response_data=response_data)
        
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.response_data == response_data
    
    def test_rate_limit_error_inheritance(self):
        """Test that rate limit error inherits from base."""
        error = RateLimitError()
        assert isinstance(error, SmartDecisionError)
        assert isinstance(error, Exception)


class TestConnectionError:
    """Test cases for ConnectionError."""
    
    def test_connection_error_default_message(self):
        """Test connection error with default message."""
        error = ConnectionError()
        
        assert error.message == "Failed to connect to the API. Please check your internet connection."
        assert error.status_code is None
        assert error.response_data == {}
    
    def test_connection_error_custom_message(self):
        """Test connection error with custom message."""
        error = ConnectionError("Network timeout occurred")
        
        assert error.message == "Network timeout occurred"
        assert error.status_code is None
        assert error.response_data == {}
    
    def test_connection_error_with_status_code(self):
        """Test connection error with status code."""
        error = ConnectionError("Connection refused", status_code=None)
        
        assert error.message == "Connection refused"
        assert error.status_code is None
        assert error.response_data == {}
    
    def test_connection_error_inheritance(self):
        """Test that connection error inherits from base."""
        error = ConnectionError()
        assert isinstance(error, SmartDecisionError)
        assert isinstance(error, Exception)


class TestExceptionChaining:
    """Test cases for exception chaining and hierarchy."""
    
    def test_exception_hierarchy(self):
        """Test the exception hierarchy."""
        # All custom exceptions should inherit from SmartDecisionError
        auth_error = AuthenticationError()
        api_error = APIError("test")
        validation_error = ValidationError()
        rate_limit_error = RateLimitError()
        connection_error = ConnectionError()
        
        assert isinstance(auth_error, SmartDecisionError)
        assert isinstance(api_error, SmartDecisionError)
        assert isinstance(validation_error, SmartDecisionError)
        assert isinstance(rate_limit_error, SmartDecisionError)
        assert isinstance(connection_error, SmartDecisionError)
        
        # All should inherit from Exception
        assert isinstance(auth_error, Exception)
        assert isinstance(api_error, Exception)
        assert isinstance(validation_error, Exception)
        assert isinstance(rate_limit_error, Exception)
        assert isinstance(connection_error, Exception)
    
    def test_exception_equality(self):
        """Test exception equality and string representation."""
        error1 = AuthenticationError("Test message")
        error2 = AuthenticationError("Test message")
        error3 = AuthenticationError("Different message")
        
        # Same message should be equal in string representation
        assert str(error1) == str(error2)
        assert str(error1) != str(error3)
        
        # But objects themselves are not equal (different instances)
        assert error1 != error2
    
    def test_exception_attributes(self):
        """Test that all exceptions have the expected attributes."""
        error = APIError("Test message", status_code=500, response_data={"key": "value"})
        
        assert hasattr(error, 'message')
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'response_data')
        
        assert error.message == "Test message"
        assert error.status_code == 500
        assert error.response_data == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__])
