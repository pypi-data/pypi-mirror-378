"""
Utility API client for AgentRouter SDK
Handles get-base-url and validate-tools API endpoints with global caching
"""

import asyncio
import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from agentrouter.api.base import BaseAPIClient
from agentrouter.exceptions import APIError, ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache entry with TTL support"""
    
    def __init__(self, data: Any, ttl_seconds: int = 3600):
        """
        Initialize cache entry
        
        Args:
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        self.data = data
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return (datetime.now() - self.created_at).total_seconds()


class GlobalCache:
    """
    Global cache singleton for shared configuration data
    Thread-safe implementation for concurrent access
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._cache: Dict[str, CacheEntry] = {}
        self._async_lock = None  # Will be created in async context
        self._thread_lock = threading.Lock()
        self._initialized = True
        logger.info("GlobalCache singleton initialized")
    
    async def _get_async_lock(self):
        """Get or create async lock"""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value (async-safe)
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if valid, None otherwise
        """
        async_lock = await self._get_async_lock()
        async with async_lock:
            with self._thread_lock:
                if key in self._cache:
                    entry = self._cache[key]
                    if not entry.is_expired():
                        logger.debug(
                            f"Global cache hit for '{key}' (age: {entry.age_seconds():.1f}s)"
                        )
                        return entry.data
                    else:
                        logger.debug(f"Global cache expired for '{key}'")
                        del self._cache[key]
                else:
                    logger.debug(f"Global cache miss for '{key}'")
                return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set cached value (async-safe)
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds
        """
        async_lock = await self._get_async_lock()
        async with async_lock:
            with self._thread_lock:
                self._cache[key] = CacheEntry(value, ttl)
                logger.debug(f"Global cache set for '{key}' with TTL {ttl}s")
    
    async def get_stale(self, key: str) -> Optional[Any]:
        """
        Get cached value even if expired (for fallback)
        
        Args:
            key: Cache key
            
        Returns:
            Cached value regardless of expiration
        """
        async_lock = await self._get_async_lock()
        async with async_lock:
            with self._thread_lock:
                if key in self._cache:
                    entry = self._cache[key]
                    logger.debug(
                        f"Returning stale global cache for '{key}' (age: {entry.age_seconds():.1f}s)"
                    )
                    return entry.data
                return None
    
    def clear(self):
        """Clear all cached entries (sync)"""
        with self._thread_lock:
            self._cache.clear()
            logger.debug("Global cache cleared")


class UtilityAPIClient(BaseAPIClient):
    """
    Client for utility API endpoints (get-base-url and validate-tools)
    Uses global caching for shared configuration data
    """
    
    GET_BASE_URL_ENDPOINT = "/usf/v1/agent/get-base-url"
    VALIDATE_TOOLS_ENDPOINT = "/usf/v1/agent/validate-tools"
    
    # Class-level global caches (shared across all instances)
    _global_provider_cache = GlobalCache()
    _global_tool_cache = GlobalCache()
    
    # Default TTL values
    DEFAULT_PROVIDER_CACHE_TTL = 3600  # 1 hour
    DEFAULT_TOOL_CACHE_TTL = 86400     # 24 hours
    
    def __init__(
        self,
        api_key: str = "utility",  # Utility APIs may not need API key
        base_url: Optional[str] = None,
        provider_cache_ttl: int = DEFAULT_PROVIDER_CACHE_TTL,
        tool_cache_ttl: int = DEFAULT_TOOL_CACHE_TTL,
        enable_cache: bool = True,
    ):
        """
        Initialize utility API client with global caching
        
        Args:
            api_key: API key (may not be required for utility endpoints)
            base_url: Base URL for API endpoints
            provider_cache_ttl: TTL for provider cache in seconds (default: 1 hour)
            tool_cache_ttl: TTL for tool validation cache in seconds (default: 24 hours)
            enable_cache: Whether to enable caching (default: True)
        """
        super().__init__(api_key, base_url)
        
        self.enable_cache = enable_cache
        self.provider_cache_ttl = provider_cache_ttl
        self.tool_cache_ttl = tool_cache_ttl
        
        logger.info(
            f"Initialized UtilityAPIClient with provider cache TTL: {provider_cache_ttl}s, "
            f"tool cache TTL: {tool_cache_ttl}s, cache enabled: {enable_cache}"
        )
    
    async def get_base_url(
        self,
        provider: Optional[str],
        model: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get base URL for a provider/model combination
        
        Args:
            provider: Provider name (e.g., 'openai', 'claude', 'groq')
                     Can be None or empty string for default models
            model: Model name
            force_refresh: Force API call regardless of cache
            
        Returns:
            API response with base URL information:
            {
                "status": 1,
                "message": "Base URL resolved successfully",
                "data": {
                    "baseUrl": "https://api.openai.com/v1",
                    "provider": "openai",
                    "model": "gpt-5",
                    "isOurModel": false
                },
                "code": 200
            }
            
        Raises:
            ConfigurationError: If provider is invalid
            APIError: If API call fails
        """
        # Model is mandatory for resolving the base URL
        if not model or model == "inherited":
            raise ConfigurationError(
                "Model must be provided to resolve base URL",
                parameter="model",
                details={"model": model}
            )

        normalized_provider = provider.strip() if isinstance(provider, str) else provider
        cache_key = f"provider:{normalized_provider or 'default'}:{model}"
        
        # Check global cache first (unless disabled or force refresh)
        if self.enable_cache and not force_refresh:
            cached = await self._global_provider_cache.get(cache_key)
            if cached:
                return cached
        
        # Prepare params for GET request
        params = {"model": model}
        if normalized_provider:
            params["provider"] = normalized_provider
        
        try:
            logger.info(f"Fetching base URL for provider '{provider}', model '{model}'")
            
            # Build URL with query parameters
            url_with_params = f"{self.base_url}{self.GET_BASE_URL_ENDPOINT}?{urlencode(params)}"
            
            # Make API call (GET request)
            response = await self.client.get(url_with_params)
            response_data = response.json()
            
            # Check for successful response
            if response_data.get("status") != 1:
                error_message = response_data.get("message", "Unknown error")
                error_code = response_data.get("code", 400)
                
                # Check if it's an invalid provider error
                if error_code == 400 and "Invalid provider" in error_message:
                    raise ConfigurationError(
                        f"Invalid provider '{provider}': {error_message}",
                        parameter="provider",
                        details={"provider": provider, "model": model}
                    )
                
                raise APIError(
                    f"get-base-url API failed: {error_message}",
                    status_code=error_code,
                    api_name="get-base-url",
                    details=response_data
                )
            
            # Cache successful response in global cache
            if self.enable_cache:
                await self._global_provider_cache.set(
                    cache_key,
                    response_data,
                    self.provider_cache_ttl
                )
            
            return response_data

        except (ConfigurationError, APIError):
            raise
        except Exception as e:
            logger.error(f"Failed to get base URL: {str(e)}", exc_info=True)
            raise APIError(
                f"Failed to get base URL: {str(e)}",
                api_name="get-base-url",
                details={"provider": normalized_provider, "model": model}
            ) from e
    
    async def validate_tools(
        self,
        tools: List[Dict[str, Any]],
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Validate tool schemas
        
        Args:
            tools: List of tool definitions in OpenAI format
            force_refresh: Force API call regardless of cache
            
        Returns:
            API response with validation result:
            {
                "status": 1,
                "message": "Tools are valid",
                "data": {
                    "toolCount": 1,
                    "toolNames": ["get_weather"]
                },
                "code": 200
            }
            
        Raises:
            ValidationError: If tool schemas are invalid
            APIError: If API call fails
        """
        if not tools:
            # Empty tools list is valid
            return {
                "status": 1,
                "message": "No tools to validate",
                "data": {
                    "toolCount": 0,
                    "toolNames": []
                },
                "code": 200
            }
        
        # Create cache key from tool names and structure
        tool_names = []
        for tool in tools:
            if isinstance(tool, dict) and "function" in tool:
                func = tool["function"]
                if "name" in func:
                    tool_names.append(func["name"])
        
        cache_key = f"tools:{','.join(sorted(tool_names))}"
        
        # Check global cache first (unless disabled or force refresh)
        if self.enable_cache and not force_refresh and tool_names:
            cached = await self._global_tool_cache.get(cache_key)
            if cached:
                return cached
        
        # Prepare payload for POST request
        payload = {
            "tools": tools
        }
        
        try:
            logger.info(f"Validating {len(tools)} tools")
            
            # Make API call (POST request)
            response = await self.post(self.VALIDATE_TOOLS_ENDPOINT, payload)
            
            # Check for successful response
            if response.get("status") != 1:
                error_message = response.get("message", "Unknown error")
                error_code = response.get("code", 400)
                
                # Check if it's a validation error
                if error_code == 400 and "Invalid tool format" in error_message:
                    raise ValidationError(
                        f"Tool validation failed: {error_message}",
                        field="tools",
                        value=tools,
                        details=response.get("data", {})
                    )
                
                raise APIError(
                    f"validate-tools API failed: {error_message}",
                    status_code=error_code,
                    api_name="validate-tools",
                    details=response
                )
            
            # Cache successful response in global cache
            if self.enable_cache and tool_names:
                await self._global_tool_cache.set(
                    cache_key,
                    response,
                    self.tool_cache_ttl
                )
            
            return response
            
        except (ValidationError, APIError):
            # Re-raise known errors
            raise
        except Exception as e:
            logger.error(f"Failed to validate tools: {str(e)}", exc_info=True)
            
            # Try to use stale cache as fallback
            if self.enable_cache and tool_names:
                stale = await self._global_tool_cache.get_stale(cache_key)
                if stale:
                    logger.warning(
                        f"validate-tools API failed, using stale cache: {e}"
                    )
                    return stale
            
            raise APIError(
                f"Failed to validate tools: {str(e)}",
                api_name="validate-tools",
                details={"tool_count": len(tools)}
            ) from e
    
    @classmethod
    def clear_global_cache(cls):
        """
        Clear all global caches
        Useful for testing or when provider configurations change
        """
        cls._global_provider_cache.clear()
        cls._global_tool_cache.clear()
        logger.info("Global caches cleared")


# Create a singleton instance for convenience
_utility_client = None
_utility_client_lock = threading.Lock()


def get_utility_client() -> UtilityAPIClient:
    """
    Get or create the singleton utility API client
    
    Returns:
        Singleton UtilityAPIClient instance
    """
    global _utility_client
    if _utility_client is None:
        with _utility_client_lock:
            if _utility_client is None:
                _utility_client = UtilityAPIClient()
    return _utility_client
