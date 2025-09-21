"""
Worker agent implementation for AgentRouter SDK
"""

import json
from typing import Any, Dict, List, Optional

from agentrouter.agents.base import BaseAgent
from agentrouter.exceptions import (
    ConfigurationError,
    ExecutionError,
    MaxIterationsError,
    ValidationError,
)
from agentrouter.types import (
    AgentStatus,
    ExecutionContext,
    FunctionDefinition,
    Message,
    RegisteredTool,
    ToolCall,
    ToolChoice,
    ToolDefinition,
    WorkerTaskSchema,
)
from agentrouter.validators.message_flow import MessageFlowValidator
from agentrouter.utils.error_formatter import ErrorFormatter, IsolatedWorkerErrorHandler
from agentrouter.utils.message_transformer import MessageTransformer
from agentrouter.utils.openai_integration import OpenAIResponseGenerator
from agentrouter.utils.logging import (
    log_agent, log_iteration, log_completion, log_stage,
    get_logger, is_debug_mode
)


logger = get_logger(__name__)


class WorkerAgent(BaseAgent):
    """
    Worker agent for specialized task execution
    """
    
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        task_schema: Optional[Dict[str, Any]] = None,
        **config_kwargs
    ):
        """
        Initialize worker agent
        
        Args:
            name: Worker agent name
            api_key: API key (optional, can inherit from parent)
            model: Model to use (optional, can inherit from parent)
            task_schema: Schema for tasks this worker can handle
            **config_kwargs: Additional configuration options
        """
        # Import validator
        from agentrouter.validators.format_validators import AgentParameterValidator, FormatValidator
        
        # Workers can have optional API key and model (inherit from parent)
        if not api_key:
            api_key = "inherited"  # Placeholder, will be replaced by parent's
        
        if not model:
            model = "inherited"  # Placeholder, will be replaced by parent's
        
        # Prepare all parameters for validation
        all_params = {
            "name": name,
            "api_key": api_key,
            "model": model,
            "task_schema": task_schema,
            **config_kwargs
        }
        
        # Validate ALL parameters with strict format checking
        try:
            validated_params = AgentParameterValidator.validate_worker_params(all_params)
        except ValueError as e:
            raise ValidationError(
                f"Worker agent initialization failed: {str(e)}"
            )
        
        # Extract validated task_schema before passing to parent
        validated_task_schema = validated_params.pop("task_schema", None)
        
        # Validate task schema if provided
        if validated_task_schema is not None:
            # Create a tool-like schema for validation
            tool_schema = {
                "type": "function",
                "function": {
                    "name": validated_params.get("name", name),
                    "description": validated_params.get("role", f"Worker agent: {name}"),
                    "parameters": validated_task_schema
                }
            }
            try:
                FormatValidator.validate_tool_schema(tool_schema)
            except ValueError as e:
                raise ValidationError(
                    f"Worker task_schema validation failed: {str(e)}"
                )
        
        # Extract base parameters for parent class
        base_name = validated_params.pop("name")
        base_api_key = validated_params.pop("api_key")
        base_model = validated_params.pop("model")
        
        super().__init__(base_name, base_api_key, base_model, **validated_params)
        
        # Worker-specific initialization
        self.task_schema = validated_task_schema
        self._sub_worker_tools: Dict[str, RegisteredTool] = {}
        
        # Workers can have their own workers (recursive)
        self._is_standalone = base_api_key != "inherited"
        
        # Log initialization (already logged in base class, just debug info here)
        logger.debug(f"WorkerAgent '{base_name}' ready")
    
    async def execute(
        self,
        messages: List[Message],
        streaming: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the worker agent
        
        Args:
            messages: Input messages in OpenAI format
            streaming: Whether to stream the response
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result in OpenAI format
        """
        try:
            # Inherit parent's config if not standalone
            if not self._is_standalone and self._parent_agent:
                self._inherit_parent_config()
            
            # Apply before execution plugins
            context = await self._apply_plugin_hook(
                "on_before_execution",
                {"messages": messages, "agent_name": self.name}
            )
            messages = context.get("messages", messages)
            
            # Update status
            self.status = AgentStatus.RUNNING
            self._execution_count += 1
            
            # Create execution context
            self._execution_context = ExecutionContext(
                messages=messages,
                tools=self._get_all_tool_definitions(),
                current_iteration=0,
                max_iterations=self.config.max_iterations,
                agent_name=self.name,
                agent_status=AgentStatus.RUNNING
            )
            
            # Execute workflow (similar to manager but scoped)
            result = await self._execute_workflow(messages, streaming)
            
            # Update status
            self.status = AgentStatus.COMPLETED
            
            # Apply after execution plugins
            context = await self._apply_plugin_hook(
                "on_after_execution",
                {
                    "messages": messages,
                    "result": result,
                    "agent_name": self.name
                }
            )
            result = context.get("result", result)
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            log_agent(self.name, f"Execution failed: {str(e)}", "error")
            if is_debug_mode():
                logger.error(f"Full error details:", exc_info=True)
            
            # Apply error plugins
            context = await self._apply_plugin_hook(
                "on_error",
                {
                    "error": e,
                    "messages": messages,
                    "agent_name": self.name
                }
            )
            
            raise ExecutionError(
                f"Worker execution failed: {str(e)}",
                agent_name=self.name
            ) from e
    
    def _inherit_parent_config(self) -> None:
        """
        Inherit configuration from parent agent
        """
        if not self._parent_agent:
            return
        
        parent_config = self._parent_agent.config
        
        # Inherit API key
        if self.config.api_key == "inherited":
            self.config.api_key = parent_config.api_key
            self.plan_api.api_key = parent_config.api_key
            self.tool_call_api.api_key = parent_config.api_key
        
        # Inherit model
        if self.config.model == "inherited":
            self.config.model = parent_config.model
        
        # Inherit other configs if not set
        if not self.config.provider:
            self.config.provider = parent_config.provider
        
        if not self.config.knowledge_cutoff:
            self.config.knowledge_cutoff = parent_config.knowledge_cutoff
        
        if not self.config.current_time:
            self.config.current_time = parent_config.current_time
        
        # Update API clients with inherited configuration
        self.plan_api.timeout = self.config.api_timeout
        self.plan_api.max_retries = self.config.max_retries
        self.plan_api.retry_delay = self.config.retry_delay
        self.plan_api.retry_multiplier = self.config.retry_multiplier
        self.plan_api.retry_max_wait = self.config.retry_max_wait
        
        self.tool_call_api.timeout = self.config.api_timeout
        self.tool_call_api.max_retries = self.config.max_retries
        self.tool_call_api.retry_delay = self.config.retry_delay
        self.tool_call_api.retry_multiplier = self.config.retry_multiplier
        self.tool_call_api.retry_max_wait = self.config.retry_max_wait

        # Ensure base URL is resolved after inheriting configuration
        self._initialize_provider_base_url()
    
    async def _execute_workflow(
        self,
        messages: List[Message],
        streaming: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the worker's workflow
        
        Args:
            messages: Current messages
            streaming: Whether to stream responses
            
        Returns:
            Final result in OpenAI format
        """
        current_messages = list(messages)
        iterations = 0
        
        while iterations < self.config.max_iterations:
            iterations += 1
            log_iteration(iterations, self.config.max_iterations, self.name)
            
            # Step 1: Call Plan API
            if self._tracer:
                # Get nesting depth
                depth = 1  # Default depth
                parent = self._parent_agent
                while parent and hasattr(parent, '_parent_agent'):
                    depth += 1
                    parent = parent._parent_agent
                
                self._tracer.record(
                    'api_call',
                    f'Plan API Call #{iterations}',
                    'plan_api',  # Always 'plan_api' for any Plan API call
                    {
                        'caller': self.name,  # Who's calling (metadata only)
                        'iteration': iterations,
                        'agent_type': 'worker',
                        'depth': depth  # Nesting depth for info only
                    }
                )
            
            plan_response = await self._call_plan_api(current_messages)
            
            # Check if tool call is needed
            if self.plan_api.should_call_tool(plan_response):
                # Add plan response to messages
                plan_message = self._extract_message_from_response(plan_response)
                current_messages.append(plan_message)
                
                # Get tool choice
                tool_choice = self.plan_api.get_tool_choice(plan_response)
                
                # Validate before Tool Call API
                try:
                    self._validate_for_tool_call(current_messages, plan_response, tool_choice)
                except ValidationError as e:
                    logger.error(f"Tool Call API validation failed: {str(e)}")
                    raise
                
                # Step 2: Call Tool Call API
                if self._tracer:
                    # Get nesting depth
                    depth = 1
                    parent = self._parent_agent
                    while parent and hasattr(parent, '_parent_agent'):
                        depth += 1
                        parent = parent._parent_agent
                    
                    self._tracer.record(
                        'api_call',
                        f'Tool Call API #{iterations}',
                        'tool_call_api',  # Always 'tool_call_api' for any Tool Call API
                        {
                            'caller': self.name,  # Who's calling (metadata only)
                            'iteration': iterations,
                            'tool_choice': tool_choice.name if hasattr(tool_choice, 'name') else str(tool_choice),
                            'agent_type': 'worker',
                            'depth': depth  # Nesting depth for info only
                        }
                    )
                
                tool_response = await self._call_tool_call_api(
                    current_messages,
                    tool_choice
                )
                
                # CRITICAL FIX: Add assistant message with tool_calls to messages
                # This must happen BEFORE executing tools to maintain proper message order
                tool_call_message = self._extract_tool_call_message(tool_response)
                current_messages.append(tool_call_message)
                if is_debug_mode():
                    logger.debug(f"Worker added tool call message with {len(tool_call_message.tool_calls) if tool_call_message.tool_calls else 0} tool calls")
                
                # Extract tool calls
                tool_calls = self.tool_call_api.extract_tool_calls(tool_response)
                
                # Step 3: Execute tools with guaranteed responses
                tool_results = await self._execute_tools(tool_calls)
                
                # Add tool results to messages - ensure all have proper responses
                for result in tool_results:
                    # Ensure we have a proper tool response even on failure
                    tool_message = ErrorFormatter.ensure_tool_response(
                        tool_call_id=result.get("tool_call_id"),
                        tool_name=result.get("tool_name", "unknown"),
                        result=result if result.get("success") else None,
                        error=Exception(result.get("content", {}).get("error", "Unknown error")) if not result.get("success") else None,
                        is_worker=False  # This is for sub-tools, not sub-workers
                    )
                    
                    # Validate tool response
                    try:
                        MessageFlowValidator.validate_tool_response(
                            tool_message,
                            result.get("tool_call_id")
                        )
                    except ValidationError as e:
                        if is_debug_mode():
                            logger.warning(f"Tool response validation warning: {str(e)}")
                    
                    current_messages.append(tool_message)
                
            else:
                # No tool call needed, prepare final response
                log_stage("Preparing final response")
                
                # Record final response generation
                if self._tracer:
                    self._tracer.record(
                        'final_response',
                        'Generate Final Response',
                        'final_response',
                        {
                            'iteration': iterations,
                            'agent': self.name
                        }
                    )
                
                # Generate final response (no forced flag needed)
                final_response = await self._generate_final_response(
                    current_messages,
                    plan_response,
                    streaming,
                    forced=False
                )
                
                # CRITICAL FIX: Defensive null check for final_response
                if final_response is None:
                    logger.error(f"WorkerAgent '{self.name}' - _generate_final_response returned None")
                    raise ExecutionError(
                        "Final response generation returned None",
                        agent_name=self.name
                    )
                
                # Update token usage
                if "usage" in final_response:
                    self._total_tokens_used += final_response["usage"].get("total_tokens", 0)
                
                return final_response
        
        # Max iterations reached - FORCE final response instead of throwing error
        logger.warning(f"Max iterations ({self.config.max_iterations}) reached - forcing final response")
        
        # Check if last message has pending tool calls that need to be executed
        if current_messages:
            last_msg = current_messages[-1]
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                logger.debug("Executing pending tool calls before forced final response")
                # Execute the pending tool calls
                tool_calls = []
                for tc in last_msg.tool_calls:
                    if isinstance(tc, dict):
                        tool_calls.append(ToolCall(**tc))
                    else:
                        tool_calls.append(tc)
                
                # Execute tools
                tool_results = await self._execute_tools(tool_calls)
                
                # Add tool results
                for result in tool_results:
                    tool_name = result.get("tool_name", "unknown")
                    tool_message = ErrorFormatter.ensure_tool_response(
                        tool_call_id=result.get("tool_call_id"),
                        tool_name=tool_name,
                        result=result if result.get("success") else None,
                        error=Exception(result.get("content", {}).get("error", "Unknown error")) if not result.get("success") else None,
                        is_worker=tool_name in self._sub_worker_tools
                    )
                    current_messages.append(tool_message)
        
        # Record forced final response
        if self._tracer:
            self._tracer.record(
                'final_response',
                'Generate Final Response (Forced - Max Iterations)',
                'final_response',
                {
                    'iteration': iterations,
                    'agent': self.name,
                    'forced': True,
                    'reason': 'max_iterations_reached'
                }
            )
        
        # Generate forced final response
        final_response = await self._generate_final_response(
            current_messages,
            None,  # No plan response when forcing
            streaming,
            forced=True
        )
        
        # CRITICAL FIX: Defensive null check for final_response
        if final_response is None:
            logger.error(f"WorkerAgent '{self.name}' - _generate_final_response returned None (forced)")
            raise ExecutionError(
                "Forced final response generation returned None",
                agent_name=self.name
            )
        
        # Update token usage
        if "usage" in final_response:
            self._total_tokens_used += final_response["usage"].get("total_tokens", 0)
        
        return final_response
    
    async def _call_plan_api(
        self,
        messages: List[Message]
    ) -> Any:
        """
        Call the Plan API
        
        Args:
            messages: Current messages
            
        Returns:
            Plan API response
        """
        # Comprehensive validation before Plan API call
        try:
            self._validate_for_plan_api(messages)
        except ValidationError as e:
            logger.error(f"Plan API validation failed: {str(e)}")
            # If last message is from plan agent, we cannot recover - throw error
            raise ValidationError(
                f"Cannot call Plan API: {str(e)}",
                field="messages",
                details={"agent": self.name, "validation_error": str(e)}
            ) from e
        
        messages_with_system = self._update_or_add_system_message(messages)

        # Get all available tools
        tools = self._get_all_tool_definitions()

        # Call Plan API
        response = await self.plan_api.create_plan(
            messages=messages_with_system,
            model=self.config.model,
            provider=self.config.provider,
            tools=tools,
            introduction=self.config.introduction,
            instruction=self.config.instruction or "",
            knowledge_cutoff=self.config.knowledge_cutoff,
            backstory=self.config.backstory,
            goal=self.config.goal,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response
    
    async def _call_tool_call_api(
        self,
        messages: List[Message],
        tool_choice: ToolChoice
    ) -> Any:
        """
        Call the Tool Call API
        
        Args:
            messages: Current messages
            tool_choice: Tool choice from Plan API
            
        Returns:
            Tool Call API response
        """
        # Prepare messages with a single leading system prompt
        messages_with_system = self._update_or_add_system_message(messages)

        # Get all available tools
        tools = self._get_all_tool_definitions()

        # Call Tool Call API
        response = await self.tool_call_api.create_tool_calls(
            messages=messages_with_system,
            tools=tools,
            tool_choice=tool_choice,
            model=self.config.model,
            provider=self.config.provider,
            introduction=self.config.introduction,
            instruction=self.config.instruction or "",
            knowledge_cutoff=self.config.knowledge_cutoff,
            backstory=self.config.backstory,
            goal=self.config.goal,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response
    
    async def _execute_tools(
        self,
        tool_calls: List[ToolCall]
    ) -> List[Dict[str, Any]]:
        """
        Execute tool calls
        
        Args:
            tool_calls: List of tool calls to execute
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.function.get("name")
            
            # Check if it's a sub-worker tool
            if tool_name in self._sub_worker_tools:
                # Record sub-worker execution (still 'worker' type for consistent color)
                if self._tracer:
                    # Calculate depth
                    depth = 1
                    parent = self._parent_agent
                    while parent and hasattr(parent, '_parent_agent'):
                        depth += 1
                        parent = parent._parent_agent
                    
                    self._tracer.record(
                        'agent_execution',
                        tool_name,
                        'worker',  # Always 'worker' for ANY worker agent
                        {
                            'arguments': tool_call.function.get("arguments"),
                            'parent': self.name,
                            'depth': depth + 1  # Sub-worker is one level deeper
                        }
                    )
                
                # Execute sub-worker
                result = await self._execute_sub_worker_tool(tool_call)
            else:
                # Record regular tool execution
                if self._tracer:
                    self._tracer.record(
                        'tool_execution',
                        tool_name,
                        'tool',  # Regular tool execution
                        {
                            'arguments': tool_call.function.get("arguments"),
                            'executor': self.name
                        }
                    )
                
                # Execute regular tool
                result = await self.tool_executor.execute(tool_call)
            
            results.append(result)
        
        return results
    
    async def _execute_sub_worker_tool(
        self,
        tool_call: ToolCall
    ) -> Dict[str, Any]:
        """
        Execute a sub-worker agent as a tool with complete isolation
        
        Args:
            tool_call: Tool call for sub-worker
            
        Returns:
            Sub-worker execution result (isolated - no internal details exposed)
        """
        tool_name = tool_call.function.get("name")
        worker_tool = self._sub_worker_tools.get(tool_name)
        
        if not worker_tool:
            # Worker not found - return clean error
            return ErrorFormatter.format_worker_error(
                worker_name=tool_name,
                tool_call_id=tool_call.id,
                error=None  # No internal details
            )
        
        # Get the sub-worker agent
        sub_worker = worker_tool.function  # The worker agent is stored as the function
        
        # Use IsolatedWorkerErrorHandler for complete isolation
        parent_messages = []
        if self._execution_context and sub_worker.config.access_parent_history:
            parent_messages = self._execution_context.messages
        
        # Execute with complete isolation using configured timeout
        result = await IsolatedWorkerErrorHandler.execute_worker_isolated(
            worker=sub_worker,
            tool_call=tool_call,
            parent_messages=parent_messages,
            timeout=self.config.worker_timeout
        )
        
        return result
    
    async def _generate_final_response(
        self,
        messages: List[Message],
        plan_response: Any,
        streaming: bool = False,
        forced: bool = False
    ) -> Dict[str, Any]:
        """
        Generate final response using OpenAI SDK
        
        Args:
            messages: All messages including iterations
            plan_response: Last plan response (can be None if forced)
            streaming: Whether to stream response
            forced: Whether this is a forced final response due to max iterations
            
        Returns:
            Final response in OpenAI format
        """
        try:
            # Debug logging for complete messages when debug mode is enabled
            if is_debug_mode():
                logger.debug(f"WorkerAgent '{self.name}' - Original messages before transformation:")
                for i, msg in enumerate(messages):
                    msg_role = msg.role if hasattr(msg, 'role') else msg.get('role', 'unknown')
                    msg_content = (msg.content if hasattr(msg, 'content') else msg.get('content', ''))[:100]
                    msg_type = getattr(msg, 'type', None) or (msg.get('type', None) if isinstance(msg, dict) else None)
                    logger.debug(f"  [{i}] Role: {msg_role}, Type: {msg_type}, Content: {msg_content}...")
            
            # Transform messages for final response
            if forced:
                # When forced, we need to handle message cleanup differently
                prepared_messages = MessageTransformer.prepare_forced_final_messages(messages)
            else:
                prepared_messages = MessageTransformer.prepare_for_final_response(
                    messages,
                    plan_response
                )
            
            # CRITICAL FIX: Defensive null checking for prepared_messages
            if prepared_messages is None:
                logger.error(f"WorkerAgent '{self.name}' - Message transformation returned None")
                raise ExecutionError(
                    "Message transformation failed - returned None instead of message list",
                    agent_name=self.name,
                    details={"original_messages_count": len(messages), "forced": forced}
                )
            
            if not isinstance(prepared_messages, list):
                logger.error(f"WorkerAgent '{self.name}' - Message transformation returned invalid type: {type(prepared_messages)}")
                raise ExecutionError(
                    f"Message transformation failed - returned {type(prepared_messages)} instead of list",
                    agent_name=self.name,
                    details={"returned_type": str(type(prepared_messages)), "forced": forced}
                )
            
            # Debug logging for prepared messages when debug mode is enabled
            if is_debug_mode():
                logger.debug(f"WorkerAgent '{self.name}' - Prepared messages after transformation:")
                for i, msg in enumerate(prepared_messages):
                    msg_role = msg.role if hasattr(msg, 'role') else msg.get('role', 'unknown')
                    msg_content = (msg.content if hasattr(msg, 'content') else msg.get('content', ''))[:100]
                    msg_type = getattr(msg, 'type', None) or (msg.get('type', None) if isinstance(msg, dict) else None)
                    logger.debug(f"  [{i}] Role: {msg_role}, Type: {msg_type}, Content: {msg_content}...")
            
            # Check if any message contains tool_calls or has role="tool"
            # CRITICAL FIX: Safe iteration with proper null checking
            has_tool_interactions = False
            if prepared_messages:  # Ensure not empty
                try:
                    has_tool_interactions = any(
                        (hasattr(msg, 'tool_calls') and msg.tool_calls) or
                        (hasattr(msg, 'role') and (msg.role == 'tool' or (hasattr(msg.role, 'value') and msg.role.value == 'tool'))) or
                        (isinstance(msg, dict) and msg.get('role') == 'tool')
                        for msg in prepared_messages
                    )
                except Exception as e:
                    logger.error(f"WorkerAgent '{self.name}' - Error checking tool interactions: {str(e)}")
                    raise ExecutionError(
                        f"Failed to analyze message interactions: {str(e)}",
                        agent_name=self.name,
                        details={"messages_count": len(prepared_messages)}
                    ) from e
            
            # Append final instructions if there were tool interactions
            if has_tool_interactions and prepared_messages:
                self._append_final_instructions(prepared_messages)
            
            # Validate messages for final response
            MessageFlowValidator.validate_for_final_response(prepared_messages)
            
            # Check if we should use OpenAI SDK
            # CRITICAL FIX: Proper null checking for provider
            use_openai = (
                (self.config.provider and "openai" in self.config.provider.lower()) or
                self.config.base_url
            )

            if not use_openai:
                logger.error(
                    f"WorkerAgent '{self.name}' - Final response generation requires a configured OpenAI-compatible provider"
                )
                raise ExecutionError(
                    "Final response generation is unavailable without an OpenAI-compatible provider or base_url",
                    agent_name=self.name,
                    details={
                        "provider": self.config.provider,
                        "base_url": self.config.base_url
                    }
                )

            try:
                # Use OpenAI SDK for final response
                generator = OpenAIResponseGenerator(
                    api_key=self.config.api_key,
                    model=self.config.model,
                    base_url=self.config.base_url
                )

                # IMPORTANT: Add system message with agent's parameters
                # This is needed because OpenAI SDK doesn't have separate parameters
                # for instruction, backstory, goal, etc. like Plan/Tool Call APIs do
                prepared_messages = self._update_or_add_system_message(prepared_messages)

                # IMPORTANT: Never pass tools to final response
                response = await generator.generate_final_response(
                    messages=prepared_messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    streaming=streaming
                    # NO tools parameter here!
                )

                return response

            except Exception as e:
                logger.error(
                    f"WorkerAgent '{self.name}' - OpenAI final response generation failed: {str(e)}",
                    exc_info=is_debug_mode()
                )
                raise ExecutionError(
                    f"OpenAI final response generation failed: {str(e)}",
                    agent_name=self.name
                ) from e

        except Exception as e:
            logger.error(f"Final response generation failed: {str(e)}")
            # Re-raise the error instead of returning a fallback
            raise ExecutionError(
                f"Failed to generate final response: {str(e)}",
                agent_name=self.name
            ) from e
    
    def _append_final_instructions(self, messages: List[Message]) -> None:
        """
        Append final instructions to the last message when tool interactions occurred
        
        Args:
            messages: Message list to modify (modified in place)
        """
        if not messages:
            return
        
        instructions_text = """\n\n---\n\n<IMPORTANT>
You are now providing your FINAL response directly to the user. You CANNOT call any new tools under any circumstances.

Remember: The user cannot see any of your previous tool calls, function invocations, or their responses. To them, this is your first and only message.

## No Tool Calling
- You **cannot** call any new tools now.
- If you don't have enough information because a previous attempt failed, you still cannot call new tools.

**Instead:**
- Say **sorry**.
- Briefly explain the reason in simple terms, without mentioning technical details or tool names, since the user does not have knowledge about tools and there existence.
- If you have enough information, then generate the response to help the user as best as possible.

### Follow these guidelines:

1. **Opening Based on Context:**
- If WE made an error or misunderstood: Start with a warm, sincere apology
- If a service/system had issues: Skip apologies. Instead, briefly acknowledge what happened using everyday language (e.g., "The search service had trouble finding that information" not "The web_search tool returned an error")

2. **Explain Simply:**
- Use plain, conversational language anyone can understand
- Avoid technical terms like "tools," "functions," "parameters," "API," etc.
- Use context-appropriate alternatives: service, system, search, database, provider, platform, etc.
- Keep explanations brief and relevant to what the user needs to know

3. **Provide What You Can:**
- If you have partial information: Share it clearly, noting any limitations
- If you cannot complete the request: Politely explain this and suggest alternatives when possible
- Focus on being helpful with whatever information is available
   
5. **Address their question directly**

Remember: This is your only chance to help the user with their current query. Make it count.
</IMPORTANT>"""
        
        last_msg = messages[-1]
        
        # Handle different content types
        if isinstance(last_msg.content, str):
            # Simple string content
            last_msg.content += instructions_text
        elif isinstance(last_msg.content, list):
            # Multimodal content (list of content items)
            text_found = False
            for i in range(len(last_msg.content) - 1, -1, -1):
                item = last_msg.content[i]
                if isinstance(item, dict) and item.get('type') == 'text':
                    # Append to last text item
                    item['text'] = item.get('text', '') + instructions_text
                    text_found = True
                    break
            
            if not text_found:
                # No text item found, add new text item
                last_msg.content.append({
                    'type': 'text',
                    'text': instructions_text
                })
        else:
            # Unknown content type, try to convert to string and append
            try:
                last_msg.content = str(last_msg.content) + instructions_text
            except Exception as e:
                if is_debug_mode():
                    logger.warning(f"Could not append instructions to content of type {type(last_msg.content)}: {e}")
    
    def _get_all_tool_definitions(self) -> List[ToolDefinition]:
        """
        Get all tool definitions including sub-workers as tools
        
        Returns:
            List of all tool definitions
        """
        # Get regular tools
        tool_defs = self.tool_registry.get_tool_definitions()
        
        # Add sub-worker tools
        for worker_tool in self._sub_worker_tools.values():
            tool_defs.append(worker_tool.schema)
        
        return tool_defs
    
    def _extract_message_from_response(self, response: Any) -> Message:
        """
        Extract message from API response, preserving the type field for Plan API responses
        
        Args:
            response: API response
            
        Returns:
            Extracted message with type preserved
        """
        if hasattr(response, 'choices') and response.choices:
            msg_data = response.choices[0].message
            
            # Build message with required fields
            message_dict = {
                "role": "assistant",
                "content": msg_data.content if hasattr(msg_data, 'content') else ""
            }
            
            # Preserve the type field for Plan API messages
            if hasattr(msg_data, 'type'):
                message_dict["type"] = msg_data.type
            
            # IMPORTANT: Preserve tool_choice for Tool Call API
            if hasattr(msg_data, 'tool_choice'):
                message_dict["tool_choice"] = msg_data.tool_choice
            
            # Preserve other Plan API response fields
            if hasattr(msg_data, 'plan'):
                message_dict["plan"] = msg_data.plan
            if hasattr(msg_data, 'reasoning'):
                message_dict["reasoning"] = msg_data.reasoning
            if hasattr(msg_data, 'agent_status'):
                message_dict["agent_status"] = msg_data.agent_status
            
            return Message(**message_dict)
        
        return Message(role="assistant", content="")
    
    def _extract_tool_call_message(self, response: Any) -> Message:
        """
        Extract assistant message with tool_calls from Tool Call API response.
        This is critical for maintaining proper message order.
        
        Args:
            response: Tool Call API response
            
        Returns:
            Assistant message with tool_calls
        """
        if hasattr(response, 'choices') and response.choices:
            msg_data = response.choices[0].message
            
            # Build message with required fields
            message_dict = {
                "role": "assistant",
                "content": msg_data.content if hasattr(msg_data, 'content') else ""
            }
            
            # CRITICAL: Include tool_calls from Tool Call API response
            if hasattr(msg_data, 'tool_calls') and msg_data.tool_calls:
                # Convert tool_calls to proper format
                tool_calls = []
                for tc in msg_data.tool_calls:
                    if isinstance(tc, dict):
                        tool_calls.append(tc)
                    else:
                        # Convert object to dict
                        tool_call_dict = {
                            "id": tc.id if hasattr(tc, 'id') else tc.get('id'),
                            "type": tc.type if hasattr(tc, 'type') else tc.get('type', 'function'),
                            "function": tc.function if hasattr(tc, 'function') else tc.get('function')
                        }
                        # Handle index if present
                        if hasattr(tc, 'index'):
                            tool_call_dict["index"] = tc.index
                        elif isinstance(tc, dict) and 'index' in tc:
                            tool_call_dict["index"] = tc['index']
                        tool_calls.append(tool_call_dict)
                
                message_dict["tool_calls"] = tool_calls
            
            # Preserve type if present (for tracking)
            if hasattr(msg_data, 'type'):
                message_dict["type"] = msg_data.type
            
            return Message(**message_dict)
        
        # Should not happen for valid Tool Call API response
        error_msg = "Tool Call API response missing expected structure"
        logger.error(error_msg)
        raise ExecutionError(
            error_msg,
            agent_name=self.name,
            details={"response": str(response) if response else "None"}
        )
    
    def _validate_for_plan_api(self, messages: List[Message]) -> None:
        """
        Comprehensive validation before calling Plan API.
        
        Args:
            messages: Current messages
            
        Raises:
            ValidationError: If validation fails
        """
        # Use existing validator
        MessageFlowValidator.validate_for_plan_api(messages)
        
        # Additional validation: Check message sequence integrity
        if messages:
            last_msg = messages[-1]
            # Check if last message has problematic type
            if hasattr(last_msg, 'type') and last_msg.type == 'agent_plan':
                raise ValidationError(
                    "Cannot call Plan API: Last message is from Plan API (type=agent_plan). "
                    "A tool response or user message is required before calling Plan API again.",
                    field="messages",
                    details={"last_message_type": last_msg.type}
                )
            
            # Check for unanswered tool calls
            for i in range(len(messages) - 1, -1, -1):
                msg = messages[i]
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Found tool calls, check if they have responses
                    tool_call_ids = set()
                    for tc in msg.tool_calls:
                        tc_id = tc.get('id') if isinstance(tc, dict) else (tc.id if hasattr(tc, 'id') else None)
                        if tc_id:
                            tool_call_ids.add(tc_id)
                    
                    # Check subsequent messages for tool responses
                    answered_ids = set()
                    for j in range(i + 1, len(messages)):
                        response_msg = messages[j]
                        # Handle different role formats
                        msg_role = response_msg.role if hasattr(response_msg, 'role') else response_msg.get('role')
                        if hasattr(msg_role, 'value'):
                            msg_role = msg_role.value
                        if msg_role == 'tool' and (hasattr(response_msg, 'tool_call_id') and response_msg.tool_call_id or isinstance(response_msg, dict) and response_msg.get('tool_call_id')):
                            tool_id = response_msg.tool_call_id if hasattr(response_msg, 'tool_call_id') else response_msg.get('tool_call_id')
                            answered_ids.add(tool_id)
                    
                    unanswered = tool_call_ids - answered_ids
                    if unanswered:
                        raise ValidationError(
                            f"Cannot call Plan API: Unanswered tool calls found",
                            field="tool_calls",
                            details={"unanswered_ids": list(unanswered)}
                        )
                    break  # Found and validated the last tool calls
    
    def _validate_for_tool_call(
        self,
        messages: List[Message],
        plan_response: Any,
        tool_choice: ToolChoice
    ) -> None:
        """
        Comprehensive validation before calling Tool Call API.
        
        Args:
            messages: Current messages
            plan_response: Last Plan API response
            tool_choice: Tool choice from Plan API
            
        Raises:
            ValidationError: If validation fails
        """
        # Check last message is from Plan API
        if not messages:
            raise ValidationError("Messages cannot be empty for Tool Call API")
        
        last_msg = messages[-1]
        if not hasattr(last_msg, 'type') or last_msg.type != 'agent_plan':
            raise ValidationError(
                "Cannot call Tool Call API: Last message must be from Plan API (type=agent_plan)",
                field="messages",
                details={"last_message_type": getattr(last_msg, 'type', 'unknown')}
            )
        
        # Verify Plan API response indicates tool call is needed
        if hasattr(plan_response, 'choices') and plan_response.choices:
            choice = plan_response.choices[0]
            if hasattr(choice, 'message'):
                message = choice.message
                
                # Check agent status
                if hasattr(message, 'agent_status'):
                    if message.agent_status == 'preparing_final_response':
                        raise ValidationError(
                            "Cannot call Tool Call API: Plan indicates preparing final response",
                            field="agent_status",
                            details={"agent_status": message.agent_status}
                        )
                
                # Check tool_choice is present
                if not hasattr(message, 'tool_choice') or not message.tool_choice:
                    raise ValidationError(
                        "Cannot call Tool Call API: Plan response does not indicate tool call needed",
                        field="tool_choice",
                        details={"has_tool_choice": False}
                    )
        
        # Validate tool exists
        if tool_choice and tool_choice.name:
            tools = self._get_all_tool_definitions()
            tool_names = [t.function.name for t in tools if hasattr(t, 'function')]
            if tool_choice.name not in tool_names:
                raise ValidationError(
                    f"Tool '{tool_choice.name}' not found in available tools",
                    field="tool_choice",
                    details={
                        "requested_tool": tool_choice.name,
                        "available_tools": tool_names
                    }
                )
    
    def create_worker(
        self,
        name: str,
        role: Optional[str] = None,
        task_schema: Optional[Dict[str, Any]] = None,
        **config_kwargs
    ) -> 'WorkerAgent':
        """
        Create and attach a sub-worker agent
        
        Args:
            name: Sub-worker name
            role: Sub-worker role description
            task_schema: Task schema for the sub-worker
            **config_kwargs: Sub-worker configuration
            
        Returns:
            Created sub-worker agent
        """
        # Inherit API key if not provided
        if "api_key" not in config_kwargs:
            config_kwargs["api_key"] = self.config.api_key
        
        # Inherit model if not provided
        if "model" not in config_kwargs:
            config_kwargs["model"] = self.config.model

        if "provider" not in config_kwargs:
            config_kwargs["provider"] = self.config.provider

        # Inherit configuration settings if not provided
        if "api_timeout" not in config_kwargs:
            config_kwargs["api_timeout"] = self.config.api_timeout
        if "worker_timeout" not in config_kwargs:
            config_kwargs["worker_timeout"] = self.config.worker_timeout
        if "max_retries" not in config_kwargs:
            config_kwargs["max_retries"] = self.config.max_retries
        if "retry_delay" not in config_kwargs:
            config_kwargs["retry_delay"] = self.config.retry_delay
        if "retry_multiplier" not in config_kwargs:
            config_kwargs["retry_multiplier"] = self.config.retry_multiplier
        if "retry_max_wait" not in config_kwargs:
            config_kwargs["retry_max_wait"] = self.config.retry_max_wait
        # Note: max_iterations can be overridden per sub-worker
        if "max_iterations" not in config_kwargs:
            config_kwargs["max_iterations"] = self.config.max_iterations
        
        # Set role
        if role:
            config_kwargs["role"] = role
        
        # Create sub-worker
        sub_worker = WorkerAgent(
            name=name,
            task_schema=task_schema,
            **config_kwargs
        )
        
        # Attach to this worker
        self.attach_worker(sub_worker)
        
        # Register sub-worker as a tool
        self._register_sub_worker_as_tool(sub_worker)
        
        logger.debug(f"Sub-worker '{name}' created under worker '{self.name}'")
        
        return sub_worker
    
    def _register_sub_worker_as_tool(self, sub_worker: 'WorkerAgent') -> None:
        """
        Register a sub-worker agent as a tool with strict name validation
        
        Args:
            sub_worker: Sub-worker agent to register
            
        Raises:
            ValidationError: If sub-worker name doesn't meet tool name requirements
        """
        # Import validator
        from agentrouter.validators.format_validators import FormatValidator
        from agentrouter.exceptions import ValidationError
        
        # Validate sub-worker name meets tool name requirements
        try:
            FormatValidator.validate_tool_name(sub_worker.name, "sub-worker name")
        except ValueError as e:
            raise ValidationError(
                f"Sub-worker name '{sub_worker.name}' cannot be used as tool name.\n"
                f"Sub-worker names must follow tool naming rules:\n"
                f"  - Only lowercase letters, numbers, underscores\n"
                f"  - Start with a letter\n"
                f"  - Length 2-50 characters\n"
                f"  - No spaces or special characters\n"
                f"Original error: {str(e)}"
            )
        
        # Check for duplicate tool name
        if sub_worker.name in self._sub_worker_tools:
            raise ValidationError(
                f"Sub-worker tool '{sub_worker.name}' already registered.\n"
                f"Each sub-worker must have a unique name."
            )
        
        # Create tool definition for sub-worker
        tool_def = sub_worker.get_tool_definition()
        
        # Create registered tool with validated name
        registered_tool = RegisteredTool(
            name=sub_worker.name,
            function=sub_worker,  # Store the sub-worker itself as the function
            schema=tool_def,
            description=f"Sub-worker agent: {sub_worker.config.role or sub_worker.name}"
        )
        
        # Register in sub-worker tools
        self._sub_worker_tools[sub_worker.name] = registered_tool
        
        logger.debug(f"Sub-worker '{sub_worker.name}' registered as tool")
    
    def get_tool_definition(self) -> ToolDefinition:
        """
        Get tool definition for this worker (for parent to use)
        
        Returns:
            Tool definition for this worker
        """
        # Use task schema if provided, otherwise create default
        if self.task_schema:
            parameters = self.task_schema
        else:
            parameters = WorkerTaskSchema(
                type="object",
                properties={
                    "task": {
                        "type": "string",
                        "description": "Task description for the worker"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context for the task"
                    }
                },
                required=["task"]
            ).model_dump()
        
        function_def = FunctionDefinition(
            name=self.name,
            description=self.config.role or f"Worker agent: {self.name}",
            parameters=parameters
        )
        
        return ToolDefinition(
            type="function",
            function=function_def
        )
