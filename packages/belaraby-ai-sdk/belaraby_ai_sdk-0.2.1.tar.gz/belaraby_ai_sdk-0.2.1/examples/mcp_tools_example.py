#!/usr/bin/env python3
"""
MCP Tools Example for BelArabyAI SDK
===================================

This example demonstrates how to integrate custom MCP (Model Context Protocol) tools:

🎯 What This Example Covers:
- Creating and initializing custom MCP tools
- Integrating MCP tools with BelArabyAI agents
- Handling tool initialization errors gracefully
- Tool discovery and validation
- Error recovery and fallback strategies

🛠️ Tools Demonstrated:
- MCPTools: Custom Model Context Protocol integration
- Custom weather service tools (get_weather, get_wind_direction)

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Install FastMCP: pip install fastmcp
3. Get API key from: https://belaraby.ai/settings/api-keys
4. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/mcp_tools_example.py

💡 Key Learning Points:
- How to create custom MCP tools using FastMCP
- MCP tool initialization and validation
- Error handling for tool connection failures
- Tool discovery and capability assessment
- Graceful degradation when tools are unavailable

🔧 MCP Tool Development:
- FastMCP framework for rapid tool development
- Async/await support for modern Python
- Tool registration and discovery
- Error handling and validation
- Custom tool endpoints and protocols

🏗️ Architecture Patterns:
- Tool Abstraction - Consistent interface for all tools
- Error Isolation - Tool failures don't affect other tools
- Graceful Degradation - Fallback when tools are unavailable
- Tool Discovery - Dynamic tool capability detection
- Connection Management - Robust tool connection handling

⚠️ Important Notes:
- MCP tools require a running MCP server
- Ensure your MCP server is accessible and running
- Handle connection failures gracefully
- Test tool functionality before production use
- Consider tool performance and reliability
- Implement proper error handling and logging

🔗 Related Files:
- mcp_server.py: Sample MCP server implementation
- kv.py: Utility for storing tool configurations
"""

import asyncio
import os

from ba.ba import BASdk
from ba.tools import MCPTools


async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv("BELARABYAI_API_KEY")
    if not api_key:
        print("Please set BELARABYAI_API_KEY environment variable")
        return

    # Initialize the client
    print("🚀 Initializing BelArabyAI client...")
    client = BASdk(api_key=api_key)

    try:
        # Create custom MCP tools (example with a hypothetical weather service)
        print("\n🔧 Setting up MCP tools...")
        weather_tools = MCPTools(
            endpoint="http://localhost:4000/mcp/",  # Replace with your MCP server
            name="weather-service",
            allowed_tools=["get_weather", "get_forecast", "get_location_info"],
        )

        # Initialize the tools
        await weather_tools.initialize()
        print(
            f"✅ MCP tools initialized. Available tools: {weather_tools.enabled_tools}"
        )

        # Create an agent with custom MCP tools
        print("\n🤖 Creating agent with MCP tools...")
        agent = await client.Agent.create(
            name="Weather Assistant",
            system_prompt="You are a weather assistant that can provide weather information using the available tools.",
            mcp_tools=[weather_tools],
            allowed_tools=["get_weather", "get_forecast"],
        )
        print(f"✅ Agent created with ID: {agent._agent_id}")

        # Create a conversation thread
        print("\n💬 Creating conversation thread...")
        thread = await client.Thread.create("Weather Chat")
        print(f"✅ Thread created with ID: {thread._thread_id}")

        # Example conversation
        messages = [
            "What's the weather like in New York?",
            "Can you get a 5-day forecast for London?",
            "What's the current temperature in Tokyo?",
        ]

        for i, message in enumerate(messages, 1):
            print(f"\n📝 Message {i}: {message}")

            # Run the agent
            run = await agent.run(message, thread)

            # Stream the response
            print("🤖 Agent response:")
            stream = await run.get_stream()
            async for chunk in stream:
                print(chunk, end="", flush=True)
            print()  # New line after response

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure fastmcp is installed: pip install fastmcp")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your MCP server is running on http://localhost:4000/mcp/")

    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
