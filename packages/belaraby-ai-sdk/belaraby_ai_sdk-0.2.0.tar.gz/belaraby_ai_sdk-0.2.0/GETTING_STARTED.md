# Getting Started with BelArabyAI SDK

This guide will help you get up and running with the BelArabyAI SDK quickly and efficiently.

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Your First Agent](#your-first-agent)
- [Basic Operations](#basic-operations)
- [Next Steps](#next-steps)
- [Common Issues](#common-issues)

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- BelArabyAI account and API key

### Install the SDK

```bash
# Using pip
pip install belaraby-ai-sdk

# Using uv (recommended)
uv add belaraby-ai-sdk
```

### Verify Installation

```python
import belaraby_ai_sdk
print(f"BelArabyAI SDK version: {belaraby_ai_sdk.__version__}")
```

## Authentication

### Get Your API Key

1. Visit [https://belaraby.ai/settings/api-keys](https://belaraby.ai/settings/api-keys)
2. Create a new API key
3. Copy the key (you won't be able to see it again)

### Set Up Authentication

#### Option 1: Environment Variable (Recommended)

```bash
export BELARABYAI_API_KEY="your-api-key-here"
```

#### Option 2: Direct in Code

```python
from ba.ba import BASdk

client = BASdk(api_key="your-api-key-here")
```

## Your First Agent

### Step 1: Create a Simple Agent

```python
import asyncio
import os
from ba.ba import BASdk
from ba.tools import AgentPressTools

async def main():
    # Initialize the client
    client = BASdk(api_key=os.getenv("BELARABYAI_API_KEY"))
    
    # Create an agent
    agent = await client.Agent.create(
        name="My First Agent",
        system_prompt="You are a helpful assistant that can answer questions and help with tasks.",
        mcp_tools=[AgentPressTools.WEB_SEARCH_TOOL],
        allowed_tools=["web_search_tool"]
    )
    
    print(f"✅ Agent created with ID: {agent._agent_id}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Create a Conversation Thread

```python
# Create a thread for the conversation
thread = await client.Thread.create("My First Conversation")
print(f"✅ Thread created with ID: {thread._thread_id}")
```

### Step 3: Run the Agent

```python
# Run the agent with a message
run = await agent.run("What's the weather like today?", thread)

# Stream the response
stream = await run.get_stream()
async for chunk in stream:
    print(chunk, end="")
print()  # New line after response
```

### Complete Example

```python
import asyncio
import os
from ba.ba import BASdk
from ba.tools import AgentPressTools

async def main():
    # Initialize the client
    client = BASdk(api_key=os.getenv("BELARABYAI_API_KEY"))
    
    try:
        # Create an agent
        agent = await client.Agent.create(
            name="My First Agent",
            system_prompt="You are a helpful assistant that can answer questions and help with tasks.",
            mcp_tools=[AgentPressTools.WEB_SEARCH_TOOL],
            allowed_tools=["web_search_tool"]
        )
        print(f"✅ Agent created with ID: {agent._agent_id}")
        
        # Create a thread
        thread = await client.Thread.create("My First Conversation")
        print(f"✅ Thread created with ID: {thread._thread_id}")
        
        # Run the agent
        run = await agent.run("What's the weather like today?", thread)
        
        # Stream the response
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Basic Operations

### Available Tools

The SDK provides several built-in tools:

- **SB_FILES_TOOL**: File system operations
- **WEB_SEARCH_TOOL**: Web search capabilities
- **SB_VISION_TOOL**: Image analysis
- **SB_SHELL_TOOL**: Command execution
- **BROWSER_TOOL**: Web browsing
- **DATA_PROVIDERS_TOOL**: Data access
- **SB_IMAGE_EDIT_TOOL**: Image editing
- **SB_DEPLOY_TOOL**: Application deployment
- **SB_EXPOSE_TOOL**: Service exposure

### Using Multiple Tools

```python
agent = await client.Agent.create(
    name="Multi-Tool Agent",
    system_prompt="You are a versatile assistant with access to multiple tools.",
    mcp_tools=[
        AgentPressTools.SB_FILES_TOOL,
        AgentPressTools.WEB_SEARCH_TOOL,
        AgentPressTools.SB_VISION_TOOL
    ],
    allowed_tools=["sb_files_tool", "web_search_tool", "sb_vision_tool"]
)
```

### Managing Conversations

```python
# Add multiple messages to a thread
await thread.add_message("Hello!")
await thread.add_message("How are you?")

# Get all messages
messages = await thread.get_messages()
for message in messages:
    print(f"Message: {message.content}")

# Get agent runs
runs = await thread.get_agent_runs()
for run in runs:
    print(f"Run ID: {run.run_id}")
```

### Error Handling

```python
try:
    agent = await client.Agent.create(
        name="My Agent",
        system_prompt="You are helpful.",
        mcp_tools=[AgentPressTools.SB_FILES_TOOL]
    )
except Exception as e:
    error_str = str(e).lower()
    if "agent_limit_exceeded" in error_str:
        print("💡 You've reached the agent limit for your current plan.")
    elif "authentication required" in error_str:
        print("💡 Please check your API key.")
    else:
        print(f"❌ Failed to create agent: {e}")
```

## Next Steps

### Explore Examples

Check out the comprehensive examples in the `examples/` directory:

- **[basic_usage.py](examples/basic_usage.py)** - Start here
- **[file_operations_example.py](examples/file_operations_example.py)** - File management
- **[web_search_example.py](examples/web_search_example.py)** - Web research
- **[data_analysis_example.py](examples/data_analysis_example.py)** - Data processing
- **[advanced_agent_management.py](examples/advanced_agent_management.py)** - Multiple agents

### Read Documentation

- **[README.md](README.md)** - Complete SDK overview
- **[API_REFERENCE.md](API_REFERENCE.md)** - Detailed API documentation
- **[examples/README.md](examples/README.md)** - Example guide

### Join the Community

- **💬 Discord**: [https://discord.gg/qAncfHmYUm](https://discord.gg/qAncfHmYUm) - Join our Discord community for real-time discussions, help, and updates
- **GitHub**: [https://github.com/rhkiswani/BelArabyAI-python-sdk](https://github.com/rhkiswani/BelArabyAI-python-sdk)
- **Discussions**: [https://github.com/rhkiswani/BelArabyAI-python-sdk/discussions](https://github.com/rhkiswani/BelArabyAI-python-sdk/discussions)
- **Issues**: [https://github.com/rhkiswani/BelArabyAI-python-sdk/issues](https://github.com/rhkiswani/BelArabyAI-python-sdk/issues)

## Common Issues

### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'belaraby_ai_sdk'`

**Solution**: 
```bash
pip install belaraby-ai-sdk
```

### 2. Authentication Errors

**Problem**: `Authentication required. Please check your API key.`

**Solution**: 
- Verify your API key is correct
- Check that `BELARABYAI_API_KEY` environment variable is set
- Ensure your API key is active

### 3. Agent Limit Exceeded

**Problem**: `Maximum of 2 agents allowed for your current plan.`

**Solution**: 
- Upgrade your plan or delete unused agents
- Check your current plan limits

### 4. Model Access Issues

**Problem**: `Your current subscription plan does not include access to anthropic/claude-sonnet-4-20250514`

**Solution**: 
- Upgrade your plan to access the model
- Or configure agents to use available models

### 5. Tool Initialization Errors

**Problem**: `Client failed to connect: All connection attempts failed`

**Solution**: 
- Ensure your MCP server is running
- Check the endpoint URL is correct
- Verify network connectivity

## Getting Help

### Debug Mode

Enable debug logging for detailed error information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your BelArabyAI code here
```

### Support Channels

1. **Check the examples** - Most common use cases are covered
2. **Read the documentation** - Comprehensive guides available
3. **Enable debug logging** - Get detailed error information
4. **Open an issue** - Get help from the community
5. **Join discussions** - Share tips and best practices

### Best Practices

1. **Start simple** - Begin with basic examples
2. **Handle errors** - Always wrap operations in try-catch blocks
3. **Use environment variables** - Never hardcode API keys
4. **Test thoroughly** - Validate your code before production
5. **Monitor usage** - Track API usage and costs

## What's Next?

Now that you have the basics down, explore:

- **[Advanced Agent Management](examples/advanced_agent_management.py)** - Multiple agents
- **[Custom MCP Tools](examples/mcp_tools_example.py)** - Build your own tools
- **[Integration Examples](examples/integration_example.py)** - Connect with external services
- **[Development Workflows](examples/development_workflow_example.py)** - Complete development pipelines

Happy coding with BelArabyAI! 🚀
