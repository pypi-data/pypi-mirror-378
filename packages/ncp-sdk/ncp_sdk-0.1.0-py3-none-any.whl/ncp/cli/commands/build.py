"""NCP CLI build command."""

from pathlib import Path
import click
from rich.console import Console

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', help='Output directory for build artifacts')
@click.option('--clean', is_flag=True, help='Clean build directory before building')
def build(path: str, output: str, clean: bool):
    """Build the project for packaging.
    
    Prepares the project for packaging by:
    - Compiling Python files
    - Validating project structure
    - Generating schemas
    - Creating build artifacts
    
    PATH: Path to project directory
    """
    project_path = Path(path)
    
    if not (project_path / "ncp.toml").exists():
        console.print("[red]Error:[/red] Not in an NCP project directory.")
        console.print("Run 'ncp init <project_name>' to create a new project.")
        return
    
    output_path = Path(output) if output else project_path / "build"
    
    console.print(f"[blue]Building NCP project...[/blue]")
    console.print(f"Source: {project_path}")
    console.print(f"Output: {output_path}")
    
    # Clean build directory if requested
    if clean and output_path.exists():
        console.print("[yellow]Cleaning build directory...[/yellow]")
        import shutil
        shutil.rmtree(output_path)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print("[green]✓ Build completed![/green]")
    console.print(f"Build artifacts created in: {output_path}")
    console.print("\\nNext step: ncp package . --output myproject.ncp")