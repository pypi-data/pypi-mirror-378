"""NCP SDK - Network Copilot for AI agent development.

The NCP SDK enables developers to create and deploy custom agents and tools 
on the NCP platform with full type safety and development support.

Example:
    from ncp import Agent, tool
    
    @tool
    def my_tool(input: str) -> str:
        return f"Processed: {input}"
    
    agent = Agent(
        name="MyAgent",
        description="Custom agent",
        instructions="Handle user queries",
        tools=[my_tool]
    )
"""

from .agents import Agent, ModelConfig
from .tools import tool
from .types import ToolResult, AgentConfig
from .mcp import MCPServerConfig

__version__ = "0.1.0"
__author__ = "NCP Team"
__email__ = "support@aviznetworks.com"

__all__ = [
    # Core components
    "Agent",
    "ModelConfig",
    "tool",

    # MCP support
    "MCPServerConfig",

    # Types
    "ToolResult",
    "AgentConfig",

    # Version info
    "__version__",
]