"""
Unit tests for the code support tools.

This module contains tests for the BoilerplateGeneratorTool, FileStructureGeneratorTool,
and UnitTestGeneratorTool classes.
"""

import os
import unittest
import tempfile
import shutil
import asyncio

from app.tool.code_support.code_tools import (
    BoilerplateGeneratorTool,
    FileStructureGeneratorTool,
    UnitTestGeneratorTool
)


class TestBoilerplateGeneratorTool(unittest.TestCase):
    """Tests for the BoilerplateGeneratorTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.tool = BoilerplateGeneratorTool(self.test_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_generate_python_script(self):
        """Test generating a Python script boilerplate."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            project_type="python_script",
            project_name="test_script"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected file was created
        script_path = os.path.join(self.test_dir, "test_script", "test_script.py")
        self.assertTrue(os.path.exists(script_path))
        
        # Check that the file has content
        with open(script_path, "r") as f:
            content = f.read()
            self.assertIn("#!/usr/bin/env python3", content)
            self.assertIn("import argparse", content)
    
    def test_generate_fastapi_app(self):
        """Test generating a FastAPI application boilerplate."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            project_type="python_fastapi_app",
            project_name="test_api"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected files were created
        main_py_path = os.path.join(self.test_dir, "test_api", "main.py")
        req_path = os.path.join(self.test_dir, "test_api", "requirements.txt")
        readme_path = os.path.join(self.test_dir, "test_api", "README.md")
        
        self.assertTrue(os.path.exists(main_py_path))
        self.assertTrue(os.path.exists(req_path))
        self.assertTrue(os.path.exists(readme_path))
        
        # Check that the main.py file has FastAPI-specific content
        with open(main_py_path, "r") as f:
            content = f.read()
            self.assertIn("from fastapi import FastAPI", content)
            self.assertIn("app = FastAPI()", content)
    
    def test_invalid_project_type(self):
        """Test handling of invalid project type."""
        # Run the tool with an invalid project type
        result = asyncio.run(self.tool.execute(
            project_type="invalid_type",
            project_name="test_project"
        ))
        
        # Check that the operation failed
        self.assertFalse(result["success"])
        self.assertIn("Unknown project type", result["error"])


class TestFileStructureGeneratorTool(unittest.TestCase):
    """Tests for the FileStructureGeneratorTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.tool = FileStructureGeneratorTool(self.test_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_generate_python_package_structure(self):
        """Test generating a Python package structure."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            structure_type="python_package",
            project_name="test_package"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected directories and files were created
        project_path = os.path.join(self.test_dir, "test_package")
        package_path = os.path.join(project_path, "test_package")
        tests_path = os.path.join(project_path, "tests")
        setup_path = os.path.join(project_path, "setup.py")
        
        self.assertTrue(os.path.exists(package_path))
        self.assertTrue(os.path.exists(tests_path))
        self.assertTrue(os.path.exists(setup_path))
        self.assertTrue(os.path.exists(os.path.join(package_path, "__init__.py")))
        self.assertTrue(os.path.exists(os.path.join(tests_path, "__init__.py")))
    
    def test_generate_web_project_structure(self):
        """Test generating a web project structure."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            structure_type="web_project_basic",
            project_name="test_web"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected directories and files were created
        project_path = os.path.join(self.test_dir, "test_web")
        css_path = os.path.join(project_path, "css")
        js_path = os.path.join(project_path, "js")
        index_path = os.path.join(project_path, "index.html")
        
        self.assertTrue(os.path.exists(css_path))
        self.assertTrue(os.path.exists(js_path))
        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(os.path.join(css_path, "style.css")))
        self.assertTrue(os.path.exists(os.path.join(js_path, "script.js")))
    
    def test_invalid_structure_type(self):
        """Test handling of invalid structure type."""
        # Run the tool with an invalid structure type
        result = asyncio.run(self.tool.execute(
            structure_type="invalid_structure",
            project_name="test_project"
        ))
        
        # Check that the operation failed
        self.assertFalse(result["success"])
        self.assertIn("Unknown structure type", result["error"])


class TestUnitTestGeneratorTool(unittest.TestCase):
    """Tests for the UnitTestGeneratorTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.tool = UnitTestGeneratorTool(self.test_dir)
        
        # Create a sample Python file for testing
        self.sample_file_path = os.path.join(self.test_dir, "sample.py")
        with open(self.sample_file_path, "w") as f:
            f.write("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

class Calculator:
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
""")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_generate_unittest_tests(self):
        """Test generating unittest tests."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            file_path=self.sample_file_path,
            test_framework="unittest"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected test file was created
        test_file_path = os.path.join(self.test_dir, "test_sample.py")
        self.assertTrue(os.path.exists(test_file_path))
        
        # Check that the test file has unittest-specific content
        with open(test_file_path, "r") as f:
            content = f.read()
            self.assertIn("import unittest", content)
            self.assertIn("class TestSampleFunctions(unittest.TestCase):", content)
            self.assertIn("def test_add(self):", content)
            self.assertIn("def test_subtract(self):", content)
            self.assertIn("class TestCalculator(unittest.TestCase):", content)
            self.assertIn("def test_multiply(self):", content)
            self.assertIn("def test_divide(self):", content)
    
    def test_generate_pytest_tests(self):
        """Test generating pytest tests."""
        # Run the tool
        result = asyncio.run(self.tool.execute(
            file_path=self.sample_file_path,
            test_framework="pytest"
        ))
        
        # Check that the operation was successful
        self.assertTrue(result["success"])
        
        # Check that the expected test file was created
        test_file_path = os.path.join(self.test_dir, "test_sample.py")
        self.assertTrue(os.path.exists(test_file_path))
        
        # Check that the test file has pytest-specific content
        with open(test_file_path, "r") as f:
            content = f.read()
            self.assertIn("import pytest", content)
            self.assertIn("def test_add():", content)
            self.assertIn("def test_subtract():", content)
            self.assertIn("class TestCalculator:", content)
            self.assertIn("@pytest.fixture", content)
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        # Run the tool with a non-existent file
        result = asyncio.run(self.tool.execute(
            file_path="/path/to/nonexistent/file.py",
            test_framework="unittest"
        ))
        
        # Check that the operation failed
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["error"])
    
    def test_non_python_file(self):
        """Test handling of non-Python file."""
        # Create a non-Python file
        non_py_file = os.path.join(self.test_dir, "not_python.txt")
        with open(non_py_file, "w") as f:
            f.write("This is not a Python file")
        
        # Run the tool with a non-Python file
        result = asyncio.run(self.tool.execute(
            file_path=non_py_file,
            test_framework="unittest"
        ))
        
        # Check that the operation failed
        self.assertFalse(result["success"])
        self.assertIn("Input must be a Python file", result["error"])


if __name__ == "__main__":
    unittest.main()
