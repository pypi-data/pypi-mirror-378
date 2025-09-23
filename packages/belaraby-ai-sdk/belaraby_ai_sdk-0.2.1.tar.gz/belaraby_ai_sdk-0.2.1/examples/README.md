# BelArabyAI SDK Examples

This directory contains comprehensive examples demonstrating how to use the BelArabyAI SDK for various use cases and scenarios. These examples are designed to help you understand the SDK's capabilities and provide practical implementations for common AI automation tasks.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Core Examples](#core-examples)
- [Advanced Examples](#advanced-examples)
- [Tool-Specific Examples](#tool-specific-examples)
- [Utility Examples](#utility-examples)
- [Running Examples](#running-examples)
- [Example Categories](#example-categories)
- [Customization](#customization)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Contributing Examples](#contributing-examples)

## Prerequisites

1. Install the SDK:
   ```bash
   pip install belaraby-ai-sdk
   ```

2. Get your API key from [https://belaraby.ai/settings/api-keys](https://belaraby.ai/settings/api-keys)

3. Set your API key as an environment variable:
   ```bash
   export BELARABYAI_API_KEY="your-api-key-here"
   ```

## Core Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the fundamental SDK operations:
- Initializing the client
- Creating an agent with built-in tools
- Creating conversation threads
- Running agents and streaming responses

```bash
python basic_usage.py
```

### 2. MCP Tools (`mcp_tools_example.py`)

Shows how to use custom MCP (Model Context Protocol) tools:
- Creating and initializing MCP tools
- Using custom tools with agents
- Handling tool initialization errors

```bash
python mcp_tools_example.py
```

**Note**: This example requires `fastmcp` to be installed:
```bash
pip install fastmcp
```

### 3. Conversation Management (`conversation_management.py`)

Demonstrates advanced conversation management:
- Managing conversation threads
- Adding and deleting messages
- Retrieving conversation history
- Handling multiple agent runs
- Updating agent configurations

```bash
python conversation_management.py
```

### 4. Error Handling (`error_handling.py`)

Shows how to handle various error conditions:
- Invalid API keys
- Missing dependencies
- Non-existent resources
- Input validation
- Graceful error recovery

```bash
python error_handling.py
```

## Advanced Examples

### 5. Advanced Agent Management (`advanced_agent_management.py`)

Demonstrates sophisticated agent management:
- Creating multiple specialized agents
- Managing agent configurations
- Switching between different agents
- Agent lifecycle management
- Bulk operations on agents

```bash
python advanced_agent_management.py
```

### 6. Development Workflow (`development_workflow_example.py`)

Complete development workflow demonstration:
- Project setup and initialization
- Code development and testing
- Application deployment
- Service exposure and monitoring
- Continuous integration practices

```bash
python development_workflow_example.py
```

## Tool-Specific Examples

### 7. File Operations (`file_operations_example.py`)

Comprehensive file operations using SB_FILES_TOOL:
- Creating files and directories
- Reading and writing files
- Searching files
- File organization
- Batch operations

```bash
python file_operations_example.py
```

### 8. Web Search (`web_search_example.py`)

Advanced web search capabilities:
- Basic web searches
- Research tasks
- Information gathering
- Source verification
- Data extraction and summarization

```bash
python web_search_example.py
```

### 9. Image Processing (`image_processing_example.py`)

Comprehensive image processing capabilities:
- Image analysis and understanding
- Image editing and manipulation
- Batch processing
- Image optimization
- Visual content extraction

```bash
python image_processing_example.py
```

### 10. Data Analysis (`data_analysis_example.py`)

Advanced data analysis capabilities:
- Data collection and processing
- Statistical analysis
- Data visualization
- Pattern recognition
- Report generation

```bash
python data_analysis_example.py
```

### 11. Integration (`integration_example.py`)

Comprehensive integration capabilities:
- Database integration
- External API integration
- Cloud service integration
- Third-party tool integration
- Custom service integration

```bash
python integration_example.py
```

## Utility Examples

### 12. Local Key-Value Store (`kv.py`)

A utility module for persistent storage of agent and thread IDs:

```python
from examples.kv import kv

# Store agent ID
kv.set("my_agent_id", "agent-123")

# Retrieve agent ID
agent_id = kv.get("my_agent_id")

# Delete stored data
kv.delete("my_agent_id")
```

**Features:**
- Persistent JSON-based storage
- Simple key-value interface
- Automatic file management
- Thread-safe operations

### 13. MCP Server (`mcp_server.py`)

A sample MCP server implementation using FastMCP:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="Kortix")

@mcp.tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is windy."

@mcp.tool
async def get_wind_direction(city: str) -> str:
    return f"The wind direction in {city} is from the north."
```

**Features:**
- FastMCP framework integration
- Custom tool definitions
- Async/await support
- Easy deployment

### 14. Demo Basic Usage (`demo_basic_usage.py`)

A demonstration script that showcases SDK capabilities without requiring an API key:

```bash
python demo_basic_usage.py
```

**Features:**
- No API key required
- Interactive demonstration
- Code examples and explanations
- Perfect for learning and testing

## Running All Examples

To run all examples in sequence:

```bash
# Make sure you have your API key set
export BELARABYAI_API_KEY="your-api-key-here"

# Run utility examples first (no API key needed)
python kv.py
python mcp_server.py
python demo_basic_usage.py

# Run core examples
python basic_usage.py
python conversation_management.py
python error_handling.py

# Run advanced examples
python advanced_agent_management.py
python development_workflow_example.py

# Run tool-specific examples
python file_operations_example.py
python web_search_example.py
python image_processing_example.py
python data_analysis_example.py
python integration_example.py
python mcp_tools_example.py
```

## Example Categories

### 🚀 Getting Started
- **basic_usage.py** - Start here to learn the fundamentals
- **error_handling.py** - Learn how to handle errors gracefully

### 🔧 Advanced Features
- **advanced_agent_management.py** - Multiple agents and complex workflows
- **conversation_management.py** - Advanced conversation handling
- **development_workflow_example.py** - Complete development lifecycle

### 🛠️ Tool-Specific Examples
- **file_operations_example.py** - File and directory management
- **web_search_example.py** - Web research and information gathering
- **image_processing_example.py** - Image analysis and manipulation
- **data_analysis_example.py** - Data processing and analysis
- **integration_example.py** - External service integration
- **mcp_tools_example.py** - Custom MCP tool integration

## Customization

Feel free to modify these examples to suit your needs:

1. **Change the system prompts** to customize agent behavior
2. **Add different tools** based on your requirements
3. **Modify conversation flows** to match your use case
4. **Add error handling** specific to your application
5. **Combine multiple examples** for complex workflows
6. **Create your own specialized agents** for specific domains

## Best Practices

### Agent Design
- Use clear, specific system prompts
- Choose appropriate tools for your use case
- Test agents with various inputs
- Monitor agent performance and adjust

### Conversation Management
- Keep conversations focused and organized
- Use meaningful thread names
- Clean up old conversations regularly
- Handle errors gracefully

### Tool Usage
- Understand tool capabilities and limitations
- Use tools efficiently and appropriately
- Handle tool errors and edge cases
- Combine tools for complex workflows

## Troubleshooting

### Common Issues

1. **ImportError for fastmcp**: Install it with `pip install fastmcp`
2. **API key not found**: Make sure `BELARABYAI_API_KEY` is set correctly
3. **Connection errors**: Check your internet connection and API key validity
4. **Tool initialization errors**: Ensure your MCP server is running and accessible
5. **Agent creation failures**: Check your system prompt and tool configuration
6. **Thread management issues**: Verify thread IDs and permissions

### Performance Tips

1. **Use appropriate tools**: Don't use unnecessary tools for simple tasks
2. **Optimize system prompts**: Be specific and concise
3. **Manage conversations**: Clean up old threads regularly
4. **Handle errors**: Implement proper error handling and recovery
5. **Monitor usage**: Track API usage and costs

### Getting Help

- **💬 Discord Community**: [https://discord.gg/qAncfHmYUm](https://discord.gg/qAncfHmYUm) - Join our Discord for real-time help and discussions
- Check the [main README](../README.md) for detailed documentation
- Visit [https://docs.belaraby.ai](https://docs.belaraby.ai) for API documentation
- Open an issue on [GitHub](https://github.com/rhkiswani/BelArabyAI-python-sdk/issues) for support
- Join the community discussions for tips and best practices

## Contributing Examples

We welcome contributions of new examples! When contributing:

1. **Follow the existing structure** and naming conventions
2. **Include comprehensive documentation** and comments
3. **Test your examples** thoroughly
4. **Update this README** to include your new example
5. **Provide clear use cases** and scenarios

## License

These examples are provided under the same MIT License as the main SDK.
