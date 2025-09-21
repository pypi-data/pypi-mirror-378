"""
Base plugin class and hooks for AgentRouter SDK
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from agentrouter.types import PluginContext


logger = logging.getLogger(__name__)


class PluginHook(str, Enum):
    """
    Available plugin hooks
    """
    # Execution hooks
    BEFORE_EXECUTION = "on_before_execution"
    AFTER_EXECUTION = "on_after_execution"
    
    # Tool hooks
    BEFORE_TOOL_EXECUTION = "on_before_tool_execution"
    AFTER_TOOL_EXECUTION = "on_after_tool_execution"
    
    # API hooks
    BEFORE_API_CALL = "on_before_api_call"
    AFTER_API_CALL = "on_after_api_call"
    
    # Message hooks
    BEFORE_MESSAGE_PROCESSING = "on_before_message_processing"
    AFTER_MESSAGE_PROCESSING = "on_after_message_processing"
    
    # Error hooks
    ON_ERROR = "on_error"
    ON_RETRY = "on_retry"
    
    # Worker hooks
    BEFORE_WORKER_EXECUTION = "on_before_worker_execution"
    AFTER_WORKER_EXECUTION = "on_after_worker_execution"
    
    # State hooks
    ON_STATUS_CHANGE = "on_status_change"
    ON_ITERATION_START = "on_iteration_start"
    ON_ITERATION_END = "on_iteration_end"


class Plugin(ABC):
    """
    Abstract base class for plugins
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize plugin
        
        Args:
            name: Plugin name
            version: Plugin version
            enabled: Whether plugin is enabled
        """
        self.name = name or self.__class__.__name__
        self.version = version or "1.0.0"
        self.enabled = enabled
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"Initialized plugin: {self.name} v{self.version}")
    
    @abstractmethod
    def get_hooks(self) -> List[PluginHook]:
        """
        Get list of hooks this plugin implements
        
        Returns:
            List of plugin hooks
        """
        pass
    
    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Initialize plugin with context
        
        Args:
            context: Initialization context
        """
        pass
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources
        """
        pass
    
    def enable(self) -> None:
        """Enable the plugin"""
        self.enabled = True
        logger.info(f"Enabled plugin: {self.name}")
    
    def disable(self) -> None:
        """Disable the plugin"""
        self.enabled = False
        logger.info(f"Disabled plugin: {self.name}")
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set plugin metadata
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get plugin metadata
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value
        """
        return self._metadata.get(key, default)
    
    # Hook implementations (optional to override)
    
    def on_before_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before agent execution
        
        Args:
            context: Execution context
            
        Returns:
            Modified context
        """
        return context
    
    def on_after_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after agent execution
        
        Args:
            context: Execution context with result
            
        Returns:
            Modified context
        """
        return context
    
    def on_before_tool_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before tool execution
        
        Args:
            context: Tool execution context
            
        Returns:
            Modified context
        """
        return context
    
    def on_after_tool_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after tool execution
        
        Args:
            context: Tool execution context with result
            
        Returns:
            Modified context
        """
        return context
    
    def on_before_api_call(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before API call
        
        Args:
            context: API call context
            
        Returns:
            Modified context
        """
        return context
    
    def on_after_api_call(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after API call
        
        Args:
            context: API call context with response
            
        Returns:
            Modified context
        """
        return context
    
    def on_before_message_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before message processing
        
        Args:
            context: Message processing context
            
        Returns:
            Modified context
        """
        return context
    
    def on_after_message_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after message processing
        
        Args:
            context: Message processing context
            
        Returns:
            Modified context
        """
        return context
    
    def on_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called when an error occurs
        
        Args:
            context: Error context
            
        Returns:
            Modified context
        """
        return context
    
    def on_retry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called when a retry occurs
        
        Args:
            context: Retry context
            
        Returns:
            Modified context
        """
        return context
    
    def on_before_worker_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before worker execution
        
        Args:
            context: Worker execution context
            
        Returns:
            Modified context
        """
        return context
    
    def on_after_worker_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after worker execution
        
        Args:
            context: Worker execution context with result
            
        Returns:
            Modified context
        """
        return context
    
    def on_status_change(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called when agent status changes
        
        Args:
            context: Status change context
            
        Returns:
            Modified context
        """
        return context
    
    def on_iteration_start(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called at the start of an iteration
        
        Args:
            context: Iteration context
            
        Returns:
            Modified context
        """
        return context
    
    def on_iteration_end(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called at the end of an iteration
        
        Args:
            context: Iteration context
            
        Returns:
            Modified context
        """
        return context
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Plugin(name='{self.name}', version='{self.version}', enabled={self.enabled})"


# Example plugins

class LoggingPlugin(Plugin):
    """
    Plugin for enhanced logging
    """
    
    def __init__(self, log_level: str = "INFO"):
        super().__init__(name="LoggingPlugin", version="1.0.0")
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("agentrouter.plugins.logging")
        self.logger.setLevel(self.log_level)
    
    def get_hooks(self) -> List[PluginHook]:
        return [
            PluginHook.BEFORE_EXECUTION,
            PluginHook.AFTER_EXECUTION,
            PluginHook.ON_ERROR,
            PluginHook.BEFORE_TOOL_EXECUTION,
            PluginHook.AFTER_TOOL_EXECUTION,
        ]
    
    def on_before_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = context.get("agent_name", "Unknown")
        message_count = len(context.get("messages", []))
        self.logger.info(
            f"Starting execution for agent '{agent_name}' with {message_count} messages"
        )
        context["execution_start_time"] = asyncio.get_event_loop().time()
        return context
    
    def on_after_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = context.get("agent_name", "Unknown")
        start_time = context.get("execution_start_time", 0)
        duration = asyncio.get_event_loop().time() - start_time
        self.logger.info(
            f"Completed execution for agent '{agent_name}' in {duration:.2f} seconds"
        )
        return context
    
    def on_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        error = context.get("error")
        agent_name = context.get("agent_name", "Unknown")
        self.logger.error(
            f"Error in agent '{agent_name}': {str(error)}",
            exc_info=error
        )
        return context


class MetricsPlugin(Plugin):
    """
    Plugin for collecting metrics
    """
    
    def __init__(self):
        super().__init__(name="MetricsPlugin", version="1.0.0")
        self.metrics = {
            "executions": 0,
            "tool_calls": 0,
            "errors": 0,
            "total_duration": 0.0,
            "token_usage": 0,
        }
    
    def get_hooks(self) -> List[PluginHook]:
        return [
            PluginHook.BEFORE_EXECUTION,
            PluginHook.AFTER_EXECUTION,
            PluginHook.ON_ERROR,
            PluginHook.AFTER_TOOL_EXECUTION,
        ]
    
    def on_before_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["metrics_start_time"] = asyncio.get_event_loop().time()
        return context
    
    def on_after_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["executions"] += 1
        
        if "metrics_start_time" in context:
            duration = asyncio.get_event_loop().time() - context["metrics_start_time"]
            self.metrics["total_duration"] += duration
        
        if "result" in context and "usage" in context["result"]:
            tokens = context["result"]["usage"].get("total_tokens", 0)
            self.metrics["token_usage"] += tokens
        
        return context
    
    def on_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["errors"] += 1
        return context
    
    def on_after_tool_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["tool_calls"] += 1
        return context
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return dict(self.metrics)
    
    def reset_metrics(self) -> None:
        """Reset metrics"""
        self.metrics = {
            "executions": 0,
            "tool_calls": 0,
            "errors": 0,
            "total_duration": 0.0,
            "token_usage": 0,
        }


class CachingPlugin(Plugin):
    """
    Plugin for caching responses
    """
    
    def __init__(self, cache_size: int = 100):
        super().__init__(name="CachingPlugin", version="1.0.0")
        self.cache: Dict[str, Any] = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_hooks(self) -> List[PluginHook]:
        return [
            PluginHook.BEFORE_EXECUTION,
            PluginHook.AFTER_EXECUTION,
        ]
    
    def on_before_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Generate cache key from messages
        messages = context.get("messages", [])
        cache_key = self._generate_cache_key(messages)
        
        if cache_key in self.cache:
            self.cache_hits += 1
            logger.info(f"Cache hit for key: {cache_key[:20]}...")
            context["cached_result"] = self.cache[cache_key]
            context["skip_execution"] = True
        else:
            self.cache_misses += 1
            context["cache_key"] = cache_key
        
        return context
    
    def on_after_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if "cache_key" in context and "result" in context:
            cache_key = context["cache_key"]
            
            # Manage cache size
            if len(self.cache) >= self.cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = context["result"]
            logger.info(f"Cached result for key: {cache_key[:20]}...")
        
        return context
    
    def _generate_cache_key(self, messages: List[Any]) -> str:
        """Generate cache key from messages"""
        import hashlib
        import json
        
        # Convert messages to string
        msg_str = json.dumps([
            {"role": m.role, "content": m.content}
            for m in messages
        ], sort_keys=True)
        
        # Generate hash
        return hashlib.sha256(msg_str.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        }
    
    def clear_cache(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        logger.info("Cache cleared")


import asyncio