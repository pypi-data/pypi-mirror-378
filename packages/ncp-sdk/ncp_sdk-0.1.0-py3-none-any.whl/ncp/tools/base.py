"""Base tool functionality for NCP SDK."""

import inspect
from typing import Any, Dict, List, Optional, Callable, get_type_hints
from pydantic import BaseModel, SkipValidation


class ToolMeta(BaseModel):
    """Metadata for NCP tools."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    async_tool: bool
    function: Optional[SkipValidation[Callable]] = None
    
    model_config = {"arbitrary_types_allowed": True}


def extract_function_info(func: Callable) -> Dict[str, Any]:
    """Extract metadata from a function for tool creation.
    
    Args:
        func: The function to analyze
        
    Returns:
        Dictionary containing function metadata
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Get type hints
    try:
        type_hints = get_type_hints(func)
    except (NameError, AttributeError):
        type_hints = {}
    
    # Extract docstring
    docstring = inspect.getdoc(func) or ""
    
    # Parse parameters
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param_name, param in sig.parameters.items():
        param_info = {
            "type": _python_type_to_json_type(type_hints.get(param_name, str))
        }
        
        # Add description from docstring if available
        param_info["description"] = f"Parameter {param_name}"
        
        # Check if parameter is required
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)
        else:
            param_info["default"] = param.default
        
        parameters["properties"][param_name] = param_info
    
    return {
        "name": func.__name__,
        "description": docstring.split('\n')[0] if docstring else f"Tool: {func.__name__}",
        "parameters": parameters,
        "async": inspect.iscoroutinefunction(func)
    }


def _python_type_to_json_type(python_type: type) -> str:
    """Convert Python type to JSON Schema type.
    
    Args:
        python_type: Python type to convert
        
    Returns:
        JSON Schema type string
    """
    type_mapping = {
        str: "string",
        int: "integer", 
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    
    # Handle typing module types
    if hasattr(python_type, '__origin__'):
        origin = python_type.__origin__
        if origin in type_mapping:
            return type_mapping[origin]
        elif origin == list:
            return "array"
        elif origin == dict:
            return "object"
    
    # Handle basic types
    if python_type in type_mapping:
        return type_mapping[python_type]
    
    # Default to string for unknown types
    return "string"


def validate_tool_function(func: Callable) -> List[str]:
    """Validate that a function can be used as a tool.
    
    Args:
        func: Function to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not callable(func):
        errors.append("Tool must be callable")
        return errors
    
    # Check function signature
    sig = inspect.signature(func)
    
    # Validate parameters
    for param_name, param in sig.parameters.items():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            errors.append(f"Tool functions cannot use *args parameter: {param_name}")
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            errors.append(f"Tool functions cannot use **kwargs parameter: {param_name}")
    
    # Check docstring
    docstring = inspect.getdoc(func)
    if not docstring:
        errors.append("Tool functions should have a docstring describing their purpose")
    
    return errors


def create_tool_schema(func: Callable) -> Dict[str, Any]:
    """Create OpenAI function calling schema for a tool.
    
    Args:
        func: The tool function
        
    Returns:
        OpenAI-compatible function schema
    """
    info = extract_function_info(func)
    
    return {
        "type": "function",
        "function": {
            "name": info["name"],
            "description": info["description"],
            "parameters": info["parameters"]
        }
    }