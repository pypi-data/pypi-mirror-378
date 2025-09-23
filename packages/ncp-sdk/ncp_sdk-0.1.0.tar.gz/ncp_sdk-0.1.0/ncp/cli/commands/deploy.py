"""NCP CLI deploy command."""

import requests
from pathlib import Path
from typing import Dict, Any
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
import urllib3
import toml

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()


@click.command()
@click.argument('package_path', type=click.Path(exists=True))
@click.option('--platform', help='NCP platform URL')
@click.option('--api-key', help='API key for authentication')
@click.option('--project-id', help='Target project ID') 
@click.option('--environment', type=click.Choice(['dev', 'staging', 'prod']), default='dev', help='Deployment environment')
@click.option('--timeout', default=300, help='Deployment timeout in seconds')
def deploy(package_path: str, platform: str, api_key: str, project_id: str, environment: str, timeout: int):
    """Deploy an NCP package to the platform.
    
    Uploads and deploys a .ncp package file to an NCP platform instance.
    The platform will validate, install, and activate the agents and tools.
    
    PACKAGE_PATH: Path to the .ncp package file to deploy
    """
    package_file = Path(package_path)
    
    if not package_file.exists():
        console.print(f"[red]Error:[/red] Package file not found: {package_path}")
        return
    
    if not package_file.suffix == '.ncp':
        console.print(f"[red]Error:[/red] Invalid package file. Expected .ncp file, got: {package_file.suffix}")
        return
    
    # Load config from ncp.toml if available
    config_data = load_config()
    
    # Get required parameters if not provided
    if not platform:
        # Try to get from config first
        deployment_config = config_data.get('deployment', {})
        platform_url = deployment_config.get('platform_url')
        if platform_url:
            platform = platform_url
        else:
            platform = Prompt.ask("NCP Platform URL", default="http://localhost:8000")
    
    
    if not api_key:
        api_key = Prompt.ask("API Key", password=True, default="demo-key")
    
    console.print(f"[blue]Deploying package to NCP platform...[/blue]")
    console.print(f"Package: {package_file}")
    console.print(f"Platform: {platform}")
    console.print(f"Environment: {environment}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        try:
            # Upload package
            task1 = progress.add_task("Uploading package...", total=1)
            upload_result = upload_package(package_file, platform, api_key, project_id, environment, timeout)
            
            if not upload_result['success']:
                console.print(f"[red]Upload failed:[/red] {upload_result['error']}")
                return
            
            progress.update(task1, completed=1)
            deployment_id = upload_result['deployment_id']
            agent_name = upload_result.get('agent_name', 'Unknown')
            
            # Monitor deployment
            task2 = progress.add_task("Verifying deployment...", total=1)
            deployment_result = monitor_deployment(deployment_id, platform, api_key, timeout)
            
            if deployment_result['success']:
                progress.update(task2, completed=1)
                console.print(f"\\n[green]✓ Deployment successful![/green]")
                console.print(f"Agent ID: {deployment_id}")
                console.print(f"Agent Name: {agent_name}")
                console.print(f"Status: {deployment_result['status']}")
                
                # Display deployed resources
                if 'resources' in deployment_result:
                    console.print("[cyan]Deployed Resources:[/cyan]")
                    for resource in deployment_result['resources']:
                        console.print(f"  - {resource['type']}: {resource['name']}")
                
                # Display access information
                if 'endpoints' in deployment_result:
                    console.print("[cyan]Access Endpoints:[/cyan]")
                    for endpoint in deployment_result['endpoints']:
                        console.print(f"  - {endpoint}")
            else:
                progress.update(task2, completed=1)
                console.print(f"[red]✗ Deployment failed![/red]")
                console.print(f"Error: {deployment_result['error']}")
                
                # Show deployment logs if available
                if 'logs' in deployment_result:
                    console.print("[yellow]Deployment Logs:[/yellow]")
                    for log_line in deployment_result['logs']:
                        console.print(f"  {log_line}")
        
        except KeyboardInterrupt:
            console.print("[yellow]Deployment cancelled by user[/yellow]")
            return
        except Exception as e:
            console.print(f"[red]Deployment failed:[/red] {e}")
            return


def upload_package(package_file: Path, platform: str, api_key: str, project_id: str, environment: str, timeout: int) -> Dict[str, Any]:
    """Upload package to NCP platform."""
    
    try:
        # Prepare upload request - use our new agents API endpoint
        url = f"{platform.rstrip('/')}/api/v1/agents/deploy"
        
        # For now, we'll skip authentication since it's for testing
        # In production, you'd use the api_key for authentication
        headers = {}
        
        # Upload file
        with open(package_file, 'rb') as f:
            files = {'package': (package_file.name, f, 'application/octet-stream')}
            
            response = requests.post(
                url, 
                headers=headers,
                files=files,
                timeout=timeout,
                verify=False  # Skip SSL certificate verification for self-signed certs
            )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'deployment_id': result.get('id'),  # Our API returns agent id
                'agent_id': result.get('id'),
                'agent_name': result.get('name'),
                'status': 'completed'  # Our deployment is immediate
            }
        else:
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', response.text)
            except:
                error_detail = response.text
            
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {error_detail}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Network error: {e}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Upload error: {e}"
        }


def monitor_deployment(deployment_id: str, platform: str, api_key: str, timeout: int) -> Dict[str, Any]:
    """Monitor deployment progress."""
    
    try:
        # Since our deployment is immediate, we just check if the agent exists
        url = f"{platform.rstrip('/')}/api/v1/agents/{deployment_id}"
        headers = {}
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'status': 'completed',
                'resources': [
                    {
                        'type': 'Agent',
                        'name': result.get('name'),
                        'id': result.get('id'),
                        'tools': len(result.get('tools', []))
                    }
                ],
                'endpoints': [
                    f"{platform}/api/v1/agents/{deployment_id}/execute"
                ]
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'error': 'Agent not found after deployment'
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Monitoring error: {e}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Monitoring error: {e}"
        }


def load_config() -> Dict[str, Any]:
    """Load configuration from ncp.toml if it exists."""
    config_path = Path.cwd() / 'ncp.toml'
    
    if config_path.exists():
        try:
            return toml.load(config_path)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load ncp.toml: {e}[/yellow]")
            return {}
    
    return {}