"""
Unit tests for agent classes
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from agentrouter.agents import ManagerAgent, WorkerAgent
from agentrouter.types import Message, AgentStatus
from agentrouter.tools import tool
from agentrouter.exceptions import ExecutionError, ValidationError


class TestManagerAgent:
    """Test the ManagerAgent class"""
    
    def test_manager_initialization(self):
        """Test manager agent initialization"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234",
            model="usf-mini",
            backstory="Test backstory",
            goal="Test goal",
            instruction="Test instructions"
        )
        
        assert manager.name == "testmanager"
        assert manager.config.api_key == "test-key-1234"
        assert manager.config.model == "usf-mini"
        assert manager.config.backstory == "Test backstory"
        assert manager.config.goal == "Test goal"
        assert manager.config.instruction == "Test instructions"
        assert manager.is_manager is True
        assert manager.is_worker is False
    
    def test_create_worker(self):
        """Test creating a worker agent"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        worker = manager.create_worker(
            name="TestWorker",
            role="Test Worker Role",
            task_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string"}
                },
                "required": ["task"]
            }
        )
        
        assert worker.name == "testworker"
        assert worker.config.role == "Test Worker Role"
        assert worker.task_schema is not None
        assert manager.get_worker(worker.name) is worker
        assert worker.name in manager.list_workers()
    
    def test_register_tool(self):
        """Test registering a tool with manager"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "Test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"}
                        },
                        "required": ["input"]
                    }
                }
            }
        )
        async def test_tool(input: str) -> str:
            return f"Processed: {input}"
        
        manager.register_tool(test_tool)
        
        assert "test_tool" in manager.list_tools()
        assert manager.tool_registry.has("test_tool")
    
    def test_attach_detach_worker(self):
        """Test attaching and detaching workers"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        worker = WorkerAgent(
            name="StandaloneWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="Standalone specialist"
        )
        
        # Attach with alias
        manager.attach_worker(worker, alias="worker_alias")
        assert manager.get_worker("worker_alias") is worker
        assert manager.get_worker(worker.name) is worker
        
        # Detach worker
        result = manager.detach_worker(worker.name)
        assert result is True
        assert manager.get_worker(worker.name) is None
    
    @pytest.mark.asyncio
    async def test_execute_workflow_mock(self):
        """Test manager execution workflow with mocked APIs"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        # Mock the API clients
        with patch.object(manager.plan_api, 'create_plan', new_callable=AsyncMock) as mock_plan:
            with patch.object(manager.plan_api, 'should_call_tool') as mock_should_call, \
                 patch('agentrouter.agents.manager.OpenAIResponseGenerator.generate_final_response', new_callable=AsyncMock) as mock_openai:
                # Setup mock responses
                mock_plan.return_value = Mock(
                    choices=[Mock(
                        message=Mock(
                            content="Test response",
                            agent_status=AgentStatus.PREPARING_FINAL_RESPONSE
                        )
                    )],
                    usage={"total_tokens": 100}
                )
                mock_should_call.return_value = False
                mock_openai.return_value = {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "Final"},
                            "finish_reason": "stop",
                            "index": 0
                        }
                    ],
                    "usage": {"total_tokens": 50}
                }
                
                # Execute
                messages = [
                    Message(role="user", content="Test message")
                ]
                
                result = await manager.execute(messages)
                
                # Verify
                assert result is not None
                assert "choices" in result
                assert mock_plan.called
    
    def test_get_statistics(self):
        """Test getting agent statistics"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        stats = manager.get_statistics()
        
        assert stats["name"] == "testmanager"
        assert stats["type"] == "ManagerAgent"
        assert stats["status"] == AgentStatus.IDLE.value
        assert stats["execution_count"] == 0
        assert stats["tools_registered"] == 0
        assert stats["workers_attached"] == 0


class TestWorkerAgent:
    """Test the WorkerAgent class"""
    
    def test_worker_initialization(self):
        """Test worker agent initialization"""
        worker = WorkerAgent(
            name="TestWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="Testing role duties",
            task_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string"}
                },
                "required": ["task"]
            }
        )
        
        assert worker.name == "testworker"
        assert worker.config.role == "Testing role duties"
        assert worker.task_schema is not None
        assert worker.is_worker is True
        assert worker.is_manager is False
    
    def test_worker_without_api_key(self):
        """Test worker without explicit API key (inherits from parent)"""
        worker = WorkerAgent(
            name="TestWorker",
            model="usf-mini",
            role="Support tasks"
        )

        assert worker.config.api_key == "inherited"
        assert worker.config.model == "usf-mini"
        assert not worker._is_standalone
    
    def test_inherit_parent_config(self):
        """Test worker inheriting configuration from parent"""
        manager = ManagerAgent(
            name="TestManager",
            api_key="parent-key-123",
            model="parent-model",
            knowledge_cutoff="1 January 2024"
        )
        
        worker = manager.create_worker(
            name="TestWorker",
            role="Worker Role"
        )
        
        # Worker should inherit parent's config
        assert worker.config.api_key == "parent-key-123"
        assert worker.config.model == "parent-model"
        assert worker._parent_agent is manager
    
    def test_create_sub_worker(self):
        """Test creating sub-workers under a worker"""
        parent_worker = WorkerAgent(
            name="ParentWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="Parent Role"
        )
        
        sub_worker = parent_worker.create_worker(
            name="SubWorker",
            role="Sub Worker Role"
        )
        
        assert sub_worker.name == "subworker"
        assert sub_worker.config.role == "Sub Worker Role"
        assert parent_worker.get_worker(sub_worker.name) is sub_worker
        assert sub_worker.name in parent_worker.list_workers()
    
    def test_get_tool_definition(self):
        """Test getting tool definition for worker"""
        worker = WorkerAgent(
            name="TestWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="Test Worker",
            task_schema={
                "type": "object",
                "properties": {
                    "custom_task": {"type": "string"},
                    "priority": {"type": "number"}
                },
                "required": ["custom_task"]
            }
        )
        
        tool_def = worker.get_tool_definition()
        
        assert tool_def.type == "function"
        assert tool_def.function.name == worker.name
        assert tool_def.function.description == "Test Worker"
        assert "custom_task" in tool_def.function.parameters["properties"]
        assert "priority" in tool_def.function.parameters["properties"]
    
    def test_worker_with_tools(self):
        """Test worker with registered tools"""
        worker = WorkerAgent(
            name="TestWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="General Worker"
        )
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "worker_tool",
                    "description": "Worker's tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"}
                        },
                        "required": ["data"]
                    }
                }
            }
        )
        async def worker_tool(data: str) -> str:
            return f"Worker processed: {data}"
        
        worker.register_tool(worker_tool)
        
        assert "worker_tool" in worker.list_tools()
        assert worker.tool_registry.has("worker_tool")
    
    @pytest.mark.asyncio
    async def test_worker_execution_mock(self):
        """Test worker execution with mocked APIs"""
        worker = WorkerAgent(
            name="TestWorker",
            api_key="test-key-1234",
            model="usf-mini",
            role="Execution Worker"
        )
        
        # Mock the API clients
        with patch.object(worker.plan_api, 'create_plan', new_callable=AsyncMock) as mock_plan:
            with patch.object(worker.plan_api, 'should_call_tool') as mock_should_call, \
                 patch('agentrouter.agents.worker.OpenAIResponseGenerator.generate_final_response', new_callable=AsyncMock) as mock_openai:
                # Setup mock responses
                mock_plan.return_value = Mock(
                    choices=[Mock(
                        message=Mock(
                            content="Worker response",
                            agent_status=AgentStatus.PREPARING_FINAL_RESPONSE
                        )
                    )],
                    usage={"total_tokens": 50}
                )
                mock_should_call.return_value = False
                mock_openai.return_value = {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "Worker final"},
                            "finish_reason": "stop",
                            "index": 0
                        }
                    ],
                    "usage": {"total_tokens": 30}
                }
                
                # Execute
                messages = [
                    Message(role="user", content="Task for worker")
                ]
                
                result = await worker.execute(messages)
                
                # Verify
                assert result is not None
                assert "choices" in result
                assert mock_plan.called


class TestAgentHierarchy:
    """Test multi-level agent hierarchies"""
    
    def test_three_level_hierarchy(self):
        """Test creating a three-level agent hierarchy"""
        # Level 1: Manager
        manager = ManagerAgent(
            name="Manager",
            api_key="test-key-1234"
        )
        
        # Level 2: Worker under Manager
        level2_worker = manager.create_worker(
            name="Level2Worker",
            role="Level 2 Worker"
        )
        
        # Level 3: Sub-worker under Worker
        level3_worker = level2_worker.create_worker(
            name="Level3Worker",
            role="Level 3 Worker"
        )
        
        # Verify hierarchy
        assert manager.get_worker(level2_worker.name) is level2_worker
        assert level2_worker.get_worker(level3_worker.name) is level3_worker
        assert level3_worker._parent_agent is level2_worker
        assert level2_worker._parent_agent is manager
    
    def test_shared_worker_multiple_parents(self):
        """Test attaching same worker to multiple parents"""
        # Create managers
        manager1 = ManagerAgent(name="Manager1", api_key="manager-key1-abc")
        manager2 = ManagerAgent(name="Manager2", api_key="manager-key2-abc")
        
        # Create standalone worker
        shared_worker = WorkerAgent(
            name="SharedWorker",
            api_key="shared-key-123",
            model="usf-mini",
            role="Shared Worker"
        )
        
        # Attach to both managers
        manager1.attach_worker(shared_worker)
        manager2.attach_worker(shared_worker)
        
        # Verify both have the worker
        assert manager1.get_worker(shared_worker.name) is shared_worker
        assert manager2.get_worker(shared_worker.name) is shared_worker
        
        # Note: In real usage, the last attachment overwrites _parent_agent
        assert shared_worker._parent_agent is manager2


class TestAgentPlugins:
    """Test agent plugin system"""
    
    def test_add_remove_plugin(self):
        """Test adding and removing plugins"""
        from agentrouter.plugins.base import Plugin, PluginHook
        
        class TestPlugin(Plugin):
            def get_hooks(self):
                return [PluginHook.BEFORE_EXECUTION]
            
            def on_before_execution(self, context):
                context["plugin_executed"] = True
                return context
        
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        plugin = TestPlugin(name="TestPlugin")
        
        # Add plugin
        manager.add_plugin(plugin)
        assert plugin in manager._plugins
        
        # Remove plugin
        result = manager.remove_plugin(plugin)
        assert result is True
        assert plugin not in manager._plugins
    
    @pytest.mark.asyncio
    async def test_plugin_execution(self):
        """Test plugin hooks are executed"""
        from agentrouter.plugins.base import Plugin, PluginHook
        
        class TrackingPlugin(Plugin):
            def __init__(self):
                super().__init__(name="TrackingPlugin")
                self.before_called = False
                self.after_called = False
            
            def get_hooks(self):
                return [
                    PluginHook.BEFORE_EXECUTION,
                    PluginHook.AFTER_EXECUTION
                ]
            
            def on_before_execution(self, context):
                self.before_called = True
                return context
            
            def on_after_execution(self, context):
                self.after_called = True
                return context
        
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234"
        )
        
        plugin = TrackingPlugin()
        manager.add_plugin(plugin)
        
        # Mock APIs to avoid actual calls
        with patch.object(manager.plan_api, 'create_plan', new_callable=AsyncMock):
            with patch.object(manager.plan_api, 'should_call_tool', return_value=False):
                # Apply hooks manually (simplified test)
                context = {"messages": [], "agent_name": "testmanager"}
                
                # Simulate before hook
                context = await manager._apply_plugin_hook(
                    "on_before_execution",
                    context
                )
                
                assert plugin.before_called
                
                # Simulate after hook
                context = await manager._apply_plugin_hook(
                    "on_after_execution",
                    context
                )
                
                assert plugin.after_called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
