"""Validation utilities for NCP SDK."""

from typing import List, Dict, Any
from ..types import AgentConfig, PackageManifest
from ..agents import Agent


def validate_agent_config(config: AgentConfig) -> List[str]:
    """Validate an agent configuration.
    
    Args:
        config: AgentConfig to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Basic validation is handled by Pydantic
    try:
        config.dict()
    except Exception as e:
        errors.append(f"Invalid configuration: {e}")
        return errors
    
    # Additional business logic validation
    if not config.name.strip():
        errors.append("Agent name cannot be empty")
    
    if len(config.name) > 100:
        errors.append("Agent name too long (max 100 characters)")
    
    if not config.description.strip():
        errors.append("Agent description cannot be empty")
    
    if len(config.description) > 500:
        errors.append("Agent description too long (max 500 characters)")
    
    if not config.instructions.strip():
        errors.append("Agent instructions cannot be empty")
    
    # Validate tool names
    for tool_name in config.tools:
        if not tool_name or not tool_name.strip():
            errors.append("Tool name cannot be empty")
        if not tool_name.replace('_', '').isalnum():
            errors.append(f"Invalid tool name '{tool_name}': must contain only letters, numbers, and underscores")
    
    return errors


def validate_agent(agent: Agent) -> List[str]:
    """Validate an Agent instance.
    
    Args:
        agent: Agent to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Use the agent's built-in validation
    errors.extend(agent.validate())
    
    # Validate the configuration
    try:
        config = agent.to_config()
        errors.extend(validate_agent_config(config))
    except Exception as e:
        errors.append(f"Failed to convert agent to configuration: {e}")
    
    return errors


def validate_package(manifest: PackageManifest) -> List[str]:
    """Validate a package manifest.
    
    Args:
        manifest: PackageManifest to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Basic validation handled by Pydantic
    try:
        manifest.dict()
    except Exception as e:
        errors.append(f"Invalid manifest: {e}")
        return errors
    
    # Package name validation
    if not manifest.name.replace('-', '').replace('_', '').isalnum():
        errors.append("Package name must contain only letters, numbers, hyphens, and underscores")
    
    # Version validation (basic semver check)
    version_parts = manifest.version.split('.')
    if len(version_parts) != 3:
        errors.append("Version must be in format major.minor.patch (e.g., 1.0.0)")
    else:
        for part in version_parts:
            if not part.isdigit():
                errors.append(f"Invalid version part '{part}': must be a number")
    
    # Validate dependencies format
    for dep in manifest.dependencies:
        if not dep or not isinstance(dep, str):
            errors.append(f"Invalid dependency: {dep}")
    
    # Validate module paths
    for agent_path in manifest.agents:
        if not agent_path.endswith('.py') and '.' not in agent_path:
            errors.append(f"Invalid agent module path: {agent_path}")
    
    for tool_path in manifest.tools:
        if not tool_path.endswith('.py') and '.' not in tool_path:
            errors.append(f"Invalid tool module path: {tool_path}")
    
    return errors


def validate_python_identifier(name: str) -> bool:
    """Validate that a string is a valid Python identifier.
    
    Args:
        name: String to validate
        
    Returns:
        True if valid Python identifier
    """
    return name.isidentifier() and not name.startswith('_')


def validate_tool_parameters(parameters: Dict[str, Any]) -> List[str]:
    """Validate tool parameter schema.
    
    Args:
        parameters: Parameter schema dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(parameters, dict):
        errors.append("Parameters must be a dictionary")
        return errors
    
    # Must have required structure
    if parameters.get("type") != "object":
        errors.append("Parameters must have type 'object'")
    
    properties = parameters.get("properties", {})
    if not isinstance(properties, dict):
        errors.append("Parameters 'properties' must be a dictionary")
        return errors
    
    required = parameters.get("required", [])
    if not isinstance(required, list):
        errors.append("Parameters 'required' must be a list")
    
    # Validate each property
    valid_types = {"string", "integer", "number", "boolean", "array", "object"}
    
    for prop_name, prop_schema in properties.items():
        if not validate_python_identifier(prop_name):
            errors.append(f"Invalid parameter name '{prop_name}': must be a valid Python identifier")
        
        if not isinstance(prop_schema, dict):
            errors.append(f"Parameter '{prop_name}' schema must be a dictionary")
            continue
        
        prop_type = prop_schema.get("type")
        if prop_type not in valid_types:
            errors.append(f"Parameter '{prop_name}' has invalid type '{prop_type}'")
    
    # Validate required parameters exist in properties
    for req_param in required:
        if req_param not in properties:
            errors.append(f"Required parameter '{req_param}' not found in properties")
    
    return errors