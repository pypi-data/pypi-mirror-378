"""
Tests for the SmartDecision SDK models.
"""

import pytest
from pydantic import ValidationError
from smartdecision_sdk.models import (
    VoteDetail,
    EnsembleDecisionRequest,
    EnsembleDecisionResponse,
    DecisionHistoryItem,
    DecisionHistoryResponse,
    DecisionStatistics,
    EnsembleStatusResponse,
    HealthResponse,
    APIKeyInfo,
)


class TestVoteDetail:
    """Test cases for VoteDetail model."""
    
    def test_vote_detail_creation(self):
        """Test creating a VoteDetail with valid data."""
        vote = VoteDetail(
            llm_name="gpt-4o",
            response="Python",
            confidence=0.85
        )
        
        assert vote.llm_name == "gpt-4o"
        assert vote.response == "Python"
        assert vote.confidence == 0.85
    
    def test_vote_detail_confidence_validation(self):
        """Test confidence validation."""
        # Valid confidence values
        VoteDetail(llm_name="test", response="test", confidence=0.0)
        VoteDetail(llm_name="test", response="test", confidence=0.5)
        VoteDetail(llm_name="test", response="test", confidence=1.0)
        
        # Invalid confidence values
        with pytest.raises(ValidationError):
            VoteDetail(llm_name="test", response="test", confidence=-0.1)
        
        with pytest.raises(ValidationError):
            VoteDetail(llm_name="test", response="test", confidence=1.1)
    
    def test_vote_detail_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            VoteDetail()
        
        with pytest.raises(ValidationError):
            VoteDetail(llm_name="test")
        
        with pytest.raises(ValidationError):
            VoteDetail(llm_name="test", response="test")


class TestEnsembleDecisionRequest:
    """Test cases for EnsembleDecisionRequest model."""
    
    def test_request_creation(self):
        """Test creating a request with valid data."""
        request = EnsembleDecisionRequest(
            prompt="What is the best programming language?",
            valid_responses=["Python", "JavaScript", "Go"]
        )
        
        assert request.prompt == "What is the best programming language?"
        assert request.valid_responses == ["Python", "JavaScript", "Go"]
    
    def test_request_prompt_validation(self):
        """Test prompt validation."""
        # Valid prompts
        EnsembleDecisionRequest(
            prompt="What is the best programming language?",
            valid_responses=["Python", "JavaScript"]
        )
        
        # Empty prompt should fail
        with pytest.raises(ValidationError):
            EnsembleDecisionRequest(
                prompt="",
                valid_responses=["Python", "JavaScript"]
            )
    
    def test_request_responses_validation(self):
        """Test valid_responses validation."""
        # Valid responses
        EnsembleDecisionRequest(
            prompt="Test question",
            valid_responses=["Option 1", "Option 2"]
        )
        
        # Too few responses should fail
        with pytest.raises(ValidationError):
            EnsembleDecisionRequest(
                prompt="Test question",
                valid_responses=["Option 1"]
            )
        
        # Empty list should fail
        with pytest.raises(ValidationError):
            EnsembleDecisionRequest(
                prompt="Test question",
                valid_responses=[]
            )
    
    def test_request_cleaning(self):
        """Test that responses are cleaned and deduplicated."""
        request = EnsembleDecisionRequest(
            prompt="What is the best programming language?",
            valid_responses=["Python", "JavaScript", "Python", "", "Go", "   "]
        )
        
        # Should be cleaned and deduplicated
        assert request.valid_responses == ["Python", "JavaScript", "Go"]
    
    def test_request_cleaning_insufficient_unique(self):
        """Test that insufficient unique responses after cleaning fails."""
        with pytest.raises(ValueError, match="At least 2 unique valid responses are required"):
            EnsembleDecisionRequest(
                prompt="What is the best programming language?",
                valid_responses=["Python", "", "   ", "Python"]
            )


class TestEnsembleDecisionResponse:
    """Test cases for EnsembleDecisionResponse model."""
    
    @pytest.fixture
    def sample_vote_details(self):
        """Sample vote details for testing."""
        return [
            VoteDetail(llm_name="gpt-4o", response="Python", confidence=0.85),
            VoteDetail(llm_name="gemini-1.5-pro", response="Python", confidence=0.82),
            VoteDetail(llm_name="claude-3-haiku", response="JavaScript", confidence=0.78)
        ]
    
    def test_response_creation(self, sample_vote_details):
        """Test creating a response with valid data."""
        response = EnsembleDecisionResponse(
            ensemble_decision="Python",
            vote_details=sample_vote_details,
            total_votes=3,
            consensus_score=0.67
        )
        
        assert response.ensemble_decision == "Python"
        assert response.vote_details == sample_vote_details
        assert response.total_votes == 3
        assert response.consensus_score == 0.67
    
    def test_response_aliases(self, sample_vote_details):
        """Test response aliases."""
        response = EnsembleDecisionResponse(
            ensemble_decision="Python",
            vote_details=sample_vote_details,
            total_votes=3,
            consensus_score=0.67
        )
        
        # Test aliases
        assert response.final_decision == "Python"
        assert response.individual_responses == sample_vote_details
    
    def test_response_vote_counts(self, sample_vote_details):
        """Test vote counts calculation."""
        response = EnsembleDecisionResponse(
            ensemble_decision="Python",
            vote_details=sample_vote_details,
            total_votes=3,
            consensus_score=0.67
        )
        
        vote_counts = response.vote_counts
        assert vote_counts["Python"] == 2
        assert vote_counts["JavaScript"] == 1
    
    def test_response_validation(self):
        """Test response validation."""
        # Valid response
        EnsembleDecisionResponse(
            ensemble_decision="Python",
            vote_details=[],
            total_votes=0,
            consensus_score=0.0
        )
        
        # Invalid total_votes
        with pytest.raises(ValidationError):
            EnsembleDecisionResponse(
                ensemble_decision="Python",
                vote_details=[],
                total_votes=-1,
                consensus_score=0.0
            )
        
        # Invalid consensus_score
        with pytest.raises(ValidationError):
            EnsembleDecisionResponse(
                ensemble_decision="Python",
                vote_details=[],
                total_votes=0,
                consensus_score=1.5
            )


class TestDecisionHistoryItem:
    """Test cases for DecisionHistoryItem model."""
    
    def test_history_item_creation(self):
        """Test creating a history item with valid data."""
        vote_details = [
            VoteDetail(llm_name="gpt-4o", response="Python", confidence=0.85)
        ]
        
        item = DecisionHistoryItem(
            id="decision-123",
            user_id="user-456",
            api_key_id="key-789",
            api_key_name="My API Key",
            workspace="my-workspace",
            question="What is the best programming language?",
            valid_responses=["Python", "JavaScript"],
            ensemble_decision="Python",
            vote_details=vote_details,
            total_votes=1,
            consensus_score=1.0,
            created_at="2024-01-01T00:00:00Z"
        )
        
        assert item.id == "decision-123"
        assert item.user_id == "user-456"
        assert item.api_key_id == "key-789"
        assert item.api_key_name == "My API Key"
        assert item.workspace == "my-workspace"
        assert item.question == "What is the best programming language?"
        assert item.valid_responses == ["Python", "JavaScript"]
        assert item.ensemble_decision == "Python"
        assert item.vote_details == vote_details
        assert item.total_votes == 1
        assert item.consensus_score == 1.0
        assert item.created_at == "2024-01-01T00:00:00Z"
        assert item.source == "smartdecision-sdk"  # Default value
        assert item.api_version == "1.0.0"  # Default value
    
    def test_history_item_defaults(self):
        """Test history item with default values."""
        vote_details = [
            VoteDetail(llm_name="gpt-4o", response="Python", confidence=0.85)
        ]
        
        item = DecisionHistoryItem(
            user_id="user-456",
            question="What is the best programming language?",
            valid_responses=["Python", "JavaScript"],
            ensemble_decision="Python",
            vote_details=vote_details,
            total_votes=1,
            consensus_score=1.0
        )
        
        assert item.id is None
        assert item.api_key_id is None
        assert item.api_key_name is None
        assert item.workspace is None
        assert item.created_at is None
        assert item.source == "smartdecision-sdk"
        assert item.api_version == "1.0.0"


class TestDecisionHistoryResponse:
    """Test cases for DecisionHistoryResponse model."""
    
    def test_history_response_creation(self):
        """Test creating a history response with valid data."""
        vote_details = [
            VoteDetail(llm_name="gpt-4o", response="Python", confidence=0.85)
        ]
        
        decision = DecisionHistoryItem(
            user_id="user-456",
            question="What is the best programming language?",
            valid_responses=["Python", "JavaScript"],
            ensemble_decision="Python",
            vote_details=vote_details,
            total_votes=1,
            consensus_score=1.0
        )
        
        response = DecisionHistoryResponse(
            decisions=[decision],
            total_count=1,
            has_more=False
        )
        
        assert len(response.decisions) == 1
        assert response.decisions[0] == decision
        assert response.total_count == 1
        assert response.has_more is False
    
    def test_history_response_defaults(self):
        """Test history response with default values."""
        response = DecisionHistoryResponse(
            decisions=[],
            total_count=0
        )
        
        assert response.decisions == []
        assert response.total_count == 0
        assert response.has_more is False


class TestDecisionStatistics:
    """Test cases for DecisionStatistics model."""
    
    def test_statistics_creation(self):
        """Test creating statistics with valid data."""
        stats = DecisionStatistics(
            total_decisions=25,
            recent_decisions=5
        )
        
        assert stats.total_decisions == 25
        assert stats.recent_decisions == 5
    
    def test_statistics_validation(self):
        """Test statistics validation."""
        # Valid values
        DecisionStatistics(total_decisions=0, recent_decisions=0)
        DecisionStatistics(total_decisions=100, recent_decisions=50)
        
        # Invalid values
        with pytest.raises(ValidationError):
            DecisionStatistics(total_decisions=-1, recent_decisions=0)
        
        with pytest.raises(ValidationError):
            DecisionStatistics(total_decisions=0, recent_decisions=-1)


class TestEnsembleStatusResponse:
    """Test cases for EnsembleStatusResponse model."""
    
    def test_status_response_creation(self):
        """Test creating a status response with valid data."""
        status = EnsembleStatusResponse(
            ready=True,
            available_count=3,
            total_services=3,
            services={
                "gpt-4o": True,
                "gemini-1.5-pro": True,
                "claude-3-haiku": False
            }
        )
        
        assert status.ready is True
        assert status.available_count == 3
        assert status.total_services == 3
        assert status.available_services == 3  # Test alias
        assert status.services["gpt-4o"] is True
        assert status.services["gemini-1.5-pro"] is True
        assert status.services["claude-3-haiku"] is False
    
    def test_status_response_validation(self):
        """Test status response validation."""
        # Valid values
        EnsembleStatusResponse(
            ready=True,
            available_count=0,
            total_services=0,
            services={}
        )
        
        # Invalid values
        with pytest.raises(ValidationError):
            EnsembleStatusResponse(
                ready=True,
                available_count=-1,
                total_services=0,
                services={}
            )
        
        with pytest.raises(ValidationError):
            EnsembleStatusResponse(
                ready=True,
                available_count=0,
                total_services=-1,
                services={}
            )


class TestHealthResponse:
    """Test cases for HealthResponse model."""
    
    def test_health_response_creation(self):
        """Test creating a health response with valid data."""
        health = HealthResponse(
            status="healthy",
            message="API is running"
        )
        
        assert health.status == "healthy"
        assert health.message == "API is running"


class TestAPIKeyInfo:
    """Test cases for APIKeyInfo model."""
    
    def test_api_key_info_creation(self):
        """Test creating API key info with valid data."""
        api_key = APIKeyInfo(
            key_id="key-123",
            name="My API Key",
            workspace="my-workspace",
            created_at="2024-01-01T00:00:00Z",
            last_used="2024-01-02T00:00:00Z",
            is_active=True
        )
        
        assert api_key.key_id == "key-123"
        assert api_key.name == "My API Key"
        assert api_key.workspace == "my-workspace"
        assert api_key.created_at == "2024-01-01T00:00:00Z"
        assert api_key.last_used == "2024-01-02T00:00:00Z"
        assert api_key.is_active is True
    
    def test_api_key_info_defaults(self):
        """Test API key info with default values."""
        api_key = APIKeyInfo(
            key_id="key-123",
            name="My API Key",
            workspace="my-workspace"
        )
        
        assert api_key.created_at is None
        assert api_key.last_used is None
        assert api_key.is_active is True


if __name__ == "__main__":
    pytest.main([__file__])
