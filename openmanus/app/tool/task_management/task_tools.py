"""
Task management tools for RenumTaskMaster.

This module provides tools for the RenumTaskMaster agent to interact with the TaskStore.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from app.tool.base import BaseTool
from app.tool.task_management.task_store import TaskStore, Task


class CreateTaskTool(BaseTool):
    """Tool for creating a new task."""
    
    name = "create_task"
    description = "Create a new task with the given description, due date, and priority."
    parameters = {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Description of the task"
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format (YYYY-MM-DD), optional"
            },
            "priority": {
                "type": "string",
                "description": "Priority level (baixa, média, alta), defaults to 'média'"
            }
        },
        "required": ["description"]
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the CreateTaskTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(self, description: str, due_date: Optional[str] = None, priority: str = "média") -> Dict:
        """
        Execute the tool to create a new task.
        
        Args:
            description: Description of the task
            due_date: Due date in ISO format (YYYY-MM-DD)
            priority: Priority level (baixa, média, alta)
            
        Returns:
            Dictionary with task details and success message
        """
        # Validate priority
        if priority.lower() not in ["baixa", "média", "alta", "media"]:
            priority = "média"
        
        # Normalize "media" to "média"
        if priority.lower() == "media":
            priority = "média"
            
        # Validate due_date format if provided
        if due_date:
            try:
                datetime.fromisoformat(due_date)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format."
                }
        
        # Create the task
        task = self.task_store.create_task(
            description=description,
            due_date=due_date,
            priority=priority
        )
        
        return {
            "success": True,
            "message": f"Task created successfully with ID: {task.id}",
            "task": task.to_dict()
        }


class GetTaskTool(BaseTool):
    """Tool for retrieving a specific task."""
    
    name = "get_task"
    description = "Get a task by ID or description."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to retrieve"
            },
            "description": {
                "type": "string",
                "description": "Description of the task to retrieve (exact match)"
            }
        }
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the GetTaskTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(self, task_id: Optional[str] = None, description: Optional[str] = None) -> Dict:
        """
        Execute the tool to retrieve a task.
        
        Args:
            task_id: ID of the task to retrieve
            description: Description of the task to retrieve (exact match)
            
        Returns:
            Dictionary with task details or error message
        """
        if not task_id and not description:
            return {
                "success": False,
                "error": "Either task_id or description must be provided."
            }
        
        task = self.task_store.get_task(task_id, description)
        
        if task:
            return {
                "success": True,
                "task": task.to_dict()
            }
        else:
            search_term = task_id if task_id else f"description '{description}'"
            return {
                "success": False,
                "error": f"No task found with {search_term}."
            }


class GetTasksTool(BaseTool):
    """Tool for retrieving multiple tasks based on filters."""
    
    name = "get_tasks"
    description = "Get tasks filtered by status, due date, or priority."
    parameters = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (pendente, em_progresso, concluída)"
            },
            "due_date": {
                "type": "string",
                "description": "Filter by due date in ISO format (YYYY-MM-DD)"
            },
            "priority": {
                "type": "string",
                "description": "Filter by priority (baixa, média, alta)"
            }
        }
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the GetTasksTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(
        self, 
        status: Optional[str] = None, 
        due_date: Optional[str] = None, 
        priority: Optional[str] = None
    ) -> Dict:
        """
        Execute the tool to retrieve tasks based on filters.
        
        Args:
            status: Filter by status
            due_date: Filter by due date
            priority: Filter by priority
            
        Returns:
            Dictionary with list of tasks
        """
        # Normalize status values
        if status:
            status_map = {
                "pendente": "pendente",
                "em progresso": "em_progresso",
                "em_progresso": "em_progresso",
                "concluída": "concluída",
                "concluida": "concluída",
                "completa": "concluída",
                "finalizada": "concluída"
            }
            status = status_map.get(status.lower(), status)
        
        # Normalize priority values
        if priority:
            priority_map = {
                "baixa": "baixa",
                "média": "média",
                "media": "média",
                "alta": "alta"
            }
            priority = priority_map.get(priority.lower(), priority)
        
        tasks = self.task_store.get_tasks(status, due_date, priority)
        
        return {
            "success": True,
            "count": len(tasks),
            "tasks": [task.to_dict() for task in tasks]
        }


class UpdateTaskStatusTool(BaseTool):
    """Tool for updating the status of a task."""
    
    name = "update_task_status"
    description = "Update the status of a task identified by ID or description."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to update"
            },
            "description": {
                "type": "string",
                "description": "Description of the task to update (exact match)"
            },
            "status": {
                "type": "string",
                "description": "New status (pendente, em_progresso, concluída)"
            }
        },
        "required": ["status"]
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the UpdateTaskStatusTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(
        self, 
        status: str, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Dict:
        """
        Execute the tool to update a task's status.
        
        Args:
            status: New status
            task_id: ID of the task to update
            description: Description of the task to update (exact match)
            
        Returns:
            Dictionary with updated task details or error message
        """
        if not task_id and not description:
            return {
                "success": False,
                "error": "Either task_id or description must be provided."
            }
        
        # Normalize status values
        status_map = {
            "pendente": "pendente",
            "em progresso": "em_progresso",
            "em_progresso": "em_progresso",
            "concluída": "concluída",
            "concluida": "concluída",
            "completa": "concluída",
            "finalizada": "concluída"
        }
        normalized_status = status_map.get(status.lower(), status)
        
        task = self.task_store.update_task_status(normalized_status, task_id, description)
        
        if task:
            return {
                "success": True,
                "message": f"Task status updated to '{normalized_status}'.",
                "task": task.to_dict()
            }
        else:
            search_term = task_id if task_id else f"description '{description}'"
            return {
                "success": False,
                "error": f"No task found with {search_term}."
            }


class UpdateTaskPriorityTool(BaseTool):
    """Tool for updating the priority of a task."""
    
    name = "update_task_priority"
    description = "Update the priority of a task identified by ID or description."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to update"
            },
            "description": {
                "type": "string",
                "description": "Description of the task to update (exact match)"
            },
            "priority": {
                "type": "string",
                "description": "New priority (baixa, média, alta)"
            }
        },
        "required": ["priority"]
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the UpdateTaskPriorityTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(
        self, 
        priority: str, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Dict:
        """
        Execute the tool to update a task's priority.
        
        Args:
            priority: New priority
            task_id: ID of the task to update
            description: Description of the task to update (exact match)
            
        Returns:
            Dictionary with updated task details or error message
        """
        if not task_id and not description:
            return {
                "success": False,
                "error": "Either task_id or description must be provided."
            }
        
        # Normalize priority values
        priority_map = {
            "baixa": "baixa",
            "média": "média",
            "media": "média",
            "alta": "alta"
        }
        normalized_priority = priority_map.get(priority.lower(), "média")
        
        task = self.task_store.update_task_priority(normalized_priority, task_id, description)
        
        if task:
            return {
                "success": True,
                "message": f"Task priority updated to '{normalized_priority}'.",
                "task": task.to_dict()
            }
        else:
            search_term = task_id if task_id else f"description '{description}'"
            return {
                "success": False,
                "error": f"No task found with {search_term}."
            }


class DeleteTaskTool(BaseTool):
    """Tool for deleting a task."""
    
    name = "delete_task"
    description = "Delete a task identified by ID or description."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to delete"
            },
            "description": {
                "type": "string",
                "description": "Description of the task to delete (exact match)"
            }
        }
    }
    
    def __init__(self, task_store: TaskStore):
        """
        Initialize the DeleteTaskTool.
        
        Args:
            task_store: TaskStore instance for persistence
        """
        super().__init__()
        self.task_store = task_store
    
    async def execute(
        self, 
        task_id: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Dict:
        """
        Execute the tool to delete a task.
        
        Args:
            task_id: ID of the task to delete
            description: Description of the task to delete (exact match)
            
        Returns:
            Dictionary with success message or error
        """
        if not task_id and not description:
            return {
                "success": False,
                "error": "Either task_id or description must be provided."
            }
        
        # Get the task first to include in the response
        task = self.task_store.get_task(task_id, description)
        if not task:
            search_term = task_id if task_id else f"description '{description}'"
            return {
                "success": False,
                "error": f"No task found with {search_term}."
            }
        
        task_dict = task.to_dict()  # Save before deletion
        
        success = self.task_store.delete_task(task_id, description)
        
        if success:
            return {
                "success": True,
                "message": "Task deleted successfully.",
                "deleted_task": task_dict
            }
        else:
            search_term = task_id if task_id else f"description '{description}'"
            return {
                "success": False,
                "error": f"Failed to delete task with {search_term}."
            }
