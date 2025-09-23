# BelArabyAI SDK

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![PyPI version](https://badge.fury.io/py/belarabyai.svg)](https://badge.fury.io/py/belarabyai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK that enables you to create, manage, and interact with AI Workers on [BelArabyAI](https://belaraby.ai).

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install belarabyai
```

### From GitHub (Development)

```bash
pip install "belarabyai @ git+https://github.com/rhkiswani/BelArabyAI-python-sdk"
```

Or using uv:

```bash
uv add belarabyai
```

## 🔧 Quick Start

### Basic Usage

```python
import asyncio
from belarabyai import BelArabyAI, AgentPressTools

async def main():
    # Initialize the client
    client = BelArabyAI(api_key="your-api-key")

    # Create an agent with built-in tools
    agent = await client.Agent.create(
        name="My Assistant",
        system_prompt="You are a helpful AI assistant.",
        mcp_tools=[AgentPressTools.SB_FILES_TOOL, AgentPressTools.WEB_SEARCH_TOOL],
        allowed_tools=["sb_files_tool", "web_search_tool"]
    )

    # Create a conversation thread
    thread = await client.Thread.create("My Conversation")

    # Run the agent
    run = await agent.run("Hello, how are you?", thread)

    # Stream the response
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Custom MCP Tools

```python
import asyncio
from belarabyai import BelArabyAI, MCPTools

async def main():
    # Initialize custom MCP tools
    weather_tools = MCPTools(
        endpoint="http://localhost:4000/mcp/",
        name="weather-service",
        allowed_tools=["get_weather", "get_forecast"]
    )
    await weather_tools.initialize()

    # Initialize the client
    client = BelArabyAI(api_key="your-api-key")

    # Create an agent with custom tools
    agent = await client.Agent.create(
        name="Weather Assistant",
        system_prompt="You are a weather assistant that can provide weather information.",
        mcp_tools=[weather_tools],
        allowed_tools=["get_weather", "get_forecast"]
    )

    # Create a conversation thread
    thread = await client.Thread.create()

    # Run the agent
    run = await agent.run("What's the weather like today?", thread)

    # Stream the response
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(main())
```

### Managing Conversations

```python
import asyncio
from belarabyai import BelArabyAI, AgentPressTools

async def main():
    client = BelArabyAI(api_key="your-api-key")

    # Create an agent
    agent = await client.Agent.create(
        name="File Assistant",
        system_prompt="You can help with file operations.",
        mcp_tools=[AgentPressTools.SB_FILES_TOOL]
    )

    # Create a thread
    thread = await client.Thread.create("File Operations")

    # Add multiple messages
    await thread.add_message("Create a new file called 'hello.txt'")
    
    # Run the agent
    run1 = await agent.run("Create a new file called 'hello.txt'", thread)
    
    # Stream the first response
    stream1 = await run1.get_stream()
    async for chunk in stream1:
        print(chunk, end="")
    
    print("\n" + "="*50 + "\n")
    
    # Add another message
    await thread.add_message("Now write 'Hello, World!' to the file")
    
    # Run the agent again
    run2 = await agent.run("Now write 'Hello, World!' to the file", thread)
    
    # Stream the second response
    stream2 = await run2.get_stream()
    async for chunk in stream2:
        print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔑 Environment Setup

1. Get your API key from [https://belaraby.ai/settings/api-keys](https://belaraby.ai/settings/api-keys)
2. Set it as an environment variable:

```bash
export BELARABYAI_API_KEY="your-api-key-here"
```

Or use it directly in your code:

```python
client = BelArabyAI(api_key="your-api-key-here")
```

## 🛠️ Available Tools

### Built-in AgentPress Tools

- `AgentPressTools.SB_FILES_TOOL` - Read, write, and edit files
- `AgentPressTools.SB_SHELL_TOOL` - Execute shell commands
- `AgentPressTools.SB_DEPLOY_TOOL` - Deploy web applications
- `AgentPressTools.SB_EXPOSE_TOOL` - Expose local services to the internet
- `AgentPressTools.SB_VISION_TOOL` - Analyze and understand images
- `AgentPressTools.BROWSER_TOOL` - Browse websites and interact with web pages
- `AgentPressTools.WEB_SEARCH_TOOL` - Search the web for information
- `AgentPressTools.SB_IMAGE_EDIT_TOOL` - Edit and manipulate images
- `AgentPressTools.DATA_PROVIDERS_TOOL` - Access structured data from various providers

### Custom MCP Tools

You can also use custom MCP (Model Context Protocol) tools by providing an HTTP endpoint:

```python
custom_tools = MCPTools(
    endpoint="http://your-mcp-server:4000/mcp/",
    name="your-service",
    allowed_tools=["tool1", "tool2"]  # Optional: filter specific tools
)
await custom_tools.initialize()
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=ba --cov-report=html
```

## 📚 API Reference

### BelArabyAI Client

```python
client = BelArabyAI(api_key="your-key", api_url="https://belaraby.ai")
```

### Agent Management

```python
# Create an agent
agent = await client.Agent.create(
    name="Agent Name",
    system_prompt="System prompt",
    mcp_tools=[...],  # List of tools
    allowed_tools=[...]  # Optional: filter tools
)

# Get an existing agent
agent = await client.Agent.get("agent-id")

# Update an agent
await agent.update(
    name="New Name",
    system_prompt="New prompt",
    mcp_tools=[...],
    allowed_tools=[...]
)
```

### Thread Management

```python
# Create a thread
thread = await client.Thread.create("Thread Name")

# Get an existing thread
thread = await client.Thread.get("thread-id")

# Delete a thread
await client.Thread.delete("thread-id")

# Add a message to thread
message_id = await thread.add_message("Hello!")

# Delete a message
await thread.delete_message("message-id")

# Get all messages
messages = await thread.get_messages()

# Get agent runs
runs = await thread.get_agent_runs()
```

### Agent Execution

```python
# Run an agent
run = await agent.run("Your prompt", thread)

# Stream the response
stream = await run.get_stream()
async for chunk in stream:
    print(chunk, end="")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- Documentation: [https://docs.belaraby.ai](https://docs.belaraby.ai)
- Issues: [https://github.com/belarabyai/belarabyai/issues](https://github.com/belarabyai/belarabyai/issues)
- Email: support@belaraby.ai
