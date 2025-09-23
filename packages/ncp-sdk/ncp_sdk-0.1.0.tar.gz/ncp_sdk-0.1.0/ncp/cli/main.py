"""Main CLI entry point for NCP SDK."""

import click
from rich.console import Console
from rich.text import Text

from .commands import init, package, validate, deploy, setup, build, playground

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="ncp")
@click.pass_context
def main(ctx):
    """NCP SDK - Network Copilot Protocol for AI agent development.
    
    The NCP SDK enables developers to create and deploy custom agents and tools
    on the NCP platform with full type safety and development support.
    """
    # Ensure ctx.obj is a dict
    ctx.ensure_object(dict)
    
    # Display welcome message for help
    if ctx.invoked_subcommand is None:
        console.print(Text("NCP SDK", style="bold blue"))
        console.print("Network Copilot for AI agent development\n")
        console.print("Use 'ncp --help' to see available commands.")


# Register command groups
main.add_command(init)
main.add_command(setup)
main.add_command(build)  
main.add_command(package)
main.add_command(validate)
main.add_command(deploy)
main.add_command(playground)


if __name__ == "__main__":
    main()