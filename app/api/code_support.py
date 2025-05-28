"""
API endpoints for Code Support Agent.

This module defines the RESTful API endpoints for the Code Support Agent,
allowing interaction with the agent's tools and capabilities.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import datetime
from app.process.factory import AgentProcessFactory
from app.agent.code_support_prompt import CODE_SUPPORT_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/agents/code-support",
    tags=["code-support"],
    responses={404: {"description": "Not found"}},
)

# Define request and response models
class BoilerplateRequest(BaseModel):
    language: str = Field(..., description="Programming language (python, javascript, java)")
    code_type: str = Field(..., description="Type of code to generate (function, class)")
    name: str = Field(..., description="Name of the function or class")
    description: Optional[str] = Field(None, description="Description of the function or class")
    params: Optional[List[Dict[str, Any]]] = Field(None, description="List of parameter dictionaries")
    return_type: Optional[str] = Field(None, description="Return type of the function")
    methods: Optional[List[Dict[str, Any]]] = Field(None, description="List of method dictionaries for classes")
    style: Optional[str] = Field("standard", description="Coding style (standard, google, pep8, etc.)")

class TestGeneratorRequest(BaseModel):
    language: str = Field(..., description="Programming language (python, javascript, java)")
    framework: str = Field(..., description="Testing framework (unittest, pytest, jest, mocha, junit)")
    test_type: str = Field(..., description="Type of test (function, class)")
    module_name: str = Field(..., description="Name of the module containing the code to test")
    function_name: Optional[str] = Field(None, description="Name of the function to test (for function tests)")
    class_name: Optional[str] = Field(None, description="Name of the class to test (for class tests)")
    methods: Optional[List[Dict[str, Any]]] = Field(None, description="List of method dictionaries (for class tests)")
    params: Optional[List[Dict[str, Any]]] = Field(None, description="List of parameter dictionaries")
    return_type: Optional[str] = Field(None, description="Return type of the function")
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="List of test case dictionaries")
    package_name: Optional[str] = Field(None, description="Java package name (for Java tests)")

class ProjectStructureRequest(BaseModel):
    language: str = Field(..., description="Programming language (python, javascript, java)")
    framework: str = Field(..., description="Framework or project type (basic, flask, node, react, maven)")
    project_name: str = Field(..., description="Name of the project")
    project_description: Optional[str] = Field(None, description="Description of the project")
    output_dir: Optional[str] = Field(None, description="Directory where the project will be generated")
    package_name: Optional[str] = Field(None, description="Name of the package (for Java/Node.js projects)")
    group_id: Optional[str] = Field(None, description="Group ID (for Java Maven projects)")

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for the Code Support Agent")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuing an existing conversation")

class AgentResponse(BaseModel):
    response: str = Field(..., description="Response from the agent")
    conversation_id: str = Field(..., description="Conversation ID for continuing the conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the response")

# Initialize agent factory
agent_factory = AgentProcessFactory()

@router.post("/boilerplate", response_model=Dict[str, Any], summary="Generate code boilerplate")
async def generate_boilerplate(request: BoilerplateRequest):
    """
    Generate code boilerplate based on the provided parameters.
    
    This endpoint uses the BoilerplateGeneratorTool to create function
    or class templates with appropriate documentation and structure.
    """
    try:
        # Create agent instance if needed
        agent_id = "code_support_boilerplate"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CODE_SUPPORT_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "language": request.language,
            "code_type": request.code_type,
            "name": request.name,
            "description": request.description,
            "params": request.params,
            "return_type": request.return_type,
            "methods": request.methods,
            "style": request.style
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the BoilerplateGeneratorTool to generate code with the following parameters:
        - Language: {request.language}
        - Code Type: {request.code_type}
        - Name: {request.name}
        - Description: {request.description or '[Not provided]'}
        - Style: {request.style}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract code from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.code_support.boilerplate_generator import BoilerplateGeneratorTool
        boilerplate_tool = BoilerplateGeneratorTool()
        boilerplate_result = await boilerplate_tool._arun(**tool_params)
        
        return boilerplate_result
        
    except Exception as e:
        logger.error(f"Error generating boilerplate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tests", response_model=Dict[str, Any], summary="Generate unit tests")
async def generate_tests(request: TestGeneratorRequest):
    """
    Generate unit tests based on the provided parameters.
    
    This endpoint uses the TestGeneratorTool to create test cases for
    functions or classes with appropriate assertions and structure.
    """
    try:
        # Create agent instance if needed
        agent_id = "code_support_tests"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CODE_SUPPORT_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "language": request.language,
            "framework": request.framework,
            "test_type": request.test_type,
            "module_name": request.module_name,
            "function_name": request.function_name,
            "class_name": request.class_name,
            "methods": request.methods,
            "params": request.params,
            "return_type": request.return_type,
            "test_cases": request.test_cases,
            "package_name": request.package_name
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the TestGeneratorTool to generate tests with the following parameters:
        - Language: {request.language}
        - Framework: {request.framework}
        - Test Type: {request.test_type}
        - Module Name: {request.module_name}
        - {'Function Name: ' + request.function_name if request.function_name else 'Class Name: ' + request.class_name}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract tests from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.code_support.test_generator import TestGeneratorTool
        test_tool = TestGeneratorTool()
        test_result = await test_tool._arun(**tool_params)
        
        return test_result
        
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project-structure", response_model=Dict[str, Any], summary="Generate project structure")
async def generate_project_structure(request: ProjectStructureRequest):
    """
    Generate project structure based on the provided parameters.
    
    This endpoint uses the ProjectStructureTool to create directory structures,
    configuration files, and boilerplate code for various project types.
    """
    try:
        # Create agent instance if needed
        agent_id = "code_support_project"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CODE_SUPPORT_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "language": request.language,
            "framework": request.framework,
            "project_name": request.project_name,
            "project_description": request.project_description,
            "output_dir": request.output_dir,
            "package_name": request.package_name,
            "group_id": request.group_id
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the ProjectStructureTool to generate a project structure with the following parameters:
        - Language: {request.language}
        - Framework: {request.framework}
        - Project Name: {request.project_name}
        - Project Description: {request.project_description or '[Not provided]'}
        - Output Directory: {request.output_dir or '[Default]'}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract result from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.code_support.project_structure import ProjectStructureTool
        project_tool = ProjectStructureTool()
        project_result = await project_tool._arun(**tool_params)
        
        return project_result
        
    except Exception as e:
        logger.error(f"Error generating project structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompt", response_model=AgentResponse, summary="Send a prompt to the Code Support Agent")
async def send_prompt(request: PromptRequest):
    """
    Send a prompt to the Code Support Agent and get a response.
    
    This endpoint allows free-form interaction with the agent, which will
    use its tools and capabilities to respond appropriately.
    """
    try:
        # Create or get agent instance
        agent_id = request.conversation_id or "code_support_" + str(hash(request.prompt))[:8]
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CODE_SUPPORT_SYSTEM_PROMPT)
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, request.prompt)
        
        # Return response
        return {
            "response": response,
            "conversation_id": agent_id,
            "metadata": {
                "prompt_length": len(request.prompt),
                "response_length": len(response),
                "timestamp": str(datetime.datetime.now())
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{conversation_id}", response_model=Dict[str, Any], summary="End a conversation")
async def end_conversation(conversation_id: str):
    """
    End a conversation with the Code Support Agent.
    
    This endpoint terminates the specified agent instance and
    cleans up associated resources.
    """
    try:
        # Check if agent exists
        if not agent_factory.agent_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Terminate agent
        agent_factory.terminate_agent(conversation_id)
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} ended successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
