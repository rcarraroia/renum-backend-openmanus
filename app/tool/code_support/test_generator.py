"""
Test Generator Tool for OpenManus.

This tool provides functionality for generating unit tests and test suites
for various programming languages and testing frameworks.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestGeneratorTool(BaseTool):
    """
    Tool for generating unit tests and test suites.
    
    This tool creates test cases for functions and classes in various
    programming languages and testing frameworks.
    """
    
    name = "generate_tests"
    description = "Generate unit tests and test suites for various programming languages and frameworks"
    
    # Language and framework-specific templates
    TEST_TEMPLATES = {
        "python": {
            "unittest": {
                "function_test": """import unittest
from {module_name} import {function_name}

class Test{function_name_camel}(unittest.TestCase):
    \"\"\"Test cases for {function_name} function.\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures, if any.\"\"\"
        pass

    def tearDown(self):
        \"\"\"Tear down test fixtures, if any.\"\"\"
        pass

    def test_{function_name}_basic(self):
        \"\"\"Test {function_name} with basic inputs.\"\"\"
{test_cases}

    def test_{function_name}_edge_cases(self):
        \"\"\"Test {function_name} with edge cases.\"\"\"
{edge_cases}

    def test_{function_name}_error_cases(self):
        \"\"\"Test {function_name} with inputs that should raise errors.\"\"\"
{error_cases}

if __name__ == '__main__':
    unittest.main()
""",
                "class_test": """import unittest
from {module_name} import {class_name}

class Test{class_name}(unittest.TestCase):
    \"\"\"Test cases for {class_name} class.\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures, if any.\"\"\"
{setup_code}

    def tearDown(self):
        \"\"\"Tear down test fixtures, if any.\"\"\"
        pass
{method_tests}

if __name__ == '__main__':
    unittest.main()
"""
            },
            "pytest": {
                "function_test": """import pytest
from {module_name} import {function_name}

def setup_function(function):
    \"\"\"Set up test fixtures, if any.\"\"\"
    pass

def teardown_function(function):
    \"\"\"Tear down test fixtures, if any.\"\"\"
    pass

def test_{function_name}_basic():
    \"\"\"Test {function_name} with basic inputs.\"\"\"
{test_cases}

def test_{function_name}_edge_cases():
    \"\"\"Test {function_name} with edge cases.\"\"\"
{edge_cases}

def test_{function_name}_error_cases():
    \"\"\"Test {function_name} with inputs that should raise errors.\"\"\"
{error_cases}

if __name__ == '__main__':
    pytest.main()
""",
                "class_test": """import pytest
from {module_name} import {class_name}

class Test{class_name}:
    \"\"\"Test cases for {class_name} class.\"\"\"

    @pytest.fixture
    def setup(self):
        \"\"\"Set up test fixtures.\"\"\"
{setup_code}
{method_tests}

if __name__ == '__main__':
    pytest.main()
"""
            }
        },
        "javascript": {
            "jest": {
                "function_test": """const {function_name} = require('{module_name}');

describe('{function_name} function', () => {
    beforeEach(() => {
        // Set up test fixtures, if any
    });

    afterEach(() => {
        // Tear down test fixtures, if any
    });

    test('should work with basic inputs', () => {
{test_cases}
    });

    test('should handle edge cases', () => {
{edge_cases}
    });

    test('should handle error cases', () => {
{error_cases}
    });
});
""",
                "class_test": """const {class_name} = require('{module_name}');

describe('{class_name} class', () => {
    let instance;

    beforeEach(() => {
        // Set up test fixtures
{setup_code}
    });

    afterEach(() => {
        // Tear down test fixtures
        instance = null;
    });
{method_tests}
});
"""
            },
            "mocha": {
                "function_test": """const assert = require('assert');
const {function_name} = require('{module_name}');

describe('{function_name} function', function() {
    beforeEach(function() {
        // Set up test fixtures, if any
    });

    afterEach(function() {
        // Tear down test fixtures, if any
    });

    it('should work with basic inputs', function() {
{test_cases}
    });

    it('should handle edge cases', function() {
{edge_cases}
    });

    it('should handle error cases', function() {
{error_cases}
    });
});
""",
                "class_test": """const assert = require('assert');
const {class_name} = require('{module_name}');

describe('{class_name} class', function() {
    let instance;

    beforeEach(function() {
        // Set up test fixtures
{setup_code}
    });

    afterEach(function() {
        // Tear down test fixtures
        instance = null;
    });
{method_tests}
});
"""
            }
        },
        "java": {
            "junit": {
                "function_test": """import static org.junit.Assert.*;
import org.junit.Before;
import org.junit.After;
import org.junit.Test;
import {package_name}.{class_name};

public class {class_name}Test {
    
    @Before
    public void setUp() {
        // Set up test fixtures, if any
    }
    
    @After
    public void tearDown() {
        // Tear down test fixtures, if any
    }
    
    @Test
    public void test{function_name_camel}Basic() {
        // Test {function_name} with basic inputs
{test_cases}
    }
    
    @Test
    public void test{function_name_camel}EdgeCases() {
        // Test {function_name} with edge cases
{edge_cases}
    }
    
    @Test
    public void test{function_name_camel}ErrorCases() {
        // Test {function_name} with inputs that should raise errors
{error_cases}
    }
}
""",
                "class_test": """import static org.junit.Assert.*;
import org.junit.Before;
import org.junit.After;
import org.junit.Test;
import {package_name}.{class_name};

public class {class_name}Test {
    
    private {class_name} instance;
    
    @Before
    public void setUp() {
        // Set up test fixtures
{setup_code}
    }
    
    @After
    public void tearDown() {
        // Tear down test fixtures
        instance = null;
    }
{method_tests}
}
"""
            }
        }
    }
    
    def __init__(self):
        """Initialize the TestGeneratorTool."""
        super().__init__()
        logger.info("TestGeneratorTool initialized")
    
    async def _arun(
        self,
        language: str,
        framework: str,
        test_type: str,
        module_name: str,
        function_name: Optional[str] = None,
        class_name: Optional[str] = None,
        methods: Optional[List[Dict[str, Any]]] = None,
        params: Optional[List[Dict[str, Any]]] = None,
        return_type: Optional[str] = None,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        package_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate test code based on the provided parameters.
        
        Args:
            language: Programming language (python, javascript, java)
            framework: Testing framework (unittest, pytest, jest, mocha, junit)
            test_type: Type of test (function, class)
            module_name: Name of the module containing the code to test
            function_name: Name of the function to test (for function tests)
            class_name: Name of the class to test (for class tests)
            methods: List of method dictionaries (for class tests)
            params: List of parameter dictionaries
            return_type: Return type of the function
            test_cases: List of test case dictionaries
            package_name: Java package name (for Java tests)
            
        Returns:
            Dictionary containing the generated test code and metadata
        """
        logger.info(f"Generating {test_type} tests for {language} using {framework}")
        
        # Validate inputs
        if not language:
            return {"error": "Language is required"}
        
        if not framework:
            return {"error": "Framework is required"}
        
        if not test_type:
            return {"error": "Test type is required"}
        
        if not module_name:
            return {"error": "Module name is required"}
        
        # Normalize inputs
        language = language.lower()
        framework = framework.lower()
        test_type = test_type.lower()
        
        # Check if language is supported
        if language not in self.TEST_TEMPLATES:
            return {"error": f"Unsupported language: {language}. Supported languages: {', '.join(self.TEST_TEMPLATES.keys())}"}
        
        # Check if framework is supported for the language
        if framework not in self.TEST_TEMPLATES[language]:
            return {"error": f"Unsupported framework for {language}: {framework}. Supported frameworks: {', '.join(self.TEST_TEMPLATES[language].keys())}"}
        
        # Generate tests based on test type
        if test_type == "function":
            if not function_name:
                return {"error": "Function name is required for function tests"}
            
            result = self._generate_function_tests(
                language=language,
                framework=framework,
                module_name=module_name,
                function_name=function_name,
                params=params or [],
                return_type=return_type,
                test_cases=test_cases or [],
                package_name=package_name
            )
        elif test_type == "class":
            if not class_name:
                return {"error": "Class name is required for class tests"}
            
            result = self._generate_class_tests(
                language=language,
                framework=framework,
                module_name=module_name,
                class_name=class_name,
                methods=methods or [],
                params=params or [],
                test_cases=test_cases or [],
                package_name=package_name
            )
        else:
            return {"error": f"Unsupported test type: {test_type}. Supported types: function, class"}
        
        return result
    
    def _generate_function_tests(
        self,
        language: str,
        framework: str,
        module_name: str,
        function_name: str,
        params: List[Dict[str, Any]],
        return_type: Optional[str],
        test_cases: List[Dict[str, Any]],
        package_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate function test code.
        
        Args:
            language: Programming language
            framework: Testing framework
            module_name: Name of the module containing the function
            function_name: Name of the function to test
            params: List of parameter dictionaries
            return_type: Return type of the function
            test_cases: List of test case dictionaries
            package_name: Java package name (for Java tests)
            
        Returns:
            Dictionary containing the generated test code and metadata
        """
        # Get template
        templates = self.TEST_TEMPLATES[language][framework]
        template = templates["function_test"]
        
        # Format function name for camel case (used in some templates)
        function_name_camel = self._to_camel_case(function_name)
        
        # Generate test cases
        formatted_test_cases = self._format_test_cases(language, framework, function_name, params, return_type, test_cases)
        
        # Generate edge cases
        edge_cases = self._format_edge_cases(language, framework, function_name, params, return_type)
        
        # Generate error cases
        error_cases = self._format_error_cases(language, framework, function_name, params)
        
        # Format code
        code = template.format(
            module_name=module_name,
            function_name=function_name,
            function_name_camel=function_name_camel,
            test_cases=formatted_test_cases,
            edge_cases=edge_cases,
            error_cases=error_cases,
            package_name=package_name or "com.example",
            class_name=self._get_class_name_from_module(module_name)
        )
        
        return {
            "success": True,
            "code": code,
            "language": language,
            "framework": framework,
            "test_type": "function",
            "function_name": function_name
        }
    
    def _generate_class_tests(
        self,
        language: str,
        framework: str,
        module_name: str,
        class_name: str,
        methods: List[Dict[str, Any]],
        params: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]],
        package_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate class test code.
        
        Args:
            language: Programming language
            framework: Testing framework
            module_name: Name of the module containing the class
            class_name: Name of the class to test
            methods: List of method dictionaries
            params: List of constructor parameter dictionaries
            test_cases: List of test case dictionaries
            package_name: Java package name (for Java tests)
            
        Returns:
            Dictionary containing the generated test code and metadata
        """
        # Get template
        templates = self.TEST_TEMPLATES[language][framework]
        template = templates["class_test"]
        
        # Generate setup code
        setup_code = self._format_setup_code(language, framework, class_name, params)
        
        # Generate method tests
        method_tests = self._format_method_tests(language, framework, class_name, methods, test_cases)
        
        # Format code
        code = template.format(
            module_name=module_name,
            class_name=class_name,
            setup_code=setup_code,
            method_tests=method_tests,
            package_name=package_name or "com.example"
        )
        
        return {
            "success": True,
            "code": code,
            "language": language,
            "framework": framework,
            "test_type": "class",
            "class_name": class_name,
            "method_count": len(methods)
        }
    
    def _format_test_cases(
        self,
        language: str,
        framework: str,
        function_name: str,
        params: List[Dict[str, Any]],
        return_type: Optional[str],
        test_cases: List[Dict[str, Any]]
    ) -> str:
        """
        Format test cases based on language and framework.
        
        Args:
            language: Programming language
            framework: Testing framework
            function_name: Name of the function to test
            params: List of parameter dictionaries
            return_type: Return type of the function
            test_cases: List of test case dictionaries
            
        Returns:
            Formatted test cases
        """
        # If test cases are provided, use them
        if test_cases:
            return self._format_provided_test_cases(language, framework, function_name, test_cases)
        
        # Otherwise, generate default test cases based on parameters
        return self._generate_default_test_cases(language, framework, function_name, params, return_type)
    
    def _format_provided_test_cases(
        self,
        language: str,
        framework: str,
        function_name: str,
        test_cases: List[Dict[str, Any]]
    ) -> str:
        """
        Format provided test cases based on language and framework.
        
        Args:
            language: Programming language
            framework: Testing framework
            function_name: Name of the function to test
            test_cases: List of test case dictionaries
            
        Returns:
            Formatted test cases
        """
        formatted_cases = []
        
        for case in test_cases:
            inputs = case.get("inputs", [])
            expected = case.get("expected", "")
            description = case.get("description", "")
            
            # Format inputs as string
            inputs_str = ", ".join([str(inp) for inp in inputs])
            
            if language == "python":
                if framework == "unittest":
                    if description:
                        formatted_cases.append(f"        # {description}")
                    formatted_cases.append(f"        result = {function_name}({inputs_str})")
                    formatted_cases.append(f"        self.assertEqual(result, {expected})")
                    formatted_cases.append("")
                elif framework == "pytest":
                    if description:
                        formatted_cases.append(f"    # {description}")
                    formatted_cases.append(f"    result = {function_name}({inputs_str})")
                    formatted_cases.append(f"    assert result == {expected}")
                    formatted_cases.append("")
            elif language == "javascript":
                if framework in ["jest", "mocha"]:
                    if description:
                        formatted_cases.append(f"        // {description}")
                    formatted_cases.append(f"        const result = {function_name}({inputs_str});")
                    if framework == "jest":
                        formatted_cases.append(f"        expect(result).toBe({expected});")
                    else:  # mocha
                        formatted_cases.append(f"        assert.strictEqual(result, {expected});")
                    formatted_cases.append("")
            elif language == "java":
                if framework == "junit":
                    if description:
                        formatted_cases.append(f"        // {description}")
                    formatted_cases.append(f"        Object result = {function_name}({inputs_str});")
                    formatted_cases.append(f"        assertEquals({expected}, result);")
                    formatted_cases.append("")
        
        return "\n".join(formatted_cases)
    
    def _generate_default_test_cases(
        self,
        language: str,
        framework: str,
        function_name: str,
        params: List[Dict[str, Any]],
        return_type: Optional[str]
    ) -> str:
        """
        Generate default test cases based on parameters.
        
        Args:
            language: Programming language
            framework: Testing framework
            function_name: Name of the function to test
            params: List of parameter dictionaries
            return_type: Return type of the function
            
        Returns:
            Generated default test cases
        """
        # Generate default parameter values
        param_values = []
        for param in params:
            param_type = param.get("type", "")
            
            # Generate default value based on type
            if param_type in ["int", "Integer", "number"]:
                param_values.append("42")
            elif param_type in ["float", "double", "Double"]:
                param_values.append("3.14")
            elif param_type in ["str", "String", "string"]:
                param_values.append('"test"')
            elif param_type in ["bool", "boolean", "Boolean"]:
                param_values.append("true")
            elif param_type in ["list", "List", "array", "Array"]:
                param_values.append("[1, 2, 3]")
            elif param_type in ["dict", "Dict", "object", "Object"]:
                param_values.append('{"key": "value"}')
            else:
                param_values.append("null")
        
        # Format inputs as string
        inputs_str = ", ".join(param_values)
        
        # Generate expected value based on return type
        if return_type in ["int", "Integer", "number"]:
            expected = "42"
        elif return_type in ["float", "double", "Double"]:
            expected = "3.14"
        elif return_type in ["str", "String", "string"]:
            expected = '"expected"'
        elif return_type in ["bool", "boolean", "Boolean"]:
            expected = "true"
        elif return_type in ["list", "List", "array", "Array"]:
            expected = "[1, 2, 3]"
        elif return_type in ["dict", "Dict", "object", "Object"]:
            expected = '{"key": "value"}'
        else:
            expected = "null"
        
        # Format test case based on language and framework
        if language == "python":
            if framework == "unittest":
                return f"        # Test with basic inputs\n        result = {function_name}({inputs_str})\n        self.assertEqual(result, {expected})\n"
            elif framework == "pytest":
                return f"    # Test with basic inputs\n    result = {function_name}({inputs_str})\n    assert result == {expected}\n"
        elif language == "javascript":
            if framework in ["jest", "mocha"]:
                if framework == "jest":
                    return f"        // Test with basic inputs\n        const result = {function_name}({inputs_str});\n        expect(result).toBe({expected});\n"
                else:  # mocha
                    return f"        // Test with basic inputs\n        const result = {function_name}({inputs_str});\n        assert.strictEqual(result, {expected});\n"
        elif language == "java":
            if framework == "junit":
                return f"        // Test with basic inputs\n        Object result = {function_name}({inputs_str});\n        assertEquals({expected}, result);\n"
        
        return "        // TODO: Add test cases\n"
    
    def _format_edge_cases(
        self,
        language: str,
        framework: str,
        function_name: str,
        params: List[Dict[str, Any]],
        return_type: Optional[str]
    ) -> str:
        """
        Format edge cases based on language and framework.
        
        Args:
            language: Programming language
            framework: Testing framework
            function_name: Name of the function to test
            params: List of parameter dictionaries
            return_type: Return type of the function
            
        Returns:
            Formatted edge cases
        """
        # Generate edge cases based on parameter types
        edge_cases = []
        
        for i, param in enumerate(params):
            param_name = param.get("name", f"param{i}")
            param_type = param.get("type", "")
            
            # Generate edge case values based on type
            edge_values = []
            if param_type in ["int", "Integer", "number"]:
                edge_values = ["0", "-1", "Integer.MAX_VALUE" if language == "java" else "2147483647"]
            elif param_type in ["float", "double", "Double"]:
                edge_values = ["0.0", "-0.0", "1e-10"]
            elif param_type in ["str", "String", "string"]:
                edge_values = ['""', '"   "', '"very_long_string" * 100' if language == "python" else '"very_long_string".repeat(100)']
            elif param_type in ["bool", "boolean", "Boolean"]:
                edge_values = ["false"]
            elif param_type in ["list", "List", "array", "Array"]:
                edge_values = ["[]", "[0]"]
            elif param_type in ["dict", "Dict", "object", "Object"]:
                edge_values = ["{}", '{"": ""}']
            
            # Format edge cases for each value
            for value in edge_values:
                # Create parameter list with the edge value
                param_values = []
                for j, p in enumerate(params):
                    if j == i:
                        param_values.append(value)
                    else:
                        # Use default value for other parameters
                        p_type = p.get("type", "")
                        if p_type in ["int", "Integer", "number"]:
                            param_values.append("1")
                        elif p_type in ["float", "double", "Double"]:
                            param_values.append("1.0")
                        elif p_type in ["str", "String", "string"]:
                            param_values.append('"default"')
                        elif p_type in ["bool", "boolean", "Boolean"]:
                            param_values.append("true")
                        elif p_type in ["list", "List", "array", "Array"]:
                            param_values.append("[1]")
                        elif p_type in ["dict", "Dict", "object", "Object"]:
                            param_values.append('{"key": "value"}')
                        else:
                            param_values.append("null")
                
                # Format inputs as string
                inputs_str = ", ".join(param_values)
                
                # Add edge case based on language and framework
                if language == "python":
                    if framework == "unittest":
                        edge_cases.append(f"        # Test with edge value for {param_name}: {value}")
                        edge_cases.append(f"        result = {function_name}({inputs_str})")
                        edge_cases.append(f"        # TODO: Add appropriate assertion")
                        edge_cases.append("")
                    elif framework == "pytest":
                        edge_cases.append(f"    # Test with edge value for {param_name}: {value}")
                        edge_cases.append(f"    result = {function_name}({inputs_str})")
                        edge_cases.append(f"    # TODO: Add appropriate assertion")
                        edge_cases.append("")
                elif language == "javascript":
                    if framework in ["jest", "mocha"]:
                        edge_cases.append(f"        // Test with edge value for {param_name}: {value}")
                        edge_cases.append(f"        const result = {function_name}({inputs_str});")
                        edge_cases.append(f"        // TODO: Add appropriate assertion")
                        edge_cases.append("")
                elif language == "java":
                    if framework == "junit":
                        edge_cases.append(f"        // Test with edge value for {param_name}: {value}")
                        edge_cases.append(f"        Object result = {function_name}({inputs_str});")
                        edge_cases.append(f"        // TODO: Add appropriate assertion")
                        edge_cases.append("")
        
        if not edge_cases:
            if language == "python":
                if framework == "unittest":
                    return "        # TODO: Add edge case tests\n        pass\n"
                elif framework == "pytest":
                    return "    # TODO: Add edge case tests\n    pass\n"
            elif language == "javascript":
                return "        // TODO: Add edge case tests\n"
            elif language == "java":
                return "        // TODO: Add edge case tests\n"
        
        return "\n".join(edge_cases)
    
    def _format_error_cases(
        self,
        language: str,
        framework: str,
        function_name: str,
        params: List[Dict[str, Any]]
    ) -> str:
        """
        Format error cases based on language and framework.
        
        Args:
            language: Programming language
            framework: Testing framework
            function_name: Name of the function to test
            params: List of parameter dictionaries
            
        Returns:
            Formatted error cases
        """
        # Generate error cases based on parameter types
        error_cases = []
        
        for i, param in enumerate(params):
            param_name = param.get("name", f"param{i}")
            param_type = param.get("type", "")
            
            # Generate invalid values based on type
            invalid_values = []
            if param_type in ["int", "Integer", "number"]:
                if language == "python":
                    invalid_values = ['"not_a_number"']
                elif language == "javascript":
                    invalid_values = ['"not_a_number"']
                elif language == "java":
                    invalid_values = ['"not_a_number"']
            elif param_type in ["float", "double", "Double"]:
                if language == "python":
                    invalid_values = ['"not_a_float"']
                elif language == "javascript":
                    invalid_values = ['"not_a_float"']
                elif language == "java":
                    invalid_values = ['"not_a_float"']
            
            # Format error cases for each invalid value
            for value in invalid_values:
                # Create parameter list with the invalid value
                param_values = []
                for j, p in enumerate(params):
                    if j == i:
                        param_values.append(value)
                    else:
                        # Use default value for other parameters
                        p_type = p.get("type", "")
                        if p_type in ["int", "Integer", "number"]:
                            param_values.append("1")
                        elif p_type in ["float", "double", "Double"]:
                            param_values.append("1.0")
                        elif p_type in ["str", "String", "string"]:
                            param_values.append('"default"')
                        elif p_type in ["bool", "boolean", "Boolean"]:
                            param_values.append("true")
                        elif p_type in ["list", "List", "array", "Array"]:
                            param_values.append("[1]")
                        elif p_type in ["dict", "Dict", "object", "Object"]:
                            param_values.append('{"key": "value"}')
                        else:
                            param_values.append("null")
                
                # Format inputs as string
                inputs_str = ", ".join(param_values)
                
                # Add error case based on language and framework
                if language == "python":
                    if framework == "unittest":
                        error_cases.append(f"        # Test with invalid value for {param_name}: {value}")
                        error_cases.append(f"        with self.assertRaises(Exception):")
                        error_cases.append(f"            {function_name}({inputs_str})")
                        error_cases.append("")
                    elif framework == "pytest":
                        error_cases.append(f"    # Test with invalid value for {param_name}: {value}")
                        error_cases.append(f"    with pytest.raises(Exception):")
                        error_cases.append(f"        {function_name}({inputs_str})")
                        error_cases.append("")
                elif language == "javascript":
                    if framework == "jest":
                        error_cases.append(f"        // Test with invalid value for {param_name}: {value}")
                        error_cases.append(f"        expect(() => {{")
                        error_cases.append(f"            {function_name}({inputs_str});")
                        error_cases.append(f"        }}).toThrow();")
                        error_cases.append("")
                    elif framework == "mocha":
                        error_cases.append(f"        // Test with invalid value for {param_name}: {value}")
                        error_cases.append(f"        assert.throws(() => {{")
                        error_cases.append(f"            {function_name}({inputs_str});")
                        error_cases.append(f"        }});")
                        error_cases.append("")
                elif language == "java":
                    if framework == "junit":
                        error_cases.append(f"        // Test with invalid value for {param_name}: {value}")
                        error_cases.append(f"        assertThrows(Exception.class, () -> {{")
                        error_cases.append(f"            {function_name}({inputs_str});")
                        error_cases.append(f"        }});")
                        error_cases.append("")
        
        if not error_cases:
            if language == "python":
                if framework == "unittest":
                    return "        # TODO: Add error case tests\n        pass\n"
                elif framework == "pytest":
                    return "    # TODO: Add error case tests\n    pass\n"
            elif language == "javascript":
                return "        // TODO: Add error case tests\n"
            elif language == "java":
                return "        // TODO: Add error case tests\n"
        
        return "\n".join(error_cases)
    
    def _format_setup_code(
        self,
        language: str,
        framework: str,
        class_name: str,
        params: List[Dict[str, Any]]
    ) -> str:
        """
        Format setup code for class tests.
        
        Args:
            language: Programming language
            framework: Testing framework
            class_name: Name of the class to test
            params: List of constructor parameter dictionaries
            
        Returns:
            Formatted setup code
        """
        # Generate parameter values for constructor
        param_values = []
        for param in params:
            param_type = param.get("type", "")
            
            # Generate default value based on type
            if param_type in ["int", "Integer", "number"]:
                param_values.append("42")
            elif param_type in ["float", "double", "Double"]:
                param_values.append("3.14")
            elif param_type in ["str", "String", "string"]:
                param_values.append('"test"')
            elif param_type in ["bool", "boolean", "Boolean"]:
                param_values.append("true")
            elif param_type in ["list", "List", "array", "Array"]:
                param_values.append("[1, 2, 3]")
            elif param_type in ["dict", "Dict", "object", "Object"]:
                param_values.append('{"key": "value"}')
            else:
                param_values.append("null")
        
        # Format inputs as string
        inputs_str = ", ".join(param_values)
        
        # Format setup code based on language and framework
        if language == "python":
            if framework == "unittest":
                return f"        self.instance = {class_name}({inputs_str})"
            elif framework == "pytest":
                return f"        instance = {class_name}({inputs_str})\n        return instance"
        elif language == "javascript":
            if framework in ["jest", "mocha"]:
                return f"        instance = new {class_name}({inputs_str});"
        elif language == "java":
            if framework == "junit":
                return f"        instance = new {class_name}({inputs_str});"
        
        return "        // TODO: Initialize test instance"
    
    def _format_method_tests(
        self,
        language: str,
        framework: str,
        class_name: str,
        methods: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]]
    ) -> str:
        """
        Format method tests for class tests.
        
        Args:
            language: Programming language
            framework: Testing framework
            class_name: Name of the class to test
            methods: List of method dictionaries
            test_cases: List of test case dictionaries
            
        Returns:
            Formatted method tests
        """
        method_tests = []
        
        for method in methods:
            method_name = method.get("name", "")
            method_params = method.get("params", [])
            method_return_type = method.get("return_type", "")
            
            if not method_name:
                continue
            
            # Find test cases for this method
            method_test_cases = [tc for tc in test_cases if tc.get("method_name") == method_name]
            
            # Generate test method
            if language == "python":
                if framework == "unittest":
                    method_tests.append(f"\n    def test_{method_name}(self):")
                    method_tests.append(f"        \"\"\"Test {method_name} method.\"\"\"")
                    
                    # Add test case implementation
                    if method_test_cases:
                        for tc in method_test_cases:
                            inputs = tc.get("inputs", [])
                            expected = tc.get("expected", "")
                            description = tc.get("description", "")
                            
                            inputs_str = ", ".join([str(inp) for inp in inputs])
                            
                            if description:
                                method_tests.append(f"        # {description}")
                            method_tests.append(f"        result = self.instance.{method_name}({inputs_str})")
                            method_tests.append(f"        self.assertEqual(result, {expected})")
                    else:
                        method_tests.append(f"        # TODO: Add test implementation")
                        method_tests.append(f"        pass")
                
                elif framework == "pytest":
                    method_tests.append(f"\n    def test_{method_name}(self, setup):")
                    method_tests.append(f"        \"\"\"Test {method_name} method.\"\"\"")
                    method_tests.append(f"        instance = setup")
                    
                    # Add test case implementation
                    if method_test_cases:
                        for tc in method_test_cases:
                            inputs = tc.get("inputs", [])
                            expected = tc.get("expected", "")
                            description = tc.get("description", "")
                            
                            inputs_str = ", ".join([str(inp) for inp in inputs])
                            
                            if description:
                                method_tests.append(f"        # {description}")
                            method_tests.append(f"        result = instance.{method_name}({inputs_str})")
                            method_tests.append(f"        assert result == {expected}")
                    else:
                        method_tests.append(f"        # TODO: Add test implementation")
                        method_tests.append(f"        pass")
            
            elif language == "javascript":
                if framework == "jest":
                    method_tests.append(f"\n    test('should test {method_name} method', () => {{")
                    
                    # Add test case implementation
                    if method_test_cases:
                        for tc in method_test_cases:
                            inputs = tc.get("inputs", [])
                            expected = tc.get("expected", "")
                            description = tc.get("description", "")
                            
                            inputs_str = ", ".join([str(inp) for inp in inputs])
                            
                            if description:
                                method_tests.append(f"        // {description}")
                            method_tests.append(f"        const result = instance.{method_name}({inputs_str});")
                            method_tests.append(f"        expect(result).toBe({expected});")
                    else:
                        method_tests.append(f"        // TODO: Add test implementation")
                    
                    method_tests.append(f"    }});")
                
                elif framework == "mocha":
                    method_tests.append(f"\n    describe('{method_name} method', function() {{")
                    method_tests.append(f"        it('should work correctly', function() {{")
                    
                    # Add test case implementation
                    if method_test_cases:
                        for tc in method_test_cases:
                            inputs = tc.get("inputs", [])
                            expected = tc.get("expected", "")
                            description = tc.get("description", "")
                            
                            inputs_str = ", ".join([str(inp) for inp in inputs])
                            
                            if description:
                                method_tests.append(f"            // {description}")
                            method_tests.append(f"            const result = instance.{method_name}({inputs_str});")
                            method_tests.append(f"            assert.strictEqual(result, {expected});")
                    else:
                        method_tests.append(f"            // TODO: Add test implementation")
                    
                    method_tests.append(f"        }});")
                    method_tests.append(f"    }});")
            
            elif language == "java":
                if framework == "junit":
                    method_name_camel = self._to_camel_case(method_name)
                    method_tests.append(f"\n    @Test")
                    method_tests.append(f"    public void test{method_name_camel}() {{")
                    method_tests.append(f"        // Test {method_name} method")
                    
                    # Add test case implementation
                    if method_test_cases:
                        for tc in method_test_cases:
                            inputs = tc.get("inputs", [])
                            expected = tc.get("expected", "")
                            description = tc.get("description", "")
                            
                            inputs_str = ", ".join([str(inp) for inp in inputs])
                            
                            if description:
                                method_tests.append(f"        // {description}")
                            method_tests.append(f"        Object result = instance.{method_name}({inputs_str});")
                            method_tests.append(f"        assertEquals({expected}, result);")
                    else:
                        method_tests.append(f"        // TODO: Add test implementation")
                    
                    method_tests.append(f"    }}")
        
        return "\n".join(method_tests)
    
    def _to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case to CamelCase.
        
        Args:
            snake_str: String in snake_case
            
        Returns:
            String in CamelCase
        """
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    def _get_class_name_from_module(self, module_name: str) -> str:
        """
        Extract class name from module name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Extracted class name
        """
        # Split by dots and get the last part
        parts = module_name.split('.')
        last_part = parts[-1]
        
        # Convert to CamelCase
        return ''.join(x.title() for x in last_part.split('_'))
