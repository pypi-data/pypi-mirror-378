"""NCP CLI playground command for interactive agent chat."""

import uuid
import json
import sys
import re
import requests
import urllib3
from typing import Optional
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()


@click.command()
@click.argument('agent_id')
@click.option('--platform', default="https://0.0.0.0:9001", help='NCP platform URL')
@click.option('--no-stream', is_flag=True, help='Disable streaming responses')
@click.option('--conversation-id', help='Continue existing conversation')
@click.option('--list-conversations', is_flag=True, help='List existing conversations')
def playground(agent_id: str, platform: str, no_stream: bool, conversation_id: Optional[str], list_conversations: bool):
    """Interactive playground for chatting with deployed agents.
    
    Provides an Ollama-like interactive chat interface with:
    - Streaming responses (like typing)
    - Conversation history 
    - Multi-turn conversations
    - Easy agent testing
    
    AGENT_ID: The deployed agent ID to chat with
    
    Examples:
        ncp playground abc123 --platform https://your-ncp.com
        ncp playground abc123 --conversation-id conv456  # Continue chat
        ncp playground abc123 --list-conversations      # Show history
    """
    
    if list_conversations:
        # TODO: Implement list conversations endpoint
        console.print("[yellow]List conversations feature coming soon![/yellow]")
        return
    
    # Verify agent exists
    try:
        agent_info = get_agent_info(platform, agent_id)
        if not agent_info:
            console.print(f"[red]Error:[/red] Agent {agent_id} not found")
            return
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to connect to platform: {e}")
        return
    
    # Start playground session
    start_playground_session(platform, agent_id, agent_info, conversation_id, not no_stream)


def get_agent_info(platform: str, agent_id: str) -> Optional[dict]:
    """Get agent information from the platform."""
    try:
        url = f"{platform.rstrip('/')}/api/v1/agents/{agent_id}"
        response = requests.get(url, verify=False, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")


def start_playground_session(platform: str, agent_id: str, agent_info: dict, conversation_id: Optional[str], stream: bool):
    """Start the interactive playground session."""
    
    # Display welcome message
    console.print(Panel.fit(
        f"[bold green]NCP Agent Playground[/bold green]\n\n"
        f"[cyan]Agent:[/cyan] {agent_info['name']}\n"
        f"[cyan]Description:[/cyan] {agent_info['description']}\n"
        f"[cyan]Tools:[/cyan] {len(agent_info.get('tools', []))} available\n"
        f"[cyan]Version:[/cyan] {agent_info.get('version', 'Unknown')}\n\n"
        f"[dim]Type your message and press Enter to chat.\n"
        f"Use /help for commands, /quit to exit.[/dim]",
        title="Welcome",
        border_style="blue"
    ))
    
    current_conversation_id = conversation_id
    message_count = 0
    
    try:
        while True:
            # Get user input
            try:
                user_input = Prompt.ask(f"\n[bold blue]You[/bold blue]", default="").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.startswith('/'):
                if user_input == '/quit' or user_input == '/exit':
                    break
                elif user_input == '/help':
                    show_help()
                    continue
                elif user_input == '/clear':
                    console.clear()
                    continue
                elif user_input == '/info':
                    show_agent_info(agent_info)
                    continue
                elif user_input == '/new':
                    current_conversation_id = None
                    message_count = 0
                    console.print("[green]Started new conversation[/green]")
                    continue
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    continue
            
            # Send message to agent
            try:
                response_text, current_conversation_id, message_count = send_message(
                    platform, agent_id, user_input, current_conversation_id, stream, agent_info['name']
                )
                
                # For streaming, the response is already displayed during streaming
                # For non-streaming, we need to display it here
                if response_text and not stream:
                    console.print(f"\n[bold green]{agent_info['name']}[/bold green]")
                    console.print(Markdown(response_text))
                    
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {e}")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")


def send_message(platform: str, agent_id: str, message: str, conversation_id: Optional[str], stream: bool, agent_name: str = "Agent") -> tuple:
    """Send message to agent and get response."""
    
    url = f"{platform.rstrip('/')}/api/v1/agents/{agent_id}/playground"
    
    payload = {
        "message": message,
        "stream": stream
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        if stream:
            return handle_streaming_response(url, payload, agent_name)
        else:
            return handle_regular_response(url, payload)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")


def handle_streaming_response(url: str, payload: dict, agent_name: str = "Agent") -> tuple:
    """Handle streaming response from the agent."""
    
    response = requests.post(
        url,
        json=payload,
        headers={"Accept": "text/plain"},
        stream=True,
        verify=False,
        timeout=60
    )
    
    if response.status_code != 200:
        error_text = response.text
        try:
            error_data = response.json()
            error_text = error_data.get('detail', error_text)
        except:
            pass
        raise Exception(f"HTTP {response.status_code}: {error_text}")
    
    # Stream the response
    response_text = ""
    conversation_id = None
    message_count = 0
    
    # Show agent name once at the start of streaming
    console.print(f"\n[bold green]{agent_name}[/bold green]")
    
    with Live(console=console, refresh_per_second=10) as live:
        display_text = Text()
        
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    try:
                        data = json.loads(data_str)

                        if 'chunk' in data:
                            chunk = data['chunk']
                            response_text += chunk

                            # Format the entire response_text
                            display_text = format_tool_calls(response_text)
                            live.update(display_text)

                        elif 'tool_call' in data:
                            # Handle specific tool call messages
                            tool_call_msg = data['tool_call']
                            tool_display = Text()
                            tool_display.append(tool_call_msg, style="bold cyan")
                            tool_display.append("\n")

                            # Add to current display
                            current_display = format_tool_calls(response_text)
                            current_display.append(tool_display)
                            live.update(current_display)

                        elif 'status' in data:
                            # Handle tool execution status messages
                            status_msg = data['status']
                            if 'tool' in status_msg.lower() or 'executing' in status_msg.lower():
                                # Show tool execution status with special formatting
                                status_display = Text()
                                status_display.append("🔧 ", style="bold yellow")
                                status_display.append(status_msg, style="dim cyan")
                                status_display.append("\n")

                                # Add to current display
                                current_display = format_tool_calls(response_text)
                                current_display.append(status_display)
                                live.update(current_display)

                        elif 'done' in data and data['done']:
                            conversation_id = data.get('conversation_id')
                            message_count = data.get('message_count', 0)
                            break

                        elif 'error' in data:
                            raise Exception(data['error'])
                            
                    except json.JSONDecodeError:
                        continue
                        
        except KeyboardInterrupt:
            console.print("\n[yellow]Response interrupted[/yellow]")
            
    return response_text, conversation_id, message_count


def format_tool_calls(text: str) -> Text:
    """Format tool calls in the text for better display."""
    formatted = Text()
    
    # Pattern to match tool calls in JSON format - make it more flexible
    tool_call_pattern = r'\{"function_name":\s*"([^"]+)",\s*"arguments":\s*(\{.*?\})\}'
    
    # Check if text contains a tool call
    if re.search(tool_call_pattern, text):
        last_end = 0
        for match in re.finditer(tool_call_pattern, text):
            # Add text before the tool call normally
            if match.start() > last_end:
                formatted.append(text[last_end:match.start()])
            
            # Format the tool call nicely
            function_name = match.group(1)
            arguments_str = match.group(2)
            
            try:
                arguments = json.loads(arguments_str)
                # Format as a nice tool call display
                formatted.append("\n")
                formatted.append("🔧 ", style="bold yellow")
                formatted.append(f"Calling {function_name}(", style="bold cyan")
                
                # Format arguments nicely
                arg_parts = []
                for key, value in arguments.items():
                    if isinstance(value, str):
                        arg_parts.append(f'{key}="{value}"')
                    else:
                        arg_parts.append(f'{key}={value}')
                formatted.append(", ".join(arg_parts), style="cyan")
                formatted.append(")", style="bold cyan")
                formatted.append("\n\n")
                
            except json.JSONDecodeError:
                # If JSON parsing fails, show the raw tool call
                formatted.append(text[match.start():match.end()], style="dim")
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            formatted.append(text[last_end:])
    else:
        # No tool calls found, return text as-is
        formatted.append(text)
    
    return formatted


def handle_regular_response(url: str, payload: dict) -> tuple:
    """Handle regular (non-streaming) response from the agent."""
    
    response = requests.post(
        url,
        json=payload,
        verify=False,
        timeout=60
    )
    
    if response.status_code != 200:
        error_text = response.text
        try:
            error_data = response.json()
            error_text = error_data.get('detail', error_text)
        except:
            pass
        raise Exception(f"HTTP {response.status_code}: {error_text}")
    
    data = response.json()
    return data['response'], data['conversation_id'], data['message_count']


def show_help():
    """Show help information."""
    help_table = Table(title="Playground Commands", show_header=True, header_style="bold magenta")
    help_table.add_column("Command", style="cyan", width=12)
    help_table.add_column("Description", style="white")
    
    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/quit, /exit", "Exit the playground")
    help_table.add_row("/clear", "Clear the screen")
    help_table.add_row("/info", "Show agent information")
    help_table.add_row("/new", "Start a new conversation")
    
    console.print(help_table)


def show_agent_info(agent_info: dict):
    """Show detailed agent information."""
    info_table = Table(title="Agent Information", show_header=True, header_style="bold magenta")
    info_table.add_column("Property", style="cyan", width=15)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Name", agent_info.get('name', 'Unknown'))
    info_table.add_row("Description", agent_info.get('description', 'No description'))
    info_table.add_row("Version", agent_info.get('version', 'Unknown'))
    info_table.add_row("Status", agent_info.get('status', 'Unknown'))
    info_table.add_row("Tools", str(len(agent_info.get('tools', []))))
    info_table.add_row("Created", agent_info.get('created_at', 'Unknown'))
    
    if agent_info.get('tools'):
        tools_str = ', '.join(agent_info['tools'])
        info_table.add_row("Tool Names", tools_str)
    
    console.print(info_table)