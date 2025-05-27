"""
API routes for interacting with the CodeSupportAgent.

This module provides FastAPI routes for accessing the code support agent's
capabilities through a REST API.
"""

from typing import Dict, Any, Optional
import os

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from app.agent.codesupport import CodeSupportAgent


# Initialize router
router = APIRouter(
    prefix="/api/codesupport",
    tags=["codesupport"],
    responses={404: {"description": "Not found"}},
)

# Initialize agent (lazy loading)
_agent = None


def get_agent() -> CodeSupportAgent:
    """
    Get or initialize the CodeSupportAgent.
    
    Returns:
        Initialized CodeSupportAgent instance
    """
    global _agent
    if _agent is None:
        # Use environment variables or defaults
        model = os.environ.get("CODESUPPORT_MODEL", "gpt-4")
        temperature = float(os.environ.get("CODESUPPORT_TEMPERATURE", "0.3"))
        output_dir = os.environ.get("CODESUPPORT_OUTPUT_DIR", "/tmp/code")
        
        _agent = CodeSupportAgent(
            model=model,
            temperature=temperature,
            output_dir=output_dir
        )
    
    return _agent


# Request/Response models
class MessageRequest(BaseModel):
    """Model for message request."""
    message: str


class ProjectRequest(BaseModel):
    """Model for project generation request."""
    project_type: str
    project_name: str


class BoilerplateRequest(BaseModel):
    """Model for boilerplate generation request."""
    project_type: str
    project_name: str


class StructureRequest(BaseModel):
    """Model for file structure generation request."""
    structure_type: str
    project_name: str


class TestGenerationRequest(BaseModel):
    """Model for test generation request."""
    file_path: str
    test_framework: Optional[str] = "unittest"


@router.post("/message")
async def process_message(request: MessageRequest) -> Dict[str, Any]:
    """
    Process a natural language message for code support.
    
    Args:
        request: Message request containing the user's message
        
    Returns:
        Dictionary with the agent's response and any generated code
    """
    try:
        agent = get_agent()
        result = await agent.process_message(request.message)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/project")
async def generate_project(request: ProjectRequest) -> Dict[str, Any]:
    """
    Generate a complete project structure based on project type.
    
    Args:
        request: Project request containing type and name
        
    Returns:
        Dictionary with the result of the operation
    """
    try:
        agent = get_agent()
        result = await agent.generate_project_structure(
            project_type=request.project_type,
            project_name=request.project_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/boilerplate")
async def generate_boilerplate(request: BoilerplateRequest) -> Dict[str, Any]:
    """
    Generate boilerplate code for a specific project type.
    
    Args:
        request: Boilerplate request containing project type and name
        
    Returns:
        Dictionary with the result of the operation
    """
    try:
        agent = get_agent()
        result = await agent.boilerplate_tool.execute(
            project_type=request.project_type,
            project_name=request.project_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/structure")
async def generate_structure(request: StructureRequest) -> Dict[str, Any]:
    """
    Generate a file structure for a specific project type.
    
    Args:
        request: Structure request containing structure type and project name
        
    Returns:
        Dictionary with the result of the operation
    """
    try:
        agent = get_agent()
        result = await agent.structure_tool.execute(
            structure_type=request.structure_type,
            project_name=request.project_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/tests")
async def generate_tests(request: TestGenerationRequest) -> Dict[str, Any]:
    """
    Generate unit tests for a Python file.
    
    Args:
        request: Test generation request containing file path and test framework
        
    Returns:
        Dictionary with the result of the operation
    """
    try:
        agent = get_agent()
        result = await agent.test_tool.execute(
            file_path=request.file_path,
            test_framework=request.test_framework
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
