"""
Code generation tools for the Renum project.

This module provides tools for generating boilerplate code, file structures,
and basic unit tests.
"""

from typing import Dict, List, Any, Optional
import os
import json

from app.tool.base import BaseTool


class BoilerplateGeneratorTool(BaseTool):
    """
    Tool for generating boilerplate code for various programming languages.
    
    This tool creates basic file structures and starter code for common
    project types like web applications, APIs, scripts, etc.
    """
    
    def __init__(self, output_dir: str = "/tmp/code"):
        """
        Initialize the BoilerplateGeneratorTool.
        
        Args:
            output_dir: Directory to save generated code
        """
        super().__init__(
            name="boilerplate_generator",
            description="Generate boilerplate code for various project types",
            parameters={
                "project_type": {
                    "type": "string",
                    "description": "Type of project to generate boilerplate for",
                    "enum": [
                        "python_script",
                        "python_fastapi_app",
                        "python_flask_app",
                        "javascript_react_app",
                        "javascript_node_express_app",
                        "html_basic_page"
                    ]
                },
                "project_name": {
                    "type": "string",
                    "description": "Name of the project (used for directory/file names)",
                    "required": True
                }
            }
        )
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the boilerplate generator tool.
        
        Args:
            project_type: Type of project to generate boilerplate for
            project_name: Name of the project
            
        Returns:
            Dictionary with the result, including the path to the generated project
        """
        project_type = kwargs.get("project_type")
        project_name = kwargs.get("project_name")
        
        if not project_name:
            return {"success": False, "error": "Project name is required"}
        
        project_path = os.path.join(self.output_dir, project_name)
        
        try:
            # Create project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Generate boilerplate based on type
            if project_type == "python_script":
                self._generate_python_script(project_path, project_name)
            
            elif project_type == "python_fastapi_app":
                self._generate_python_fastapi_app(project_path, project_name)
            
            elif project_type == "python_flask_app":
                self._generate_python_flask_app(project_path, project_name)
            
            elif project_type == "javascript_react_app":
                # Note: Actual React app creation usually involves tools like create-react-app
                # This is a simplified version for demonstration
                self._generate_javascript_react_app(project_path, project_name)
            
            elif project_type == "javascript_node_express_app":
                self._generate_javascript_node_express_app(project_path, project_name)
            
            elif project_type == "html_basic_page":
                self._generate_html_basic_page(project_path, project_name)
            
            else:
                return {"success": False, "error": f"Unknown project type: {project_type}"}
            
            return {
                "success": True,
                "message": f"Generated boilerplate for {project_type} project: {project_name}",
                "project_path": project_path
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_python_script(self, project_path, project_name):
        """Generate boilerplate for a simple Python script."""
        script_path = os.path.join(project_path, f"{project_name}.py")
        with open(script_path, "w") as f:
            f.write("""#!/usr/bin/env python3

import argparse

def main(args):
    print(f"Hello from {project_name}!")
    print(f"Arguments received: {args}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{project_name} script")
    # Add arguments here
    # parser.add_argument("--input", help="Input file path")
    
    args = parser.parse_args()
    main(args)
""")
        
        # Make script executable
        os.chmod(script_path, 0o755)
    
    def _generate_python_fastapi_app(self, project_path, project_name):
        """Generate boilerplate for a FastAPI application."""
        # Create main app file
        main_py_path = os.path.join(project_path, "main.py")
        with open(main_py_path, "w") as f:
            f.write("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {project_name}!"}

# Add more routes here...
# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}
""")
        
        # Create requirements file
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("fastapi\nuvicorn[standard]\n")
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\nBasic FastAPI application.\n\n## Setup\n```bash\npip install -r requirements.txt\n```\n\n## Run\n```bash\nuvicorn main:app --reload\n```\n")
    
    def _generate_python_flask_app(self, project_path, project_name):
        """Generate boilerplate for a Flask application."""
        # Create main app file
        app_py_path = os.path.join(project_path, "app.py")
        with open(app_py_path, "w") as f:
            f.write("""from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": f"Welcome to {project_name}!"})

# Add more routes here...
# @app.route("/hello/<name>")
# def hello(name):
#     return jsonify({"greeting": f"Hello, {name}!"})

if __name__ == "__main__":
    app.run(debug=True, host=\"0.0.0.0\")
""")
        
        # Create requirements file
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("Flask\n")
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\nBasic Flask application.\n\n## Setup\n```bash\npip install -r requirements.txt\n```\n\n## Run\n```bash\npython app.py\n```\n")
    
    def _generate_javascript_react_app(self, project_path, project_name):
        """Generate boilerplate for a basic React application (simplified)."""
        # Create index.html
        index_html_path = os.path.join(project_path, "index.html")
        with open(index_html_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
</head>
<body>
    <div id="root"></div>
    <!-- Include React and ReactDOM from CDN for simplicity -->
    <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
    <!-- Include Babel for JSX transpilation -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel" src="app.js"></script>
</body>
</html>
""")
        
        # Create app.js
        app_js_path = os.path.join(project_path, "app.js")
        with open(app_js_path, "w") as f:
            f.write("""const App = () => {
    return (
        <div>
            <h1>Welcome to {project_name}!</h1>
            <p>This is a basic React app.</p>
        </div>
    );
};

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<App />);
""")
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\nBasic React application using CDN links.\n\n## Run\nOpen `index.html` in your browser.\n")
    
    def _generate_javascript_node_express_app(self, project_path, project_name):
        """Generate boilerplate for a Node.js Express application."""
        # Create server.js
        server_js_path = os.path.join(project_path, "server.js")
        with open(server_js_path, "w") as f:
            f.write("""const express = require("express");
const app = express();
const port = process.env.PORT || 3000;

app.get("/", (req, res) => {
    res.json({ message: `Welcome to ${project_name}!` });
});

// Add more routes here...
// app.get("/api/data", (req, res) => {
//     res.json({ data: [1, 2, 3] });
// });

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
""")
        
        # Create package.json
        package_json_path = os.path.join(project_path, "package.json")
        with open(package_json_path, "w") as f:
            f.write(json.dumps({
                "name": project_name.lower(),
                "version": "1.0.0",
                "description": "",
                "main": "server.js",
                "scripts": {
                    "start": "node server.js",
                    "dev": "nodemon server.js"  # Optional: requires nodemon
                },
                "dependencies": {
                    "express": "^4.17.1"
                },
                "devDependencies": {
                    "nodemon": "^2.0.15" # Optional
                },
                "author": "",
                "license": "ISC"
            }, indent=2))
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\nBasic Node.js Express application.\n\n## Setup\n```bash\nnpm install\n```\n\n## Run\n```bash\nnpm start\n```\n\n## Run (Development with nodemon - Optional)\n```bash\nnpm run dev\n```\n")
    
    def _generate_html_basic_page(self, project_path, project_name):
        """Generate a basic HTML page."""
        # Create index.html
        index_html_path = os.path.join(project_path, "index.html")
        with open(index_html_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Welcome to {project_name}!</h1>
    <p>This is a basic HTML page.</p>
    
    <script src="script.js"></script>
</body>
</html>
""")
        
        # Create style.css
        style_css_path = os.path.join(project_path, "style.css")
        with open(style_css_path, "w") as f:
            f.write("""body {
    font-family: sans-serif;
    margin: 20px;
}

h1 {
    color: #333;
}
""")
        
        # Create script.js
        script_js_path = os.path.join(project_path, "script.js")
        with open(script_js_path, "w") as f:
            f.write("""console.log("Script loaded for {project_name}!");

// Add your JavaScript code here
""")
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\nBasic HTML, CSS, and JavaScript project.\n\n## Run\nOpen `index.html` in your browser.\n")


class FileStructureGeneratorTool(BaseTool):
    """
    Tool for generating common file and directory structures.
    
    This tool creates standard directory layouts for different types of projects,
    helping to organize code and resources effectively.
    """
    
    def __init__(self, base_dir: str = "/tmp/projects"):
        """
        Initialize the FileStructureGeneratorTool.
        
        Args:
            base_dir: Base directory where project structures will be created
        """
        super().__init__(
            name="file_structure_generator",
            description="Generate common file and directory structures for projects",
            parameters={
                "structure_type": {
                    "type": "string",
                    "description": "Type of project structure to generate",
                    "enum": [
                        "python_package",
                        "web_project_basic",
                        "data_science_project",
                        "docs_project"
                    ]
                },
                "project_name": {
                    "type": "string",
                    "description": "Name of the project (used for root directory)",
                    "required": True
                }
            }
        )
        self.base_dir = base_dir
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the file structure generator tool.
        
        Args:
            structure_type: Type of project structure to generate
            project_name: Name of the project
            
        Returns:
            Dictionary with the result, including the path to the generated structure
        """
        structure_type = kwargs.get("structure_type")
        project_name = kwargs.get("project_name")
        
        if not project_name:
            return {"success": False, "error": "Project name is required"}
        
        project_path = os.path.join(self.base_dir, project_name)
        
        try:
            # Create project root directory
            os.makedirs(project_path, exist_ok=True)
            
            # Generate structure based on type
            if structure_type == "python_package":
                self._generate_python_package_structure(project_path, project_name)
            
            elif structure_type == "web_project_basic":
                self._generate_web_project_basic_structure(project_path)
            
            elif structure_type == "data_science_project":
                self._generate_data_science_project_structure(project_path, project_name)
            
            elif structure_type == "docs_project":
                self._generate_docs_project_structure(project_path)
            
            else:
                return {"success": False, "error": f"Unknown structure type: {structure_type}"}
            
            return {
                "success": True,
                "message": f"Generated {structure_type} structure for project: {project_name}",
                "project_path": project_path
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_dirs_and_files(self, base_path, structure):
        """Helper function to create directories and empty files."""
        for item in structure:
            item_path = os.path.join(base_path, item)
            if item.endswith("/"):
                os.makedirs(item_path, exist_ok=True)
            else:
                # Ensure parent directory exists
                parent_dir = os.path.dirname(item_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                
                # Create empty file
                with open(item_path, "w") as f:
                    pass # Create empty file
    
    def _generate_python_package_structure(self, project_path, project_name):
        """Generate structure for a standard Python package."""
        package_name = project_name.lower().replace("-", "_")
        structure = [
            f"{package_name}/",
            f"{package_name}/__init__.py",
            f"{package_name}/module1.py",
            f"{package_name}/module2.py",
            "tests/",
            "tests/__init__.py",
            "tests/test_module1.py",
            "tests/test_module2.py",
            "setup.py",
            "requirements.txt",
            "README.md",
            ".gitignore"
        ]
        self._create_dirs_and_files(project_path, structure)
        
        # Add basic content to setup.py
        setup_path = os.path.join(project_path, "setup.py")
        with open(setup_path, "w") as f:
            f.write("""from setuptools import setup, find_packages

setup(
    name=\"{project_name}\",
    version=\"0.1.0\",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
    ],
    entry_points={
        # Define command-line scripts here
        # \'console_scripts\': [
        #     \'{project_name}={package_name}.cli:main\',
        # ],
    },
)
""")
        
        # Add basic content to .gitignore
        gitignore_path = os.path.join(project_path, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("""# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
# Usually these files are written by a python script from a template
# before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.* 
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.idea/
.vscode/
""")
    
    def _generate_web_project_basic_structure(self, project_path):
        """Generate structure for a basic web project."""
        structure = [
            "css/",
            "css/style.css",
            "js/",
            "js/script.js",
            "img/",
            "index.html",
            "README.md"
        ]
        self._create_dirs_and_files(project_path, structure)
    
    def _generate_data_science_project_structure(self, project_path, project_name):
        """Generate structure for a data science project."""
        package_name = project_name.lower().replace("-", "_")
        structure = [
            "data/",
            "data/raw/",
            "data/processed/",
            "notebooks/",
            "notebooks/01_data_exploration.ipynb",
            "notebooks/02_feature_engineering.ipynb",
            "notebooks/03_model_training.ipynb",
            f"{package_name}/",
            f"{package_name}/__init__.py",
            f"{package_name}/data_processing.py",
            f"{package_name}/modeling.py",
            f"{package_name}/utils.py",
            "scripts/",
            "scripts/train_model.py",
            "scripts/evaluate_model.py",
            "tests/",
            "tests/__init__.py",
            "tests/test_data_processing.py",
            "tests/test_modeling.py",
            "requirements.txt",
            "README.md",
            ".gitignore"
        ]
        self._create_dirs_and_files(project_path, structure)
        
        # Add basic content to .gitignore (similar to Python package)
        gitignore_path = os.path.join(project_path, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("""# Data files
data/

# Notebook checkpoints
.ipynb_checkpoints/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
dist/
*.egg-info/

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.cache

# Environments
.env
.venv
env/
venv/

# IDEs
.idea/
.vscode/
""")
    
    def _generate_docs_project_structure(self, project_path):
        """Generate structure for a documentation project (e.g., using Sphinx or MkDocs)."""
        structure = [
            "source/",
            "source/conf.py",  # For Sphinx
            "source/index.rst", # For Sphinx
            "source/_static/",
            "source/_templates/",
            "docs/", # For MkDocs
            "docs/index.md", # For MkDocs
            "mkdocs.yml", # For MkDocs
            "Makefile", # For Sphinx
            "requirements.txt",
            "README.md"
        ]
        self._create_dirs_and_files(project_path, structure)


class UnitTestGeneratorTool(BaseTool):
    """
    Tool for generating basic unit tests for Python code.
    
    This tool analyzes a Python file and generates a basic test structure
    with placeholder tests for functions and classes found.
    """
    
    def __init__(self, output_dir: str = "/tmp/tests"):
        """
        Initialize the UnitTestGeneratorTool.
        
        Args:
            output_dir: Directory to save generated test files
        """
        super().__init__(
            name="unit_test_generator",
            description="Generate basic unit test structure for Python code",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to generate tests for",
                    "required": True
                },
                "test_framework": {
                    "type": "string",
                    "description": "Testing framework to use",
                    "enum": ["unittest", "pytest"],
                    "required": False
                }
            }
        )
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the unit test generator tool.
        
        Args:
            file_path: Path to the Python file
            test_framework: Testing framework to use (optional, defaults to unittest)
            
        Returns:
            Dictionary with the result, including the path to the generated test file
        """
        file_path = kwargs.get("file_path")
        test_framework = kwargs.get("test_framework", "unittest")
        
        if not file_path or not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        if not file_path.endswith(".py"):
            return {"success": False, "error": "Input must be a Python file (.py)"}
        
        try:
            # Analyze the Python file
            functions, classes = self._analyze_python_file(file_path)
            
            # Generate test file content
            if test_framework == "pytest":
                test_content = self._generate_pytest_content(file_path, functions, classes)
            else: # Default to unittest
                test_content = self._generate_unittest_content(file_path, functions, classes)
            
            # Determine output file path
            base_name = os.path.basename(file_path)
            test_file_name = f"test_{base_name}"
            output_path = os.path.join(self.output_dir, test_file_name)
            
            # Write test file
            with open(output_path, "w") as f:
                f.write(test_content)
            
            return {
                "success": True,
                "message": f"Generated basic {test_framework} tests for {base_name}",
                "test_file_path": output_path
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_python_file(self, file_path):
        """Analyze a Python file to find functions and classes using AST."""
        import ast
        
        functions = []
        classes = []
        
        with open(file_path, "r") as source:
            tree = ast.parse(source.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Exclude private methods (starting with _)
                if not node.name.startswith("_"):
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                # Exclude private classes (starting with _)
                if not node.name.startswith("_"):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                            class_methods.append(item.name)
                    classes.append({"name": node.name, "methods": class_methods})
        
        return functions, classes
    
    def _generate_unittest_content(self, file_path, functions, classes):
        """Generate test content using the unittest framework."""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        content = """import unittest
# TODO: Import the module or specific functions/classes to test
# from your_module import ...

"""
        
        # Generate tests for standalone functions
        if functions:
            content += f"class Test{module_name.capitalize()}Functions(unittest.TestCase):\n"
            for func in functions:
                content += f"    def test_{func}(self):\n"
                content += f"        # TODO: Implement test for {func}\n"
                content += f"        self.fail(\"Test not implemented\")\n\n"
            content += "\n"
        
        # Generate tests for classes and their methods
        for cls_info in classes:
            cls_name = cls_info["name"]
            content += f"class Test{cls_name}(unittest.TestCase):\n"
            content += f"    def setUp(self):\n"
            content += f"        # TODO: Set up necessary objects for testing {cls_name}\n"
            content += f"        # self.instance = {cls_name}()\n"
            content += f"        pass\n\n"
            
            for method in cls_info["methods"]:
                content += f"    def test_{method}(self):\n"
                content += f"        # TODO: Implement test for {cls_name}.{method}\n"
                content += f"        self.fail(\"Test not implemented\")\n\n"
            content += "\n"
        
        content += "if __name__ == \"__main__\":\n"
        content += "    unittest.main()\n"
        
        return content
    
    def _generate_pytest_content(self, file_path, functions, classes):
        """Generate test content using the pytest framework."""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        content = """import pytest
# TODO: Import the module or specific functions/classes to test
# from your_module import ...

"""
        
        # Generate tests for standalone functions
        for func in functions:
            content += f"def test_{func}():\n"
            content += f"    # TODO: Implement test for {func}\n"
            content += f"    assert False, \"Test not implemented\"\n\n"
        
        # Generate tests for classes and their methods
        for cls_info in classes:
            cls_name = cls_info["name"]
            content += f"class Test{cls_name}:\n"
            content += f"    @pytest.fixture\n"
            content += f"    def instance(self):\n"
            content += f"        # TODO: Set up and return an instance of {cls_name}\n"
            content += f"        # return {cls_name}()\n"
            content += f"        pass\n\n"
            
            for method in cls_info["methods"]:
                content += f"    def test_{method}(self, instance):\n"
                content += f"        # TODO: Implement test for {cls_name}.{method}\n"
                content += f"        assert False, \"Test not implemented\"\n\n"
            content += "\n"
        
        return content
