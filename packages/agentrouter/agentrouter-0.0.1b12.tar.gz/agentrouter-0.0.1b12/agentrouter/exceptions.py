"""
Exception classes for AgentRouter SDK
"""

from typing import Optional, Any, Dict


class AgentRouterError(Exception):
    """Base exception for all AgentRouter errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(AgentRouterError):
    """Raised when API calls fail"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.api_name = api_name


class ValidationError(AgentRouterError):
    """Raised when validation fails"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.field = field
        self.value = value


class ExecutionError(AgentRouterError):
    """Raised when agent execution fails"""
    
    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        step: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.agent_name = agent_name
        self.step = step


class ToolError(AgentRouterError):
    """Raised when tool execution fails"""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.tool_name = tool_name
        self.arguments = arguments


class ConfigurationError(AgentRouterError):
    """Raised when configuration is invalid"""
    
    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.parameter = parameter


class PluginError(AgentRouterError):
    """Raised when plugin operations fail"""
    
    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        hook: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.plugin_name = plugin_name
        self.hook = hook


class TimeoutError(AgentRouterError):
    """Raised when operations timeout"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class RateLimitError(APIError):
    """Raised when rate limits are exceeded"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(APIError):
    """Raised when authorization fails"""
    
    def __init__(
        self,
        message: str = "Authorization failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=403, details=details)


class ResourceNotFoundError(APIError):
    """Raised when a resource is not found"""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=404, details=details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class MaxIterationsError(ExecutionError):
    """Raised when maximum iterations are exceeded"""
    
    def __init__(
        self,
        message: str,
        max_iterations: int,
        current_iteration: int,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details=details)
        self.max_iterations = max_iterations
        self.current_iteration = current_iteration