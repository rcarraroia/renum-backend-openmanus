"""
Project Structure Tool for OpenManus.

This tool provides functionality for generating project structures and
scaffolding for various programming languages and frameworks.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Union

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectStructureTool(BaseTool):
    """
    Tool for generating project structures and scaffolding.
    
    This tool creates directory structures, configuration files, and
    boilerplate code for various programming languages and frameworks.
    """
    
    name = "generate_project_structure"
    description = "Generate project structures and scaffolding for various programming languages and frameworks"
    
    # Project templates for different languages and frameworks
    PROJECT_TEMPLATES = {
        "python": {
            "basic": {
                "directories": [
                    "",
                    "src",
                    "tests",
                    "docs"
                ],
                "files": {
                    "README.md": "# {project_name}\n\n{project_description}\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```python\nfrom src import main\n\nmain.run()\n```\n",
                    "requirements.txt": "# Add your dependencies here\n",
                    "setup.py": """from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
)
""",
                    "src/__init__.py": "",
                    "src/main.py": """def run():
    \"\"\"Main entry point for the application.\"\"\"
    print("Hello, world!")

if __name__ == "__main__":
    run()
""",
                    "tests/__init__.py": "",
                    "tests/test_main.py": """import unittest
from src import main

class TestMain(unittest.TestCase):
    def test_run(self):
        # TODO: Add proper test
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
"""
                }
            },
            "flask": {
                "directories": [
                    "",
                    "app",
                    "app/static",
                    "app/static/css",
                    "app/static/js",
                    "app/templates",
                    "tests"
                ],
                "files": {
                    "README.md": "# {project_name}\n\n{project_description}\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\nflask run\n```\n",
                    "requirements.txt": "flask==2.0.1\npython-dotenv==0.19.0\n",
                    ".env": "FLASK_APP=app\nFLASK_ENV=development\n",
                    ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n",
                    "app/__init__.py": """from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from app import routes
    
    return app
""",
                    "app/routes.py": """from flask import render_template
from app import create_app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html', title='Home')
""",
                    "app/templates/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - {project_name}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <h1>{project_name}</h1>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        <p>&copy; {current_year} {project_name}</p>
    </footer>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
""",
                    "app/templates/index.html": """{% extends "base.html" %}

{% block content %}
    <h2>Welcome to {project_name}</h2>
    <p>{project_description}</p>
{% endblock %}
""",
                    "app/static/css/style.css": """/* Main styles */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    color: #333;
}

header, footer {
    background-color: #f4f4f4;
    text-align: center;
    padding: 1rem;
}

main {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
}
""",
                    "app/static/js/script.js": """// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('{project_name} loaded');
});
""",
                    "tests/__init__.py": "",
                    "tests/test_app.py": """import unittest
from app import create_app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
"""
                }
            }
        },
        "javascript": {
            "node": {
                "directories": [
                    "",
                    "src",
                    "tests"
                ],
                "files": {
                    "README.md": "# {project_name}\n\n{project_description}\n\n## Installation\n\n```bash\nnpm install\n```\n\n## Usage\n\n```bash\nnode src/index.js\n```\n",
                    "package.json": """{
  "name": "{package_name}",
  "version": "1.0.0",
  "description": "{project_description}",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {},
  "devDependencies": {
    "jest": "^27.0.6"
  }
}
""",
                    ".gitignore": "node_modules/\nnpm-debug.log\n.env\n",
                    "src/index.js": """/**
 * Main entry point for the application.
 */
function main() {
    console.log('Hello, world!');
}

main();

module.exports = { main };
""",
                    "tests/index.test.js": """const { main } = require('../src/index');

test('main function exists', () => {
    expect(typeof main).toBe('function');
});
"""
                }
            },
            "react": {
                "directories": [
                    "",
                    "public",
                    "src",
                    "src/components",
                    "src/styles"
                ],
                "files": {
                    "README.md": "# {project_name}\n\n{project_description}\n\n## Installation\n\n```bash\nnpm install\n```\n\n## Usage\n\n```bash\nnpm start\n```\n",
                    "package.json": """{
  "name": "{package_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-scripts": "4.0.3"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
""",
                    ".gitignore": "# dependencies\n/node_modules\n/.pnp\n.pnp.js\n\n# testing\n/coverage\n\n# production\n/build\n\n# misc\n.DS_Store\n.env.local\n.env.development.local\n.env.test.local\n.env.production.local\n\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*\n",
                    "public/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="{project_description}"
    />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
""",
                    "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';
import App from './components/App';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
""",
                    "src/components/App.js": """import React from 'react';
import '../styles/App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>{project_description}</p>
      </header>
    </div>
  );
}

export default App;
""",
                    "src/styles/index.css": """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
""",
                    "src/styles/App.css": """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}
"""
                }
            }
        },
        "java": {
            "maven": {
                "directories": [
                    "",
                    "src/main/java/{package_path}",
                    "src/test/java/{package_path}"
                ],
                "files": {
                    "README.md": "# {project_name}\n\n{project_description}\n\n## Building\n\n```bash\nmvn clean package\n```\n\n## Running\n\n```bash\njava -jar target/{package_name}-1.0-SNAPSHOT.jar\n```\n",
                    "pom.xml": """<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>{group_id}</groupId>
    <artifactId>{package_name}</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.2.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <addClasspath>true</addClasspath>
                            <mainClass>{package_name}.App</mainClass>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
""",
                    ".gitignore": "target/\n*.class\n*.jar\n*.war\n*.ear\n*.logs\n.idea/\n.eclipse\n",
                    "src/main/java/{package_path}/App.java": """package {package_name};

/**
 * Main application class.
 */
public class App {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }
}
""",
                    "src/test/java/{package_path}/AppTest.java": """package {package_name};

import static org.junit.Assert.assertTrue;
import org.junit.Test;

/**
 * Unit tests for App.
 */
public class AppTest {
    @Test
    public void testApp() {
        assertTrue(true);
    }
}
"""
                }
            }
        }
    }
    
    def __init__(self):
        """Initialize the ProjectStructureTool."""
        super().__init__()
        logger.info("ProjectStructureTool initialized")
    
    async def _arun(
        self,
        language: str,
        framework: str,
        project_name: str,
        project_description: Optional[str] = None,
        output_dir: Optional[str] = None,
        package_name: Optional[str] = None,
        group_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate project structure based on the provided parameters.
        
        Args:
            language: Programming language (python, javascript, java)
            framework: Framework or project type (basic, flask, node, react, maven)
            project_name: Name of the project
            project_description: Description of the project
            output_dir: Directory where the project will be generated
            package_name: Name of the package (for Java/Node.js projects)
            group_id: Group ID (for Java Maven projects)
            
        Returns:
            Dictionary containing the result of the operation
        """
        logger.info(f"Generating {language} {framework} project: {project_name}")
        
        # Validate inputs
        if not language:
            return {"error": "Language is required"}
        
        if not framework:
            return {"error": "Framework is required"}
        
        if not project_name:
            return {"error": "Project name is required"}
        
        # Normalize inputs
        language = language.lower()
        framework = framework.lower()
        
        # Set default values
        if not project_description:
            project_description = f"A {language} {framework} project"
        
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), project_name)
        
        if not package_name:
            # Convert project name to package name format
            package_name = project_name.lower().replace(" ", "_").replace("-", "_")
        
        if not group_id and language == "java":
            group_id = f"com.example.{package_name}"
        
        # Check if language and framework are supported
        if language not in self.PROJECT_TEMPLATES:
            return {"error": f"Unsupported language: {language}. Supported languages: {', '.join(self.PROJECT_TEMPLATES.keys())}"}
        
        if framework not in self.PROJECT_TEMPLATES[language]:
            return {"error": f"Unsupported framework for {language}: {framework}. Supported frameworks: {', '.join(self.PROJECT_TEMPLATES[language].keys())}"}
        
        # Get template
        template = self.PROJECT_TEMPLATES[language][framework]
        
        # Create project structure
        try:
            # Create directories
            created_dirs = []
            for dir_path in template["directories"]:
                # Replace placeholders in directory path
                if language == "java" and "{package_path}" in dir_path:
                    package_path = group_id.replace(".", "/")
                    dir_path = dir_path.replace("{package_path}", package_path)
                
                full_dir_path = os.path.join(output_dir, dir_path)
                os.makedirs(full_dir_path, exist_ok=True)
                created_dirs.append(full_dir_path)
            
            # Create files
            created_files = []
            for file_path, content in template["files"].items():
                # Replace placeholders in file path
                if language == "java" and "{package_path}" in file_path:
                    package_path = group_id.replace(".", "/")
                    file_path = file_path.replace("{package_path}", package_path)
                
                # Format content with project details
                import datetime
                formatted_content = content.format(
                    project_name=project_name,
                    project_description=project_description,
                    package_name=package_name,
                    group_id=group_id,
                    current_year=datetime.datetime.now().year
                )
                
                # Write file
                full_file_path = os.path.join(output_dir, file_path)
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                with open(full_file_path, "w") as f:
                    f.write(formatted_content)
                created_files.append(full_file_path)
            
            return {
                "success": True,
                "message": f"Project structure generated successfully at {output_dir}",
                "project_dir": output_dir,
                "created_dirs": created_dirs,
                "created_files": created_files,
                "language": language,
                "framework": framework,
                "project_name": project_name
            }
            
        except Exception as e:
            logger.error(f"Error generating project structure: {e}")
            return {"error": f"Failed to generate project structure: {str(e)}"}
    
    async def generate_python_project(
        self,
        project_name: str,
        project_type: str = "basic",
        project_description: Optional[str] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a Python project.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of generating Python projects.
        
        Args:
            project_name: Name of the project
            project_type: Type of Python project (basic, flask)
            project_description: Description of the project
            output_dir: Directory where the project will be generated
            
        Returns:
            Dictionary containing the result of the operation
        """
        return await self._arun(
            language="python",
            framework=project_type,
            project_name=project_name,
            project_description=project_description,
            output_dir=output_dir,
            **kwargs
        )
    
    async def generate_javascript_project(
        self,
        project_name: str,
        project_type: str = "node",
        project_description: Optional[str] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a JavaScript project.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of generating JavaScript projects.
        
        Args:
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react)
            project_description: Description of the project
            output_dir: Directory where the project will be generated
            
        Returns:
            Dictionary containing the result of the operation
        """
        return await self._arun(
            language="javascript",
            framework=project_type,
            project_name=project_name,
            project_description=project_description,
            output_dir=output_dir,
            **kwargs
        )
    
    async def generate_java_project(
        self,
        project_name: str,
        project_type: str = "maven",
        project_description: Optional[str] = None,
        output_dir: Optional[str] = None,
        group_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a Java project.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of generating Java projects.
        
        Args:
            project_name: Name of the project
            project_type: Type of Java project (maven)
            project_description: Description of the project
            output_dir: Directory where the project will be generated
            group_id: Group ID for Maven projects
            
        Returns:
            Dictionary containing the result of the operation
        """
        return await self._arun(
            language="java",
            framework=project_type,
            project_name=project_name,
            project_description=project_description,
            output_dir=output_dir,
            group_id=group_id,
            **kwargs
        )
