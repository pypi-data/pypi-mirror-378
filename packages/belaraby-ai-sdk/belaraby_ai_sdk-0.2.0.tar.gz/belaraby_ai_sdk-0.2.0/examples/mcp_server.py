#!/usr/bin/env python3
"""
Sample MCP Server Implementation for BelArabyAI SDK
=================================================

This file demonstrates how to create a simple MCP (Model Context Protocol) server
using the FastMCP framework. This server provides weather-related tools that can be
used by BelArabyAI agents.

🎯 What This Server Provides:
- Sample weather service tools
- FastMCP framework integration
- Async/await support
- Tool registration and discovery
- Simple HTTP endpoint for MCP communication

🛠️ Tools Available:
- get_weather(city: str) -> str: Get weather information for a city
- get_wind_direction(city: str) -> str: Get wind direction for a city

📋 Prerequisites:
1. Install FastMCP: pip install fastmcp
2. Install BelArabyAI SDK: pip install belaraby-ai-sdk

🚀 Running This Server:

```bash
# Start the MCP server
python examples/mcp_server.py
```

The server will start on the default port and be accessible for MCP tool integration.

💡 Key Learning Points:
- How to create MCP tools using FastMCP
- Tool function definition and registration
- Async/await patterns for MCP tools
- Tool parameter validation and typing
- Error handling in MCP tools

🔧 Customization Ideas:
- Add more sophisticated weather data sources
- Implement caching for weather data
- Add error handling and validation
- Create tools for other services (news, stocks, etc.)
- Add authentication and rate limiting

🏗️ Architecture Patterns:
- Tool Registration - Decorator-based tool registration
- Async Operations - Non-blocking tool execution
- Type Safety - Strong typing for tool parameters
- Service Abstraction - Clean separation of concerns
- Error Handling - Graceful error management

⚠️ Important Notes:
- This is a sample implementation for demonstration
- In production, implement proper error handling
- Add authentication and rate limiting as needed
- Consider data source reliability and caching
- Monitor tool performance and usage

🔗 Related Files:
- mcp_tools_example.py: Shows how to use this server with BelArabyAI
- kv.py: Utility for storing server configurations
"""

from fastmcp import FastMCP

# Initialize the MCP server with a name
mcp = FastMCP(name="Kortix")


@mcp.tool
async def get_weather(city: str) -> str:
    """
    Get weather information for a specified city.
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        A string describing the weather conditions
    """
    return f"The weather in {city} is windy."


@mcp.tool
async def get_wind_direction(city: str) -> str:
    """
    Get wind direction information for a specified city.
    
    Args:
        city: The name of the city to get wind direction for
        
    Returns:
        A string describing the wind direction
    """
    return f"The wind direction in {city} is from the north."
