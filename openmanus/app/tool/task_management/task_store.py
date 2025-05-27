"""
TaskStore module for RenumTaskMaster.

This module provides a simple persistence layer for tasks, using a JSON file
as storage. It implements basic CRUD operations and query capabilities.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union


class Task:
    """Represents a task in the system."""

    def __init__(
        self,
        description: str,
        due_date: Optional[str] = None,
        priority: str = "média",
        status: str = "pendente",
        task_id: Optional[str] = None,
    ):
        """
        Initialize a new Task.

        Args:
            description: Description of the task
            due_date: Due date in ISO format (YYYY-MM-DD)
            priority: Priority level (baixa, média, alta)
            status: Current status (pendente, em_progresso, concluída)
            task_id: Unique identifier (generated if not provided)
        """
        self.id = task_id or str(uuid.uuid4())
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """Create a Task instance from a dictionary."""
        task = cls(
            description=data["description"],
            due_date=data.get("due_date"),
            priority=data.get("priority", "média"),
            status=data.get("status", "pendente"),
            task_id=data.get("id"),
        )
        task.created_at = data.get("created_at", task.created_at)
        task.updated_at = data.get("updated_at", task.updated_at)
        return task


class TaskStore:
    """Manages task persistence using a JSON file."""

    def __init__(self, storage_path: str = "tasks.json"):
        """
        Initialize the TaskStore.

        Args:
            storage_path: Path to the JSON file for task storage
        """
        self.storage_path = storage_path
        self.tasks: Dict[str, Task] = {}
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from the storage file if it exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        self.tasks[task.id] = task
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading tasks: {e}")
                # Create a backup of the corrupted file
                if os.path.exists(self.storage_path):
                    backup_path = f"{self.storage_path}.bak"
                    os.rename(self.storage_path, backup_path)
                    print(f"Created backup of corrupted file at {backup_path}")

    def _save_tasks(self) -> None:
        """Save tasks to the storage file."""
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            with open(self.storage_path, "w") as f:
                json.dump(tasks_data, f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def create_task(
        self, description: str, due_date: Optional[str] = None, priority: str = "média"
    ) -> Task:
        """
        Create a new task.

        Args:
            description: Description of the task
            due_date: Due date in ISO format (YYYY-MM-DD)
            priority: Priority level (baixa, média, alta)

        Returns:
            The created Task object
        """
        task = Task(description=description, due_date=due_date, priority=priority)
        self.tasks[task.id] = task
        self._save_tasks()
        return task

    def get_task(self, task_id: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
        """
        Get a task by ID or description.

        Args:
            task_id: ID of the task to retrieve
            description: Description of the task to retrieve (exact match)

        Returns:
            Task object if found, None otherwise
        """
        if task_id and task_id in self.tasks:
            return self.tasks[task_id]
        
        if description:
            for task in self.tasks.values():
                if task.description.lower() == description.lower():
                    return task
        
        return None

    def get_tasks(
        self, 
        status: Optional[str] = None, 
        due_date: Optional[str] = None, 
        priority: Optional[str] = None
    ) -> List[Task]:
        """
        Get tasks filtered by criteria.

        Args:
            status: Filter by status
            due_date: Filter by due date
            priority: Filter by priority

        Returns:
            List of Task objects matching the criteria
        """
        filtered_tasks = list(self.tasks.values())
        
        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status.lower() == status.lower()]
        
        if due_date:
            filtered_tasks = [task for task in filtered_tasks if task.due_date == due_date]
        
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority.lower() == priority.lower()]
        
        return filtered_tasks

    def update_task_status(
        self, 
        status: str, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update the status of a task.

        Args:
            status: New status
            task_id: ID of the task to update
            description: Description of the task to update (exact match)

        Returns:
            Updated Task object if found, None otherwise
        """
        task = self.get_task(task_id, description)
        if task:
            task.status = status
            task.updated_at = datetime.now().isoformat()
            self._save_tasks()
        return task

    def update_task_priority(
        self, 
        priority: str, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update the priority of a task.

        Args:
            priority: New priority
            task_id: ID of the task to update
            description: Description of the task to update (exact match)

        Returns:
            Updated Task object if found, None otherwise
        """
        task = self.get_task(task_id, description)
        if task:
            task.priority = priority
            task.updated_at = datetime.now().isoformat()
            self._save_tasks()
        return task

    def delete_task(
        self, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete
            description: Description of the task to delete (exact match)

        Returns:
            True if task was deleted, False otherwise
        """
        task = self.get_task(task_id, description)
        if task:
            del self.tasks[task.id]
            self._save_tasks()
            return True
        return False
