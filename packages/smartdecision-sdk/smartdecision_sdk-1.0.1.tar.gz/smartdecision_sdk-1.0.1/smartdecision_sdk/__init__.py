"""
SmartDecision Python SDK

A Python SDK for the SmartDecision AI-powered ensemble decision making API.
"""

from .client import SmartDecisionClient
from .models import (
    EnsembleDecisionRequest,
    EnsembleDecisionResponse,
    VoteDetail,
    DecisionHistoryResponse,
    DecisionHistoryItem,
    DecisionStatistics,
    EnsembleStatusResponse,
    HealthResponse,
)
from .exceptions import (
    SmartDecisionError,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
)
from .utils import (
    get_api_key_from_env,
    validate_api_key,
    validate_base_url,
    clean_categories,
    format_confidence,
    format_response_time,
    create_user_agent,
)

__version__ = "1.0.1"
__author__ = "Alex Zhang"
__email__ = "1108alexzhang@gmail.com"

__all__ = [
    "SmartDecisionClient",
    "EnsembleDecisionRequest",
    "EnsembleDecisionResponse", 
    "VoteDetail",
    "DecisionHistoryResponse",
    "DecisionHistoryItem",
    "DecisionStatistics",
    "EnsembleStatusResponse",
    "HealthResponse",
    "SmartDecisionError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "RateLimitError",
    "ConnectionError",
    "get_api_key_from_env",
    "validate_api_key",
    "validate_base_url",
    "clean_categories",
    "format_confidence",
    "format_response_time",
    "create_user_agent",
]
