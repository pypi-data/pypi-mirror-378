#!/usr/bin/env python3
"""
Basic usage example for BelArabyAI SDK.

This example demonstrates how to:
1. Initialize the SDK client
2. Create an agent with built-in tools
3. Create a conversation thread
4. Run the agent and stream responses
"""

import asyncio
import os
from belarabyai import BelArabyAI, AgentPressTools


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
    print(f"✅ Connected to: {client.api_url}")

    # Create an agent with file and web search capabilities
    print("\n🤖 Creating agent...")
    agent = await client.Agent.create(
        name="Assistant Bot",
        system_prompt="You are a helpful AI assistant that can help with file operations and web searches.",
        mcp_tools=[
            AgentPressTools.SB_FILES_TOOL,
            AgentPressTools.WEB_SEARCH_TOOL,
            AgentPressTools.SB_SHELL_TOOL
        ],
        allowed_tools=["sb_files_tool", "web_search_tool", "sb_shell_tool"]
    )
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Basic Usage Example")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Example conversation
    messages = [
        "Hello! Can you help me create a simple Python script?",
        "Please create a file called 'hello.py' with a simple hello world program",
        "Now can you search the web for 'Python best practices' and summarize what you find?"
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

    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
