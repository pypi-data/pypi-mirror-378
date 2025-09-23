"""NCP CLI package command."""

import zipfile
import json
import toml
from pathlib import Path
from typing import Dict, Any
import click
from rich.console import Console
from rich.progress import Progress

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', help='Output package file path')
@click.option('--exclude', multiple=True, help='Patterns to exclude from package')
def package(path: str, output: str, exclude: tuple):
    """Package an NCP project into a deployable .ncp file.
    
    Creates a compressed package containing:
    - Agent and tool definitions
    - Project configuration
    - Dependencies specification
    - Metadata for deployment
    
    PATH: Path to project directory to package
    """
    project_path = Path(path)
    
    # Validate project structure
    if not (project_path / "ncp.toml").exists():
        console.print("[red]Error:[/red] Not in an NCP project directory.")
        console.print("Run 'ncp init <project_name>' to create a new project.")
        return
    
    # Load project configuration
    try:
        config_data = toml.load(project_path / "ncp.toml")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load ncp.toml: {e}")
        return
    
    project_name = config_data.get('project', {}).get('name', 'unnamed-project')
    
    # Determine output file
    if not output:
        output = f"{project_name}.ncp"
    
    output_path = Path(output)
    if output_path.exists():
        if not click.confirm(f"Output file '{output}' exists. Overwrite?"):
            return
    
    console.print(f"[blue]Packaging NCP project: {project_name}[/blue]")
    console.print(f"Source: {project_path}")
    console.print(f"Output: {output_path}")
    
    # Create package
    with Progress(console=console) as progress:
        task = progress.add_task("Creating package...", total=100)
        
        try:
            # Create the package manifest
            progress.update(task, advance=10, description="Creating manifest...")
            manifest = create_package_manifest(project_path, config_data)
            
            # Create package archive
            progress.update(task, advance=20, description="Creating archive...")
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as package_zip:
                
                # Add manifest
                manifest_json = json.dumps(manifest, indent=2)
                package_zip.writestr("manifest.json", manifest_json)
                progress.update(task, advance=10)
                
                # Add project files
                progress.update(task, advance=10, description="Adding project files...")
                
                # Files to include
                include_patterns = [
                    "agents/**/*.py",
                    "tools/**/*.py", 
                    "*.py",
                    "requirements.txt",
                    "ncp.toml",
                    "README.md"
                ]
                
                # Default exclude patterns
                default_excludes = {
                    "__pycache__",
                    "*.pyc",
                    ".git",
                    ".gitignore",
                    "venv",
                    ".venv",
                    "build",
                    "dist",
                    "*.egg-info"
                }
                
                # Add user excludes
                exclude_patterns = set(exclude) | default_excludes
                
                # Add files to package
                files_added = 0
                for pattern in include_patterns:
                    for file_path in project_path.glob(pattern):
                        if file_path.is_file():
                            # Check if file should be excluded
                            relative_path = file_path.relative_to(project_path)
                            if not should_exclude(relative_path, exclude_patterns):
                                package_zip.write(file_path, relative_path)
                                files_added += 1
                
                progress.update(task, advance=40, description=f"Added {files_added} files...")
                
                # Add metadata
                progress.update(task, advance=10, description="Adding metadata...")
                metadata = {
                    "created_by": "ncp-sdk",
                    "sdk_version": "0.1.0", 
                    "files_count": files_added,
                    "package_version": "1.0"
                }
                package_zip.writestr("metadata.json", json.dumps(metadata, indent=2))
                
                progress.update(task, completed=100, description="Package created!")
        
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to create package: {e}")
            return
    
    # Display results
    package_size = output_path.stat().st_size
    console.print(f"[green]✓ Package created successfully![/green]")
    console.print(f"Package: {output_path}")
    console.print(f"Size: {package_size:,} bytes")
    console.print(f"[cyan]Next steps:[/cyan]")
    console.print(f"  ncp validate {output_path}")
    console.print(f"  ncp deploy {output_path}")


def create_package_manifest(project_path: Path, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create package manifest from project configuration."""
    
    project_config = config_data.get('project', {})
    
    manifest = {
        "name": project_config.get('name', 'unnamed-project'),
        "version": project_config.get('version', '0.1.0'),
        "description": project_config.get('description', ''),
        "author": project_config.get('author', ''),
        "license": project_config.get('license', ''),
        "agents": [],
        "tools": [],
        "dependencies": []
    }
    
    # Load dependencies from requirements.txt
    requirements_file = project_path / "requirements.txt"
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r') as f:
                dependencies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencies.append(line)
                manifest["dependencies"] = dependencies
        except Exception:
            pass
    
    # Extract agent and tool information from config
    agents_config = config_data.get('agents', {})
    tools_config = config_data.get('tools', {})
    
    for agent_name, agent_path in agents_config.items():
        manifest["agents"].append({
            "name": agent_name,
            "module_path": agent_path
        })
    
    for tool_name, tool_path in tools_config.items():
        manifest["tools"].append({
            "name": tool_name,
            "module_path": tool_path
        })
    
    # Add deployment configuration if present
    deployment_config = config_data.get('deployment', {})
    if deployment_config:
        manifest["deployment"] = deployment_config
    
    return manifest


def should_exclude(file_path: Path, exclude_patterns: set) -> bool:
    """Check if a file should be excluded from the package."""
    
    file_str = str(file_path)
    
    for pattern in exclude_patterns:
        # Simple pattern matching
        if pattern in file_str:
            return True
        
        # Check if any part of the path matches
        for part in file_path.parts:
            if pattern == part:
                return True
            
        # Simple wildcard support
        if pattern.startswith('*.'):
            extension = pattern[1:]
            if file_str.endswith(extension):
                return True
    
    return False