"""
Integration tests for the CodeSupportAgent.

This module contains tests for the CodeSupportAgent's ability to generate
code, file structures, and unit tests based on user prompts.
"""

import os
import unittest
import tempfile
import shutil
import asyncio
import json

from app.agent.codesupport import CodeSupportAgent


class TestCodeSupportAgentIntegration(unittest.TestCase):
    """Integration tests for the CodeSupportAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Initialize the agent with the test directory
        self.agent = CodeSupportAgent(
            model="gpt-4",  # Can be mocked in actual tests
            temperature=0.3,
            output_dir=self.test_dir
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    async def test_process_message_boilerplate_request(self):
        """Test processing a message requesting boilerplate code."""
        # Mock the generate_response method to avoid actual LLM calls
        original_generate_response = self.agent.generate_response
        
        async def mock_generate_response(message):
            # Simulate the agent using the boilerplate tool
            result = await self.agent.boilerplate_tool.execute(
                project_type="python_script",
                project_name="test_script"
            )
            
            # Create a response that mentions the file path
            script_path = os.path.join(self.test_dir, "test_script", "test_script.py")
            return f"I've created a Python script for you at {script_path}. This script includes basic argument parsing and a main function."
        
        try:
            # Replace the generate_response method with our mock
            self.agent.generate_response = mock_generate_response
            
            # Process a message
            result = await self.agent.process_message("Can you create a simple Python script for me?")
            
            # Check that the response contains the expected text
            self.assertIn("I've created a Python script for you", result["response"])
            
            # Check that the generated files list contains the script
            self.assertEqual(len(result["generated_files"]), 1)
            self.assertIn("test_script.py", result["generated_files"][0]["path"])
            
            # Check that the file content is as expected
            self.assertIn("#!/usr/bin/env python3", result["generated_files"][0]["content"])
            self.assertIn("import argparse", result["generated_files"][0]["content"])
        
        finally:
            # Restore the original method
            self.agent.generate_response = original_generate_response
    
    async def test_process_message_structure_request(self):
        """Test processing a message requesting a file structure."""
        # Mock the generate_response method to avoid actual LLM calls
        original_generate_response = self.agent.generate_response
        
        async def mock_generate_response(message):
            # Simulate the agent using the structure tool
            result = await self.agent.structure_tool.execute(
                structure_type="python_package",
                project_name="test_package"
            )
            
            # Create a response that mentions the project path
            project_path = os.path.join(self.test_dir, "test_package")
            return f"I've created a Python package structure for you at {project_path}. This includes the main package directory, tests directory, and setup files."
        
        try:
            # Replace the generate_response method with our mock
            self.agent.generate_response = mock_generate_response
            
            # Process a message
            result = await self.agent.process_message("Can you set up a Python package structure for me?")
            
            # Check that the response contains the expected text
            self.assertIn("I've created a Python package structure for you", result["response"])
            
            # Check that the generated files list contains setup.py
            setup_py_found = False
            for file_info in result["generated_files"]:
                if "setup.py" in file_info["path"]:
                    setup_py_found = True
                    break
            
            self.assertTrue(setup_py_found)
        
        finally:
            # Restore the original method
            self.agent.generate_response = original_generate_response
    
    async def test_process_message_test_generator_request(self):
        """Test processing a message requesting unit test generation."""
        # Create a sample Python file for testing
        sample_file_path = os.path.join(self.test_dir, "sample.py")
        with open(sample_file_path, "w") as f:
            f.write("""
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b
""")
        
        # Mock the generate_response method to avoid actual LLM calls
        original_generate_response = self.agent.generate_response
        
        async def mock_generate_response(message):
            # Simulate the agent using the test tool
            result = await self.agent.test_tool.execute(
                file_path=sample_file_path,
                test_framework="unittest"
            )
            
            # Create a response that mentions the test file path
            test_file_path = os.path.join(self.test_dir, "tests", "test_sample.py")
            return f"I've created unit tests for your Python file at {test_file_path}. These tests include test cases for the add function and Calculator class."
        
        try:
            # Replace the generate_response method with our mock
            self.agent.generate_response = mock_generate_response
            
            # Process a message
            result = await self.agent.process_message(f"Can you generate unit tests for {sample_file_path}?")
            
            # Check that the response contains the expected text
            self.assertIn("I've created unit tests for your Python file", result["response"])
            
            # Check that the generated files list contains the test file
            test_file_found = False
            for file_info in result["generated_files"]:
                if "test_sample.py" in file_info["path"]:
                    test_file_found = True
                    self.assertIn("import unittest", file_info["content"])
                    self.assertIn("def test_add", file_info["content"])
                    self.assertIn("class TestCalculator", file_info["content"])
                    break
            
            self.assertTrue(test_file_found)
        
        finally:
            # Restore the original method
            self.agent.generate_response = original_generate_response
    
    async def test_generate_project_structure(self):
        """Test the generate_project_structure convenience method."""
        # Call the method
        result = await self.agent.generate_project_structure(
            project_type="python_fastapi_app",
            project_name="test_api"
        )
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected files were created
        project_path = os.path.join(self.test_dir, "test_api")
        main_py_path = os.path.join(project_path, "main.py")
        
        self.assertTrue(os.path.exists(project_path))
        self.assertTrue(os.path.exists(main_py_path))
        
        # Check that the main.py file has FastAPI-specific content
        with open(main_py_path, "r") as f:
            content = f.read()
            self.assertIn("from fastapi import FastAPI", content)
            self.assertIn("app = FastAPI()", content)


# Run the tests
if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add the test cases
    suite.addTest(unittest.makeSuite(TestCodeSupportAgentIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(suite)
