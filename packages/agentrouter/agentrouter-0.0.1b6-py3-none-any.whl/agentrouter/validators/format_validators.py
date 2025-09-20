"""
Strict format validators for AgentRouter SDK.
Provides comprehensive validation for all parameters with clear error messages.
"""

import re
import inspect
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

class FormatValidator:
    """
    Comprehensive format validation for all agent and tool parameters.
    Validates formats with strict rules and provides clear, actionable error messages.
    """
    
    # Valid model names (can be extended)
    VALID_MODELS = {
        "usf-mini",
        "usf-mini-x1",
        "usf-mini-x1-fast",
        "asi1-mini",
        "asi1-mini-04-25",
        "asi1-mini-04-25-fast",
        "shunya-mini",
        "shunya-mini-x1",
        "shunya1-mini-x1-fast",
        "shunya-mini-code"
    }
    
    # Month names for knowledge cutoff validation
    VALID_MONTHS = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    }
    
    @staticmethod
    def validate_knowledge_cutoff(value: Optional[str], field_name: str = "knowledge_cutoff") -> Optional[str]:
        """
        Validate knowledge cutoff format: 'DD Month YYYY'
        
        Args:
            value: Knowledge cutoff string to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If format is invalid
        """
        if value is None or value == "":
            return value
        
        # Pattern: DD Month YYYY (e.g., "15 January 2025")
        pattern = r'^(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})$'
        match = re.match(pattern, value)
        
        if not match:
            raise ValueError(
                f"Invalid {field_name} format: '{value}'\n"
                f"Required format: 'DD Month YYYY' (e.g., '15 January 2025')\n"
                f"Valid months: {', '.join(FormatValidator.VALID_MONTHS)}\n"
                f"Example: '1 March 2024' or '31 December 2025'"
            )
        
        day, month, year = match.groups()
        day = int(day)
        year = int(year)
        
        # Validate day range
        if day < 1 or day > 31:
            raise ValueError(
                f"Invalid day in {field_name}: {day}\n"
                f"Day must be between 1 and 31"
            )
        
        # Validate year range (reasonable bounds)
        if year < 2020 or year > 2030:
            raise ValueError(
                f"Invalid year in {field_name}: {year}\n"
                f"Year should be between 2020 and 2030"
            )
        
        # Month-specific day validation
        month_days = {
            "February": 29,  # Allow leap year
            "April": 30, "June": 30, "September": 30, "November": 30
        }
        
        max_day = month_days.get(month, 31)
        if day > max_day:
            raise ValueError(
                f"Invalid day for {month}: {day}\n"
                f"{month} has maximum {max_day} days"
            )
        
        return value
    
    @staticmethod
    def validate_current_time(value: Optional[str], field_name: str = "current_time") -> Optional[str]:
        """
        Validate current time in ISO 8601 format.
        
        Args:
            value: Time string to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If format is invalid
        """
        if value is None or value == "":
            return value
        
        # Try to parse ISO 8601 format
        try:
            # Accept various ISO 8601 formats
            if 'T' in value:
                # Full datetime
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                raise ValueError("Missing 'T' separator")
        except Exception as e:
            raise ValueError(
                f"Invalid {field_name} format: '{value}'\n"
                f"Required format: ISO 8601 (e.g., '2025-01-15T14:30:00Z')\n"
                f"Examples:\n"
                f"  - '2025-01-15T14:30:00Z' (UTC)\n"
                f"  - '2025-01-15T14:30:00+04:00' (with timezone)\n"
                f"  - '2025-01-15T14:30:00.123Z' (with milliseconds)\n"
                f"Error: {str(e)}"
            )
        
        return value
    
    @staticmethod
    def validate_agent_name(value: str, field_name: str = "name") -> str:
        """
        Validate and normalize agent name.
        Auto-converts to lowercase, handles underscores, and validates format.
        
        Args:
            value: Name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Normalized and validated name (lowercase)
            
        Raises:
            ValueError: If format is invalid (fail-fast approach)
        """
        if not value:
            raise ValueError(
                f"Agent {field_name} cannot be empty"
            )
        
        # Trim spaces from both sides
        trimmed = value.strip()
        
        if not trimmed:
            raise ValueError(
                f"Agent {field_name} cannot be only spaces"
            )
        
        # Check for special characters or non-ASCII before normalization
        if not all(c.isalnum() or c in '_- ' for c in trimmed):
            invalid_chars = set(c for c in trimmed if not (c.isalnum() or c in '_- '))
            raise ValueError(
                f"Invalid agent {field_name}: '{value}'\n"
                f"Contains invalid characters: {', '.join(repr(c) for c in invalid_chars)}\n"
                f"Agent names can only contain:\n"
                f"  - Letters (a-z, A-Z)\n"
                f"  - Numbers (0-9)\n"
                f"  - Underscores (_)\n"
                f"  - Hyphens (-)\n"
                f"No special characters or non-English characters allowed."
            )
        
        # Check if starts with a number before normalization
        if trimmed[0].isdigit():
            raise ValueError(
                f"Invalid agent {field_name}: '{value}'\n"
                f"Agent names cannot start with a number.\n"
                f"Must start with a letter (a-z or A-Z)."
            )
        
        # AUTO-CONVERT to lowercase
        normalized = trimmed.lower()
        
        # Replace spaces and hyphens with underscores
        normalized = normalized.replace(' ', '_')
        normalized = normalized.replace('-', '_')
        
        # Collapse multiple underscores to single
        while '__' in normalized:
            normalized = normalized.replace('__', '_')
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        # Check if empty after normalization
        if not normalized:
            raise ValueError(
                f"Invalid agent {field_name}: '{value}'\n"
                f"Name becomes empty after normalization.\n"
                f"Please provide a valid name with letters or numbers."
            )
        
        # Final validation after normalization
        pattern = r'^[a-z][a-z0-9_]*$'
        if not re.match(pattern, normalized):
            raise ValueError(
                f"Invalid agent {field_name}: '{value}'\n"
                f"After normalization: '{normalized}'\n"
                f"Rules:\n"
                f"  - Must start with a letter\n"
                f"  - Can only contain lowercase letters, numbers, and underscores\n"
                f"Examples: 'orderprocessor', 'order_processor', 'worker1'"
            )
        
        if len(normalized) < 2:
            raise ValueError(
                f"Agent {field_name} too short: {len(normalized)} characters\n"
                f"Minimum length: 2 characters"
            )
        
        if len(normalized) > 50:
            raise ValueError(
                f"Agent {field_name} too long: {len(normalized)} characters\n"
                f"Maximum length: 50 characters"
            )
        
        return normalized  # Return the normalized lowercase version
    
    @staticmethod
    def validate_api_key(value: str, field_name: str = "api_key") -> str:
        """
        Validate API key format.
        
        Args:
            value: API key to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If format is invalid
        """
        if not value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )
        
        if value == "inherited":
            # Special case for worker agents
            return value
        
        if len(value) < 10:
            raise ValueError(
                f"Invalid {field_name}: too short ({len(value)} characters)\n"
                f"API keys should be at least 10 characters long"
            )
        
        if ' ' in value:
            raise ValueError(
                f"Invalid {field_name}: contains spaces\n"
                f"API keys should not contain spaces"
            )
        
        if value.startswith(' ') or value.endswith(' '):
            raise ValueError(
                f"Invalid {field_name}: has leading or trailing spaces\n"
                f"Please remove any whitespace from the API key"
            )
        
        return value
    
    @staticmethod
    def validate_model_name(value: str, field_name: str = "model") -> str:
        """
        Validate model name.
        
        Args:
            value: Model name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If format is invalid
        """
        if not value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )
        
        if value == "inherited":
            # Special case for worker agents
            return value
        
        # Check if it's a known model or follows a pattern
        if value not in FormatValidator.VALID_MODELS:
            # Allow custom models but validate format
            pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-._/]*$'
            if not re.match(pattern, value):
                raise ValueError(
                    f"Invalid {field_name}: '{value}'\n"
                    f"Known models: {', '.join(sorted(FormatValidator.VALID_MODELS))}\n"
                    f"Custom model format:\n"
                    f"  - Must start with alphanumeric character\n"
                    f"  - Can contain letters, numbers, hyphens, dots, underscores, slashes\n"
                    f"  - Examples: 'custom-model-v1', 'org/model-name', 'model.v2'"
                )
        
        return value
    
    @staticmethod
    def validate_non_empty_string(value: Optional[str], field_name: str) -> Optional[str]:
        """
        Validate string fields. Allow empty strings as they can be defaults.
        
        Args:
            value: String to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If value is not a string
        """
        # Allow empty strings for backstory, goal, instruction, introduction
        # as they are used as defaults
        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a string, got {type(value).__name__}"
            )
        
        return value
    
    @staticmethod
    def validate_temperature(value: float, field_name: str = "temperature") -> float:
        """
        Validate temperature parameter.
        
        Args:
            value: Temperature value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If value is out of range
        """
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Invalid {field_name} type: {type(value).__name__}\n"
                f"Expected: float or int\n"
                f"Example: 0.7"
            )
        
        if not 0.0 <= value <= 2.0:
            raise ValueError(
                f"Invalid {field_name}: {value}\n"
                f"Valid range: 0.0 to 2.0\n"
                f"Recommended values:\n"
                f"  - 0.0: Deterministic/consistent responses\n"
                f"  - 0.7: Balanced creativity (default)\n"
                f"  - 1.0: Creative responses\n"
                f"  - 2.0: Maximum randomness"
            )
        
        return float(value)
    
    @staticmethod
    def validate_max_tokens(value: Optional[int], field_name: str = "max_tokens") -> Optional[int]:
        """
        Validate max_tokens parameter.
        
        Args:
            value: Max tokens value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If value is invalid
        """
        if value is None:
            return value
        
        if not isinstance(value, int):
            raise ValueError(
                f"Invalid {field_name} type: {type(value).__name__}\n"
                f"Expected: int or None\n"
                f"Example: 1000"
            )
        
        if value <= 0:
            raise ValueError(
                f"Invalid {field_name}: {value}\n"
                f"Must be a positive integer\n"
                f"Typical values: 100 to 4000"
            )
        
        if value > 100000:
            raise ValueError(
                f"Invalid {field_name}: {value}\n"
                f"Value seems unreasonably high (> 100,000)\n"
                f"Typical maximum: 4000-8000 for most models"
            )
        
        return value
    
    @staticmethod
    def validate_async_function(func: Callable, function_name: Optional[str] = None) -> None:
        """
        Validate that a function is async.
        
        Args:
            func: Function to validate
            function_name: Optional name for better error messages
            
        Raises:
            ValueError: If function is not async
        """
        name = function_name or func.__name__
        
        if not asyncio.iscoroutinefunction(func):
            # Generate helpful error message
            error_msg = (
                f"Tool function '{name}' must be async (asynchronous).\n"
                f"\n"
                f"Current function signature:\n"
                f"  def {name}(...)\n"
                f"\n"
                f"Required change:\n"
                f"  async def {name}(...)\n"
                f"\n"
                f"Example:\n"
                f"  @tool(schema={{...}})\n"
                f"  async def {name}(param: str):\n"
                f"      # Your async implementation\n"
                f"      result = await some_async_operation()\n"
                f"      return result\n"
                f"\n"
                f"If your function doesn't use async operations, you can still make it async:\n"
                f"  @tool(schema={{...}})\n"
                f"  async def {name}(param: str):\n"
                f"      # Synchronous code works in async functions\n"
                f"      return \"result\""
            )
            raise ValueError(error_msg)
    
    @staticmethod
    def validate_tool_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool schema format.
        
        Args:
            schema: Tool schema to validate
            
        Returns:
            Validated schema
            
        Raises:
            ValueError: If schema is invalid
        """
        if not schema:
            raise ValueError(
                "Tool schema cannot be empty.\n"
                "Required structure:\n"
                "{\n"
                "  \"type\": \"function\",\n"
                "  \"function\": {\n"
                "    \"name\": \"tool_name\",\n"
                "    \"description\": \"Tool description\",\n"
                "    \"parameters\": {\n"
                "      \"type\": \"object\",\n"
                "      \"properties\": {...},\n"
                "      \"required\": [...]\n"
                "    }\n"
                "  }\n"
                "}"
            )
        
        # Check top-level structure
        if "type" not in schema:
            raise ValueError(
                "Tool schema missing 'type' field.\n"
                "Add: \"type\": \"function\""
            )
        
        if schema["type"] != "function":
            raise ValueError(
                f"Invalid tool schema type: '{schema['type']}'\n"
                f"Expected: 'function'"
            )
        
        if "function" not in schema:
            raise ValueError(
                "Tool schema missing 'function' field.\n"
                "Required structure:\n"
                "\"function\": {\n"
                "  \"name\": \"tool_name\",\n"
                "  \"description\": \"Tool description\",\n"
                "  \"parameters\": {...}\n"
                "}"
            )
        
        function_def = schema["function"]
        
        # Validate function definition
        if "name" not in function_def:
            raise ValueError(
                "Tool function definition missing 'name' field"
            )
        
        if not function_def["name"]:
            raise ValueError(
                "Tool function name cannot be empty"
            )
        
        if "parameters" not in function_def:
            raise ValueError(
                "Tool function definition missing 'parameters' field.\n"
                "Required structure:\n"
                "\"parameters\": {\n"
                "  \"type\": \"object\",\n"
                "  \"properties\": {\n"
                "    \"param_name\": {\"type\": \"string\", \"description\": \"...\"}\n"
                "  },\n"
                "  \"required\": [\"param_name\"]\n"
                "}"
            )
        
        params = function_def["parameters"]
        
        if not isinstance(params, dict):
            raise ValueError(
                f"Tool parameters must be a dictionary, got {type(params).__name__}"
            )
        
        if "type" not in params:
            raise ValueError(
                "Tool parameters missing 'type' field.\n"
                "Add: \"type\": \"object\""
            )
        
        if params["type"] != "object":
            raise ValueError(
                f"Invalid parameters type: '{params['type']}'\n"
                f"Expected: 'object'"
            )
        
        if "properties" not in params:
            raise ValueError(
                "Tool parameters missing 'properties' field.\n"
                "This defines the parameters your tool accepts"
            )
        
        # Validate description
        description = function_def.get("description", "")
        if not description:
            raise ValueError(
                "Tool function must have a non-empty description.\n"
                "This helps the AI understand when to use your tool.\n"
                "Example: \"Search the knowledge base for relevant information\""
            )
        
        return schema
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str) -> bool:
        """
        Validate boolean fields.
        
        Args:
            value: Value to validate as boolean
            field_name: Name of the field for error messages
            
        Returns:
            Boolean value
            
        Raises:
            ValueError: If value is not a valid boolean
        """
        if not isinstance(value, bool):
            raise ValueError(
                f"Invalid {field_name} type: {type(value).__name__}\n"
                f"Expected: bool (True or False)\n"
                f"Got: {value}"
            )
        return value
    
    @staticmethod
    def validate_tool_name(value: str, field_name: str = "tool_name") -> str:
        """
        STRICT validation for tool names (fail-fast approach).
        No auto-fixing - must be valid as provided.
        
        Args:
            value: Tool name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated tool name (trimmed)
            
        Raises:
            ValueError: If tool name is invalid (fail-fast)
        """
        if not value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )
        
        # Trim spaces from both sides
        trimmed = value.strip()
        
        if not trimmed:
            raise ValueError(
                f"{field_name} cannot be only spaces"
            )
        
        # Check for any spaces in the middle
        if ' ' in trimmed:
            raise ValueError(
                f"Invalid {field_name}: '{value}'\n"
                f"Tool names cannot contain spaces.\n"
                f"Use underscores instead: '{trimmed.replace(' ', '_')}'"
            )
        
        # Check for special characters or non-ASCII
        if not re.match(r'^[a-z0-9_]+$', trimmed):
            invalid_chars = set(c for c in trimmed if not re.match(r'[a-z0-9_]', c))
            raise ValueError(
                f"Invalid {field_name}: '{value}'\n"
                f"Contains invalid characters: {', '.join(repr(c) for c in invalid_chars)}\n"
                f"Tool names can only contain:\n"
                f"  - Lowercase letters (a-z)\n"
                f"  - Numbers (0-9)\n"
                f"  - Underscores (_)\n"
                f"No uppercase, special characters, or non-English characters allowed."
            )
        
        # Check if starts with a number
        if trimmed[0].isdigit():
            raise ValueError(
                f"Invalid {field_name}: '{value}'\n"
                f"Tool names cannot start with a number.\n"
                f"Must start with a lowercase letter (a-z)."
            )
        
        # Check length constraints
        if len(trimmed) < 2:
            raise ValueError(
                f"Invalid {field_name}: '{value}'\n"
                f"Too short: {len(trimmed)} character(s).\n"
                f"Minimum length: 2 characters."
            )
        
        if len(trimmed) > 50:
            raise ValueError(
                f"Invalid {field_name}: '{value}'\n"
                f"Too long: {len(trimmed)} characters.\n"
                f"Maximum length: 50 characters."
            )
        
        return trimmed  # Return validated name
    
    @staticmethod
    def validate_worker_role(value: str, field_name: str = "role") -> str:
        """
        Validate worker role description (REQUIRED for workers).
        
        Args:
            value: Role description to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated role description
            
        Raises:
            ValueError: If role is invalid or missing
        """
        if not value:
            raise ValueError(
                f"Worker {field_name} is REQUIRED.\n"
                f"Provide a clear 1-2 line description of the worker's specific job.\n"
                f"This helps the manager select the right worker for each task.\n"
                f"Example: 'Handles order processing, tracking, and status updates'"
            )
        
        # Trim spaces
        value = value.strip()
        
        if not value:
            raise ValueError(
                f"Worker {field_name} cannot be only spaces.\n"
                f"Provide a meaningful description of the worker's purpose."
            )
        
        if len(value) < 10:
            raise ValueError(
                f"Worker {field_name} too short: {len(value)} characters.\n"
                f"Minimum: 10 characters\n"
                f"Provide a meaningful description of the worker's purpose.\n"
                f"Example: 'Processes customer refund requests'"
            )
        
        if len(value) > 2000:
            raise ValueError(
                f"Worker {field_name} too long: {len(value)} characters.\n"
                f"Maximum: 2000 characters\n"
                f"Keep it concise - ideally 1-2 lines."
            )
        
        # Warning for non-ideal length (but don't fail)
        if len(value) > 200:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Worker {field_name} is {len(value)} characters. "
                f"Ideal length: 50-200 characters (1-2 lines). "
                f"Consider making it more concise for better clarity."
            )
        
        return value
    
    @staticmethod
    def validate_provider(value: Optional[str], field_name: str = "provider") -> Optional[str]:
        """
        Validate provider name format.
        
        Args:
            value: Provider name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If format is invalid
        """
        if value is None or value == "":
            return value
        
        # Common providers
        known_providers = {
            "openai", "anthropic", "google", "mistral", "cohere",
            "huggingface", "replicate", "together", "anyscale"
        }
        
        # Allow known providers or custom format
        if value.lower() not in known_providers:
            pattern = r'^[a-zA-Z][a-zA-Z0-9-._]*$'
            if not re.match(pattern, value):
                raise ValueError(
                    f"Invalid {field_name}: '{value}'\n"
                    f"Known providers: {', '.join(sorted(known_providers))}\n"
                    f"Custom provider format:\n"
                    f"  - Must start with a letter\n"
                    f"  - Can contain letters, numbers, hyphens, dots, underscores\n"
                    f"  - No spaces or special characters"
                )
        
        return value


class AgentParameterValidator:
    """
    Comprehensive validation for Manager and Worker agent parameters.
    """
    
    @staticmethod
    def validate_manager_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all Manager agent parameters with strict format checking.
        
        Args:
            params: Dictionary of parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValueError: If any parameter is invalid
        """
        validated = {}
        
        # Required parameters
        if "name" not in params:
            raise ValueError("Manager agent requires 'name' parameter")
        validated["name"] = FormatValidator.validate_agent_name(params["name"])
        
        if "api_key" not in params:
            raise ValueError("Manager agent requires 'api_key' parameter")
        validated["api_key"] = FormatValidator.validate_api_key(params["api_key"])
        
        # Model validation
        model = params.get("model", "usf-mini")
        validated["model"] = FormatValidator.validate_model_name(model)
        
        # Optional string parameters with format validation
        if "backstory" in params:
            validated["backstory"] = FormatValidator.validate_non_empty_string(
                params["backstory"], "backstory"
            )
        
        if "goal" in params:
            validated["goal"] = FormatValidator.validate_non_empty_string(
                params["goal"], "goal"
            )
        
        if "instruction" in params:
            validated["instruction"] = FormatValidator.validate_non_empty_string(
                params["instruction"], "instruction"
            )
        
        if "introduction" in params:
            validated["introduction"] = FormatValidator.validate_non_empty_string(
                params["introduction"], "introduction"
            )
        
        if "knowledge_cutoff" in params:
            validated["knowledge_cutoff"] = FormatValidator.validate_knowledge_cutoff(
                params["knowledge_cutoff"]
            )
        
        if "current_time" in params:
            validated["current_time"] = FormatValidator.validate_current_time(
                params["current_time"]
            )
        
        if "provider" in params:
            validated["provider"] = FormatValidator.validate_provider(params["provider"])
        
        # Numeric parameters
        if "temperature" in params:
            validated["temperature"] = FormatValidator.validate_temperature(params["temperature"])
        
        if "max_tokens" in params:
            validated["max_tokens"] = FormatValidator.validate_max_tokens(params["max_tokens"])
        
        # Copy other parameters that are validated by Pydantic
        for key in ["base_url", "is_our_model", "api_timeout", "max_retries", 
                    "retry_delay", "retry_multiplier", "retry_max_wait", 
                    "max_iterations", "worker_timeout"]:
            if key in params:
                validated[key] = params[key]
        
        return validated
    
    @staticmethod
    def validate_worker_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all Worker agent parameters with strict format checking.
        
        Args:
            params: Dictionary of parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValueError: If any parameter is invalid
        """
        validated = {}
        
        # Required parameters
        if "name" not in params:
            raise ValueError("Worker agent requires 'name' parameter")
        validated["name"] = FormatValidator.validate_agent_name(params["name"])
        
        # API key can be inherited
        api_key = params.get("api_key", "inherited")
        validated["api_key"] = FormatValidator.validate_api_key(api_key)
        
        # Model can be inherited
        model = params.get("model", "inherited")
        validated["model"] = FormatValidator.validate_model_name(model)
        
        # Role is REQUIRED for worker agents
        if "role" not in params:
            raise ValueError(
                "Worker agent requires 'role' parameter.\n"
                "The role describes what this worker does and helps the manager select the right worker.\n"
                "Example: role='Handles order processing and tracking'"
            )
        validated["role"] = FormatValidator.validate_worker_role(params["role"])
        
        if "access_parent_history" in params:
            validated["access_parent_history"] = FormatValidator.validate_boolean(
                params["access_parent_history"], "access_parent_history"
            )
        
        if "trim_last_parent_user_message" in params:
            validated["trim_last_parent_user_message"] = FormatValidator.validate_boolean(
                params["trim_last_parent_user_message"], "trim_last_parent_user_message"
            )
        
        # Task schema validation
        if "task_schema" in params and params["task_schema"] is not None:
            schema = params["task_schema"]
            if not isinstance(schema, dict):
                raise ValueError(
                    f"Worker task_schema must be a dictionary, got {type(schema).__name__}"
                )
            validated["task_schema"] = schema
        
        # Apply same validations as manager for other fields
        for field in ["backstory", "goal", "instruction", "introduction",
                     "knowledge_cutoff", "current_time", "provider"]:
            if field in params:
                if field == "knowledge_cutoff":
                    validated[field] = FormatValidator.validate_knowledge_cutoff(params[field])
                elif field == "current_time":
                    validated[field] = FormatValidator.validate_current_time(params[field])
                elif field == "provider":
                    validated[field] = FormatValidator.validate_provider(params[field])
                else:
                    validated[field] = FormatValidator.validate_non_empty_string(
                        params[field], field
                    )
        
        # Numeric parameters
        if "temperature" in params:
            validated["temperature"] = FormatValidator.validate_temperature(params["temperature"])
        
        if "max_tokens" in params:
            validated["max_tokens"] = FormatValidator.validate_max_tokens(params["max_tokens"])
        
        # Copy other parameters
        for key in ["base_url", "is_our_model", "api_timeout", "max_retries",
                    "retry_delay", "retry_multiplier", "retry_max_wait",
                    "max_iterations", "worker_timeout"]:
            if key in params:
                validated[key] = params[key]
        
        return validated