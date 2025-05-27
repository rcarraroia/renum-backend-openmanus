"""
API routes for interacting with the RenumTaskMaster agent.

This module provides FastAPI routes for sending prompts to the RenumTaskMaster
agent and receiving responses.
"""

import os
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.process.manager import ProcessManager

# Create router
router = APIRouter(prefix="/taskmaster", tags=["taskmaster"])

# Global ProcessManager instance
process_manager: Optional[ProcessManager] = None


class PromptRequest(BaseModel):
    """Request model for sending prompts to the agent."""
    prompt: str


class PromptResponse(BaseModel):
    """Response model for agent responses."""
    response: Dict[str, Any]


async def get_process_manager() -> ProcessManager:
    """
    Get or initialize the ProcessManager.
    
    Returns:
        Initialized ProcessManager instance
    """
    global process_manager
    
    if process_manager is None or not process_manager.is_running:
        # Define paths based on the project structure
        executable_path = os.environ.get("PYTHON_EXECUTABLE", "python")
        script_path = os.environ.get(
            "OPENMANUS_SCRIPT_PATH", 
            os.path.join(os.getcwd(), "openmanus", "run_mcp_server.py")
        )
        working_dir = os.environ.get(
            "OPENMANUS_WORKING_DIR",
            os.path.join(os.getcwd(), "openmanus")
        )
        
        # Create and initialize the ProcessManager
        process_manager = ProcessManager(
            executable_path=executable_path,
            script_path=script_path,
            working_dir=working_dir
        )
        
        # Initialize the process
        success = await process_manager.initialize()
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize OpenManus process"
            )
    
    return process_manager


@router.post("/prompt", response_model=PromptResponse)
async def send_prompt(
    request: PromptRequest,
    process_manager: ProcessManager = Depends(get_process_manager)
) -> PromptResponse:
    """
    Send a prompt to the RenumTaskMaster agent and get the response.
    
    Args:
        request: The prompt request
        process_manager: The ProcessManager instance
        
    Returns:
        The agent's response
    """
    try:
        # Send the prompt to the agent
        response = await process_manager.send_prompt_and_get_response(request.prompt)
        
        # Return the response
        return PromptResponse(response=response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prompt: {str(e)}"
        )


@router.post("/shutdown")
async def shutdown_agent(
    background_tasks: BackgroundTasks,
    process_manager: ProcessManager = Depends(get_process_manager)
) -> Dict[str, str]:
    """
    Shutdown the RenumTaskMaster agent.
    
    Args:
        background_tasks: FastAPI background tasks
        process_manager: The ProcessManager instance
        
    Returns:
        Success message
    """
    # Schedule shutdown in the background
    background_tasks.add_task(process_manager.shutdown)
    
    return {"message": "Agent shutdown initiated"}


@router.get("/status")
async def get_agent_status(
    process_manager: ProcessManager = Depends(get_process_manager)
) -> Dict[str, Any]:
    """
    Get the status of the RenumTaskMaster agent.
    
    Args:
        process_manager: The ProcessManager instance
        
    Returns:
        Status information
    """
    return {
        "initialized": process_manager.is_initialized,
        "running": process_manager.is_running,
        "last_activity": process_manager.last_activity
    }
