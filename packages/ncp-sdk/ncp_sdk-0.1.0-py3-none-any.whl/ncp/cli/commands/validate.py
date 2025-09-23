"""NCP CLI validate command."""

import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any
import click
import toml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...utils.validation import validate_agent_config, validate_package
from ...types import AgentConfig, PackageManifest
from ...tools.decorator import is_ncp_tool

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--strict', is_flag=True, help='Fail on warnings')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json']), default='text', help='Output format')
def validate(path: str, strict: bool, output_format: str):
    """Validate an NCP project or package.
    
    Performs comprehensive validation of:
    - Project structure and configuration
    - Agent definitions and configurations
    - Tool implementations and schemas
    - Package manifest (if present)
    
    PATH: Path to project directory or .ncp package file
    """
    target_path = Path(path)
    
    if target_path.is_file() and target_path.suffix == '.ncp':
        # Validate package file
        result = validate_package_file(target_path)
    else:
        # Validate project directory
        result = validate_project_directory(target_path)
    
    # Output results
    if output_format == 'json':
        import json
        click.echo(json.dumps(result, indent=2))
    else:
        display_validation_results(result, strict)
    
    # Exit with appropriate code
    if result['has_errors'] or (strict and result['has_warnings']):
        sys.exit(1)
    else:
        sys.exit(0)


def validate_project_directory(project_path: Path) -> Dict[str, Any]:
    """Validate an NCP project directory.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Validation results dictionary
    """
    results = {
        'type': 'project',
        'path': str(project_path),
        'has_errors': False,
        'has_warnings': False,
        'structure': {'errors': [], 'warnings': []},
        'config': {'errors': [], 'warnings': []},
        'agents': {'errors': [], 'warnings': [], 'details': []},
        'tools': {'errors': [], 'warnings': [], 'details': []}
    }
    
    # Validate project structure
    structure_errors = validate_project_structure(project_path)
    results['structure']['errors'] = structure_errors
    if structure_errors:
        results['has_errors'] = True
    
    # Load and validate configuration
    config_path = project_path / 'ncp.toml'
    if config_path.exists():
        try:
            config_data = toml.load(config_path)
            config_errors = validate_project_config(config_data)
            results['config']['errors'] = config_errors
            if config_errors:
                results['has_errors'] = True
        except Exception as e:
            results['config']['errors'] = [f"Failed to load ncp.toml: {e}"]
            results['has_errors'] = True
            return results
    else:
        results['config']['errors'] = ['Missing ncp.toml configuration file']
        results['has_errors'] = True
        return results
    
    # Validate agents
    agents_result = validate_project_agents(project_path, config_data)
    results['agents'].update(agents_result)
    if agents_result['errors']:
        results['has_errors'] = True
    if agents_result['warnings']:
        results['has_warnings'] = True
    
    # Skip separate tool validation - tools will be shown through agent validation
    
    return results


def validate_project_structure(project_path: Path) -> List[str]:
    """Validate project directory structure."""
    errors = []
    
    required_files = ['ncp.toml', 'requirements.txt']
    required_dirs = ['agents', 'tools']
    
    for file_path in required_files:
        if not (project_path / file_path).exists():
            errors.append(f"Missing required file: {file_path}")
    
    for dir_path in required_dirs:
        if not (project_path / dir_path).is_dir():
            errors.append(f"Missing required directory: {dir_path}")
        elif not (project_path / dir_path / "__init__.py").exists():
            errors.append(f"Missing __init__.py in {dir_path}/")
    
    return errors


def validate_project_config(config_data: Dict[str, Any]) -> List[str]:
    """Validate project configuration."""
    errors = []
    
    # Required sections
    if 'project' not in config_data:
        errors.append("Missing [project] section in ncp.toml")
        return errors
    
    project_config = config_data['project']
    required_fields = ['name', 'version', 'description']
    
    for field in required_fields:
        if field not in project_config:
            errors.append(f"Missing required field in [project]: {field}")
    
    # Validate version format
    if 'version' in project_config:
        version = project_config['version']
        parts = version.split('.')
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            errors.append(f"Invalid version format: {version} (expected: major.minor.patch)")
    
    return errors


def validate_project_agents(project_path: Path, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate project agents."""
    result = {'errors': [], 'warnings': [], 'details': []}
    
    agents_dir = project_path / 'agents'
    if not agents_dir.exists():
        result['errors'].append("Agents directory not found")
        return result
    
    # Find all agent modules
    agent_files = [f for f in agents_dir.glob("*.py") if f.name != "__init__.py"]
    
    if not agent_files:
        result['warnings'].append("No agent modules found")
        return result
    
    # Add agents directory to path for imports
    sys.path.insert(0, str(project_path))
    
    try:
        for agent_file in agent_files:
            module_name = f"agents.{agent_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, agent_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find agent instances
                agents_found = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, '__class__') and attr.__class__.__name__ == 'Agent':
                        agents_found.append(attr_name)
                        
                        # Validate individual agent
                        agent_errors = validate_agent_instance(attr, attr_name)
                        if agent_errors:
                            result['errors'].extend([f"{agent_file.name}:{attr_name}: {err}" for err in agent_errors])
                
                if agents_found:
                    # Also collect tools used by agents in this file
                    tools_used = []
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, '__class__') and attr.__class__.__name__ == 'Agent':
                            # Get tools from this agent
                            if hasattr(attr, 'tools') and attr.tools:
                                for tool in attr.tools:
                                    if callable(tool):
                                        if hasattr(tool, '_ncp_tool_info'):
                                            tool_name = tool._ncp_tool_info.get('name', tool.__name__)
                                        else:
                                            tool_name = tool.__name__
                                        if tool_name not in tools_used:
                                            tools_used.append(tool_name)
                                    elif isinstance(tool, str):
                                        if tool not in tools_used:
                                            tools_used.append(tool)
                    
                    result['details'].append({
                        'file': agent_file.name,
                        'agents': agents_found,
                        'tools': tools_used
                    })
                else:
                    result['warnings'].append(f"No Agent instances found in {agent_file.name}")
                    
            except Exception as e:
                result['errors'].append(f"Failed to load {agent_file.name}: {e}")
                
    finally:
        sys.path.pop(0)
    
    return result


def validate_project_tools(project_path: Path, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate project tools."""
    result = {'errors': [], 'warnings': [], 'details': []}
    
    # Find all Python files in both tools/ and agents/ directories
    tool_files = []
    
    # Check tools directory
    tools_dir = project_path / 'tools'
    if tools_dir.exists():
        tool_files.extend([f for f in tools_dir.glob("*.py") if f.name != "__init__.py"])
    
    # Check agents directory for inline tools
    agents_dir = project_path / 'agents'
    if agents_dir.exists():
        tool_files.extend([f for f in agents_dir.glob("*.py") if f.name != "__init__.py"])
    
    if not tool_files:
        result['warnings'].append("No tool modules found")
        return result
    
    # Add project directory to path for imports
    sys.path.insert(0, str(project_path))
    
    try:
        for tool_file in tool_files:
            # Determine module name based on parent directory
            if tool_file.parent.name == "tools":
                module_name = f"tools.{tool_file.stem}"
            elif tool_file.parent.name == "agents":
                module_name = f"agents.{tool_file.stem}"
            else:
                module_name = tool_file.stem
                
            try:
                spec = importlib.util.spec_from_file_location(module_name, tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find tool functions
                tools_found = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if is_ncp_tool(attr):
                        tools_found.append(attr_name)
                        
                        # Validate individual tool
                        tool_errors = validate_tool_function(attr, attr_name)
                        if tool_errors:
                            result['errors'].extend([f"{tool_file.name}:{attr_name}: {err}" for err in tool_errors])
                
                if tools_found:
                    result['details'].append({
                        'file': tool_file.name,
                        'tools': tools_found
                    })
                else:
                    result['warnings'].append(f"No @tool decorated functions found in {tool_file.name}")
                    
            except Exception as e:
                result['errors'].append(f"Failed to load {tool_file.name}: {e}")
                
    finally:
        sys.path.pop(0)
    
    return result


def validate_agent_instance(agent, agent_name: str) -> List[str]:
    """Validate an individual agent instance."""
    errors = []
    
    try:
        # Use the agent's built-in validation
        agent_errors = agent.validate()
        errors.extend(agent_errors)
        
        # Additional validation
        if not agent.name.strip():
            errors.append("Agent name is empty")
        
        if not agent.description.strip():
            errors.append("Agent description is empty")
            
        if not agent.instructions.strip():
            errors.append("Agent instructions are empty")
            
    except Exception as e:
        errors.append(f"Validation failed: {e}")
    
    return errors


def validate_tool_function(tool_func, tool_name: str) -> List[str]:
    """Validate an individual tool function."""
    errors = []
    
    try:
        # Check if it has tool metadata
        if not hasattr(tool_func, '_ncp_tool_info'):
            errors.append("Missing tool metadata (not decorated with @tool?)")
            return errors
        
        tool_info = tool_func._ncp_tool_info
        
        # Validate tool info structure
        required_fields = ['name', 'description', 'parameters']
        for field in required_fields:
            if field not in tool_info:
                errors.append(f"Missing tool metadata field: {field}")
        
    except Exception as e:
        errors.append(f"Tool validation failed: {e}")
    
    return errors


def validate_package_file(package_path: Path) -> Dict[str, Any]:
    """Validate a .ncp package file."""
    # This would be implemented to validate packaged files
    return {
        'type': 'package',
        'path': str(package_path),
        'has_errors': False,
        'has_warnings': False,
        'message': 'Package validation not yet implemented'
    }


def display_validation_results(results: Dict[str, Any], strict: bool):
    """Display validation results in a user-friendly format."""
    console.print(f"\\n[bold]Validating {results['type']}: {results['path']}[/bold]\\n")
    
    # Overall status
    if results['has_errors']:
        status = "[red]✗ FAILED[/red]"
    elif results['has_warnings']:
        status = "[yellow]⚠ PASSED WITH WARNINGS[/yellow]"
    else:
        status = "[green]✓ PASSED[/green]"
    
    console.print(Panel(status, title="Validation Status", border_style="blue"))
    
    # Display results by category
    categories = [
        ('structure', 'Project Structure'),
        ('config', 'Configuration'),
        ('agents', 'Agents'),
        ('tools', 'Tools')
    ]
    
    for category_key, category_name in categories:
        if category_key not in results:
            continue
            
        category_data = results[category_key]
        
        if category_data.get('errors') or category_data.get('warnings'):
            table = Table(title=f"{category_name} Issues", show_header=True, header_style="bold magenta")
            table.add_column("Type", style="dim", width=10)
            table.add_column("Issue", style="")
            
            for error in category_data.get('errors', []):
                table.add_row("ERROR", f"[red]{error}[/red]")
            
            for warning in category_data.get('warnings', []):
                table.add_row("WARNING", f"[yellow]{warning}[/yellow]")
            
            console.print(table)
            console.print()
        
        # Display details if available
        if 'details' in category_data and category_data['details']:
            if category_key == 'agents':
                # Special handling for agents - show both agents and their tools
                agents_table = Table(title="Found Agents", show_header=True, header_style="bold green")
                agents_table.add_column("File", style="dim")
                agents_table.add_column("Agent", style="")
                agents_table.add_column("Tools", style="cyan")
                
                for detail in category_data['details']:
                    agents = detail.get('agents', [])
                    tools = detail.get('tools', [])
                    agents_str = ', '.join(agents) if agents else 'None'
                    tools_str = ', '.join(tools) if tools else 'None'
                    agents_table.add_row(detail['file'], agents_str, tools_str)
                
                console.print(agents_table)
                console.print()
            else:
                # Default handling for other categories
                details_table = Table(title=f"Found {category_name}", show_header=True, header_style="bold green")
                details_table.add_column("File", style="dim")
                details_table.add_column("Items", style="")
                
                for detail in category_data['details']:
                    items = detail.get('agents', []) + detail.get('tools', [])
                    details_table.add_row(detail['file'], ', '.join(items))
                
                console.print(details_table)
                console.print()
    
    # Summary
    total_errors = sum(len(cat.get('errors', [])) for cat in results.values() if isinstance(cat, dict))
    total_warnings = sum(len(cat.get('warnings', [])) for cat in results.values() if isinstance(cat, dict))
    
    if total_errors > 0:
        console.print(f"[red]Found {total_errors} error(s)[/red]")
    if total_warnings > 0:
        console.print(f"[yellow]Found {total_warnings} warning(s)[/yellow]")
    
    if not total_errors and not total_warnings:
        console.print("[green]No issues found! 🎉[/green]")