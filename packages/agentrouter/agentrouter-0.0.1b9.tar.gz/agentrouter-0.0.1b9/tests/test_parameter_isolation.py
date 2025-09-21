"""
Test parameter isolation and system message generation
Verifies that each agent uses its own parameters with no data leakage
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from agentrouter.agents.manager import ManagerAgent
from agentrouter.agents.worker import WorkerAgent
from agentrouter.types import Message, MessageRole


class TestParameterIsolation:
    """Test that agent parameters are properly isolated"""
    
    @pytest.mark.asyncio
    async def test_manager_parameters_in_api_calls(self):
        """Test that manager uses its own parameters in API calls"""
        
        # Create manager with specific parameters
        manager = ManagerAgent(
            name="TestManager",
            api_key="test-key-1234",
            model="gpt-4",
            instruction="Manager instruction",
            backstory="Manager backstory",
            goal="Manager goal",
            knowledge_cutoff="15 January 2025",
            introduction="Manager introduction"
        )
        
        # Mock the Plan API
        with patch.object(manager.plan_api, 'create_plan', new=AsyncMock()) as mock_plan:
            mock_plan.return_value = MagicMock(
                choices=[MagicMock(
                    message=MagicMock(
                        content="Test response",
                        agent_status="preparing_final_response"
                    )
                )]
            )
            
            # Test message
            messages = [Message(role=MessageRole.USER, content="Test query")]
            
            # Call _call_plan_api
            await manager._call_plan_api(messages)
            
            # Verify Plan API was called with manager's parameters
            mock_plan.assert_called_once()
            call_args = mock_plan.call_args[1]
            
            assert call_args['instruction'] == "Manager instruction"
            assert call_args['backstory'] == "Manager backstory"
            assert call_args['goal'] == "Manager goal"
            assert call_args['knowledge_cutoff'] == "15 January 2025"
            assert call_args['introduction'] == "Manager introduction"
    
    @pytest.mark.asyncio
    async def test_worker_parameters_in_api_calls(self):
        """Test that worker uses its own parameters in API calls"""
        
        # Create standalone worker with its own parameters
        worker = WorkerAgent(
            name="TestWorker",
            api_key="worker-key-123",
            model="gpt-3.5",
            instruction="Worker instruction",
            backstory="Worker backstory",
            goal="Worker goal",
            knowledge_cutoff="1 December 2024",
            introduction="Worker introduction",
            role="Autonomous worker"
        )
        
        # Mock the Plan API
        with patch.object(worker.plan_api, 'create_plan', new=AsyncMock()) as mock_plan:
            mock_plan.return_value = MagicMock(
                choices=[MagicMock(
                    message=MagicMock(
                        content="Worker response",
                        agent_status="preparing_final_response"
                    )
                )]
            )
            
            # Test message
            messages = [Message(role=MessageRole.USER, content="Worker task")]
            
            # Call _call_plan_api
            await worker._call_plan_api(messages)
            
            # Verify Plan API was called with worker's parameters
            mock_plan.assert_called_once()
            call_args = mock_plan.call_args[1]
            
            assert call_args['instruction'] == "Worker instruction"
            assert call_args['backstory'] == "Worker backstory"
            assert call_args['goal'] == "Worker goal"
            assert call_args['knowledge_cutoff'] == "1 December 2024"
            assert call_args['introduction'] == "Worker introduction"
    
    @pytest.mark.asyncio
    async def test_worker_created_by_manager_has_own_parameters(self):
        """Test that workers created by manager have their own parameters"""
        
        # Create manager
        manager = ManagerAgent(
            name="ParentManager",
            api_key="manager-key-123",
            model="gpt-4",
            instruction="Manager instruction",
            backstory="Manager backstory",
            goal="Manager goal"
        )
        
        # Create worker with different parameters
        worker = manager.create_worker(
            name="ChildWorker",
            role="Child role",
            instruction="Worker specific instruction",
            backstory="Worker specific backstory",
            goal="Worker specific goal"
        )
        
        # Verify worker has its own parameters
        assert worker.config.instruction == "Worker specific instruction"
        assert worker.config.backstory == "Worker specific backstory"
        assert worker.config.goal == "Worker specific goal"
        
        # Verify worker did NOT inherit manager's parameters
        assert worker.config.instruction != manager.config.instruction
        assert worker.config.backstory != manager.config.backstory
        assert worker.config.goal != manager.config.goal
        
        # Verify worker DID inherit api_key and model
        assert worker.config.api_key == manager.config.api_key
        assert worker.config.model == manager.config.model
    
    def test_system_message_generation(self):
        """Test that system message contains agent's own parameters"""
        
        # Create manager with parameters
        manager = ManagerAgent(
            name="SysManager",
            api_key="test-key-1234",
            instruction="System test instruction",
            backstory="System test backstory",
            goal="System test goal",
            knowledge_cutoff="20 February 2025",
            introduction="System test introduction"
        )
        
        # Generate system message
        system_msg = manager._prepare_system_message()
        
        # Verify system message contains manager's parameters
        assert system_msg is not None
        assert "System test introduction" in system_msg.content
        assert "System test backstory" in system_msg.content
        assert "System test goal" in system_msg.content
        assert "20 February 2025" in system_msg.content
        assert "System test instruction" in system_msg.content
    
    def test_update_or_add_system_message(self):
        """Test that _update_or_add_system_message properly adds system message"""
        
        # Create agent with parameters
        agent = ManagerAgent(
            name="UpdateTest",
            api_key="test-key-1234",
            instruction="Update test instruction",
            backstory="Update test backstory",
            goal="Update test goal"
        )
        
        # Test messages without system message
        messages = [
            Message(role=MessageRole.USER, content="User query")
        ]
        
        # Add system message
        updated = agent._update_or_add_system_message(messages)
        
        # Verify system message was added at the beginning
        assert len(updated) == 2
        assert updated[0].role == "system"
        assert "Update test instruction" in updated[0].content
        assert "Update test backstory" in updated[0].content
        assert "Update test goal" in updated[0].content
        
        # Test with existing system message
        messages_with_system = [
            Message(role=MessageRole.SYSTEM, content="Existing system"),
            Message(role=MessageRole.USER, content="User query")
        ]
        
        # Update existing system message
        updated2 = agent._update_or_add_system_message(messages_with_system)
        
        # Verify system message was updated (not duplicated)
        assert len(updated2) == 2
        assert updated2[0].role == "system"
        assert "Existing system" in updated2[0].content
        assert "Update test instruction" in updated2[0].content
    
    @pytest.mark.asyncio
    async def test_openai_sdk_receives_system_message(self):
        """Test that OpenAI SDK receives system message with agent parameters"""
        
        # Create agent with parameters
        agent = ManagerAgent(
            name="OpenAITest",
            api_key="test-key-1234",
            model="gpt-4",
            instruction="OpenAI test instruction",
            backstory="OpenAI test backstory",
            goal="OpenAI test goal",
            provider="openai"  # This triggers OpenAI SDK usage
        )
        
        # Mock OpenAI SDK generator
        with patch('agentrouter.agents.manager.OpenAIResponseGenerator') as MockGenerator:
            mock_instance = MockGenerator.return_value
            mock_instance.generate_final_response = AsyncMock(return_value={
                "id": "test",
                "object": "chat.completion",
                "created": 123456,
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Test response"},
                    "finish_reason": "stop"
                }],
                "usage": {}
            })
            
            # Mock plan response
            plan_response = MagicMock(
                choices=[MagicMock(
                    message=MagicMock(
                        content="Plan content",
                        agent_status="preparing_final_response"
                    )
                )]
            )
            
            # Call _generate_final_response
            messages = [Message(role=MessageRole.USER, content="Test")]
            result = await agent._generate_final_response(
                messages, plan_response, streaming=False
            )
            
            # Verify OpenAI SDK was called
            mock_instance.generate_final_response.assert_called_once()
            
            # Get the messages passed to OpenAI SDK
            call_args = mock_instance.generate_final_response.call_args[1]
            passed_messages = call_args['messages']
            
            # Verify system message was added
            system_messages = [m for m in passed_messages if m.role == "system"]
            assert len(system_messages) > 0
            
            # Verify system message contains agent's parameters
            system_content = system_messages[0].content
            assert "OpenAI test instruction" in system_content
            assert "OpenAI test backstory" in system_content
            assert "OpenAI test goal" in system_content


class TestParameterInheritance:
    """Test parameter inheritance rules for workers"""
    
    def test_worker_inherits_correct_fields(self):
        """Test that workers inherit only the correct fields from parent"""
        
        # Create manager
        manager = ManagerAgent(
            name="ParentMgr",
            api_key="parent-key-123",
            model="parent-model",
            provider="openai",
            knowledge_cutoff="1 January 2025",
            current_time="2025-01-15T12:00:00Z",
            instruction="Parent instruction",
            backstory="Parent backstory",
            goal="Parent goal"
        )
        
        # Create worker without specifying inherited fields
        worker = manager.create_worker(
            name="ChildWrk",
            role="Primary support",
            # Don't specify api_key, model, provider, knowledge_cutoff, current_time
            # Don't specify instruction, backstory, goal (these should NOT inherit)
        )
        
        # Verify correct inheritance
        # These SHOULD be inherited:
        assert worker.config.api_key == manager.config.api_key
        assert worker.config.model == manager.config.model
        
        # These should NOT be inherited (should be empty/default):
        assert worker.config.instruction == ""  # Empty default
        assert worker.config.backstory == ""     # Empty default
        assert worker.config.goal == ""          # Empty default
        
        # Worker can have its own values
        worker2 = manager.create_worker(
            name="ChildWrk2",
            role="Secondary support",
            instruction="Worker2 instruction",
            backstory="Worker2 backstory",
            goal="Worker2 goal"
        )
        
        # Verify worker has its own values
        assert worker2.config.instruction == "Worker2 instruction"
        assert worker2.config.backstory == "Worker2 backstory"
        assert worker2.config.goal == "Worker2 goal"
        
        # Still inherits api_key and model
        assert worker2.config.api_key == manager.config.api_key
        assert worker2.config.model == manager.config.model


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
