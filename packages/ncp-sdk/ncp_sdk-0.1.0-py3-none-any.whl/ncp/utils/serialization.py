"""Serialization utilities for NCP SDK."""

import json
import pickle
from typing import Dict, Any, Optional
from ..agents import Agent
from ..types import AgentConfig


def serialize_agent(agent: Agent) -> Dict[str, Any]:
    """Serialize an agent to a dictionary.
    
    Args:
        agent: Agent instance to serialize
        
    Returns:
        Dictionary representation of the agent
    """
    return {
        "type": "ncp_agent",
        "version": "1.0",
        "config": agent.to_config().dict(),
        "tool_definitions": [
            {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": tool_def.parameters,
                "async": tool_def.async_tool,
                # Note: function code is not serialized for security
            }
            for tool_def in agent.get_tool_definitions()
        ]
    }


def deserialize_agent(data: Dict[str, Any]) -> Agent:
    """Deserialize an agent from dictionary data.
    
    Args:
        data: Dictionary containing serialized agent data
        
    Returns:
        Agent instance
        
    Raises:
        ValueError: If data is invalid
    """
    if data.get("type") != "ncp_agent":
        raise ValueError("Invalid agent data: missing or incorrect type")
    
    version = data.get("version", "1.0")
    if version != "1.0":
        raise ValueError(f"Unsupported agent version: {version}")
    
    config_data = data.get("config", {})
    config = AgentConfig(**config_data)
    
    # Create agent with string tool references (functions can't be deserialized)
    return Agent(
        name=config.name,
        description=config.description,
        instructions=config.instructions,
        tools=config.tools,  # These will be string references
        llm_config=config.llm_config,
        metadata=config.metadata
    )


def serialize_to_json(obj: Any) -> str:
    """Serialize object to JSON string.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string representation
    """
    if hasattr(obj, 'dict'):
        # Pydantic model
        return json.dumps(obj.dict(), indent=2, default=str)
    else:
        return json.dumps(obj, indent=2, default=str)


def deserialize_from_json(json_str: str, target_class: Optional[type] = None) -> Any:
    """Deserialize object from JSON string.
    
    Args:
        json_str: JSON string to deserialize
        target_class: Optional target class to deserialize into
        
    Returns:
        Deserialized object
    """
    data = json.loads(json_str)
    
    if target_class and hasattr(target_class, '__init__'):
        return target_class(**data)
    else:
        return data


def serialize_agent_config(config: AgentConfig) -> str:
    """Serialize agent configuration to JSON.
    
    Args:
        config: AgentConfig to serialize
        
    Returns:
        JSON string
    """
    return serialize_to_json(config)


def deserialize_agent_config(json_str: str) -> AgentConfig:
    """Deserialize agent configuration from JSON.
    
    Args:
        json_str: JSON string containing agent configuration
        
    Returns:
        AgentConfig instance
    """
    return deserialize_from_json(json_str, AgentConfig)