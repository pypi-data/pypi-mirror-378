"""Tool decorator for NCP SDK.

This module provides the @tool decorator that developers use to create
tools that can be used by NCP agents.
"""

import functools
import inspect
from typing import Callable, Any, Optional
from .base import extract_function_info, validate_tool_function, ToolMeta


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Callable:
    """Decorator to mark a function as an NCP tool.
    
    This decorator marks a function as a tool that can be used by NCP agents.
    The decorated function will have metadata attached for schema generation
    and validation.
    
    Args:
        func: The function to decorate (when used as @tool)
        name: Optional custom name for the tool (defaults to function name)
        description: Optional custom description (defaults to docstring)
    
    Returns:
        Decorated function with NCP tool metadata
    
    Example:
        @tool
        def get_weather(city: str) -> str:
            '''Get current weather for a city.'''
            return f"Weather in {city}: Sunny, 22°C"
        
        @tool(name="custom_name", description="Custom description")
        def my_function(input: str) -> str:
            return f"Processed: {input}"
    """
    
    def decorator(func: Callable) -> Callable:
        # Validate the function
        errors = validate_tool_function(func)
        if errors:
            raise ValueError(f"Invalid tool function '{func.__name__}': {', '.join(errors)}")
        
        # Extract function information
        func_info = extract_function_info(func)
        
        # Override with custom values if provided
        if name:
            func_info["name"] = name
        if description:
            func_info["description"] = description
        
        # Create wrapper that preserves original function behavior
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Attach NCP tool metadata
        wrapper._ncp_tool_info = func_info
        wrapper._ncp_tool_meta = ToolMeta(
            name=func_info["name"],
            description=func_info["description"],
            parameters=func_info["parameters"],
            async_tool=func_info["async"],
            function=func
        )
        
        # Mark as NCP tool
        wrapper._is_ncp_tool = True
        
        return wrapper
    
    # Handle both @tool and @tool() syntax
    if func is None:
        # Called with arguments: @tool(name="...", description="...")
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)


def is_ncp_tool(obj: Any) -> bool:
    """Check if an object is an NCP tool.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object is an NCP tool
    """
    return (
        callable(obj) and 
        hasattr(obj, '_is_ncp_tool') and 
        obj._is_ncp_tool is True
    )


def get_tool_info(tool_func: Callable) -> Optional[dict]:
    """Get tool information from a decorated function.
    
    Args:
        tool_func: Function decorated with @tool
        
    Returns:
        Tool information dictionary or None if not a tool
    """
    if not is_ncp_tool(tool_func):
        return None
    
    return getattr(tool_func, '_ncp_tool_info', None)


def get_tool_meta(tool_func: Callable) -> Optional[ToolMeta]:
    """Get tool metadata from a decorated function.
    
    Args:
        tool_func: Function decorated with @tool
        
    Returns:
        ToolMeta object or None if not a tool
    """
    if not is_ncp_tool(tool_func):
        return None
        
    return getattr(tool_func, '_ncp_tool_meta', None)