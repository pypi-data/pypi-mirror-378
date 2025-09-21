"""
Comprehensive validation tests for AgentRouter SDK.
Tests strict format validation for all parameters.
"""

import pytest
import asyncio
from typing import Any, Dict
from agentrouter.agents import ManagerAgent, WorkerAgent
from agentrouter.tools import tool
from agentrouter.exceptions import ValidationError
from agentrouter.validators.format_validators import FormatValidator, AgentParameterValidator


class TestKnowledgeCutoffValidation:
    """Test knowledge cutoff format validation"""
    
    def test_valid_knowledge_cutoff(self):
        """Test valid knowledge cutoff formats"""
        valid_formats = [
            "15 January 2025",
            "1 March 2024",
            "31 December 2025",
            "29 February 2024",  # Leap year
            "30 April 2025"
        ]
        
        for format_str in valid_formats:
            result = FormatValidator.validate_knowledge_cutoff(format_str)
            assert result == format_str
    
    def test_invalid_knowledge_cutoff(self):
        """Test invalid knowledge cutoff formats"""
        invalid_formats = [
            "January 2025",  # Missing day
            "15-01-2025",  # Wrong format
            "15/01/2025",  # Wrong format
            "2025-01-15",  # ISO format (not allowed)
            "15 Jan 2025",  # Abbreviated month
            "15 january 2025",  # Lowercase month
            "32 January 2025",  # Invalid day
            "31 February 2025",  # Invalid day for February
            "15 InvalidMonth 2025",  # Invalid month
            "15 January 2019",  # Year too old
            "15 January 2031",  # Year too far
            "January 15, 2025",  # US format
            "15th January 2025",  # With ordinal
        ]
        
        for format_str in invalid_formats:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_knowledge_cutoff(format_str)
            assert str(exc_info.value)


class TestCurrentTimeValidation:
    """Test current time format validation"""
    
    def test_valid_current_time(self):
        """Test valid ISO 8601 formats"""
        valid_formats = [
            "2025-01-15T14:30:00Z",
            "2025-01-15T14:30:00+04:00",
            "2025-01-15T14:30:00.123Z",
            "2025-01-15T14:30:00-05:00",
            "2025-12-31T23:59:59Z"
        ]
        
        for format_str in valid_formats:
            result = FormatValidator.validate_current_time(format_str)
            assert result == format_str
    
    def test_invalid_current_time(self):
        """Test invalid time formats"""
        invalid_formats = [
            "2025-01-15",  # Missing time
            "14:30:00",  # Missing date
            "2025-01-15 14:30:00",  # Missing T separator
            "2025/01/15T14:30:00Z",  # Wrong date separator
            "01-15-2025T14:30:00Z",  # US date format
            "2025-13-01T14:30:00Z",  # Invalid month
            "2025-01-32T14:30:00Z",  # Invalid day
            "2025-01-15T25:30:00Z",  # Invalid hour
            "not-a-date",  # Complete garbage
        ]
        
        for format_str in invalid_formats:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_current_time(format_str)
            assert "ISO 8601" in str(exc_info.value)


class TestAgentNameValidation:
    """Test agent name validation"""
    
    def test_valid_agent_names(self):
        """Test valid agent names with auto-normalization"""
        test_cases = [
            ("manager1", "manager1"),
            ("Manager1", "manager1"),  # Uppercase to lowercase
            ("MANAGER1", "manager1"),  # All caps to lowercase
            ("order_processor", "order_processor"),
            ("order-processor", "order_processor"),  # Hyphen to underscore
            ("Customer-Service", "customer_service"),  # Mixed case with hyphen
            ("Order Processor", "order_processor"),  # Spaces to underscores
            ("Order__Processor", "order_processor"),  # Multiple underscores collapsed
            ("  agent  ", "agent"),  # Trimmed spaces
            ("A123", "a123"),
            ("MyAgent_test", "myagent_test"),
            ("ab", "ab"),  # Min length 2
            ("a" * 50, "a" * 50)  # Max length
        ]
        
        for input_name, expected in test_cases:
            result = FormatValidator.validate_agent_name(input_name)
            assert result == expected, f"Expected '{expected}' but got '{result}' for input '{input_name}'"
    
    def test_invalid_agent_names(self):
        """Test invalid agent names that should fail"""
        invalid_names = [
            "",  # Empty
            "   ",  # Only spaces
            "123agent",  # Starts with number
            "9Worker",  # Starts with number
            "agent@123",  # Special character
            "agent.name",  # Contains dot
            "!agent",  # Special char at start
            "ñame",  # Non-ASCII
            "工作者",  # Non-English characters
            "a" * 51,  # Too long
            "a",  # Too short (min 2 chars)
            "_",  # Just underscore
            "agent/worker",  # Contains slash
        ]
        
        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_agent_name(name)
            error_msg = str(exc_info.value)
            if name and name.strip():
                assert any(x in error_msg for x in ["Invalid agent", "too short", "too long", "cannot be empty", "cannot be only spaces"])


    def test_tool_name_validation(self):
        """Test strict tool name validation (fail-fast)"""
        # Valid tool names
        valid_names = [
            "search",
            "web_search",
            "get_weather",
            "process_order_123",
            "ab",  # Min length 2
            "t" * 50  # Max length
        ]
        
        for name in valid_names:
            result = FormatValidator.validate_tool_name(name)
            assert result == name
        
        # Invalid tool names (should all fail)
        invalid_names = [
            "",  # Empty
            "   ",  # Only spaces
            "Tool Name",  # Spaces
            "WebSearch",  # Uppercase
            "web-search",  # Hyphens
            "123tool",  # Starts with number
            "9_worker",  # Starts with number
            "tool@name",  # Special characters
            "tool.name",  # Dots
            "!tool",  # Special char
            "ñame",  # Non-ASCII
            "工具",  # Non-English
            "t",  # Too short
            "t" * 51,  # Too long
        ]
        
        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_tool_name(name)
            error_msg = str(exc_info.value)
            assert "Invalid tool_name" in error_msg or "cannot be empty" in error_msg or "cannot be only spaces" in error_msg
    
    def test_worker_role_validation(self):
        """Test worker role validation (required field)"""
        # Valid roles
        valid_roles = [
            "Handles order processing",  # Simple description
            "Processes customer refund requests and manages return procedures",  # Detailed
            "Manages inventory tracking, stock updates, and reorder notifications for the warehouse system",  # Long but valid
            "x" * 10,  # Min length
            "x" * 200,  # Ideal max length (should log warning but pass)
        ]
        
        for role in valid_roles:
            result = FormatValidator.validate_worker_role(role)
            assert result == role.strip()
        
        # Invalid roles
        invalid_roles = [
            "",  # Empty (required field)
            "   ",  # Only spaces
            "Short",  # Too short (< 10 chars)
            "x" * 9,  # Just under minimum
            "x" * 2001,  # Too long
        ]
        
        for role in invalid_roles:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_worker_role(role)
            error_msg = str(exc_info.value)
            assert "Worker role" in error_msg


class TestAPIKeyValidation:
    """Test API key validation"""
    
    def test_valid_api_keys(self):
        """Test valid API keys"""
        valid_keys = [
            "sk-1234567890",
            "api_key_123456",
            "verylongapikeywithmanychars",
            "inherited",  # Special case for workers
        ]
        
        for key in valid_keys:
            result = FormatValidator.validate_api_key(key)
            assert result == key
    
    def test_invalid_api_keys(self):
        """Test invalid API keys"""
        invalid_keys = [
            "",  # Empty
            "short",  # Too short
            "api key 123",  # Contains space
            " apikey123",  # Leading space
            "apikey123 ",  # Trailing space
        ]
        
        for key in invalid_keys:
            with pytest.raises(ValueError):
                FormatValidator.validate_api_key(key)


class TestModelNameValidation:
    """Test model name validation"""
    
    def test_valid_model_names(self):
        """Test valid model names"""
        valid_models = [
            "usf-mini",
            "gpt-4",
            "claude-3-opus",
            "custom-model-v1",
            "org/model-name",
            "model.v2",
            "inherited",  # Special case for workers
        ]
        
        for model in valid_models:
            result = FormatValidator.validate_model_name(model)
            assert result == model
    
    def test_invalid_model_names(self):
        """Test invalid model names"""
        invalid_models = [
            "",  # Empty
            " model",  # Starts with space
            "model name",  # Contains space
            "@model",  # Starts with special char
        ]
        
        for model in invalid_models:
            with pytest.raises(ValueError):
                FormatValidator.validate_model_name(model)


class TestNumericValidation:
    """Test numeric parameter validation"""
    
    def test_temperature_validation(self):
        """Test temperature validation"""
        # Valid temperatures
        valid_temps = [0.0, 0.5, 1.0, 1.5, 2.0]
        for temp in valid_temps:
            result = FormatValidator.validate_temperature(temp)
            assert result == temp
        
        # Invalid temperatures
        invalid_temps = [-0.1, 2.1, 3.0]
        for temp in invalid_temps:
            with pytest.raises(ValueError) as exc_info:
                FormatValidator.validate_temperature(temp)
            assert "Valid range: 0.0 to 2.0" in str(exc_info.value)
    
    def test_max_tokens_validation(self):
        """Test max_tokens validation"""
        # Valid values
        valid_tokens = [100, 1000, 4000, None]
        for tokens in valid_tokens:
            result = FormatValidator.validate_max_tokens(tokens)
            assert result == tokens
        
        # Invalid values
        invalid_tokens = [0, -100, 200000]
        for tokens in invalid_tokens:
            with pytest.raises(ValueError):
                FormatValidator.validate_max_tokens(tokens)


class TestToolValidation:
    """Test tool decorator validation"""
    
    def test_async_function_required(self):
        """Test that tools must be async functions"""
        # This should fail - sync function
        with pytest.raises(ValidationError) as exc_info:
            @tool(
                schema={
                    "type": "function",
                    "function": {
                        "name": "sync_tool",
                        "description": "A sync tool",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }
                }
            )
            def sync_tool(query: str):
                return f"Result: {query}"
        
        assert "must be async" in str(exc_info.value)
        assert "async def sync_tool" in str(exc_info.value)
    
    def test_async_function_accepted(self):
        """Test that async functions are accepted"""
        # This should succeed
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "async_tool",
                    "description": "An async tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        )
        async def async_tool(query: str):
            return f"Result: {query}"
        
        # Should have tool metadata
        assert hasattr(async_tool, '_is_tool')
        assert async_tool._is_tool == True
    
    def test_invalid_tool_schema(self):
        """Test tool schema validation"""
        # Missing function field
        with pytest.raises(ValidationError) as exc_info:
            @tool(schema={"type": "function"})
            async def bad_tool():
                pass
        
        assert "missing 'function' field" in str(exc_info.value)
        
        # Missing description
        with pytest.raises(ValidationError) as exc_info:
            @tool(
                schema={
                    "type": "function",
                    "function": {
                        "name": "no_desc_tool",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            )
            async def no_desc_tool():
                pass
        
        assert "must have a non-empty description" in str(exc_info.value)


class TestManagerAgentValidation:
    """Test Manager agent parameter validation"""
    
    def test_valid_manager_creation(self):
        """Test creating a manager with valid parameters"""
        manager = ManagerAgent(
            name="test_manager",
            api_key="valid-api-key-123",
            model="gpt-4",
            knowledge_cutoff="15 January 2025",
            current_time="2025-01-15T10:00:00Z",
            temperature=0.7,
            max_tokens=1000
        )
        assert manager.name == "test_manager"
    
    def test_invalid_manager_parameters(self):
        """Test manager creation with invalid parameters"""
        # Invalid knowledge cutoff
        with pytest.raises(ValidationError) as exc_info:
            ManagerAgent(
                name="test_manager",
                api_key="valid-api-key-123",
                knowledge_cutoff="January 2025"  # Missing day
            )
        assert "knowledge_cutoff" in str(exc_info.value).lower()
        
        # Invalid agent name
        with pytest.raises(ValidationError) as exc_info:
            ManagerAgent(
                name="123-invalid",  # Starts with number
                api_key="valid-api-key-123"
            )
        assert "Must start with a letter" in str(exc_info.value)
        
        # Invalid temperature
        with pytest.raises(ValidationError) as exc_info:
            ManagerAgent(
                name="test_manager",
                api_key="valid-api-key-123",
                temperature=3.0  # Out of range
            )
        assert "Valid range: 0.0 to 2.0" in str(exc_info.value)


class TestWorkerAgentValidation:
    """Test Worker agent parameter validation"""
    
    def test_valid_worker_creation(self):
        """Test creating a worker with valid parameters"""
        worker = WorkerAgent(
            name="test_worker",
            api_key="valid-api-key-123",
            model="gpt-4",
            role="Process orders",
            access_parent_history=True,
            knowledge_cutoff="15 January 2025"
        )
        assert worker.name == "test_worker"
    
    def test_worker_with_inherited_values(self):
        """Test worker with inherited API key and model"""
        worker = WorkerAgent(
            name="test_worker",
            model="usf-mini",
            # api_key and model will be "inherited"
            role="Process orders"
        )
        assert worker.config.api_key == "inherited"
        assert worker.config.model == "usf-mini"
    
    def test_invalid_worker_parameters(self):
        """Test worker creation with invalid parameters"""
        # Invalid boolean parameter
        with pytest.raises(ValidationError) as exc_info:
            WorkerAgent(
                name="test_worker",
                model="usf-mini",
                role="Process orders",
                access_parent_history="yes"  # Should be boolean
            )
        assert "Expected: bool" in str(exc_info.value)
        
        # Invalid task schema
        with pytest.raises(ValidationError) as exc_info:
            WorkerAgent(
                name="test_worker",
                model="usf-mini",
                role="Process orders",
                task_schema="not a dict"  # Should be dict
            )
        assert "must be a dictionary" in str(exc_info.value)


class TestComprehensiveParameterValidation:
    """Test comprehensive validation of all parameters"""
    
    def test_manager_all_parameters(self):
        """Test manager with all parameters validated"""
        params = {
            "name": "Comprehensive-Manager",  # Should be normalized to lowercase
            "api_key": "sk-very-long-api-key-123456",
            "model": "gpt-4",
            "backstory": "I am a comprehensive manager",
            "goal": "Test all validations",
            "instruction": "Be thorough",
            "introduction": "Hello, I am a test",
            "knowledge_cutoff": "15 January 2025",
            "current_time": "2025-01-15T10:00:00Z",
            "temperature": 0.8,
            "max_tokens": 2000,
            "api_timeout": 30.0,
            "max_retries": 5,
            "retry_delay": 2.0,
            "max_iterations": 25,
            "worker_timeout": 45.0
        }
        
        validated = AgentParameterValidator.validate_manager_params(params)
        assert validated["name"] == "comprehensive_manager"  # Normalized
        assert validated["knowledge_cutoff"] == "15 January 2025"
        assert validated["temperature"] == 0.8
    
    def test_worker_all_parameters(self):
        """Test worker with all parameters validated with required role"""
        # Valid worker with role
        params = {
            "name": "Comprehensive Worker",  # Should be normalized
            "api_key": "inherited",
            "model": "inherited",
            "role": "Process order fulfillment and shipping tasks",  # REQUIRED
            "access_parent_history": True,
            "trim_last_parent_user_message": False,
            "backstory": "Worker backstory",
            "goal": "Worker goal",
            "knowledge_cutoff": "1 March 2024",
            "current_time": "2024-03-01T09:00:00Z",
            "temperature": 0.5,
            "max_tokens": 1500
        }
        
        validated = AgentParameterValidator.validate_worker_params(params)
        assert validated["name"] == "comprehensive_worker"  # Normalized
        assert validated["role"] == "Process order fulfillment and shipping tasks"
        assert validated["access_parent_history"] == True
        assert validated["knowledge_cutoff"] == "1 March 2024"
    
    def test_worker_role_required(self):
        """Test that worker role is required"""
        # Worker without role should fail
        params_no_role = {
            "name": "worker_without_role",
            "api_key": "inherited",
            "model": "inherited",
            # Missing required 'role' field
        }
        
        with pytest.raises(ValueError) as exc_info:
            AgentParameterValidator.validate_worker_params(params_no_role)
        assert "Worker agent requires 'role' parameter" in str(exc_info.value)
        
        # Worker with invalid role should fail
        params_bad_role = {
            "name": "worker_bad_role",
            "api_key": "inherited",
            "model": "inherited",
            "role": "Short",  # Too short
        }
        
        with pytest.raises(ValueError) as exc_info:
            AgentParameterValidator.validate_worker_params(params_bad_role)
        assert "Worker role too short" in str(exc_info.value)


class TestErrorMessages:
    """Test that error messages are clear and helpful"""
    
    def test_knowledge_cutoff_error_message(self):
        """Test knowledge cutoff error message is helpful"""
        with pytest.raises(ValueError) as exc_info:
            FormatValidator.validate_knowledge_cutoff("bad format")
        
        error_msg = str(exc_info.value)
        assert "Required format: 'DD Month YYYY'" in error_msg
        assert "Example:" in error_msg
        assert "'15 January 2025'" in error_msg
    
    def test_async_function_error_message(self):
        """Test async function error message is helpful"""
        def sync_func():
            pass
        
        with pytest.raises(ValueError) as exc_info:
            FormatValidator.validate_async_function(sync_func, "my_tool")
        
        error_msg = str(exc_info.value)
        assert "must be async" in error_msg
        assert "async def my_tool" in error_msg
        assert "Example:" in error_msg
        assert "@tool" in error_msg
    
    def test_temperature_error_message(self):
        """Test temperature error message is helpful"""
        with pytest.raises(ValueError) as exc_info:
            FormatValidator.validate_temperature(2.5)
        
        error_msg = str(exc_info.value)
        assert "Valid range: 0.0 to 2.0" in error_msg
        assert "Recommended values:" in error_msg
        assert "0.7: Balanced creativity" in error_msg


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
