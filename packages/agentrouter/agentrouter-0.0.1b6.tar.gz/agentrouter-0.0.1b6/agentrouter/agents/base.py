"""
Base agent class for AgentRouter SDK
"""

import asyncio
import json
import threading
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from agentrouter.api import PlanAPIClient, ToolCallAPIClient, UtilityAPIClient, get_utility_client
from agentrouter.exceptions import (
    AgentRouterError,
    ConfigurationError,
    ExecutionError,
    ValidationError,
)
from agentrouter.tools import ToolRegistry, ToolExecutor
from agentrouter.types import (
    AgentConfig,
    AgentStatus,
    ExecutionContext,
    Message,
    ToolDefinition,
    WorkerTask,
    APIResponse,
)
from agentrouter.visualization import (
    ExecutionTracer,
    ExecutionVisualizer,
    PipelineInspector,
)
from agentrouter.utils.logging import log_agent, get_logger


logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents
    """
    
    def __init__(
        self,
        name: str,
        api_key: str,
        model: str = "usf-mini",
        trace: bool = False,
        **config_kwargs
    ):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            api_key: API key for authentication
            model: Model to use
            trace: Enable execution tracing for visualization (default: False)
            **config_kwargs: Additional configuration options
        """
        # Create unique instance ID
        self.instance_id = str(uuid.uuid4())
        
        # Initialize configuration
        self.config = AgentConfig(
            name=name,
            api_key=api_key,
            model=model,
            **config_kwargs
        )
        
        # Initialize provider base URL if provider is specified
        self._initialize_provider_base_url()
        
        # Initialize API clients with configuration from AgentConfig
        base_url = getattr(self.config, 'base_url', None)
        self.plan_api = PlanAPIClient(
            api_key=api_key,
            base_url=base_url,
            timeout=self.config.api_timeout,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            retry_multiplier=self.config.retry_multiplier,
            retry_max_wait=self.config.retry_max_wait
        )
        self.tool_call_api = ToolCallAPIClient(
            api_key=api_key,
            base_url=base_url,
            timeout=self.config.api_timeout,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            retry_multiplier=self.config.retry_multiplier,
            retry_max_wait=self.config.retry_max_wait
        )
        
        # Initialize tool registry and executor
        self.tool_registry = ToolRegistry(name=f"{name}_tools")
        self.tool_executor = ToolExecutor(self.tool_registry)
        
        # Initialize worker agents
        self._workers: Dict[str, 'BaseAgent'] = {}
        self._worker_aliases: Dict[str, str] = {}
        
        # Initialize plugins
        self._plugins: List[Any] = []
        
        # Initialize state
        self.status = AgentStatus.IDLE
        self._execution_context: Optional[ExecutionContext] = None
        self._parent_agent: Optional['BaseAgent'] = None
        
        # Statistics
        self._execution_count = 0
        self._total_tokens_used = 0
        
        # Initialize tracer (zero overhead when disabled)
        self._tracer: Optional[ExecutionTracer] = None
        if trace:
            self._tracer = ExecutionTracer(enabled=True)
            log_agent(name, "Tracing enabled", "debug")
        
        # Simple initialization log
        log_agent(name, f"Initialized ({self.__class__.__name__})", "info")
    
    def _initialize_provider_base_url(self) -> None:
        """Resolve and cache the provider base URL via get-base-url API"""
        model = getattr(self.config, "model", None)
        provider = getattr(self.config, "provider", None)

        if not model or model == "inherited":
            logger.debug(
                "Skipping base URL resolution for agent '%s' until model is provided",
                getattr(self.config, 'name', 'unknown')
            )
            return

        try:
            async def _resolve():
                # Create a fresh UtilityAPIClient bound to the current event loop
                utility_client = UtilityAPIClient()
                try:
                    return await utility_client.get_base_url(
                        provider=provider,
                        model=model
                    )
                finally:
                    # Ensure HTTP resources are released
                    await utility_client.close()

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                result_container: Dict[str, Any] = {}
                error_container: Dict[str, Exception] = {}

                def _run_in_thread() -> None:
                    try:
                        result_container["value"] = asyncio.run(_resolve())
                    except Exception as thread_exc:  # pragma: no cover - propagate below
                        error_container["error"] = thread_exc

                resolver_thread = threading.Thread(target=_run_in_thread, daemon=True)
                resolver_thread.start()
                resolver_thread.join()

                if "error" in error_container:
                    raise error_container["error"]

                result = result_container.get("value")
            else:
                created_loop = False
                if loop is None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    created_loop = True
                try:
                    result = loop.run_until_complete(_resolve())
                finally:
                    if created_loop:
                        loop.close()
                        asyncio.set_event_loop(None)

            if result and result.get("status") == 1:
                data = result.get("data", {})
                base_url = data.get("baseUrl")

                if not base_url:
                    raise ConfigurationError(
                        "get-base-url response did not include a baseUrl value",
                        parameter="base_url",
                        details={"provider": provider, "model": model, "response": data}
                    )

                self.config.base_url = base_url
                self.config.is_our_model = data.get("isOurModel", False)
                logger.debug(
                    f"Resolved base URL for provider '{provider or 'default'}': {base_url}"
                )
            else:
                message = (result or {}).get("message", "Unknown error") if result else "No response"
                raise ConfigurationError(
                    f"Failed to get base URL: {message}",
                    parameter="provider",
                    details={"provider": provider, "model": model}
                )

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize provider base URL: {str(e)}",
                parameter="provider",
                details={"provider": provider, "model": model}
            ) from e
    
    @property
    def name(self) -> str:
        """Get agent name"""
        return self.config.name
    
    @property
    def is_manager(self) -> bool:
        """Check if agent is a manager"""
        return self.__class__.__name__ == "ManagerAgent"
    
    @property
    def is_worker(self) -> bool:
        """Check if agent is a worker"""
        return self.__class__.__name__ == "WorkerAgent"
    
    def register_tool(self, tool_func: Any, alias: Optional[str] = None) -> None:
        """
        Register a tool with the agent
        
        Args:
            tool_func: Tool function decorated with @tool
            alias: Optional alias for the tool
        """
        self.tool_registry.register(tool_func, alias=alias)
        logger.debug(f"Tool registered: {tool_func.__name__ if hasattr(tool_func, '__name__') else 'tool'}")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name or alias
            
        Returns:
            True if tool was unregistered
        """
        return self.tool_registry.unregister(name)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tools
        
        Returns:
            List of tool names
        """
        return self.tool_registry.list_tools()
    
    def attach_worker(
        self,
        worker: 'BaseAgent',
        alias: Optional[str] = None
    ) -> None:
        """
        Attach a worker agent with strict name uniqueness validation
        
        Args:
            worker: Worker agent to attach
            alias: Optional alias for the worker
            
        Raises:
            ValidationError: If worker name is duplicate or invalid
        """
        if not worker.is_worker:
            raise ValidationError(
                f"Can only attach WorkerAgent instances, got {type(worker)}"
            )
        
        worker_name = worker.name
        
        # STRICT NAME UNIQUENESS CHECK (fail-fast approach)
        if worker_name in self._workers:
            raise ValidationError(
                f"Worker '{worker_name}' already attached to '{self.name}'.\n"
                f"Each worker must have a unique name.\n"
                f"Existing workers: {', '.join(self._workers.keys())}"
            )
        
        # Check alias uniqueness if provided
        if alias:
            if alias in self._worker_aliases:
                raise ValidationError(
                    f"Alias '{alias}' already in use for worker '{self._worker_aliases[alias]}'.\n"
                    f"Each alias must be unique.\n"
                    f"Existing aliases: {', '.join(self._worker_aliases.keys())}"
                )
            if alias in self._workers:
                raise ValidationError(
                    f"Alias '{alias}' conflicts with existing worker name.\n"
                    f"Aliases cannot match worker names."
                )
        
        # Attach worker
        self._workers[worker_name] = worker
        worker._parent_agent = self
        
        # Set alias if provided
        if alias:
            self._worker_aliases[alias] = worker_name
        
        logger.debug(f"Worker '{worker_name}' attached" + (f" with alias '{alias}'" if alias else ""))
    
    def detach_worker(self, name: str) -> bool:
        """
        Detach a worker agent
        
        Args:
            name: Worker name or alias
            
        Returns:
            True if worker was detached
        """
        # Resolve alias
        worker_name = self._worker_aliases.get(name, name)
        
        if worker_name in self._workers:
            worker = self._workers[worker_name]
            worker._parent_agent = None
            del self._workers[worker_name]
            
            # Remove aliases
            aliases_to_remove = [
                alias for alias, target in self._worker_aliases.items()
                if target == worker_name
            ]
            for alias in aliases_to_remove:
                del self._worker_aliases[alias]
            
            logger.debug(f"Worker '{worker_name}' detached")
            return True
        
        return False
    
    def get_worker(self, name: str) -> Optional['BaseAgent']:
        """
        Get an attached worker
        
        Args:
            name: Worker name or alias
            
        Returns:
            Worker agent if found
        """
        worker_name = self._worker_aliases.get(name, name)
        return self._workers.get(worker_name)
    
    def list_workers(self) -> List[str]:
        """
        List all attached workers
        
        Returns:
            List of worker names
        """
        return list(self._workers.keys())
    
    def add_plugin(self, plugin: Any) -> None:
        """
        Add a plugin to the agent
        
        Args:
            plugin: Plugin instance
        """
        self._plugins.append(plugin)
        logger.debug(f"Plugin added to agent '{self.name}'")
    
    def remove_plugin(self, plugin: Any) -> bool:
        """
        Remove a plugin from the agent
        
        Args:
            plugin: Plugin instance
            
        Returns:
            True if plugin was removed
        """
        if plugin in self._plugins:
            self._plugins.remove(plugin)
            logger.debug(f"Plugin removed from agent '{self.name}'")
            return True
        return False
    
    async def _apply_plugin_hook(
        self,
        hook_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply plugin hooks
        
        Args:
            hook_name: Name of the hook
            context: Context to pass to plugins
            
        Returns:
            Modified context
        """
        for plugin in self._plugins:
            if hasattr(plugin, hook_name):
                hook_method = getattr(plugin, hook_name)
                if callable(hook_method):
                    try:
                        context = await hook_method(context) if asyncio.iscoroutinefunction(hook_method) else hook_method(context)
                    except Exception as e:
                        logger.error(
                            f"Plugin hook '{hook_name}' failed: {str(e)}",
                            exc_info=True
                        )
        return context
    
    def _prepare_system_message(self) -> Optional[Message]:
        """
        Prepare system message with agent configuration
        
        Returns:
            System message if configuration exists
        """
        parts = []
        
        if self.config.introduction:
            parts.append(f"### Introduction: {self.config.introduction}")

        if self.config.backstory:
            parts.append(f"### Backstory: {self.config.backstory}")
        
        if self.config.goal:
            parts.append(f"### Goal: {self.config.goal}")

        if self.config.knowledge_cutoff:
            parts.append(f"### Knowledge cutoff: {self.config.knowledge_cutoff}")

        if self.config.current_time:
            parts.append(f"### Current time: {self.config.current_time}")
        
        if self.config.instruction:
            parts.append(f"### Instructions: {self.config.instruction}")
        
        if parts:
            return Message(
                role="system",
                content="\n\n---\n\n".join(parts)
            )
        
        return None
    
    def _update_or_add_system_message(
        self,
        messages: List[Message]
    ) -> List[Message]:
        """
        Update existing system message or add new one
        
        Args:
            messages: Current messages (can be Message objects or dicts)
            
        Returns:
            Updated messages
        """
        system_msg = self._prepare_system_message()
        if not system_msg:
            return messages
        
        # Check if system message exists (handle both dict and Message objects)
        has_system = any(
            (msg.get("role") if isinstance(msg, dict) else msg.role) == "system"
            for msg in messages
        )
        
        if has_system:
            # Update existing system message
            updated_messages = []
            for msg in messages:
                msg_role = msg.get("role") if isinstance(msg, dict) else msg.role
                msg_content = msg.get("content") if isinstance(msg, dict) else msg.content
                
                if msg_role == "system":
                    # Append to existing system message
                    updated_content = msg_content + "\n\n---\n\n" + system_msg.content
                    updated_messages.append(
                        Message(role="system", content=updated_content)
                    )
                else:
                    updated_messages.append(msg)
            return updated_messages
        else:
            # Add new system message at the beginning
            return [system_msg] + messages
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get agent statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "name": self.name,
            "instance_id": self.instance_id,
            "type": self.__class__.__name__,
            "status": self.status.value,
            "execution_count": self._execution_count,
            "total_tokens_used": self._total_tokens_used,
            "tools_registered": len(self.tool_registry),
            "workers_attached": len(self._workers),
            "plugins_installed": len(self._plugins),
            "tool_execution_stats": self.tool_executor.get_statistics()
        }
    
    def reset_statistics(self) -> None:
        """Reset agent statistics"""
        self._execution_count = 0
        self._total_tokens_used = 0
        self.tool_executor.clear_history()
        logger.debug(f"Statistics reset for agent '{self.name}'")
    
    @abstractmethod
    async def execute(
        self,
        messages: List[Message],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the agent
        
        Args:
            messages: Input messages
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result in OpenAI format
        """
        pass
    
    @abstractmethod
    def create_worker(
        self,
        name: str,
        **config_kwargs
    ) -> 'BaseAgent':
        """
        Create a new worker agent
        
        Args:
            name: Worker name
            **config_kwargs: Worker configuration
            
        Returns:
            Created worker agent
        """
        pass
    
    def enable_tracing(self) -> ExecutionTracer:
        """
        Enable execution tracing for this agent instance.
        
        Returns:
            ExecutionTracer instance
        """
        if not self._tracer:
            self._tracer = ExecutionTracer(enabled=True)
            log_agent(self.name, "Tracing enabled", "debug")
        return self._tracer
    
    def disable_tracing(self) -> None:
        """Disable execution tracing for this agent"""
        if self._tracer:
            self._tracer.enabled = False
            log_agent(self.name, "Tracing disabled", "debug")
    
    def visualize(
        self,
        format: str = "mermaid",
        output: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Visualize the last execution (only if tracing was enabled).
        
        Args:
            format: Output format ('mermaid', 'html', 'json', 'custom')
            output: Optional file path to save visualization
            **kwargs: Additional format-specific options
        
        Returns:
            Visualization as string (Mermaid, HTML, or JSON)
        """
        if not self._tracer or not self._tracer.enabled:
            return "No execution data available. Enable tracing with trace=True or enable_tracing()"
        
        viz = ExecutionVisualizer(self._tracer)
        
        # Generate visualization
        if format == "mermaid":
            result = viz.generate_mermaid()
        elif format == "html":
            result = viz.generate_html()
        elif format == "json":
            result = json.dumps(viz.generate_json(kwargs.get("include_styles", True)))
        elif format == "custom" and "formatter" in kwargs:
            result = viz.export_custom(kwargs["formatter"])
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save to file if requested
        if output:
            with open(output, "w") as f:
                f.write(result)
            logger.debug(f"Visualization saved to {output}")
        
        return result
    
    def inspect(self) -> PipelineInspector:
        """
        Create a pipeline inspector for this agent.
        
        Returns:
            PipelineInspector instance for analyzing agent structure
        """
        return PipelineInspector(self)
    
    def visualize_pipeline(
        self,
        format: str = "console",
        output: Optional[str] = None
    ) -> str:
        """
        Visualize the static pipeline structure (before execution).
        
        Args:
            format: Visualization format ('console', 'mermaid', 'json')
            output: Optional file path to save output
        
        Returns:
            Pipeline visualization as string
        """
        inspector = self.inspect()
        return inspector.visualize(format, output)
    
    def get_tracer_stats(self) -> Dict[str, Any]:
        """
        Get execution tracer statistics.
        
        Returns:
            Tracer statistics if enabled, empty dict otherwise
        """
        if self._tracer and self._tracer.enabled:
            return self._tracer.get_statistics()
        return {"enabled": False}
    
    def __repr__(self) -> str:
        """String representation"""
        tracing = " [TRACING]" if self._tracer and self._tracer.enabled else ""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"model='{self.config.model}', "
            f"tools={len(self.tool_registry)}, "
            f"workers={len(self._workers)}){tracing}"
        )
