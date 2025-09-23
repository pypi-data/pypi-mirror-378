"""NCP CLI setup command."""

import subprocess
import sys
import os
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.command()
@click.option('--dev', is_flag=True, help='Install development dependencies')
@click.option('--python', default='python', help='Python interpreter to use')
def setup(dev: bool, python: str):
    """Set up the development environment for an NCP project.
    
    This command:
    - Creates a virtual environment (if needed)
    - Installs project dependencies
    - Installs development tools (if --dev flag is used)
    - Validates the project structure
    """
    project_path = Path.cwd()
    
    # Check if we're in an NCP project
    if not (project_path / "ncp.toml").exists():
        console.print("[red]Error:[/red] Not in an NCP project directory.")
        console.print("Run 'ncp init <project_name>' to create a new project.")
        return
    
    console.print("[bold blue]Setting up NCP development environment...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Check for virtual environment
        task1 = progress.add_task("Checking virtual environment...", total=1)
        venv_path = project_path / "venv"
        if not venv_path.exists():
            progress.update(task1, description="Creating virtual environment...")
            try:
                subprocess.run([python, "-m", "venv", "venv"], check=True, cwd=project_path)
                console.print("  [green]✓[/green] Created virtual environment")
            except subprocess.CalledProcessError:
                console.print("  [red]✗[/red] Failed to create virtual environment")
                return
        else:
            console.print("  [green]✓[/green] Virtual environment exists")
        progress.update(task1, completed=1)
        
        # Determine pip command
        pip_cmd = str(venv_path / "bin" / "pip") if os.name != 'nt' else str(venv_path / "Scripts" / "pip.exe")
        
        # Install requirements
        task2 = progress.add_task("Installing dependencies...", total=1)
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], 
                             check=True, cwd=project_path, capture_output=True)
                console.print("  [green]✓[/green] Installed project dependencies")
            except subprocess.CalledProcessError as e:
                console.print(f"  [red]✗[/red] Failed to install dependencies: {e}")
                return
        progress.update(task2, completed=1)
        
        # Install development dependencies
        if dev:
            task3 = progress.add_task("Installing development tools...", total=1)
            dev_packages = [
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0", 
                "black>=23.0.0",
                "isort>=5.12.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0"
            ]
            
            try:
                subprocess.run([pip_cmd, "install"] + dev_packages,
                             check=True, cwd=project_path, capture_output=True)
                console.print("  [green]✓[/green] Installed development tools")
            except subprocess.CalledProcessError as e:
                console.print(f"  [red]✗[/red] Failed to install development tools: {e}")
            progress.update(task3, completed=1)
        
        # Validate project structure
        task4 = progress.add_task("Validating project structure...", total=1)
        validation_errors = validate_project_structure(project_path)
        if not validation_errors:
            console.print("  [green]✓[/green] Project structure is valid")
        else:
            console.print("  [yellow]⚠[/yellow] Project structure issues found:")
            for error in validation_errors:
                console.print(f"    - {error}")
        progress.update(task4, completed=1)
    
    console.print("\\n[bold green]✓ Setup complete![/bold green]")
    console.print("\\n[cyan]Next steps:[/cyan]")
    
    # Provide activation instructions
    if os.name == 'nt':
        console.print("  .\\venv\\Scripts\\activate")
    else:
        console.print("  source venv/bin/activate")
    
    console.print("  # Edit your agents and tools")
    console.print("  ncp validate .")
    
    if dev:
        console.print("\\n[cyan]Development commands:[/cyan]")
        console.print("  black .          # Format code")
        console.print("  isort .          # Sort imports")
        console.print("  flake8 .         # Lint code")
        console.print("  mypy .           # Type check")
        console.print("  pytest           # Run tests")


def validate_project_structure(project_path: Path) -> list:
    """Validate the project structure.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        List of validation errors
    """
    errors = []
    
    required_files = [
        "ncp.toml",
        "requirements.txt",
        "agents/__init__.py",
        "tools/__init__.py"
    ]
    
    for file_path in required_files:
        full_path = project_path / file_path
        if not full_path.exists():
            errors.append(f"Missing required file: {file_path}")
    
    # Check for at least one agent
    agents_dir = project_path / "agents"
    if agents_dir.exists():
        agent_files = [f for f in agents_dir.glob("*.py") if f.name != "__init__.py"]
        if not agent_files:
            errors.append("No agent files found in agents/ directory")
    
    return errors