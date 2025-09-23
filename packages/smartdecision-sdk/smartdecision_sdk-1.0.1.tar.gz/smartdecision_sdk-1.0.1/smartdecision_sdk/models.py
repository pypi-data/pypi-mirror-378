"""
Data models for the SmartDecision SDK.

This module contains Pydantic models for request and response data structures.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VoteDetail(BaseModel):
    """Individual vote detail from an LLM."""
    
    model_config = ConfigDict(protected_namespaces=())
    
    llm_name: str = Field(..., description="Name of the LLM that provided this vote")
    response: str = Field(..., description="The response from this LLM")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")


class EnsembleDecisionRequest(BaseModel):
    """Request model for making an ensemble decision."""
    
    prompt: str = Field(..., min_length=1, description="The question or prompt to send to the models")
    valid_responses: List[str] = Field(..., min_length=2, description="List of valid response options for the models to choose from")
    
    def model_post_init(self, __context: Any) -> None:
        """Validate and clean the request data."""
        # Remove duplicates and empty strings
        cleaned_responses = list(dict.fromkeys([
            resp.strip() for resp in self.valid_responses 
            if resp and resp.strip()
        ]))
        
        if len(cleaned_responses) < 2:
            raise ValueError("At least 2 unique valid responses are required after cleaning")
        
        # Update the cleaned responses
        object.__setattr__(self, 'valid_responses', cleaned_responses)


class EnsembleDecisionResponse(BaseModel):
    """Response model for ensemble decision results."""
    
    ensemble_decision: str = Field(..., description="The final ensemble decision")
    vote_details: List[VoteDetail] = Field(..., description="Individual vote details from each LLM")
    total_votes: int = Field(..., ge=0, description="Total number of votes received")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Consensus score (0.0 to 1.0)")
    
    @property
    def final_decision(self) -> str:
        """Alias for ensemble_decision for backward compatibility."""
        return self.ensemble_decision
    
    @property
    def individual_responses(self) -> List[VoteDetail]:
        """Alias for vote_details for backward compatibility."""
        return self.vote_details
    
    @property
    def vote_counts(self) -> Dict[str, int]:
        """Get vote counts for each response option."""
        counts = {}
        for vote in self.vote_details:
            response = vote.response
            if response not in counts:
                counts[response] = 0
            counts[response] += 1
        return counts


class DecisionHistoryItem(BaseModel):
    """Individual decision history item."""
    
    id: Optional[str] = Field(None, description="Unique identifier for the decision")
    user_id: str = Field(..., description="ID of the user who made the decision")
    api_key_id: Optional[str] = Field(None, description="ID of the API key used")
    api_key_name: Optional[str] = Field(None, description="Name of the API key used")
    workspace: Optional[str] = Field(None, description="Workspace where the decision was made")
    question: str = Field(..., description="The original question/prompt")
    valid_responses: List[str] = Field(..., description="Valid response options that were provided")
    ensemble_decision: str = Field(..., description="The final ensemble decision")
    vote_details: List[VoteDetail] = Field(..., description="Individual vote details")
    total_votes: int = Field(..., ge=0, description="Total number of votes")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Consensus score")
    created_at: Optional[str] = Field(None, description="ISO timestamp when the decision was made")
    source: str = Field(default="smartdecision-sdk", description="Source of the decision")
    api_version: str = Field(default="1.0.0", description="API version used")


class DecisionHistoryResponse(BaseModel):
    """Response model for decision history."""
    
    decisions: List[DecisionHistoryItem] = Field(..., description="List of decision history items")
    total_count: int = Field(..., ge=0, description="Total number of decisions")
    has_more: bool = Field(default=False, description="Whether there are more decisions available")


class DecisionStatistics(BaseModel):
    """Decision statistics for a user."""
    
    total_decisions: int = Field(..., ge=0, description="Total number of decisions made")
    recent_decisions: int = Field(..., ge=0, description="Number of recent decisions")


class EnsembleStatusResponse(BaseModel):
    """Response model for ensemble service status."""
    
    ready: bool = Field(..., description="Whether the ensemble service is ready")
    available_count: int = Field(..., ge=0, description="Number of available LLM services")
    total_services: int = Field(..., ge=0, description="Total number of configured LLM services")
    services: Dict[str, bool] = Field(..., description="Status of individual LLM services")
    
    @property
    def available_services(self) -> int:
        """Alias for available_count for backward compatibility."""
        return self.available_count


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Health message")


class APIKeyInfo(BaseModel):
    """Information about an API key."""
    
    key_id: str = Field(..., description="Unique identifier for the API key")
    name: str = Field(..., description="Human-readable name for the API key")
    workspace: str = Field(..., description="Workspace associated with the key")
    created_at: Optional[str] = Field(None, description="ISO timestamp when the key was created")
    last_used: Optional[str] = Field(None, description="ISO timestamp when the key was last used")
    is_active: bool = Field(default=True, description="Whether the key is active")
