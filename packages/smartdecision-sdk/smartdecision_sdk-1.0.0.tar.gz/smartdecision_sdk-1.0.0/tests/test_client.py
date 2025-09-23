"""
Tests for the SmartDecisionClient class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import httpx
from smartdecision_sdk import SmartDecisionClient
from smartdecision_sdk.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
)


class TestSmartDecisionClient:
    """Test cases for SmartDecisionClient."""
    
    def test_client_initialization(self):
        """Test client initialization with valid parameters."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.smartdecision.ai"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert "X-API-Key" in client.headers
        assert client.headers["X-API-Key"] == "test-api-key"
    
    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters."""
        custom_headers = {"X-Custom": "value"}
        client = SmartDecisionClient(
            api_key="test-api-key",
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
            headers=custom_headers
        )
        
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.headers["X-Custom"] == "value"
        assert client.headers["X-API-Key"] == "test-api-key"
    
    def test_client_initialization_with_empty_api_key(self):
        """Test that empty API key raises ValidationError."""
        with pytest.raises(ValidationError, match="API key is required"):
            SmartDecisionClient(api_key="")
        
        with pytest.raises(ValidationError, match="API key is required"):
            SmartDecisionClient(api_key="   ")
    
    def test_client_initialization_with_whitespace_api_key(self):
        """Test that API key is trimmed of whitespace."""
        client = SmartDecisionClient(api_key="  test-api-key  ")
        assert client.api_key == "test-api-key"
    
    def test_context_manager(self):
        """Test client as context manager."""
        with SmartDecisionClient(api_key="test-api-key") as client:
            assert client.api_key == "test-api-key"
        # Client should be closed after context exit
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test client as async context manager."""
        async with SmartDecisionClient(api_key="test-api-key").async_context() as client:
            assert client.api_key == "test-api-key"
        # Client should be closed after context exit


class TestEnsembleDecision:
    """Test cases for ensemble decision making."""
    
    @pytest.fixture
    def mock_response_data(self):
        """Mock response data for ensemble decision."""
        return {
            "ensemble_decision": "Python",
            "vote_details": [
                {
                    "llm_name": "gpt-4o",
                    "response": "Python",
                    "confidence": 0.85
                },
                {
                    "llm_name": "gemini-1.5-pro",
                    "response": "Python",
                    "confidence": 0.82
                },
                {
                    "llm_name": "claude-3-haiku",
                    "response": "JavaScript",
                    "confidence": 0.78
                }
            ],
            "total_votes": 3,
            "consensus_score": 0.67
        }
    
    @patch('smartdecision_sdk.client.asyncio.run')
    def test_make_ensemble_decision_sync(self, mock_run, mock_response_data):
        """Test synchronous ensemble decision making."""
        mock_run.return_value = Mock(**mock_response_data)
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_response_data):
            response = client.make_ensemble_decision(
                question="What is the best programming language?",
                categories=["Python", "JavaScript", "Go"]
            )
        
        assert response.ensemble_decision == "Python"
        assert response.total_votes == 3
        assert response.consensus_score == 0.67
        assert len(response.vote_details) == 3
    
    @pytest.mark.asyncio
    async def test_make_ensemble_decision_async(self, mock_response_data):
        """Test asynchronous ensemble decision making."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_response_data):
            response = await client.make_ensemble_decision_async(
                question="What is the best programming language?",
                categories=["Python", "JavaScript", "Go"]
            )
        
        assert response.ensemble_decision == "Python"
        assert response.final_decision == "Python"  # Test alias
        assert response.total_votes == 3
        assert response.consensus_score == 0.67
        assert len(response.vote_details) == 3
        assert len(response.individual_responses) == 3  # Test alias
    
    def test_make_ensemble_decision_vote_counts(self, mock_response_data):
        """Test vote counts calculation."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_response_data):
            with patch('smartdecision_sdk.client.asyncio.run') as mock_run:
                mock_response = Mock()
                mock_response.vote_counts = {"Python": 2, "JavaScript": 1}
                mock_run.return_value = mock_response
                
                response = client.make_ensemble_decision(
                    question="What is the best programming language?",
                    categories=["Python", "JavaScript", "Go"]
                )
        
        # The vote_counts should be calculated from vote_details
        expected_counts = {"Python": 2, "JavaScript": 1}
        assert response.vote_counts == expected_counts
    
    @pytest.mark.asyncio
    async def test_make_ensemble_decision_validation_error(self):
        """Test validation error for insufficient categories."""
        from pydantic import ValidationError as PydanticValidationError
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with pytest.raises(PydanticValidationError):
            await client.make_ensemble_decision_async(
                question="What is the best programming language?",
                categories=["Python"]  # Only one category should fail
            )
    
    @pytest.mark.asyncio
    async def test_make_ensemble_decision_authentication_error(self):
        """Test authentication error handling."""
        client = SmartDecisionClient(api_key="invalid-key")
        
        with patch.object(client, '_make_request', side_effect=AuthenticationError("Invalid API key")):
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                await client.make_ensemble_decision_async(
                    question="What is the best programming language?",
                    categories=["Python", "JavaScript", "Go"]
                )


class TestStatusAndHealth:
    """Test cases for status and health check methods."""
    
    @pytest.mark.asyncio
    async def test_get_ensemble_status(self):
        """Test getting ensemble status."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        status = await client.get_ensemble_status_async()
        
        assert status.ready is True
        assert status.available_count == 3
        assert status.total_services == 3
        assert status.available_services == 3  # Test alias
        assert len(status.services) == 3
        assert status.services["gpt-4o"] is True
        assert status.services["gemini-1.5-pro"] is True
        assert status.services["claude-3-haiku"] is True
    
    def test_get_ensemble_status_sync(self):
        """Test synchronous ensemble status."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch('smartdecision_sdk.client.asyncio.run') as mock_run:
            mock_status = Mock()
            mock_status.ready = True
            mock_status.available_count = 3
            mock_run.return_value = mock_status
            
            status = client.get_ensemble_status()
        
        assert status.ready is True
        assert status.available_count == 3
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        mock_health_data = {
            "status": "healthy",
            "message": "SmartDecision Ensemble API is running"
        }
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_health_data):
            health = await client.health_check_async()
        
        assert health.status == "healthy"
        assert health.message == "SmartDecision Ensemble API is running"
    
    def test_health_check_sync(self):
        """Test synchronous health check."""
        mock_health_data = {
            "status": "healthy",
            "message": "SmartDecision Ensemble API is running"
        }
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch('smartdecision_sdk.client.asyncio.run') as mock_run:
            mock_health = Mock()
            mock_health.status = "healthy"
            mock_health.message = "SmartDecision Ensemble API is running"
            mock_run.return_value = mock_health
            
            with patch.object(client, '_make_request', return_value=mock_health_data):
                health = client.health_check()
        
        assert health.status == "healthy"
        assert health.message == "SmartDecision Ensemble API is running"


class TestDecisionHistory:
    """Test cases for decision history methods."""
    
    @pytest.fixture
    def mock_history_data(self):
        """Mock decision history data."""
        return {
            "decisions": [
                {
                    "id": "decision-1",
                    "user_id": "user-123",
                    "question": "What is the best programming language?",
                    "valid_responses": ["Python", "JavaScript", "Go"],
                    "ensemble_decision": "Python",
                    "vote_details": [
                        {
                            "llm_name": "gpt-4o",
                            "response": "Python",
                            "confidence": 0.85
                        }
                    ],
                    "total_votes": 1,
                    "consensus_score": 1.0,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "total_count": 1,
            "has_more": False
        }
    
    @pytest.mark.asyncio
    async def test_get_decision_history(self, mock_history_data):
        """Test getting decision history."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_history_data):
            history = await client.get_decision_history_async(limit=10, offset=0)
        
        assert history.total_count == 1
        assert len(history.decisions) == 1
        assert history.has_more is False
        
        decision = history.decisions[0]
        assert decision.id == "decision-1"
        assert decision.user_id == "user-123"
        assert decision.question == "What is the best programming language?"
        assert decision.ensemble_decision == "Python"
    
    def test_get_decision_history_sync(self, mock_history_data):
        """Test synchronous decision history."""
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch('smartdecision_sdk.client.asyncio.run') as mock_run:
            mock_history = Mock()
            mock_history.total_count = 1
            mock_run.return_value = mock_history
            
            with patch.object(client, '_make_request', return_value=mock_history_data):
                history = client.get_decision_history(limit=10, offset=0)
        
        assert history.total_count == 1
    
    @pytest.mark.asyncio
    async def test_get_decision_by_id(self):
        """Test getting a specific decision by ID."""
        mock_decision_data = {
            "id": "decision-123",
            "user_id": "user-456",
            "question": "What is the best framework?",
            "ensemble_decision": "React"
        }
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_decision_data):
            decision = await client.get_decision_by_id_async("decision-123")
        
        assert decision["id"] == "decision-123"
        assert decision["user_id"] == "user-456"
        assert decision["question"] == "What is the best framework?"
        assert decision["ensemble_decision"] == "React"
    
    @pytest.mark.asyncio
    async def test_get_decision_statistics(self):
        """Test getting decision statistics."""
        mock_stats_data = {
            "total_decisions": 25,
            "recent_decisions": 5
        }
        
        client = SmartDecisionClient(api_key="test-api-key")
        
        with patch.object(client, '_make_request', return_value=mock_stats_data):
            stats = await client.get_decision_statistics_async()
        
        assert stats.total_decisions == 25
        assert stats.recent_decisions == 5


class TestErrorHandling:
    """Test cases for error handling."""
    
    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test authentication error handling."""
        client = SmartDecisionClient(api_key="invalid-key")
        
        with patch.object(client, '_make_request', side_effect=AuthenticationError("Invalid API key", 401)):
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                await client.make_ensemble_decision_async(
                    question="Test question",
                    categories=["Option 1", "Option 2"]
                )
    
    @pytest.mark.asyncio
    async def test_validation_error(self):
        """Test validation error handling."""
        client = SmartDecisionClient(api_key="test-key")
        
        with patch.object(client, '_make_request', side_effect=ValidationError("Validation failed", 400)):
            with pytest.raises(ValidationError, match="Validation failed"):
                await client.make_ensemble_decision_async(
                    question="Test question",
                    categories=["Option 1", "Option 2"]
                )
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Test rate limit error handling."""
        client = SmartDecisionClient(api_key="test-key")
        
        with patch.object(client, '_make_request', side_effect=RateLimitError("Rate limit exceeded", 429)):
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                await client.make_ensemble_decision_async(
                    question="Test question",
                    categories=["Option 1", "Option 2"]
                )
    
    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test connection error handling."""
        client = SmartDecisionClient(api_key="test-key")
        
        with patch.object(client, '_make_request', side_effect=ConnectionError("Connection failed")):
            with pytest.raises(ConnectionError, match="Connection failed"):
                await client.make_ensemble_decision_async(
                    question="Test question",
                    categories=["Option 1", "Option 2"]
                )
    
    @pytest.mark.asyncio
    async def test_api_error(self):
        """Test general API error handling."""
        client = SmartDecisionClient(api_key="test-key")
        
        with patch.object(client, '_make_request', side_effect=APIError("Server error", 500)):
            with pytest.raises(APIError, match="Server error"):
                await client.make_ensemble_decision_async(
                    question="Test question",
                    categories=["Option 1", "Option 2"]
                )


class TestHTTPClientManagement:
    """Test cases for HTTP client management."""
    
    @pytest.mark.asyncio
    async def test_client_creation_and_cleanup(self):
        """Test HTTP client creation and cleanup."""
        client = SmartDecisionClient(api_key="test-key")
        
        # Client should be None initially
        assert client._client is None
        
        # Get client should create it
        http_client = await client._get_client()
        assert http_client is not None
        assert client._client is not None
        
        # Close client
        await client.aclose()
        assert client._client.is_closed
    
    @pytest.mark.asyncio
    async def test_client_reuse(self):
        """Test that HTTP client is reused for multiple requests."""
        client = SmartDecisionClient(api_key="test-key")
        
        # Get client twice
        client1 = await client._get_client()
        client2 = await client._get_client()
        
        # Should be the same instance
        assert client1 is client2
        
        await client.aclose()
    
    def test_sync_close(self):
        """Test synchronous close method."""
        client = SmartDecisionClient(api_key="test-key")
        
        # Should not raise any errors
        client.close()
        
        # Multiple closes should not raise errors
        client.close()


if __name__ == "__main__":
    pytest.main([__file__])
