"""
Type definitions and Pydantic models for AgentRouter SDK
"""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# Enums
class AgentStatus(str, Enum):
    """Agent execution status"""
    RUNNING = "running"
    PREPARING_FINAL_RESPONSE = "preparing_final_response"
    COMPLETED = "completed"
    FAILED = "failed"
    IDLE = "idle"


class MessageRole(str, Enum):
    """OpenAI-compatible message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"


class ToolChoiceType(str, Enum):
    """Tool choice types"""
    AUTO = "auto"
    NONE = "none"
    FUNCTION = "function"


# Base Models
class Message(BaseModel):
    """OpenAI-compatible message format with optional agent type"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    type: Optional[Literal["agent_plan", "agent_tool_calls"]] = None  # For Plan/Tool Call API messages
    
    model_config = ConfigDict(use_enum_values=True)


class ToolChoice(BaseModel):
    """Tool choice specification"""
    type: ToolChoiceType
    name: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


class FunctionDefinition(BaseModel):
    """Function definition for tools"""
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolDefinition(BaseModel):
    """Tool definition in OpenAI format"""
    type: Literal["function"] = "function"
    function: FunctionDefinition


class ToolCall(BaseModel):
    """Tool call request"""
    id: str
    type: Literal["function"] = "function"
    function: Dict[str, Any]


class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# Agent-specific models
class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    api_key: str
    model: str = "usf-mini"
    provider: Optional[str] = None
    base_url: Optional[str] = None  # Resolved base URL from provider
    is_our_model: bool = False  # Whether using our model or external provider
    role: Optional[str] = None
    backstory: Optional[str] = ""
    goal: Optional[str] = ""
    instruction: Optional[str] = ""
    introduction: Optional[str] = ""
    knowledge_cutoff: Optional[str] = None
    current_time: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    access_parent_history: bool = True
    trim_last_parent_user_message: bool = True
    
    # Network and retry configuration
    api_timeout: float = Field(
        default=60.0,
        ge=5.0,
        le=300.0,
        description="API request timeout in seconds (5-300)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts (0-10)"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Initial delay between retries in seconds (0.1-60)"
    )
    retry_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff multiplier for retries (1-10)"
    )
    retry_max_wait: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum wait time between retries in seconds (1-300)"
    )
    
    # Execution configuration
    max_iterations: int = Field(
        default=30,
        ge=3,
        le=50,
        description="Maximum workflow iterations (3-50)"
    )
    worker_timeout: float = Field(
        default=60.0,
        ge=5.0,
        le=300.0,
        description="Worker execution timeout in seconds (5-300)"
    )
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    @field_validator('knowledge_cutoff')
    @classmethod
    def validate_knowledge_cutoff(cls, v: Optional[str]) -> Optional[str]:
        """Validate knowledge cutoff format: DD Month YYYY"""
        if v is None or v == "":
            return v
        
        import re
        pattern = r'^(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})$'
        match = re.match(pattern, v)
        
        if not match:
            raise ValueError(
                f"Invalid knowledge_cutoff format: '{v}'\n"
                f"Required format: 'DD Month YYYY' (e.g., '15 January 2025')\n"
                f"Example: '1 March 2024' or '31 December 2025'"
            )
        
        day, month, year = match.groups()
        day = int(day)
        year = int(year)
        
        # Validate day range
        if day < 1 or day > 31:
            raise ValueError(f"Invalid day in knowledge_cutoff: {day}. Day must be between 1 and 31")
        
        # Validate year range
        if year < 2020 or year > 2030:
            raise ValueError(f"Invalid year in knowledge_cutoff: {year}. Year should be between 2020 and 2030")
        
        # Month-specific day validation
        month_days = {
            "February": 29,  # Allow leap year
            "April": 30, "June": 30, "September": 30, "November": 30
        }
        
        max_day = month_days.get(month, 31)
        if day > max_day:
            raise ValueError(f"Invalid day for {month}: {day}. {month} has maximum {max_day} days")
        
        return v
    
    @field_validator('current_time')
    @classmethod
    def validate_current_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate current time in ISO 8601 format"""
        if v is None or v == "":
            return v
        
        try:
            # Accept various ISO 8601 formats
            if 'T' not in v:
                raise ValueError("Missing 'T' separator in datetime")
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except Exception as e:
            raise ValueError(
                f"Invalid current_time format: '{v}'\n"
                f"Required format: ISO 8601 (e.g., '2025-01-15T14:30:00Z')\n"
                f"Error: {str(e)}"
            )
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name format"""
        if not v:
            raise ValueError("Agent name cannot be empty")
        
        import re
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid agent name: '{v}'\n"
                f"Must start with a letter and contain only letters, numbers, underscores, and hyphens"
            )
        
        if len(v) > 50:
            raise ValueError(f"Agent name too long: {len(v)} characters. Maximum: 50")
        
        return v
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format"""
        if not v:
            raise ValueError("API key cannot be empty")
        
        if v == "inherited":
            return v  # Special case for worker agents

        if len(v) < 1:
            raise ValueError(f"API key too short: {len(v)} characters. Minimum: 1")
        
        if ' ' in v:
            raise ValueError("API key should not contain spaces")
        
        return v
    
    @field_validator('backstory', 'goal', 'instruction', 'introduction')
    @classmethod
    def validate_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        """Validate that strings are non-empty when explicitly provided.
        Empty strings are allowed as they are used as defaults for these fields."""
        # Allow empty strings for these fields as they can be defaults
        # We only want to ensure they're strings, not other types
        if v is not None and not isinstance(v, str):
            raise ValueError(f"Field must be a string, got {type(v).__name__}")
        return v
    
    @model_validator(mode='after')
    def validate_worker_timeout(self) -> 'AgentConfig':
        """Validate that worker_timeout >= api_timeout"""
        if self.worker_timeout < self.api_timeout:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"worker_timeout ({self.worker_timeout}s) is less than "
                f"api_timeout ({self.api_timeout}s) - this may cause issues. "
                f"Worker timeout should be >= API timeout since workers make API calls."
            )
        return self


class WorkerTaskSchema(BaseModel):
    """Schema for worker agent tasks"""
    type: Literal["object"] = "object"
    properties: Dict[str, Any]
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = False


# API Response Models
class PlanAPIMessage(BaseModel):
    """Message format from Plan API"""
    role: str
    content: str
    type: Literal["agent_plan"]
    tool_choice: Optional[ToolChoice] = None
    plan: str
    final_decision: str
    reasoning: str
    agent_status: AgentStatus
    
    model_config = ConfigDict(use_enum_values=True)


class ToolCallAPIMessage(BaseModel):
    """Message format from Tool Call API"""
    role: str
    content: str = ""
    tool_calls: List[ToolCall]
    reasoning: str
    plan: str
    final_decision: str
    agent_status: AgentStatus
    type: Literal["agent_tool_calls"]
    
    model_config = ConfigDict(use_enum_values=True)


class APIChoice(BaseModel):
    """Choice in API response"""
    index: int
    message: Union[PlanAPIMessage, ToolCallAPIMessage, Message]
    finish_reason: str


class APIResponse(BaseModel):
    """Standard API response format"""
    status: int
    message: str
    code: int
    id: str
    model: str
    conversation_id: Optional[str] = None
    choices: List[APIChoice]
    usage: Optional[Usage] = None
    
    model_config = ConfigDict(use_enum_values=True)


# Execution context
class ExecutionContext(BaseModel):
    """Context for agent execution"""
    messages: List[Message]
    tools: List[ToolDefinition] = Field(default_factory=list)
    current_iteration: int = 0
    max_iterations: int = 10
    agent_name: str
    agent_status: AgentStatus = AgentStatus.IDLE
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)


# Plugin context
class PluginContext(BaseModel):
    """Context passed to plugins"""
    agent_name: str
    messages: List[Message]
    tools: List[ToolDefinition] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


# Tool registration
class RegisteredTool(BaseModel):
    """Registered tool information"""
    name: str
    function: Any  # Callable
    schema: ToolDefinition
    description: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


# Worker agent task
class WorkerTask(BaseModel):
    """Task payload passed to a worker agent"""
    task: str
    context: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
