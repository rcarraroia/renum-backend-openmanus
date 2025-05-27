"""
Unit tests for TaskStore module.

This module contains tests for the TaskStore class and Task model.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime

import pytest

from app.tool.task_management.task_store import Task, TaskStore


class TestTask:
    """Tests for the Task class."""

    def test_task_initialization(self):
        """Test that a Task can be initialized with default values."""
        task = Task(description="Test task")
        
        assert task.description == "Test task"
        assert task.due_date is None
        assert task.priority == "média"
        assert task.status == "pendente"
        assert task.id is not None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_initialization_with_values(self):
        """Test that a Task can be initialized with specific values."""
        task = Task(
            description="Test task",
            due_date="2025-05-28",
            priority="alta",
            status="em_progresso",
            task_id="test-id-123"
        )
        
        assert task.description == "Test task"
        assert task.due_date == "2025-05-28"
        assert task.priority == "alta"
        assert task.status == "em_progresso"
        assert task.id == "test-id-123"

    def test_task_to_dict(self):
        """Test that a Task can be converted to a dictionary."""
        task = Task(
            description="Test task",
            due_date="2025-05-28",
            priority="alta",
            status="em_progresso",
            task_id="test-id-123"
        )
        
        task_dict = task.to_dict()
        
        assert task_dict["id"] == "test-id-123"
        assert task_dict["description"] == "Test task"
        assert task_dict["due_date"] == "2025-05-28"
        assert task_dict["priority"] == "alta"
        assert task_dict["status"] == "em_progresso"
        assert "created_at" in task_dict
        assert "updated_at" in task_dict

    def test_task_from_dict(self):
        """Test that a Task can be created from a dictionary."""
        task_dict = {
            "id": "test-id-123",
            "description": "Test task",
            "due_date": "2025-05-28",
            "priority": "alta",
            "status": "em_progresso",
            "created_at": "2025-05-27T12:00:00",
            "updated_at": "2025-05-27T12:00:00"
        }
        
        task = Task.from_dict(task_dict)
        
        assert task.id == "test-id-123"
        assert task.description == "Test task"
        assert task.due_date == "2025-05-28"
        assert task.priority == "alta"
        assert task.status == "em_progresso"
        assert task.created_at == "2025-05-27T12:00:00"
        assert task.updated_at == "2025-05-27T12:00:00"


class TestTaskStore:
    """Tests for the TaskStore class."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield path
        os.unlink(path)

    def test_task_store_initialization(self, temp_file):
        """Test that a TaskStore can be initialized."""
        store = TaskStore(storage_path=temp_file)
        assert store.tasks == {}

    def test_create_task(self, temp_file):
        """Test that a task can be created and stored."""
        store = TaskStore(storage_path=temp_file)
        task = store.create_task(
            description="Test task",
            due_date="2025-05-28",
            priority="alta"
        )
        
        assert task.description == "Test task"
        assert task.due_date == "2025-05-28"
        assert task.priority == "alta"
        assert task.id in store.tasks
        assert store.tasks[task.id] == task

    def test_get_task_by_id(self, temp_file):
        """Test that a task can be retrieved by ID."""
        store = TaskStore(storage_path=temp_file)
        task = store.create_task(description="Test task")
        
        retrieved_task = store.get_task(task_id=task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.description == "Test task"

    def test_get_task_by_description(self, temp_file):
        """Test that a task can be retrieved by description."""
        store = TaskStore(storage_path=temp_file)
        store.create_task(description="Test task")
        
        retrieved_task = store.get_task(description="Test task")
        
        assert retrieved_task is not None
        assert retrieved_task.description == "Test task"

    def test_get_tasks_no_filter(self, temp_file):
        """Test that all tasks can be retrieved."""
        store = TaskStore(storage_path=temp_file)
        store.create_task(description="Task 1")
        store.create_task(description="Task 2")
        
        tasks = store.get_tasks()
        
        assert len(tasks) == 2
        assert any(task.description == "Task 1" for task in tasks)
        assert any(task.description == "Task 2" for task in tasks)

    def test_get_tasks_with_status_filter(self, temp_file):
        """Test that tasks can be filtered by status."""
        store = TaskStore(storage_path=temp_file)
        task1 = store.create_task(description="Task 1")
        task2 = store.create_task(description="Task 2")
        
        store.update_task_status("concluída", task_id=task1.id)
        
        pending_tasks = store.get_tasks(status="pendente")
        completed_tasks = store.get_tasks(status="concluída")
        
        assert len(pending_tasks) == 1
        assert pending_tasks[0].description == "Task 2"
        
        assert len(completed_tasks) == 1
        assert completed_tasks[0].description == "Task 1"

    def test_update_task_status(self, temp_file):
        """Test that a task's status can be updated."""
        store = TaskStore(storage_path=temp_file)
        task = store.create_task(description="Test task")
        
        updated_task = store.update_task_status("concluída", task_id=task.id)
        
        assert updated_task is not None
        assert updated_task.status == "concluída"
        assert store.tasks[task.id].status == "concluída"

    def test_update_task_priority(self, temp_file):
        """Test that a task's priority can be updated."""
        store = TaskStore(storage_path=temp_file)
        task = store.create_task(description="Test task")
        
        updated_task = store.update_task_priority("alta", task_id=task.id)
        
        assert updated_task is not None
        assert updated_task.priority == "alta"
        assert store.tasks[task.id].priority == "alta"

    def test_delete_task(self, temp_file):
        """Test that a task can be deleted."""
        store = TaskStore(storage_path=temp_file)
        task = store.create_task(description="Test task")
        
        success = store.delete_task(task_id=task.id)
        
        assert success is True
        assert task.id not in store.tasks

    def test_persistence(self, temp_file):
        """Test that tasks are persisted to and loaded from storage."""
        # Create tasks in one instance
        store1 = TaskStore(storage_path=temp_file)
        task1 = store1.create_task(description="Task 1")
        task2 = store1.create_task(description="Task 2")
        
        # Create a new instance that should load from the same file
        store2 = TaskStore(storage_path=temp_file)
        
        # Check that tasks were loaded
        assert len(store2.tasks) == 2
        assert task1.id in store2.tasks
        assert task2.id in store2.tasks
        assert store2.tasks[task1.id].description == "Task 1"
        assert store2.tasks[task2.id].description == "Task 2"

    def test_corrupted_file_handling(self, temp_file):
        """Test that corrupted storage files are handled gracefully."""
        # Write invalid JSON to the file
        with open(temp_file, "w") as f:
            f.write("This is not valid JSON")
        
        # Should not raise an exception
        store = TaskStore(storage_path=temp_file)
        
        # Should start with an empty task list
        assert store.tasks == {}
        
        # Should create a backup of the corrupted file
        assert os.path.exists(f"{temp_file}.bak")
