"""
Base API client for AgentRouter SDK
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState,
)

from agentrouter.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    TimeoutError,
)
from agentrouter.types import APIResponse


logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Base API client with configurable retry logic and error handling
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_multiplier: float = 2.0,
        retry_max_wait: float = 60.0,
    ):
        """
        Initialize base API client with configurable settings
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds (5-300)
            max_retries: Maximum number of retry attempts (0-10)
            retry_delay: Initial delay between retries in seconds (0.1-60)
            retry_multiplier: Exponential backoff multiplier (1-10)
            retry_max_wait: Maximum wait time between retries (1-300)
        """
        self.api_key = api_key
        self._base_url = base_url or "https://api.us.inc"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_max_wait = retry_max_wait
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._get_default_headers(),
        )
    
    @property
    def base_url(self) -> str:
        """Get the current base URL"""
        return self._base_url
    
    @base_url.setter
    def base_url(self, value: str):
        """
        Set a new base URL
        
        Args:
            value: New base URL
        """
        self._base_url = value
        logger.debug(f"Base URL updated to: {value}")
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AgentRouter-SDK/0.1.0",
        }
    
    def _create_retry_decorator(self):
        """
        Create a retry decorator with current configuration
        
        Returns:
            Configured retry decorator
        """
        return retry(
            stop=stop_after_attempt(self.max_retries) if self.max_retries > 0 else stop_after_attempt(1),
            wait=wait_exponential(
                multiplier=self.retry_multiplier,
                min=self.retry_delay,
                max=self.retry_max_wait
            ),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
            before_sleep=self._log_retry_attempt,
        )
    
    def _log_retry_attempt(self, retry_state: RetryCallState) -> None:
        """
        Log retry attempts for debugging
        
        Args:
            retry_state: Current retry state
        """
        if retry_state.attempt_number > 1:
            logger.warning(
                f"Retry attempt {retry_state.attempt_number} after {retry_state.outcome.exception()}"
            )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make an HTTP request with configurable retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            payload: Request payload
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            APIError: If the request fails
        """
        # Apply retry decorator dynamically
        retry_decorator = self._create_retry_decorator()
        
        @retry_decorator
        async def _request_with_retry():
            return await self._execute_request(method, endpoint, payload, headers)
        
        return await _request_with_retry()
    
    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Execute the actual HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            payload: Request payload
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            Various exceptions based on response
        """
        # Build URL robustly and avoid duplicate path segments (e.g., '/usf/v1/usf/v1/...').
        base = (self._base_url or "").rstrip("/")
        ep = endpoint or ""
        # Absolute endpoint overrides base_url
        if ep.startswith("http://") or ep.startswith("https://"):
            url = ep
        else:
            # Ensure endpoint has a single leading slash
            if not ep.startswith("/"):
                ep = "/" + ep
            # De-duplicate standard API prefix if present on both base and endpoint
            prefix = "/usf/v1"
            if base.endswith(prefix) and ep.startswith(prefix + "/"):
                ep = ep[len(prefix):]
                if not ep.startswith("/"):
                    ep = "/" + ep
            url = f"{base}{ep}"
        
        # Prepare payload (don't add API key here)
        if payload is None:
            payload = {}
        
        # Merge headers and add API key to headers
        request_headers = self._get_default_headers()
        # Add API key to headers (not payload)
        request_headers["apiKey"] = self.api_key
        if headers:
            request_headers.update(headers)
        
        # Log request
        logger.debug(
            f"Making {method} request to {url}",
            extra={
                "method": method,
                "url": url,
                "headers": request_headers,
                "timeout": self.timeout,
                "max_retries": self.max_retries,
            }
        )
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=payload if method != "GET" else None,
                params=payload if method == "GET" else None,
                headers=request_headers,
            )
            
            # Check response status
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise AuthorizationError("Access forbidden")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=int(retry_after) if retry_after else None,
                )
            elif response.status_code >= 400:
                raise APIError(
                    f"API request failed: {response.text}",
                    status_code=response.status_code,
                    api_name=endpoint,
                )
            
            return response
            
        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {self.timeout} seconds",
                timeout_seconds=self.timeout,
                operation=f"{method} {url}",
            ) from e
        except httpx.NetworkError as e:
            raise APIError(
                f"Network error: {str(e)}",
                api_name=endpoint,
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error during API request: {str(e)}",
                exc_info=True,
            )
            raise APIError(
                f"Unexpected error: {str(e)}",
                api_name=endpoint,
            ) from e
    
    async def post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request with configured retry settings
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            headers: Additional headers
            
        Returns:
            Response data as dictionary
        """
        response = await self._make_request("POST", endpoint, payload, headers)
        return response.json()
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request with configured retry settings
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dictionary
        """
        response = await self._make_request("GET", endpoint, params, headers)
        return response.json()
    
    def update_retry_config(
        self,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_multiplier: Optional[float] = None,
        retry_max_wait: Optional[float] = None,
    ) -> None:
        """
        Update retry configuration at runtime
        
        Args:
            max_retries: New max retries value
            retry_delay: New retry delay value
            retry_multiplier: New retry multiplier value
            retry_max_wait: New max wait value
        """
        if max_retries is not None:
            self.max_retries = max_retries
        if retry_delay is not None:
            self.retry_delay = retry_delay
        if retry_multiplier is not None:
            self.retry_multiplier = retry_multiplier
        if retry_max_wait is not None:
            self.retry_max_wait = retry_max_wait
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()