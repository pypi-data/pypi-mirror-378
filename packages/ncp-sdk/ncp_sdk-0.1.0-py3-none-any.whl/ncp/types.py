"""NCP SDK Type definitions.

This module provides all the type definitions used throughout the NCP SDK
for type safety and IDE support during development.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from typing_extensions import TypedDict, Literal
from pydantic import BaseModel, Field, SkipValidation
from enum import Enum


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LLAMA = "llama"
    CUSTOM = "custom"


class ModelConfig(BaseModel):
    """Configuration for LLM models."""
    
    model: str = Field(..., description="Model identifier")
    api_key: str = Field(..., description="API key for the model provider")
    base_url: Optional[str] = Field(None, description="Custom base URL for API")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(2048, gt=0, description="Maximum tokens to generate")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    
    model_config = {"extra": "forbid"}


class ToolResult(BaseModel):
    """Result from a tool execution."""
    
    success: bool = Field(..., description="Whether the tool executed successfully")
    result: Any = Field(None, description="The actual result data")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {"arbitrary_types_allowed": True}


class ToolDefinition(BaseModel):
    """Definition of a tool that can be used by agents."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    function: SkipValidation[Callable] = Field(..., description="The actual function implementation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameter schema")
    async_tool: bool = Field(False, description="Whether the tool is async")
    
    model_config = {"arbitrary_types_allowed": True}


class AgentConfig(BaseModel):
    """Configuration for an NCP Agent."""

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Brief description of the agent")
    instructions: str = Field(..., description="Detailed instructions for the agent")
    llm_config: Optional[ModelConfig] = Field(None, description="LLM configuration")
    tools: List[str] = Field(default_factory=list, description="List of tool names")
    mcp_servers: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list,
        description="MCP server configurations (URLs or config dicts)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {"extra": "forbid"}


class PackageManifest(BaseModel):
    """Manifest for an NCP package."""
    
    name: str = Field(..., description="Package name")
    version: str = Field(..., description="Package version")
    description: str = Field(..., description="Package description")
    author: Optional[str] = Field(None, description="Package author")
    license: Optional[str] = Field(None, description="Package license")
    dependencies: List[str] = Field(default_factory=list, description="Python dependencies")
    agents: List[str] = Field(default_factory=list, description="Agent module paths")
    tools: List[str] = Field(default_factory=list, description="Tool module paths")
    entry_point: Optional[str] = Field(None, description="Main entry point")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {"extra": "forbid"}


class DeploymentConfig(BaseModel):
    """Configuration for deploying to NCP platform."""
    
    platform_url: str = Field(..., description="NCP platform URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    project_id: Optional[str] = Field(None, description="Target project ID")
    environment: Literal["dev", "staging", "prod"] = Field("dev", description="Deployment environment")
    timeout: int = Field(300, description="Deployment timeout in seconds")
    
    model_config = {"extra": "forbid"}


# Type aliases for common patterns
ToolFunction = Callable[..., Any]
AsyncToolFunction = Callable[..., Any]  # Should be awaitable
ParameterSchema = Dict[str, Any]
SchemaDict = Dict[str, Any]

# Runtime types (what actually gets executed on platform)
class AgentRuntime(TypedDict):
    """Runtime representation of an agent on the platform."""
    id: str
    name: str
    status: Literal["active", "inactive", "error"]
    created_at: str
    updated_at: str
    

class ExecutionResult(TypedDict):
    """Result from executing an agent on the platform."""
    agent_id: str
    execution_id: str
    status: Literal["running", "completed", "failed"]
    result: Optional[str]
    error: Optional[str]
    started_at: str
    completed_at: Optional[str]
    

# Validation schemas
TOOL_PARAMETER_TYPES = {
    "string", "integer", "number", "boolean", "array", "object"
}