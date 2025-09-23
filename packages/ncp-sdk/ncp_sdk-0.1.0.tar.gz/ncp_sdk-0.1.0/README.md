# NCP SDK

**Network Copilot SDK for AI agent development**

The NCP SDK enables developers to create and deploy custom agents and tools on the NCP platform with full type safety and development support.

## Features

- 🤖 **Agent Development**: Create sophisticated AI agents with custom tools
- 🔧 **Type Safety**: Full Python type definitions for IDE support  
- 📦 **Easy Packaging**: Package agents for deployment with one command
- 🚀 **Simple Deployment**: Deploy to NCP platform instances
- 🛠️ **CLI Tools**: Complete command-line interface for development workflow
- 🔍 **Validation**: Comprehensive project and package validation

## Quick Start

### Installation

```bash
pip install git+https://github.com/AvizNetworks/ncp-sdk.git
```

### Create a New Project

```bash
# Initialize new project
ncp init my-agent-project
cd my-agent-project
```

### Create Your First Agent

Edit `agents/main_agent.py`:

```python
from ncp import Agent, tool, ModelConfig

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: Sunny, 22°C"

@tool
def calculate_tip(bill: float, percentage: float = 15.0) -> dict:
    """Calculate tip amount and total."""
    tip = bill * (percentage / 100)
    return {
        "bill": bill,
        "tip": tip, 
        "total": bill + tip,
        "percentage": percentage
    }

# Create your agent
my_agent = Agent(
    name="HelperBot",
    description="A helpful assistant with weather and calculation tools",
    instructions="Help users with weather information and calculations. Be friendly and accurate.",
    tools=[get_weather, calculate_tip],
    llm_config=ModelConfig(
        model="gpt-4-turbo",
        api_key="your-api-key-here"
    )
)
```

## CLI Commands

### Project Management

```bash
# Create new project
ncp init my-project
```

### Packaging and Deployment

```bash
# Package project
ncp package . --output my-project.ncp

# Deploy package
ncp deploy my-project.ncp --platform https://ncp.example.com
```

## Development Workflow

1. **Initialize**: `ncp init my-project`
2. **Setup**: `ncp setup --dev` 
3. **Develop**: Edit agents and tools
4. **Validate**: `ncp validate .`
5. **Package**: `ncp package .`
6. **Deploy**: `ncp deploy my-project.ncp`