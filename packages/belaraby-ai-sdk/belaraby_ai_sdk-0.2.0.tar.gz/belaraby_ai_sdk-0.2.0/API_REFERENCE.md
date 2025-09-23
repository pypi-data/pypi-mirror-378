# BelArabyAI SDK API Reference

This document provides comprehensive API reference for the BelArabyAI SDK.

## Table of Contents

- [Client Initialization](#client-initialization)
- [Agent Management](#agent-management)
- [Thread Management](#thread-management)
- [Agent Execution](#agent-execution)
- [Tools](#tools)
- [Error Handling](#error-handling)
- [Data Models](#data-models)

## Client Initialization

### BASdk

The main client class for interacting with BelArabyAI services.

```python
from ba.ba import BASdk

client = BASdk(api_key="your-api-key", api_url="https://belaraby.ai")
```

#### Parameters

- `api_key` (str): Your BelArabyAI API key
- `api_url` (str, optional): Base URL for the API (default: "https://belaraby.ai")

#### Properties

- `Agent`: Agent management interface
- `Thread`: Thread management interface

## Agent Management

### Agent Creation

```python
agent = await client.Agent.create(
    name="Agent Name",
    system_prompt="You are a helpful assistant.",
    mcp_tools=[AgentPressTools.SB_FILES_TOOL],
    allowed_tools=["sb_files_tool"]
)
```

#### Parameters

- `name` (str): Name of the agent
- `system_prompt` (str): System prompt defining agent behavior
- `mcp_tools` (list): List of tools to enable
- `allowed_tools` (list, optional): Specific tools to allow

#### Returns

- `Agent`: Agent instance

### Agent Retrieval

```python
agent = await client.Agent.get("agent-id")
```

#### Parameters

- `agent_id` (str): ID of the agent to retrieve

#### Returns

- `Agent`: Agent instance

### Agent Update

```python
await agent.update(
    name="New Name",
    system_prompt="New prompt",
    mcp_tools=[...],
    allowed_tools=[...]
)
```

#### Parameters

- `name` (str, optional): New name for the agent
- `system_prompt` (str, optional): New system prompt
- `mcp_tools` (list, optional): New list of tools
- `allowed_tools` (list, optional): New list of allowed tools

## Thread Management

### Thread Creation

```python
thread = await client.Thread.create("Thread Name")
```

#### Parameters

- `name` (str, optional): Name for the thread

#### Returns

- `Thread`: Thread instance

### Thread Retrieval

```python
thread = await client.Thread.get("thread-id")
```

#### Parameters

- `thread_id` (str): ID of the thread to retrieve

#### Returns

- `Thread`: Thread instance

### Thread Deletion

```python
await client.Thread.delete("thread-id")
```

#### Parameters

- `thread_id` (str): ID of the thread to delete

### Message Management

#### Add Message

```python
message_id = await thread.add_message("Hello!")
```

#### Parameters

- `content` (str): Message content

#### Returns

- `str`: Message ID

#### Delete Message

```python
await thread.delete_message("message-id")
```

#### Parameters

- `message_id` (str): ID of the message to delete

#### Get Messages

```python
messages = await thread.get_messages()
```

#### Returns

- `list`: List of messages

#### Get Agent Runs

```python
runs = await thread.get_agent_runs()
```

#### Returns

- `list`: List of agent runs

## Agent Execution

### Run Agent

```python
run = await agent.run("Your prompt", thread)
```

#### Parameters

- `message` (str): Message to send to the agent
- `thread` (Thread): Thread to use for the conversation

#### Returns

- `AgentRun`: Agent run instance

### Stream Response

```python
stream = await run.get_stream()
async for chunk in stream:
    print(chunk, end="")
```

#### Returns

- `AsyncGenerator[str]`: Stream of response chunks

## Tools

### AgentPress Tools

Built-in tools available for agents:

#### SB_FILES_TOOL
File system operations (read, write, create, delete files and directories)

#### SB_SHELL_TOOL
Execute shell commands and system operations

#### SB_DEPLOY_TOOL
Deploy web applications and services

#### SB_EXPOSE_TOOL
Expose local services to the internet

#### SB_VISION_TOOL
Analyze and understand images

#### BROWSER_TOOL
Browse websites and interact with web pages

#### WEB_SEARCH_TOOL
Search the web for information

#### SB_IMAGE_EDIT_TOOL
Edit and manipulate images

#### DATA_PROVIDERS_TOOL
Access structured data from various providers

### MCP Tools

Custom tools using Model Context Protocol:

```python
from ba.tools import MCPTools

mcp_tools = MCPTools(
    endpoint="http://localhost:4000/mcp/",
    name="weather-service",
    allowed_tools=["get_weather", "get_forecast"]
)
await mcp_tools.initialize()
```

#### Parameters

- `endpoint` (str): MCP server endpoint
- `name` (str): Name of the MCP service
- `allowed_tools` (list, optional): Specific tools to allow

## Error Handling

### Common Exceptions

#### HTTPStatusError
Raised for HTTP errors (authentication, rate limits, etc.)

```python
try:
    agent = await client.Agent.create(...)
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e}")
```

#### ValueError
Raised for invalid input or configuration

```python
try:
    thread = await client.Thread.create(...)
except ValueError as e:
    print(f"Invalid input: {e}")
```

#### PermissionError
Raised for access denied or insufficient permissions

```python
try:
    run = await agent.run(...)
except PermissionError as e:
    print(f"Permission denied: {e}")
```

### Error Handling Best Practices

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

## Data Models

### AgentResponse

```python
@dataclass
class AgentResponse:
    agent_id: str
    name: str
    system_prompt: str
    custom_mcps: list[CustomMCP]
    agentpress_tools: dict[AgentPressTools, AgentPress_ToolConfig]
    is_default: bool
    created_at: str
    account_id: str | None = None
    description: str | None = None
    avatar: str | None = None
    avatar_color: str | None = None
    updated_at: str | None = None
    is_public: bool | None = False
    marketplace_published_at: str | None = None
    download_count: int | None = 0
    tags: list[str] | None = None
    current_version_id: str | None = None
    version_count: int | None = 1
    current_version: AgentVersionResponse | None = None
    metadata: dict[str, Any] | None = None
```

### ThreadResponse

```python
@dataclass
class ThreadResponse:
    thread_id: str
    name: str
    created_at: str
    updated_at: str | None = None
    metadata: dict[str, Any] | None = None
```

### MessageResponse

```python
@dataclass
class MessageResponse:
    message_id: str
    thread_id: str
    content: str | dict[str, Any]
    type: MessageType
    created_at: str
    updated_at: str | None = None
    metadata: dict[str, Any] | None = None
```

### AgentRunResponse

```python
@dataclass
class AgentRunResponse:
    run_id: str
    agent_id: str
    thread_id: str
    status: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None
```

## Rate Limits and Quotas

### Agent Limits

- **Free Plan**: 2 agents maximum
- **Pro Plan**: 10 agents maximum
- **Enterprise Plan**: Unlimited agents

### API Rate Limits

- **Requests per minute**: 60 requests
- **Concurrent requests**: 5 concurrent requests
- **Streaming connections**: 10 concurrent streams

### Error Codes

- `AGENT_LIMIT_EXCEEDED`: Maximum number of agents reached
- `RATE_LIMIT_EXCEEDED`: Too many requests in a time period
- `AUTHENTICATION_REQUIRED`: Invalid or missing API key
- `PERMISSION_DENIED`: Insufficient permissions for operation
- `MODEL_ACCESS_DENIED`: Model not available for current plan

## Best Practices

### Performance Optimization

1. **Reuse agents** instead of creating new ones for each task
2. **Stream responses** for better user experience
3. **Batch operations** when possible
4. **Handle rate limits** gracefully
5. **Monitor usage** and optimize accordingly

### Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Validate user inputs** before passing to agents
4. **Implement proper authentication** for production apps
5. **Monitor for suspicious activity**

### Error Handling

1. **Always wrap operations** in try-catch blocks
2. **Provide specific error messages** to users
3. **Implement retry logic** for transient failures
4. **Log errors** for debugging and monitoring
5. **Gracefully degrade** when services are unavailable

## Examples

For comprehensive examples, see the [examples directory](examples/README.md).

## Support

- **Documentation**: [https://docs.belaraby.ai](https://docs.belaraby.ai)
- **Discord Community**: [https://discord.gg/qAncfHmYUm](https://discord.gg/qAncfHmYUm) - Join our community for discussions, help, and updates
- **Issues**: [https://github.com/rhkiswani/BelArabyAI-python-sdk/issues](https://github.com/rhkiswani/BelArabyAI-python-sdk/issues)
- **Email**: support@belaraby.ai
