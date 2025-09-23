"""Base Agent class for NCP SDK.

This module provides the main Agent class that developers use to define
AI agents. Agents created with this class are designed for deployment
and execution on the NCP platform.
"""

from typing import List, Optional, Dict, Any, Union, Callable
from pydantic import BaseModel, Field, validator, SkipValidation
from ..types import AgentConfig, ToolDefinition
from .config import ModelConfig
from ..mcp.config import MCPServerConfig


class Agent(BaseModel):
    """NCP Agent class for creating AI agents.
    
    An Agent represents an AI assistant with specific instructions, capabilities,
    and tools. Agents are defined locally using this class and then deployed
    to the NCP platform for execution.
    
    Example:
        from ncp import Agent, tool, ModelConfig, MCPServerConfig

        @tool
        def get_weather(city: str) -> str:
            return f"Weather in {city}: Sunny, 22°C"

        # Agent with local tools
        agent = Agent(
            name="WeatherBot",
            description="Provides weather information",
            instructions="Help users get weather information for any city",
            tools=[get_weather],
            llm_config=ModelConfig(
                model="gpt-4-turbo",
                api_key="sk-..."
            )
        )

        # Agent with MCP server tools
        mcp_agent = Agent(
            name="FileManager",
            description="File management assistant with MCP tools",
            instructions="Help users manage files using MCP file server tools",
            mcp_servers=[
                "http://localhost:3000",  # Simple URL
                MCPServerConfig(
                    url="https://secure-mcp.example.com",
                    auth_token="your-token",
                    timeout=30
                )
            ],
            llm_config=ModelConfig(model="gpt-4")
        )
    """
    
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str = Field(..., min_length=1, max_length=500, description="Brief description")
    instructions: str = Field(..., min_length=1, description="Detailed behavior instructions")
    
    # Tools (can be functions or tool names for deployed agents)
    tools: List[Union[SkipValidation[Callable], str]] = Field(default_factory=list, description="Agent tools")
    
    # Model configuration (optional - can use platform default)
    llm_config: Optional[ModelConfig] = Field(None, description="LLM configuration")

    # MCP server configurations (optional - for external tools)
    mcp_servers: List[Union[str, MCPServerConfig]] = Field(
        default_factory=list,
        description="MCP server configurations (URLs or MCPServerConfig objects)"
    )

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {"extra": "forbid", "validate_assignment": True, "arbitrary_types_allowed": True}
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate agent name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Agent name must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    @validator('tools')
    def validate_tools(cls, v: List[Union[callable, str]]) -> List[Union[callable, str]]:
        """Validate tools list."""
        for tool in v:
            if not (callable(tool) or isinstance(tool, str)):
                raise ValueError("Tools must be callable functions or strings")
        return v

    @validator('mcp_servers')
    def validate_mcp_servers(cls, v: List[Union[str, MCPServerConfig]]) -> List[Union[str, MCPServerConfig]]:
        """Validate MCP servers list."""
        for server in v:
            if isinstance(server, str):
                # Basic URL validation
                if not (server.startswith('http://') or server.startswith('https://')):
                    raise ValueError(f"MCP server URL must start with http:// or https://, got: {server}")
            elif not isinstance(server, MCPServerConfig):
                raise ValueError("MCP servers must be URL strings or MCPServerConfig objects")
        return v
    
    def to_config(self) -> AgentConfig:
        """Convert to AgentConfig for serialization."""
        return AgentConfig(
            name=self.name,
            description=self.description,
            instructions=self.instructions,
            llm_config=self.llm_config,
            tools=[tool.__name__ if callable(tool) else tool for tool in self.tools],
            mcp_servers=self.mcp_servers,
            metadata=self.metadata,
        )
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Extract tool definitions from callable tools.
        
        Returns:
            List of ToolDefinition objects for callable tools.
            String tool references are not included.
        """
        definitions = []
        
        for tool in self.tools:
            if callable(tool) and hasattr(tool, '_ncp_tool_info'):
                # Extract tool info from decorator
                tool_info = tool._ncp_tool_info
                definitions.append(ToolDefinition(
                    name=tool_info['name'],
                    description=tool_info['description'],
                    function=tool,
                    parameters=tool_info['parameters'],
                    async_tool=tool_info['async']
                ))
        
        return definitions
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        names = []
        for tool in self.tools:
            if callable(tool):
                if hasattr(tool, '_ncp_tool_info'):
                    names.append(tool._ncp_tool_info['name'])
                else:
                    names.append(tool.__name__)
            else:
                names.append(tool)
        return names
    
    def add_tool(self, tool: Union[callable, str]) -> None:
        """Add a tool to the agent.
        
        Args:
            tool: Either a callable function decorated with @tool or a string tool name
        """
        if tool not in self.tools:
            self.tools.append(tool)
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the agent by name.
        
        Args:
            tool_name: Name of the tool to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        for i, tool in enumerate(self.tools):
            name = tool.__name__ if callable(tool) else tool
            if name == tool_name:
                self.tools.pop(i)
                return True
        return False
    
    def validate(self) -> List[str]:
        """Validate agent configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for duplicate tool names
        tool_names = self.get_tool_names()
        if len(tool_names) != len(set(tool_names)):
            errors.append("Duplicate tool names found")
        
        # Validate callable tools have proper decoration
        for tool in self.tools:
            if callable(tool) and not hasattr(tool, '_ncp_tool_info'):
                errors.append(f"Tool '{tool.__name__}' is not decorated with @tool")
        
        # Validate model config if provided
        if self.llm_config:
            try:
                self.llm_config.model_dump()
            except Exception as e:
                errors.append(f"Invalid model configuration: {e}")
        
        return errors
    
    def __str__(self) -> str:
        """String representation."""
        return f"Agent(name='{self.name}', tools={len(self.tools)})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Agent(name='{self.name}', description='{self.description[:50]}...', "
            f"tools={self.get_tool_names()}, model={self.llm_config.model if self.llm_config else 'default'})"
        )