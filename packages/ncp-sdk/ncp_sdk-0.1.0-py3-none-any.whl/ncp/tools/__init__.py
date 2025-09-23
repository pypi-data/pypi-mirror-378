"""NCP SDK Tools module.

This module provides the @tool decorator and related functionality for creating
tools that can be used by NCP agents. Tools are functions that agents can call
to perform specific tasks.
"""

from .decorator import tool
from .base import ToolMeta, validate_tool_function

__all__ = ["tool", "ToolMeta", "validate_tool_function"]