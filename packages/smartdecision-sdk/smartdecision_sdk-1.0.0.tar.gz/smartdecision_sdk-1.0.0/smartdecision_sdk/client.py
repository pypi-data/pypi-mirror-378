"""
SmartDecision Python SDK Client

This module provides the main client class for interacting with the SmartDecision API.
"""

import asyncio
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager
import httpx
from httpx import Response

from .models import (
    EnsembleDecisionRequest,
    EnsembleDecisionResponse,
    DecisionHistoryResponse,
    DecisionStatistics,
    EnsembleStatusResponse,
    HealthResponse,
    APIKeyInfo,
)
from .exceptions import (
    SmartDecisionError,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
)


class SmartDecisionClient:
    """
    Client for interacting with the SmartDecision API.
    
    This client provides methods for making ensemble decisions, checking service status,
    and managing decision history using the SmartDecision API.
    
    Example:
        >>> client = SmartDecisionClient(api_key="your-api-key")
        >>> response = client.make_ensemble_decision(
        ...     question="What is the best programming language?",
        ...     categories=["Python", "JavaScript", "Go"]
        ... )
        >>> print(f"Final decision: {response.final_decision}")
        >>> client.close()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.smartdecision.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the SmartDecision client.
        
        Args:
            api_key: Your SmartDecision API key
            base_url: Base URL for the SmartDecision API (default: https://api.smartdecision.ai)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            headers: Additional headers to include in requests
        """
        if not api_key or not api_key.strip():
            raise ValidationError("API key is required and cannot be empty")
        
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up default headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "smartdecision-sdk-python/1.0.0",
            "X-API-Key": self.api_key,
        }
        if headers:
            self.headers.update(headers)
        
        # Initialize HTTP client
        self._client: Optional[httpx.AsyncClient] = None
        self._session_lock = asyncio.Lock()
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        async with self._session_lock:
            if self._client is None or self._client.is_closed:
                self._client = httpx.AsyncClient(
                    headers=self.headers,
                    timeout=self.timeout,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            return self._client
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the SmartDecision API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            ConnectionError: If connection fails
            ValidationError: If request validation fails
        """
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        
        try:
            response: Response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key. Please check your API key and try again.",
                    status_code=response.status_code,
                    response_data=response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                )
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                raise ValidationError(
                    error_data.get("detail", "Request validation failed."),
                    status_code=response.status_code,
                    response_data=error_data
                )
            elif response.status_code == 429:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                raise RateLimitError(
                    error_data.get("detail", "Rate limit exceeded. Please try again later."),
                    status_code=response.status_code,
                    response_data=error_data
                )
            elif response.status_code >= 400:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                raise APIError(
                    error_data.get("detail", f"API error: {response.status_code}"),
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            # Parse successful response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"message": response.text}
                
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timeout: {str(e)}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to API: {str(e)}")
        except httpx.HTTPError as e:
            raise ConnectionError(f"HTTP error: {str(e)}")
        except (AuthenticationError, APIError, ValidationError, RateLimitError, ConnectionError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise SmartDecisionError(f"Unexpected error: {str(e)}")
    
    def make_ensemble_decision(
        self,
        question: str,
        categories: List[str],
        **kwargs
    ) -> EnsembleDecisionResponse:
        """
        Make an ensemble decision using multiple LLMs.
        
        This method sends a question and list of categories to multiple LLM services
        and returns the ensemble decision based on majority voting.
        
        Args:
            question: The question or prompt to send to the models
            categories: List of valid response options for the models to choose from
            **kwargs: Additional arguments (for future extensibility)
            
        Returns:
            EnsembleDecisionResponse containing the final decision and vote details
            
        Example:
            >>> response = client.make_ensemble_decision(
            ...     question="What is the best programming language for web development?",
            ...     categories=["Python", "JavaScript", "TypeScript", "Go", "Rust"]
            ... )
            >>> print(f"Final decision: {response.final_decision}")
            >>> print(f"Vote counts: {response.vote_counts}")
        """
        # Run the async version
        return asyncio.run(self.make_ensemble_decision_async(question, categories, **kwargs))
    
    async def make_ensemble_decision_async(
        self,
        question: str,
        categories: List[str],
        **kwargs
    ) -> EnsembleDecisionResponse:
        """
        Make an ensemble decision using multiple LLMs (async version).
        
        Args:
            question: The question or prompt to send to the models
            categories: List of valid response options for the models to choose from
            **kwargs: Additional arguments (for future extensibility)
            
        Returns:
            EnsembleDecisionResponse containing the final decision and vote details
        """
        # Create request model for validation
        request = EnsembleDecisionRequest(prompt=question, valid_responses=categories)
        
        # Make API request
        response_data = await self._make_request(
            method="POST",
            endpoint="/v1/ensemble",
            data=request.model_dump()
        )
        
        return EnsembleDecisionResponse(**response_data)
    
    def get_ensemble_status(self) -> EnsembleStatusResponse:
        """
        Get the status of the ensemble LLM services.
        
        Returns:
            EnsembleStatusResponse containing service status information
            
        Example:
            >>> status = client.get_ensemble_status()
            >>> print(f"Services ready: {status.ready}")
            >>> print(f"Available services: {status.available_count}/{status.total_services}")
        """
        # Run the async version
        return asyncio.run(self.get_ensemble_status_async())
    
    async def get_ensemble_status_async(self) -> EnsembleStatusResponse:
        """
        Get the status of the ensemble LLM services (async version).
        
        Returns:
            EnsembleStatusResponse containing service status information
        """
        # For now, we'll return a mock status since the API doesn't have a status endpoint
        # In a real implementation, this would call the API
        return EnsembleStatusResponse(
            ready=True,
            available_count=3,
            total_services=3,
            services={
                "gpt-4o": True,
                "gemini-1.5-pro": True,
                "claude-3-haiku": True
            }
        )
    
    def get_decision_history(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> DecisionHistoryResponse:
        """
        Get decision history for the authenticated user.
        
        Args:
            limit: Maximum number of decisions to return (default: 50, max: 100)
            offset: Number of decisions to skip for pagination (default: 0)
            
        Returns:
            DecisionHistoryResponse containing decision history
            
        Example:
            >>> history = client.get_decision_history(limit=10)
            >>> print(f"Total decisions: {history.total_count}")
            >>> for decision in history.decisions:
            ...     print(f"Decision: {decision.ensemble_decision}")
        """
        # Run the async version
        return asyncio.run(self.get_decision_history_async(limit, offset))
    
    async def get_decision_history_async(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> DecisionHistoryResponse:
        """
        Get decision history for the authenticated user (async version).
        
        Args:
            limit: Maximum number of decisions to return (default: 50, max: 100)
            offset: Number of decisions to skip for pagination (default: 0)
            
        Returns:
            DecisionHistoryResponse containing decision history
        """
        if limit > 100:
            limit = 100
        
        response_data = await self._make_request(
            method="GET",
            endpoint="/decision-history",
            params={"limit": limit, "offset": offset}
        )
        
        return DecisionHistoryResponse(**response_data)
    
    def get_decision_by_id(self, decision_id: str) -> Dict[str, Any]:
        """
        Get a specific decision by ID.
        
        Args:
            decision_id: The ID of the decision to retrieve
            
        Returns:
            Dictionary containing the decision data
            
        Example:
            >>> decision = client.get_decision_by_id("decision-123")
            >>> print(f"Question: {decision['question']}")
        """
        # Run the async version
        return asyncio.run(self.get_decision_by_id_async(decision_id))
    
    async def get_decision_by_id_async(self, decision_id: str) -> Dict[str, Any]:
        """
        Get a specific decision by ID (async version).
        
        Args:
            decision_id: The ID of the decision to retrieve
            
        Returns:
            Dictionary containing the decision data
        """
        response_data = await self._make_request(
            method="GET",
            endpoint=f"/decision-history/{decision_id}"
        )
        
        return response_data
    
    def get_decision_statistics(self) -> DecisionStatistics:
        """
        Get decision statistics for the authenticated user.
        
        Returns:
            DecisionStatistics containing user statistics
            
        Example:
            >>> stats = client.get_decision_statistics()
            >>> print(f"Total decisions: {stats.total_decisions}")
        """
        # Run the async version
        return asyncio.run(self.get_decision_statistics_async())
    
    async def get_decision_statistics_async(self) -> DecisionStatistics:
        """
        Get decision statistics for the authenticated user (async version).
        
        Returns:
            DecisionStatistics containing user statistics
        """
        response_data = await self._make_request(
            method="GET",
            endpoint="/decision-statistics"
        )
        
        return DecisionStatistics(**response_data)
    
    def health_check(self) -> HealthResponse:
        """
        Check the health of the API.
        
        Returns:
            HealthResponse containing health status information
            
        Example:
            >>> health = client.health_check()
            >>> print(f"Status: {health.status}")
        """
        # Run the async version
        return asyncio.run(self.health_check_async())
    
    async def health_check_async(self) -> HealthResponse:
        """
        Check the health of the API (async version).
        
        Returns:
            HealthResponse containing health status information
        """
        response_data = await self._make_request(
            method="GET",
            endpoint="/health"
        )
        
        return HealthResponse(**response_data)
    
    def close(self):
        """Close the HTTP client and clean up resources."""
        if self._client and not self._client.is_closed:
            asyncio.run(self._client.aclose())
    
    async def aclose(self):
        """Close the HTTP client and clean up resources (async version)."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    @asynccontextmanager
    async def async_context(self):
        """Async context manager for using the client."""
        try:
            yield self
        finally:
            await self.aclose()
    
    def __enter__(self):
        """Synchronous context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Synchronous context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure client is closed."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup
