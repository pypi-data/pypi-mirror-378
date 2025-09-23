"""NCP CLI init command."""

import os
import click
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

PROJECT_TEMPLATE = {
    "agents/__init__.py": "",
    "agents/main_agent.py": '''"""Main agent for {project_name}."""

from ncp import Agent
from tools.sample_tools import process_data, calculate_statistics

# Create your main agent
main_agent = Agent(
    name="{agent_name}",
    description="A sample NCP agent",
    instructions="You are a helpful assistant that can process text using available tools.",
    tools=[process_data, calculate_statistics],
)
''',
    "tools/__init__.py": "",
    "tools/sample_tools.py": '''"""Sample tools for NCP agents."""

from ncp import tool
from typing import List, Dict, Any


@tool
def process_data(data: List[str], format: str = "json") -> Dict[str, Any]:
    """Process a list of data items.
    
    Args:
        data: List of strings to process
        format: Output format (json, csv, text)
        
    Returns:
        Processed data in the specified format
    """
    processed = [item.upper() for item in data]
    
    if format == "json":
        return {{"processed_items": processed, "count": len(processed)}}
    elif format == "csv":
        return {{"csv": ",".join(processed)}}
    else:
        return {{"text": " ".join(processed)}}


@tool  
def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of numbers.
    
    Args:
        numbers: List of numbers to analyze
        
    Returns:
        Dictionary with statistical measures
    """
    if not numbers:
        return {{"error": "Empty list provided"}}
    
    return {{
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }}
''',
    "requirements.txt": '''# Add your additional Python dependencies here''',
    "apt-requirements.txt": '''# Add your system (APT) dependencies here
# One package per line, comments start with #
# Examples:
# curl
# git
# ffmpeg
# imagemagick
''',
    "README.md": '''# {project_name}

A custom NCP agent project.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your agent in `agents/main_agent.py`

3. Add custom tools in the `tools/` directory

4. Add system dependencies in `apt-requirements.txt` if needed

## Dependencies

- **requirements.txt**: Python packages (pandas, numpy, requests, etc.)
- **apt-requirements.txt**: System packages (curl, git, ffmpeg, etc.)

## Development

```bash
# Validate your project
ncp validate .

# Package for deployment  
ncp package . --output {project_name}.ncp

# Deploy to NCP platform
ncp deploy {project_name}.ncp --platform https://your-ncp-instance.com
```

## Project Structure

- `agents/` - Agent definitions
- `tools/` - Custom tool implementations
- `requirements.txt` - Python dependencies
- `ncp.toml` - Project configuration
''',
    "ncp.toml": '''[project]
name = "{project_name}"
version = "0.1.0"
description = "A custom NCP agent project"
author = "Your Name"

[agents]
main = "agents.main_agent:main_agent"

[deployment]
# platform_url = "https://your-ncp-instance.com"
'''
}


@click.command()
@click.argument('project_name')
@click.option('--author', '-a', help='Project author name')
@click.option('--description', '-d', help='Project description')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing directory')
def init(project_name: str, author: str, description: str, force: bool):
    """Initialize a new NCP agent project.
    
    Creates a new project directory with the standard NCP project structure,
    including sample agents, tools, and configuration files.
    
    PROJECT_NAME: Name of the project directory to create
    """
    project_path = Path(project_name)
    
    # Check if directory exists
    if project_path.exists() and not force:
        if not Confirm.ask(f"Directory '{project_name}' already exists. Continue?"):
            console.print("[red]Project initialization cancelled.[/red]")
            return
    
    # Prompt for missing information
    if not author:
        author = Prompt.ask("Author name", default="Anonymous")
    
    if not description:
        description = Prompt.ask("Project description", default=f"A custom NCP agent project")
    
    # Create project directory
    project_path.mkdir(exist_ok=True)
    
    console.print(f"[green]Creating NCP project '{project_name}'...[/green]")
    
    # Generate agent name from project name
    agent_name = project_name.replace('-', ' ').replace('_', ' ').title().replace(' ', '')
    
    # Create project files
    template_vars = {
        "project_name": project_name,
        "agent_name": agent_name,
        "author": author,
        "description": description
    }
    
    for file_path, content in PROJECT_TEMPLATE.items():
        full_path = project_path / file_path
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Format content with template variables
        formatted_content = content.format(**template_vars)
        
        # Write file
        with open(full_path, 'w') as f:
            f.write(formatted_content)
        
        console.print(f"  Created {file_path}")
    
    console.print(f"[bold green]✓[/bold green] Project '{project_name}' created successfully!")
    console.print(f"[cyan]Next steps:[/cyan]")
    console.print(f"  cd {project_name}")
    console.print(f"  # Edit agents/main_agent.py to customize your agent")
    console.print(f"  ncp validate .")
    console.print(f"  ncp package .")