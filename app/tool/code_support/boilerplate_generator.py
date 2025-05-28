"""
Boilerplate Generator Tool for OpenManus.

This tool provides functionality for generating code boilerplate in various
programming languages, following best practices and conventions.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoilerplateGeneratorTool(BaseTool):
    """
    Tool for generating code boilerplate in various programming languages.
    
    This tool creates function, class, and module templates following
    language-specific best practices and coding conventions.
    """
    
    name = "generate_function_boilerplate"
    description = "Generate code boilerplate for functions, classes, and modules in various languages"
    
    # Language-specific templates and conventions
    LANGUAGE_TEMPLATES = {
        "python": {
            "function": {
                "with_docstring": """def {function_name}({params_str}):
    \"\"\"
    {docstring}
    
    {param_docs}
    
    Returns:
        {return_type}: {return_description}
    \"\"\"
    {body}
""",
                "without_docstring": """def {function_name}({params_str}):
    {body}
"""
            },
            "class": {
                "with_docstring": """class {class_name}:
    \"\"\"
    {docstring}
    \"\"\"
    
    def __init__(self{init_params_str}):
        \"\"\"
        Initialize the {class_name}.
        
        {init_param_docs}
        \"\"\"
        {init_body}
    
    {methods}
""",
                "without_docstring": """class {class_name}:
    def __init__(self{init_params_str}):
        {init_body}
    
    {methods}
"""
            }
        },
        "javascript": {
            "function": {
                "with_docstring": """/**
 * {docstring}
 *
 {param_docs}
 * @returns {return_description}
 */
function {function_name}({params_str}) {
    {body}
}
""",
                "without_docstring": """function {function_name}({params_str}) {
    {body}
}
"""
            },
            "class": {
                "with_docstring": """/**
 * {docstring}
 */
class {class_name} {
    /**
     * Create a new {class_name}.
     *
     {init_param_docs}
     */
    constructor({init_params_str}) {
        {init_body}
    }
    
    {methods}
}
""",
                "without_docstring": """class {class_name} {
    constructor({init_params_str}) {
        {init_body}
    }
    
    {methods}
}
"""
            }
        },
        "java": {
            "function": {
                "with_docstring": """/**
 * {docstring}
 *
{param_docs}
 * @return {return_description}
 */
public {return_type} {function_name}({params_str}) {
    {body}
}
""",
                "without_docstring": """public {return_type} {function_name}({params_str}) {
    {body}
}
"""
            },
            "class": {
                "with_docstring": """/**
 * {docstring}
 */
public class {class_name} {
    /**
     * Create a new {class_name}.
     *
{init_param_docs}
     */
    public {class_name}({init_params_str}) {
        {init_body}
    }
    
    {methods}
}
""",
                "without_docstring": """public class {class_name} {
    public {class_name}({init_params_str}) {
        {init_body}
    }
    
    {methods}
}
"""
            }
        }
    }
    
    def __init__(self):
        """Initialize the BoilerplateGeneratorTool."""
        super().__init__()
        logger.info("BoilerplateGeneratorTool initialized")
    
    async def _arun(
        self,
        language: str,
        function_name: str,
        params: Optional[List[Dict[str, str]]] = None,
        docstring: Optional[bool] = False,
        return_type: Optional[str] = None,
        return_description: Optional[str] = None,
        description: Optional[str] = None,
        template_type: Optional[str] = "function",
        class_name: Optional[str] = None,
        methods: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate code boilerplate based on the provided parameters.
        
        Args:
            language: Programming language (python, javascript, java)
            function_name: Name of the function to generate
            params: List of parameter dictionaries with name, type, and description
            docstring: Whether to include docstring
            return_type: Return type of the function
            return_description: Description of the return value
            description: Description for the docstring
            template_type: Type of template (function, class)
            class_name: Name of the class (for class templates)
            methods: List of method dictionaries (for class templates)
            
        Returns:
            Dictionary containing the generated code and metadata
        """
        logger.info(f"Generating {template_type} boilerplate for {language}")
        
        # Validate inputs
        if not language:
            return {"error": "Language is required"}
        
        # Normalize language
        language = language.lower()
        
        # Check if language is supported
        if language not in self.LANGUAGE_TEMPLATES:
            return {"error": f"Unsupported language: {language}. Supported languages: {', '.join(self.LANGUAGE_TEMPLATES.keys())}"}
        
        # Generate code based on template type
        if template_type == "function":
            if not function_name:
                return {"error": "Function name is required"}
            
            result = self._generate_function(
                language=language,
                function_name=function_name,
                params=params or [],
                docstring=docstring,
                return_type=return_type,
                return_description=return_description,
                description=description
            )
        elif template_type == "class":
            if not class_name:
                return {"error": "Class name is required"}
            
            result = self._generate_class(
                language=language,
                class_name=class_name,
                methods=methods or [],
                params=params or [],
                docstring=docstring,
                description=description
            )
        else:
            return {"error": f"Unsupported template type: {template_type}. Supported types: function, class"}
        
        return result
    
    def _generate_function(
        self,
        language: str,
        function_name: str,
        params: List[Dict[str, str]],
        docstring: bool,
        return_type: Optional[str],
        return_description: Optional[str],
        description: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate function boilerplate.
        
        Args:
            language: Programming language
            function_name: Name of the function
            params: List of parameter dictionaries
            docstring: Whether to include docstring
            return_type: Return type of the function
            return_description: Description of the return value
            description: Description for the docstring
            
        Returns:
            Dictionary containing the generated code and metadata
        """
        # Get language-specific templates
        templates = self.LANGUAGE_TEMPLATES[language]["function"]
        
        # Format parameters
        params_str = self._format_params(language, params)
        
        # Format docstring
        param_docs = self._format_param_docs(language, params)
        
        # Set default return type and description if not provided
        if not return_type:
            if language == "python":
                return_type = "Any"
            elif language == "javascript":
                return_type = ""
            elif language == "java":
                return_type = "void"
        
        if not return_description:
            return_description = "Result of the operation"
        
        # Set default description if not provided
        if not description:
            description = f"{function_name} function"
        
        # Set default body
        if language == "python":
            body = "    pass"
        elif language == "javascript" or language == "java":
            body = "    // TODO: Implement function body"
        
        # Generate code
        template_key = "with_docstring" if docstring else "without_docstring"
        template = templates[template_key]
        
        code = template.format(
            function_name=function_name,
            params_str=params_str,
            docstring=description,
            param_docs=param_docs,
            return_type=return_type,
            return_description=return_description,
            body=body
        )
        
        return {
            "success": True,
            "code": code,
            "language": language,
            "template_type": "function",
            "function_name": function_name,
            "has_docstring": docstring
        }
    
    def _generate_class(
        self,
        language: str,
        class_name: str,
        methods: List[Dict[str, Any]],
        params: List[Dict[str, str]],
        docstring: bool,
        description: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate class boilerplate.
        
        Args:
            language: Programming language
            class_name: Name of the class
            methods: List of method dictionaries
            params: List of constructor parameter dictionaries
            docstring: Whether to include docstring
            description: Description for the docstring
            
        Returns:
            Dictionary containing the generated code and metadata
        """
        # Get language-specific templates
        templates = self.LANGUAGE_TEMPLATES[language]["class"]
        
        # Format constructor parameters
        init_params_str = self._format_params(language, params, is_method=True)
        
        # Format constructor parameter docs
        init_param_docs = self._format_param_docs(language, params)
        
        # Set default description if not provided
        if not description:
            description = f"{class_name} class"
        
        # Set default constructor body
        if language == "python":
            init_body = "        pass"
            for param in params:
                param_name = param.get("name", "")
                if param_name:
                    init_body = f"        self.{param_name} = {param_name}"
        elif language == "javascript":
            init_body = "        // Initialize properties"
            for param in params:
                param_name = param.get("name", "")
                if param_name:
                    init_body += f"\n        this.{param_name} = {param_name};"
        elif language == "java":
            init_body = "        // Initialize properties"
            for param in params:
                param_name = param.get("name", "")
                param_type = param.get("type", "")
                if param_name:
                    init_body += f"\n        this.{param_name} = {param_name};"
        
        # Generate methods
        methods_code = ""
        for method in methods:
            method_name = method.get("name", "")
            method_params = method.get("params", [])
            method_description = method.get("description", f"{method_name} method")
            method_return_type = method.get("return_type", "")
            method_return_description = method.get("return_description", "")
            
            if method_name:
                method_result = self._generate_function(
                    language=language,
                    function_name=method_name,
                    params=method_params,
                    docstring=docstring,
                    return_type=method_return_type,
                    return_description=method_return_description,
                    description=method_description
                )
                
                # Adjust method code for class context
                method_code = method_result["code"]
                if language == "python":
                    # Add self parameter and indentation
                    method_code = method_code.replace("def ", "def ")
                    if "(" in method_code:
                        method_code = method_code.replace("(", "(self, " if method_params else "(self")
                    method_code = "\n".join(["    " + line for line in method_code.split("\n")])
                elif language == "javascript":
                    # Convert to class method syntax
                    method_code = method_code.replace(f"function {method_name}", method_name)
                
                methods_code += f"\n{method_code}\n"
        
        # Generate code
        template_key = "with_docstring" if docstring else "without_docstring"
        template = templates[template_key]
        
        code = template.format(
            class_name=class_name,
            docstring=description,
            init_params_str=init_params_str,
            init_param_docs=init_param_docs,
            init_body=init_body,
            methods=methods_code
        )
        
        return {
            "success": True,
            "code": code,
            "language": language,
            "template_type": "class",
            "class_name": class_name,
            "has_docstring": docstring,
            "method_count": len(methods)
        }
    
    def _format_params(
        self,
        language: str,
        params: List[Dict[str, str]],
        is_method: bool = False
    ) -> str:
        """
        Format parameters based on language.
        
        Args:
            language: Programming language
            params: List of parameter dictionaries
            is_method: Whether the parameters are for a method
            
        Returns:
            Formatted parameter string
        """
        if not params:
            return ""
        
        param_parts = []
        
        for param in params:
            param_name = param.get("name", "")
            param_type = param.get("type", "")
            param_default = param.get("default", "")
            
            if not param_name:
                continue
            
            if language == "python":
                param_str = param_name
                if param_type:
                    param_str += f": {param_type}"
                if param_default:
                    param_str += f" = {param_default}"
            elif language == "javascript":
                param_str = param_name
                if param_default:
                    param_str += f" = {param_default}"
            elif language == "java":
                if not param_type:
                    param_type = "Object"
                param_str = f"{param_type} {param_name}"
            else:
                param_str = param_name
            
            param_parts.append(param_str)
        
        return ", ".join(param_parts)
    
    def _format_param_docs(
        self,
        language: str,
        params: List[Dict[str, str]]
    ) -> str:
        """
        Format parameter documentation based on language.
        
        Args:
            language: Programming language
            params: List of parameter dictionaries
            
        Returns:
            Formatted parameter documentation
        """
        if not params:
            return ""
        
        doc_parts = []
        
        for param in params:
            param_name = param.get("name", "")
            param_type = param.get("type", "")
            param_description = param.get("description", "")
            
            if not param_name:
                continue
            
            if not param_description:
                param_description = f"{param_name} parameter"
            
            if language == "python":
                doc_parts.append(f"    Args:\n        {param_name}: {param_description}")
            elif language == "javascript":
                if param_type:
                    doc_parts.append(f" * @param {{{param_type}}} {param_name} {param_description}")
                else:
                    doc_parts.append(f" * @param {param_name} {param_description}")
            elif language == "java":
                doc_parts.append(f" * @param {param_name} {param_description}")
        
        return "\n".join(doc_parts)
