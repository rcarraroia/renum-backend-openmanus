"""
Code Support agent implementation for the Renum project.

This agent specializes in generating code boilerplate, file structures,
and unit tests based on user prompts.
"""

from typing import Dict, List, Any, Optional
import os
import json
import asyncio

from app.agent.base import BaseAgent
from app.tool.code_support import (
    BoilerplateGeneratorTool,
    FileStructureGeneratorTool,
    UnitTestGeneratorTool
)


class CodeSupportAgent(BaseAgent):
    """
    Agent specialized in code support and generation.
    
    This agent can generate boilerplate code, file structures, and unit tests
    based on natural language prompts.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.3, output_dir: str = "/tmp/code"):
        """
        Initialize the CodeSupportAgent.
        
        Args:
            model: LLM model to use
            temperature: Temperature for generation (lower = more precise)
            output_dir: Directory for storing generated code
        """
        super().__init__(model=model, temperature=temperature)
        
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Register tools
        self._register_tools()
        
        # Set system prompt
        self._set_system_prompt()
    
    def _register_tools(self) -> None:
        """Register all tools for the code support agent."""
        # Boilerplate generator tool
        boilerplate_tool = BoilerplateGeneratorTool(self.output_dir)
        self.register_tool(boilerplate_tool)
        
        # File structure generator tool
        structure_tool = FileStructureGeneratorTool(self.output_dir)
        self.register_tool(structure_tool)
        
        # Unit test generator tool
        test_tool = UnitTestGeneratorTool(os.path.join(self.output_dir, "tests"))
        self.register_tool(test_tool)
        
        # Store references to tools for direct access
        self.boilerplate_tool = boilerplate_tool
        self.structure_tool = structure_tool
        self.test_tool = test_tool
    
    def _set_system_prompt(self) -> None:
        """Set the system prompt for the code support agent."""
        system_prompt = """
        You are a professional software developer specializing in code generation and project setup.
        Your expertise includes creating boilerplate code, setting up project structures, and generating unit tests.
        
        When responding to user requests:
        1. Analyze the user's intent and identify what type of code support they need
        2. Extract key information such as programming language, project type, and specific requirements
        3. Use the appropriate tool to generate the requested code or structure
        4. Provide clear explanations of the generated code and how to use it
        
        For boilerplate code generation:
        - Consider the specific project type the user needs
        - Generate code that follows best practices for the chosen language/framework
        - Explain the structure and purpose of the generated code
        
        For file structure generation:
        - Choose the most appropriate structure template for the user's needs
        - Explain the purpose of each directory and file in the structure
        - Provide guidance on how to extend the structure for specific needs
        
        For unit test generation:
        - Analyze the provided code to identify functions and classes to test
        - Generate comprehensive test templates that cover the main functionality
        - Explain how to complete and extend the generated tests
        
        Always aim to be helpful, clear, and responsive to the user's specific needs.
        """
        
        self.set_system_prompt(system_prompt)
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and perform code support operations.
        
        Args:
            message: User message requesting code support
            
        Returns:
            Dictionary with the agent's response and any generated code
        """
        # Process the message using the LLM and tools
        response = await self.generate_response(message)
        
        # Extract any file paths from the response
        file_paths = self._extract_file_paths(response)
        
        # Collect all results
        results = {
            "response": response,
            "generated_files": []
        }
        
        # Add file contents if any were created
        for path in file_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                    results["generated_files"].append({
                        "path": path,
                        "content": content
                    })
        
        return results
    
    def _extract_file_paths(self, response: str) -> List[str]:
        """
        Extract file paths from the agent's response.
        
        Args:
            response: Agent's response text
            
        Returns:
            List of file paths mentioned in the response
        """
        import re
        
        # Pattern to match file paths
        pattern = r'(/tmp/.*?\.(?:py|js|html|css|json|md|txt))'
        
        # Find all matches
        matches = re.findall(pattern, response)
        
        return matches
    
    async def generate_project_structure(self, project_type: str, project_name: str) -> Dict[str, Any]:
        """
        Generate a complete project structure based on project type.
        
        This is a convenience method that combines boilerplate and structure generation.
        
        Args:
            project_type: Type of project to generate
            project_name: Name of the project
            
        Returns:
            Dictionary with the result of the operation
        """
        try:
            # Map project type to appropriate structure and boilerplate types
            structure_map = {
                "python_script": "python_package",
                "python_fastapi_app": "python_package",
                "python_flask_app": "python_package",
                "javascript_react_app": "web_project_basic",
                "javascript_node_express_app": "web_project_basic",
                "html_basic_page": "web_project_basic",
                "data_science": "data_science_project",
                "documentation": "docs_project"
            }
            
            # Generate structure first
            structure_type = structure_map.get(project_type, "python_package")
            structure_result = await self.structure_tool.execute(
                structure_type=structure_type,
                project_name=project_name
            )
            
            if not structure_result["success"]:
                return structure_result
            
            # Then generate boilerplate if applicable
            if project_type in ["python_script", "python_fastapi_app", "python_flask_app", 
                               "javascript_react_app", "javascript_node_express_app", "html_basic_page"]:
                boilerplate_result = await self.boilerplate_tool.execute(
                    project_type=project_type,
                    project_name=project_name
                )
                
                if not boilerplate_result["success"]:
                    return {
                        "success": True,
                        "message": f"Generated structure but failed to generate boilerplate: {boilerplate_result['error']}",
                        "project_path": structure_result["project_path"]
                    }
            
            return {
                "success": True,
                "message": f"Generated complete project structure for {project_type}: {project_name}",
                "project_path": structure_result["project_path"]
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
