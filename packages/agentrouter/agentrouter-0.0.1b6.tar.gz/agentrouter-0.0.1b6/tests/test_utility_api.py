"""
Tests for utility API client (get-base-url and validate-tools)
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from agentrouter.api.utility_api import (
    UtilityAPIClient,
    GlobalCache,
    CacheEntry,
    get_utility_client
)
from agentrouter.exceptions import ConfigurationError, ValidationError, APIError


class TestCacheEntry:
    """Test CacheEntry class"""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation"""
        data = {"test": "data"}
        entry = CacheEntry(data, ttl_seconds=3600)
        
        assert entry.data == data
        assert entry.ttl_seconds == 3600
        assert isinstance(entry.created_at, datetime)
    
    def test_cache_entry_not_expired(self):
        """Test cache entry is not expired"""
        entry = CacheEntry("test", ttl_seconds=3600)
        assert not entry.is_expired()
    
    def test_cache_entry_expired(self):
        """Test cache entry expiration"""
        entry = CacheEntry("test", ttl_seconds=0)
        # Sleep a tiny bit to ensure expiration
        import time
        time.sleep(0.01)
        assert entry.is_expired()
    
    def test_cache_entry_age(self):
        """Test cache entry age calculation"""
        entry = CacheEntry("test", ttl_seconds=3600)
        age = entry.age_seconds()
        assert age >= 0
        assert age < 1  # Should be very small


class TestGlobalCache:
    """Test GlobalCache singleton"""
    
    def test_singleton_pattern(self):
        """Test that GlobalCache is a singleton"""
        cache1 = GlobalCache()
        cache2 = GlobalCache()
        assert cache1 is cache2
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test setting and getting cached values"""
        cache = GlobalCache()
        cache.clear()  # Clear any existing cache
        
        # Set a value
        await cache.set("test_key_1234", {"data": "value"}, ttl=3600)
        
        # Get the value
        result = await cache.get("test_key_1234")
        assert result == {"data": "value"}
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = GlobalCache()
        cache.clear()
        
        result = await cache.get("nonexistent_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Test cache expiration"""
        cache = GlobalCache()
        cache.clear()
        
        # Set with very short TTL
        await cache.set("expire_key", "data", ttl=0)
        
        # Sleep to ensure expiration
        await asyncio.sleep(0.01)
        
        # Should return None due to expiration
        result = await cache.get("expire_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_stale(self):
        """Test getting stale cache entries"""
        cache = GlobalCache()
        cache.clear()
        
        # Set with very short TTL
        await cache.set("stale_key", "stale_data", ttl=0)
        
        # Sleep to ensure expiration
        await asyncio.sleep(0.01)
        
        # get_stale should still return the data
        result = await cache.get_stale("stale_key")
        assert result == "stale_data"


class TestUtilityAPIClient:
    """Test UtilityAPIClient"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        UtilityAPIClient.clear_global_cache()
        return UtilityAPIClient(
            api_key="test_key_1234",
            enable_cache=True,
            provider_cache_ttl=3600,
            tool_cache_ttl=86400
        )
    
    @pytest.mark.asyncio
    async def test_get_base_url_no_provider(self, client):
        """Test get_base_url with no provider"""
        mock_response = {
            "status": 1,
            "message": "Base URL resolved successfully",
            "data": {
                "baseUrl": "https://api.us.inc/v1",
                "provider": None,
                "model": "usf-mini",
                "isOurModel": True
            },
            "code": 200
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: mock_response,
                status_code=200
            )

            result = await client.get_base_url(None, "usf-mini")

            assert result == mock_response
            assert result["data"]["provider"] is None
            assert result["data"]["baseUrl"] == "https://api.us.inc/v1"
    
    @pytest.mark.asyncio
    async def test_get_base_url_with_provider(self, client):
        """Test get_base_url with provider"""
        # Mock the HTTP response
        mock_response = {
            "status": 1,
            "message": "Base URL resolved successfully",
            "data": {
                "baseUrl": "https://api.openai.com/v1",
                "provider": "openai",
                "model": "gpt-4",
                "isOurModel": False
            },
            "code": 200
        }
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: mock_response,
                status_code=200
            )
            
            result = await client.get_base_url("openai", "gpt-4")
            
            assert result == mock_response
            assert result["data"]["baseUrl"] == "https://api.openai.com/v1"
            assert result["data"]["provider"] == "openai"
            assert result["data"]["isOurModel"] is False
    
    @pytest.mark.asyncio
    async def test_get_base_url_invalid_provider(self, client):
        """Test get_base_url with invalid provider"""
        mock_response = {
            "status": 0,
            "message": "Invalid provider 'invalid'. You can only choose from these providers: openrouter, openai, claude, groq, huggingface-inference or leave blank/null for our models directly.",
            "data": {
                "provider": "invalid",
                "model": "test-model"
            },
            "code": 400
        }
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: mock_response,
                status_code=400
            )
            
            with pytest.raises(ConfigurationError) as exc_info:
                await client.get_base_url("invalid", "test-model")
            
            assert "Invalid provider" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_base_url_caching(self, client):
        """Test that get_base_url uses cache"""
        mock_response = {
            "status": 1,
            "message": "Base URL resolved successfully",
            "data": {
                "baseUrl": "https://api.openai.com/v1",
                "provider": "openai",
                "model": "gpt-4",
                "isOurModel": False
            },
            "code": 200
        }
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: mock_response,
                status_code=200
            )
            
            # First call - should hit API
            result1 = await client.get_base_url("openai", "gpt-4")
            assert mock_get.call_count == 1
            
            # Second call - should use cache
            result2 = await client.get_base_url("openai", "gpt-4")
            assert mock_get.call_count == 1  # Still 1, not 2
            
            assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_get_base_url_force_refresh(self, client):
        """Test force refresh bypasses cache"""
        mock_response = {
            "status": 1,
            "message": "Base URL resolved successfully",
            "data": {
                "baseUrl": "https://api.openai.com/v1",
                "provider": "openai",
                "model": "gpt-4",
                "isOurModel": False
            },
            "code": 200
        }
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: mock_response,
                status_code=200
            )
            
            # First call
            await client.get_base_url("openai", "gpt-4")
            assert mock_get.call_count == 1
            
            # Second call with force_refresh
            await client.get_base_url("openai", "gpt-4", force_refresh=True)
            assert mock_get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_validate_tools_empty(self, client):
        """Test validate_tools with empty tools list"""
        result = await client.validate_tools([])
        
        assert result["status"] == 1
        assert result["data"]["toolCount"] == 0
        assert result["data"]["toolNames"] == []
    
    @pytest.mark.asyncio
    async def test_validate_tools_valid(self, client):
        """Test validate_tools with valid tools"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        mock_response = {
            "status": 1,
            "message": "Tools are valid",
            "data": {
                "toolCount": 1,
                "toolNames": ["get_weather"]
            },
            "code": 200
        }
        
        with patch.object(client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await client.validate_tools(tools)
            
            assert result == mock_response
            assert result["data"]["toolCount"] == 1
            assert "get_weather" in result["data"]["toolNames"]
    
    @pytest.mark.asyncio
    async def test_validate_tools_invalid(self, client):
        """Test validate_tools with invalid tools"""
        tools = [
            {
                "type": "invalid",
                "function": {}
            }
        ]
        
        mock_response = {
            "status": 0,
            "message": "Invalid tool format. Please provide the correct tool schema for tool calling.",
            "data": {},
            "code": 400
        }
        
        with patch.object(client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(ValidationError) as exc_info:
                await client.validate_tools(tools)
            
            assert "Tool validation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_validate_tools_caching(self, client):
        """Test that validate_tools uses cache"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "Test",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]
        
        mock_response = {
            "status": 1,
            "message": "Tools are valid",
            "data": {
                "toolCount": 1,
                "toolNames": ["test_tool"]
            },
            "code": 200
        }
        
        with patch.object(client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            # First call - should hit API
            result1 = await client.validate_tools(tools)
            assert mock_post.call_count == 1
            
            # Second call - should use cache
            result2 = await client.validate_tools(tools)
            assert mock_post.call_count == 1  # Still 1, not 2
            
            assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_get_base_url_raises_on_api_failure(self, client):
        """Test get_base_url raises an error when the API call fails"""
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("API is down")

            with pytest.raises(APIError) as exc_info:
                await client.get_base_url("openai", "gpt-4")

            assert "Failed to get base URL" in str(exc_info.value)
    
    def test_clear_global_cache(self):
        """Test clearing global caches"""
        UtilityAPIClient.clear_global_cache()
        # Should not raise any errors


class TestGetUtilityClient:
    """Test get_utility_client singleton function"""
    
    def test_singleton_client(self):
        """Test that get_utility_client returns singleton"""
        client1 = get_utility_client()
        client2 = get_utility_client()
        assert client1 is client2
    
    def test_client_is_utility_api_client(self):
        """Test that returned client is UtilityAPIClient instance"""
        client = get_utility_client()
        assert isinstance(client, UtilityAPIClient)


class TestIntegrationWithAgents:
    """Test integration with agent classes"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization_with_provider(self):
        """Test that agent initialization calls get_base_url for provider"""
        from agentrouter.agents.manager import ManagerAgent
        
        mock_response = {
            "status": 1,
            "message": "Base URL resolved successfully",
            "data": {
                "baseUrl": "https://api.openai.com/v1",
                "provider": "openai",
                "model": "gpt-4",
                "isOurModel": False
            },
            "code": 200
        }
        
        with patch('agentrouter.agents.base.get_utility_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_base_url = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client
            
            # Create agent with provider
            agent = ManagerAgent(
                name="test_manager",
                api_key="test_key_1234",
                model="gpt-4",
                provider="openai"
            )
            
            # Check that base URL was set
            assert agent.config.base_url == "https://api.openai.com/v1"
            assert agent.config.is_our_model is False


class TestIntegrationWithToolDecorator:
    """Test integration with tool decorator"""
    
    def test_tool_decorator_validates_schema(self):
        """Test that tool decorator calls validate_tools"""
        from agentrouter.tools.decorator import tool
        
        mock_response = {
            "status": 1,
            "message": "Tools are valid",
            "data": {
                "toolCount": 1,
                "toolNames": ["test_function"]
            },
            "code": 200
        }
        
        with patch('agentrouter.tools.decorator.get_utility_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.validate_tools = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client
            
            # Create a tool with decorator
            @tool(
                schema={
                    "type": "function",
                    "function": {
                        "name": "test_function",
                        "description": "Test function",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "param": {"type": "string"}
                            },
                            "required": ["param"]
                        }
                    }
                }
            )
            async def test_function(param: str):
                return f"Result: {param}"
            
            # Function should be decorated
            assert hasattr(test_function, '_is_tool')
            assert test_function._is_tool is True
            assert test_function._tool_name == "test_function"
    
    def test_tool_decorator_handles_validation_failure(self):
        """Test that tool decorator handles validation API failures gracefully"""
        from agentrouter.tools.decorator import tool
        
        with patch('agentrouter.tools.decorator.get_utility_client') as mock_get_client:
            mock_client = AsyncMock()
            # Simulate API failure
            mock_client.validate_tools = AsyncMock(
                side_effect=Exception("API is down")
            )
            mock_get_client.return_value = mock_client
            
            # Should still create tool despite API failure (with warning)
            @tool(
                schema={
                    "type": "function",
                    "function": {
                        "name": "test_function",
                        "description": "Test function",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "param": {"type": "string"}
                            },
                            "required": ["param"]
                        }
                    }
                }
            )
            async def test_function(param: str):
                return f"Result: {param}"
            
            # Function should still be decorated
            assert hasattr(test_function, '_is_tool')
            assert test_function._is_tool is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
