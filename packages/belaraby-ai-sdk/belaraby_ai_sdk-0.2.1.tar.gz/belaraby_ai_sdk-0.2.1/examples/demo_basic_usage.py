#!/usr/bin/env python3
"""
Demo of BelArabyAI SDK Basic Usage

This example demonstrates the basic functionality of the BelArabyAI SDK
without making actual API calls. It shows the structure and capabilities.
"""

import asyncio
import os

from ba.ba import BASdk
from ba.tools import AgentPressTools


async def demo_main():
    """Demo main function showing SDK capabilities."""
    print("🚀 BelArabyAI SDK Demo")
    print("=" * 50)
    
    # Initialize the client
    print("\n📡 Initializing BelArabyAI client...")
    client = BASdk(api_key="demo-key")
    print(f"✅ Connected to: {client.api_url}")
    
    # Show available tools
    print("\n🛠️ Available AgentPress Tools:")
    print("-" * 30)
    for tool in AgentPressTools:
        print(f"  • {tool.value}: {tool.get_description()}")
    
    # Demonstrate agent creation structure
    print("\n🤖 Agent Creation Example:")
    print("-" * 30)
    print("""
    agent = await client.Agent.create(
        name="Assistant Bot",
        system_prompt="You are a helpful AI assistant...",
        mcp_tools=[
            AgentPressTools.SB_FILES_TOOL,
            AgentPressTools.WEB_SEARCH_TOOL,
        ],
        allowed_tools=["sb_files_tool", "web_search_tool"]
    )
    """)
    
    # Demonstrate thread creation
    print("💬 Thread Creation Example:")
    print("-" * 30)
    print("""
    thread = await client.Thread.create("My Conversation")
    """)
    
    # Demonstrate agent execution
    print("⚡ Agent Execution Example:")
    print("-" * 30)
    print("""
    run = await agent.run("Hello, how are you?", thread)
    
    # Stream the response
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="", flush=True)
    """)
    
    # Show environment setup
    print("\n🔧 Environment Setup:")
    print("-" * 30)
    print("1. Set your API key:")
    print("   export BELARABYAI_API_KEY='your-api-key-here'")
    print("\n2. Install the SDK:")
    print("   pip install belaraby-ai-sdk")
    print("\n3. Run the example:")
    print("   python examples/basic_usage.py")
    
    print("\n✨ Demo completed! The SDK is ready to use.")
    print("   For real usage, set a valid BELARABYAI_API_KEY environment variable.")


if __name__ == "__main__":
    asyncio.run(demo_main())
