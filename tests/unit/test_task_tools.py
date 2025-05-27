"""
Unit tests for task management tools.

This module contains tests for the task management tools used by the RenumTaskMaster agent.
"""

import os
import tempfile
from typing import Dict, Any

import pytest

from app.tool.task_management.task_store import TaskStore
from app.tool.task_management.task_tools import (
    CreateTaskTool,
    GetTaskTool,
    GetTasksTool,
    UpdateTaskStatusTool,
    UpdateTaskPriorityTool,
    DeleteTaskTool
)


class TestTaskTools:
    """Tests for the task management tools."""

    @pytest.fixture
    def task_store(self):
        """Create a TaskStore instance for testing."""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        store = TaskStore(storage_path=path)
        yield store
        os.unlink(path)

    @pytest.mark.asyncio
    async def test_create_task_tool(self, task_store):
        """Test that the CreateTaskTool creates a task correctly."""
        tool = CreateTaskTool(task_store)
        
        # Test with minimal parameters
        result = await tool.execute(description="Test task")
        
        assert result["success"] is True
        assert "Task created successfully" in result["message"]
        assert result["task"]["description"] == "Test task"
        assert result["task"]["priority"] == "média"
        assert result["task"]["status"] == "pendente"
        
        # Test with all parameters
        result = await tool.execute(
            description="Another task",
            due_date="2025-05-28",
            priority="alta"
        )
        
        assert result["success"] is True
        assert result["task"]["description"] == "Another task"
        assert result["task"]["due_date"] == "2025-05-28"
        assert result["task"]["priority"] == "alta"
        
        # Test with invalid priority (should default to "média")
        result = await tool.execute(
            description="Invalid priority task",
            priority="invalid"
        )
        
        assert result["success"] is True
        assert result["task"]["priority"] == "média"
        
        # Test with invalid date format
        result = await tool.execute(
            description="Invalid date task",
            due_date="28/05/2025"  # Not ISO format
        )
        
        assert result["success"] is False
        assert "Invalid date format" in result["error"]

    @pytest.mark.asyncio
    async def test_get_task_tool(self, task_store):
        """Test that the GetTaskTool retrieves a task correctly."""
        # Create a task to retrieve
        task = task_store.create_task(
            description="Test task",
            due_date="2025-05-28",
            priority="alta"
        )
        
        tool = GetTaskTool(task_store)
        
        # Test retrieval by ID
        result = await tool.execute(task_id=task.id)
        
        assert result["success"] is True
        assert result["task"]["id"] == task.id
        assert result["task"]["description"] == "Test task"
        
        # Test retrieval by description
        result = await tool.execute(description="Test task")
        
        assert result["success"] is True
        assert result["task"]["id"] == task.id
        
        # Test retrieval with non-existent ID
        result = await tool.execute(task_id="non-existent-id")
        
        assert result["success"] is False
        assert "No task found" in result["error"]
        
        # Test retrieval with no parameters
        result = await tool.execute()
        
        assert result["success"] is False
        assert "Either task_id or description must be provided" in result["error"]

    @pytest.mark.asyncio
    async def test_get_tasks_tool(self, task_store):
        """Test that the GetTasksTool retrieves tasks correctly."""
        # Create some tasks with different properties
        task_store.create_task(
            description="Pending task",
            priority="baixa"
        )
        task_store.create_task(
            description="In progress task",
            priority="média",
            status="em_progresso"
        )
        completed_task = task_store.create_task(
            description="Completed task",
            priority="alta"
        )
        task_store.update_task_status("concluída", task_id=completed_task.id)
        
        tool = GetTasksTool(task_store)
        
        # Test retrieval of all tasks
        result = await tool.execute()
        
        assert result["success"] is True
        assert result["count"] == 3
        
        # Test filtering by status
        result = await tool.execute(status="pendente")
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["description"] == "Pending task"
        
        # Test filtering by priority
        result = await tool.execute(priority="alta")
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["description"] == "Completed task"
        
        # Test filtering by status with normalization
        result = await tool.execute(status="concluída")
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["description"] == "Completed task"

    @pytest.mark.asyncio
    async def test_update_task_status_tool(self, task_store):
        """Test that the UpdateTaskStatusTool updates a task's status correctly."""
        # Create a task to update
        task = task_store.create_task(description="Test task")
        
        tool = UpdateTaskStatusTool(task_store)
        
        # Test update by ID
        result = await tool.execute(
            task_id=task.id,
            status="concluída"
        )
        
        assert result["success"] is True
        assert "Task status updated" in result["message"]
        assert result["task"]["status"] == "concluída"
        
        # Test update by description
        task2 = task_store.create_task(description="Another task")
        
        result = await tool.execute(
            description="Another task",
            status="em_progresso"
        )
        
        assert result["success"] is True
        assert result["task"]["status"] == "em_progresso"
        
        # Test update with non-existent task
        result = await tool.execute(
            task_id="non-existent-id",
            status="concluída"
        )
        
        assert result["success"] is False
        assert "No task found" in result["error"]
        
        # Test update with no task identifier
        result = await tool.execute(status="concluída")
        
        assert result["success"] is False
        assert "Either task_id or description must be provided" in result["error"]
        
        # Test status normalization
        result = await tool.execute(
            task_id=task.id,
            status="completa"  # Should be normalized to "concluída"
        )
        
        assert result["success"] is True
        assert result["task"]["status"] == "concluída"

    @pytest.mark.asyncio
    async def test_update_task_priority_tool(self, task_store):
        """Test that the UpdateTaskPriorityTool updates a task's priority correctly."""
        # Create a task to update
        task = task_store.create_task(description="Test task")
        
        tool = UpdateTaskPriorityTool(task_store)
        
        # Test update by ID
        result = await tool.execute(
            task_id=task.id,
            priority="alta"
        )
        
        assert result["success"] is True
        assert "Task priority updated" in result["message"]
        assert result["task"]["priority"] == "alta"
        
        # Test update by description
        task2 = task_store.create_task(description="Another task")
        
        result = await tool.execute(
            description="Another task",
            priority="baixa"
        )
        
        assert result["success"] is True
        assert result["task"]["priority"] == "baixa"
        
        # Test update with non-existent task
        result = await tool.execute(
            task_id="non-existent-id",
            priority="alta"
        )
        
        assert result["success"] is False
        assert "No task found" in result["error"]
        
        # Test update with no task identifier
        result = await tool.execute(priority="alta")
        
        assert result["success"] is False
        assert "Either task_id or description must be provided" in result["error"]
        
        # Test priority normalization
        result = await tool.execute(
            task_id=task.id,
            priority="media"  # Should be normalized to "média"
        )
        
        assert result["success"] is True
        assert result["task"]["priority"] == "média"

    @pytest.mark.asyncio
    async def test_delete_task_tool(self, task_store):
        """Test that the DeleteTaskTool deletes a task correctly."""
        # Create a task to delete
        task = task_store.create_task(description="Test task")
        
        tool = DeleteTaskTool(task_store)
        
        # Test deletion by ID
        result = await tool.execute(task_id=task.id)
        
        assert result["success"] is True
        assert "Task deleted successfully" in result["message"]
        assert result["deleted_task"]["id"] == task.id
        
        # Verify that the task was actually deleted
        assert task_store.get_task(task_id=task.id) is None
        
        # Test deletion by description
        task2 = task_store.create_task(description="Another task")
        
        result = await tool.execute(description="Another task")
        
        assert result["success"] is True
        assert "Task deleted successfully" in result["message"]
        
        # Test deletion with non-existent task
        result = await tool.execute(task_id="non-existent-id")
        
        assert result["success"] is False
        assert "No task found" in result["error"]
        
        # Test deletion with no task identifier
        result = await tool.execute()
        
        assert result["success"] is False
        assert "Either task_id or description must be provided" in result["error"]
