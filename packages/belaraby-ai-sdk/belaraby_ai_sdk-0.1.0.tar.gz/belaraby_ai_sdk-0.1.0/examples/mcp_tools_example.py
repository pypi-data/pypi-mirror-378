#!/usr/bin/env python3
"""
MCP Tools example for BelArabyAI SDK.

This example demonstrates how to:
1. Create and initialize custom MCP tools
2. Use MCP tools with agents
3. Handle tool initialization errors
"""

import asyncio
import os
from belarabyai import BelArabyAI, MCPTools


async def main():
    """Main example function."""
    # Get API key from environment variable
    api_key = os.getenv("BELARABYAI_API_KEY")
    if not api_key:
        print("Please set BELARABYAI_API_KEY environment variable")
        return

    # Initialize the client
    print("🚀 Initializing BelArabyAI client...")
    client = BelArabyAI(api_key=api_key)

    try:
        # Create custom MCP tools (example with a hypothetical weather service)
        print("\n🔧 Setting up MCP tools...")
        weather_tools = MCPTools(
            endpoint="http://localhost:4000/mcp/",  # Replace with your MCP server
            name="weather-service",
            allowed_tools=["get_weather", "get_forecast", "get_location_info"]
        )
        
        # Initialize the tools
        await weather_tools.initialize()
        print(f"✅ MCP tools initialized. Available tools: {weather_tools.enabled_tools}")

        # Create an agent with custom MCP tools
        print("\n🤖 Creating agent with MCP tools...")
        agent = await client.Agent.create(
            name="Weather Assistant",
            system_prompt="You are a weather assistant that can provide weather information using the available tools.",
            mcp_tools=[weather_tools],
            allowed_tools=["get_weather", "get_forecast"]
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
            "What's the current temperature in Tokyo?"
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
