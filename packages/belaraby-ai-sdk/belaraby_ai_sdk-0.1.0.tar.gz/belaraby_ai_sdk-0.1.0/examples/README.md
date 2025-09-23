# BelArabyAI SDK Examples

This directory contains practical examples demonstrating how to use the BelArabyAI SDK.

## Prerequisites

1. Install the SDK:
   ```bash
   pip install belarabyai
   ```

2. Get your API key from [https://belaraby.ai/settings/api-keys](https://belaraby.ai/settings/api-keys)

3. Set your API key as an environment variable:
   ```bash
   export BELARABYAI_API_KEY="your-api-key-here"
   ```

## Examples

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

## Running All Examples

To run all examples in sequence:

```bash
# Make sure you have your API key set
export BELARABYAI_API_KEY="your-api-key-here"

# Run all examples
python basic_usage.py
python conversation_management.py
python error_handling.py
```

## Customization

Feel free to modify these examples to suit your needs:

1. **Change the system prompts** to customize agent behavior
2. **Add different tools** based on your requirements
3. **Modify conversation flows** to match your use case
4. **Add error handling** specific to your application

## Troubleshooting

### Common Issues

1. **ImportError for fastmcp**: Install it with `pip install fastmcp`
2. **API key not found**: Make sure `BELARABYAI_API_KEY` is set correctly
3. **Connection errors**: Check your internet connection and API key validity
4. **Tool initialization errors**: Ensure your MCP server is running and accessible

### Getting Help

- Check the [main README](../README.md) for detailed documentation
- Visit [https://docs.belaraby.ai](https://docs.belaraby.ai) for API documentation
- Open an issue on [GitHub](https://github.com/belarabyai/belarabyai/issues) for support
