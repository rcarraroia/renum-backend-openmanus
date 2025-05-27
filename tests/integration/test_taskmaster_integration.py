"""
Integration tests for the RenumTaskMaster agent.

This module contains tests for the integration between the ProcessManager,
RenumTaskMaster agent, and the task management tools.
"""

import asyncio
import json
import os
import tempfile
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.process.manager import ProcessManager


class MockProcess:
    """Mock subprocess for testing."""
    
    def __init__(self, responses=None):
        """
        Initialize the mock process.
        
        Args:
            responses: Dictionary mapping prompts to responses
        """
        self.responses = responses or {}
        self.stdin = AsyncMock()
        self.stdout = AsyncMock()
        self.stderr = AsyncMock()
        self.returncode = None
        
        # Configure stdout.readline to return responses
        self.stdout.readline.side_effect = self._get_response
        
    async def _get_response(self):
        """Simulate reading a response from stdout."""
        # Default response if no specific response is configured
        default_response = json.dumps({
            "response": "This is a mock response from the RenumTaskMaster agent."
        }).encode("utf-8") + b"\n"
        
        # Return the default response
        return default_response
    
    async def wait(self):
        """Simulate waiting for the process to complete."""
        return 0
    
    def terminate(self):
        """Simulate terminating the process."""
        self.returncode = 0
    
    def kill(self):
        """Simulate killing the process."""
        self.returncode = -9


class TestProcessManagerIntegration:
    """Integration tests for the ProcessManager."""
    
    @pytest.fixture
    def mock_process(self):
        """Create a mock subprocess for testing."""
        return MockProcess()
    
    @pytest.mark.asyncio
    async def test_process_manager_initialization(self, mock_process):
        """Test that the ProcessManager can be initialized."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            success = await manager.initialize()
            
            assert success is True
            assert manager.is_initialized is True
            assert manager.is_running is True
    
    @pytest.mark.asyncio
    async def test_send_prompt_and_get_response(self, mock_process):
        """Test sending a prompt and getting a response."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            
            # Configure mock to return a specific response
            mock_response = json.dumps({
                "response": "Task created successfully",
                "task": {
                    "id": "test-id-123",
                    "description": "Test task",
                    "priority": "alta",
                    "status": "pendente"
                }
            }).encode("utf-8") + b"\n"
            
            mock_process.stdout.readline.return_value = mock_response
            
            response = await manager.send_prompt_and_get_response(
                "Create a task 'Test task' with high priority"
            )
            
            assert "response" in response
            assert response["response"] == "Task created successfully"
            assert "task" in response
            assert response["task"]["description"] == "Test task"
            
            # Verify that the prompt was sent correctly
            mock_process.stdin.write.assert_called_once()
            
            # The write call should contain the prompt in JSON format
            call_args = mock_process.stdin.write.call_args[0][0]
            sent_data = json.loads(call_args.decode("utf-8"))
            assert "prompt" in sent_data
            assert sent_data["prompt"] == "Create a task 'Test task' with high priority"
    
    @pytest.mark.asyncio
    async def test_process_manager_recovery(self, mock_process):
        """Test that the ProcessManager can recover from failures."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp",
                max_retries=1,
                retry_delay=0.1
            )
            
            await manager.initialize()
            
            # Simulate a broken pipe
            mock_process.stdin.write.side_effect = BrokenPipeError("Broken pipe")
            
            # Create a new mock process for recovery
            recovery_mock = MockProcess()
            
            # Configure the recovery mock to return a specific response
            recovery_response = json.dumps({
                "response": "Task created after recovery",
                "task": {
                    "id": "recovery-id-456",
                    "description": "Recovery task",
                    "priority": "média",
                    "status": "pendente"
                }
            }).encode("utf-8") + b"\n"
            
            recovery_mock.stdout.readline.return_value = recovery_response
            
            # Replace the create_subprocess_exec mock to return the recovery mock
            with patch("asyncio.create_subprocess_exec", return_value=recovery_mock):
                response = await manager.send_prompt_and_get_response(
                    "Create a task 'Recovery task'"
                )
                
                assert "response" in response
                assert response["response"] == "Task created after recovery"
                assert "task" in response
                assert response["task"]["description"] == "Recovery task"
    
    @pytest.mark.asyncio
    async def test_process_manager_shutdown(self, mock_process):
        """Test that the ProcessManager can be shut down."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            await manager.shutdown()
            
            assert manager.is_running is False
            assert manager.is_initialized is False
            assert mock_process.terminate.called


class TestTaskMasterIntegration:
    """
    Integration tests for the RenumTaskMaster agent.
    
    These tests simulate real interactions with the agent through the ProcessManager.
    """
    
    @pytest.fixture
    def task_responses(self):
        """Create a dictionary of mock responses for different task commands."""
        return {
            "Create a task 'Test task' with high priority": json.dumps({
                "response": "I've created a new task 'Test task' with high priority.",
                "task": {
                    "id": "test-id-123",
                    "description": "Test task",
                    "priority": "alta",
                    "status": "pendente",
                    "due_date": None,
                    "created_at": "2025-05-27T12:00:00",
                    "updated_at": "2025-05-27T12:00:00"
                }
            }),
            
            "What tasks do I have pending?": json.dumps({
                "response": "You have 1 pending task:",
                "tasks": [
                    {
                        "id": "test-id-123",
                        "description": "Test task",
                        "priority": "alta",
                        "status": "pendente",
                        "due_date": None,
                        "created_at": "2025-05-27T12:00:00",
                        "updated_at": "2025-05-27T12:00:00"
                    }
                ]
            }),
            
            "Mark 'Test task' as completed": json.dumps({
                "response": "I've marked the task 'Test task' as completed.",
                "task": {
                    "id": "test-id-123",
                    "description": "Test task",
                    "priority": "alta",
                    "status": "concluída",
                    "due_date": None,
                    "created_at": "2025-05-27T12:00:00",
                    "updated_at": "2025-05-27T12:30:00"
                }
            })
        }
    
    @pytest.fixture
    def mock_taskmaster_process(self, task_responses):
        """Create a mock process that simulates the RenumTaskMaster agent."""
        process = MockProcess()
        
        # Configure the mock to return different responses based on the prompt
        async def custom_readline():
            # Get the last prompt sent to stdin
            if not process.stdin.write.call_args:
                return json.dumps({"response": "No prompt received yet"}).encode("utf-8") + b"\n"
            
            last_call = process.stdin.write.call_args[0][0]
            try:
                sent_data = json.loads(last_call.decode("utf-8"))
                prompt = sent_data.get("prompt", "")
                
                # Look up the response for this prompt
                if prompt in task_responses:
                    return task_responses[prompt].encode("utf-8") + b"\n"
                else:
                    return json.dumps({
                        "response": f"I don't have a specific response for: {prompt}"
                    }).encode("utf-8") + b"\n"
                    
            except (json.JSONDecodeError, UnicodeDecodeError):
                return json.dumps({"response": "Invalid prompt format"}).encode("utf-8") + b"\n"
        
        process.stdout.readline.side_effect = custom_readline
        return process
    
    @pytest.mark.asyncio
    async def test_create_task_flow(self, mock_taskmaster_process):
        """Test the flow of creating a task."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_taskmaster_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            
            response = await manager.send_prompt_and_get_response(
                "Create a task 'Test task' with high priority"
            )
            
            assert "response" in response
            assert "I've created a new task" in response["response"]
            assert "task" in response
            assert response["task"]["description"] == "Test task"
            assert response["task"]["priority"] == "alta"
    
    @pytest.mark.asyncio
    async def test_query_tasks_flow(self, mock_taskmaster_process):
        """Test the flow of querying tasks."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_taskmaster_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            
            # First create a task
            await manager.send_prompt_and_get_response(
                "Create a task 'Test task' with high priority"
            )
            
            # Then query pending tasks
            response = await manager.send_prompt_and_get_response(
                "What tasks do I have pending?"
            )
            
            assert "response" in response
            assert "You have 1 pending task" in response["response"]
            assert "tasks" in response
            assert len(response["tasks"]) == 1
            assert response["tasks"][0]["description"] == "Test task"
    
    @pytest.mark.asyncio
    async def test_update_task_flow(self, mock_taskmaster_process):
        """Test the flow of updating a task's status."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_taskmaster_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            
            # First create a task
            await manager.send_prompt_and_get_response(
                "Create a task 'Test task' with high priority"
            )
            
            # Then mark it as completed
            response = await manager.send_prompt_and_get_response(
                "Mark 'Test task' as completed"
            )
            
            assert "response" in response
            assert "I've marked the task" in response["response"]
            assert "task" in response
            assert response["task"]["status"] == "concluída"
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, mock_taskmaster_process):
        """Test a complete workflow of creating, querying, and updating tasks."""
        with patch("asyncio.create_subprocess_exec", return_value=mock_taskmaster_process):
            manager = ProcessManager(
                executable_path="python",
                script_path="test_script.py",
                working_dir="/tmp"
            )
            
            await manager.initialize()
            
            # Create a task
            create_response = await manager.send_prompt_and_get_response(
                "Create a task 'Test task' with high priority"
            )
            
            assert "I've created a new task" in create_response["response"]
            
            # Query pending tasks
            query_response = await manager.send_prompt_and_get_response(
                "What tasks do I have pending?"
            )
            
            assert "You have 1 pending task" in query_response["response"]
            
            # Mark task as completed
            update_response = await manager.send_prompt_and_get_response(
                "Mark 'Test task' as completed"
            )
            
            assert "I've marked the task" in update_response["response"]
            assert update_response["task"]["status"] == "concluída"
            
            # Verify the process remained active throughout
            assert manager.is_running is True
            assert mock_taskmaster_process.terminate.call_count == 0
