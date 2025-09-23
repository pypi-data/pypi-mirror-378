#!/usr/bin/env python3
"""
Basic Usage Example for BelArabyAI SDK
======================================

This example demonstrates the fundamental operations of the BelArabyAI SDK:

🎯 What This Example Covers:
- Client initialization and connection
- Agent creation with built-in AgentPress tools
- Conversation thread management
- Agent execution and response streaming
- Error handling for common scenarios

🛠️ Tools Demonstrated:
- SB_FILES_TOOL: File system operations
- WEB_SEARCH_TOOL: Web search capabilities

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Get API key from: https://belaraby.ai/settings/api-keys
3. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/basic_usage.py

💡 Key Learning Points:
- How to properly initialize the SDK client
- Agent creation with system prompts and tools
- Thread-based conversation management
- Streaming responses for real-time interaction
- Comprehensive error handling patterns

🔧 Customization Ideas:
- Modify the system prompt to change agent behavior
- Add different AgentPress tools for various capabilities
- Implement custom conversation flows
- Add user input handling for interactive sessions
"""

import asyncio
import os

from ba.ba import BASdk
from ba.tools import AgentPressTools


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
    print(f"✅ Connected to: {client.api_url}")

    # Create an agent with file and web search capabilities
    print("\n🤖 Creating agent...")
    try:
        agent = await client.Agent.create(
            name="Assistant Bot",
            system_prompt="You are a helpful AI assistant that can help with file operations and web searches.",
            mcp_tools=[
                AgentPressTools.SB_FILES_TOOL,
                AgentPressTools.WEB_SEARCH_TOOL,
                AgentPressTools.SB_SHELL_TOOL,
            ],
            allowed_tools=["sb_files_tool", "web_search_tool", "sb_shell_tool"],
        )
        print(f"✅ Agent created with ID: {agent._agent_id}")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        
        # Check for specific error types
        error_str = str(e).lower()
        if "agent_limit_exceeded" in error_str or "maximum of" in error_str:
            print("💡 You've reached the agent limit for your current plan.")
            print("   Consider upgrading your plan or deleting unused agents.")
        elif "authentication required" in error_str or "redirected to" in error_str:
            print("💡 This usually means your API key is invalid or expired.")
            print("   Please check your BELARABYAI_API_KEY environment variable.")
        else:
            print("💡 Please check your API key and try again.")
        return

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Basic Usage Example")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Example conversation
    messages = [
        "Hello! Can you help me create a simple Python script?",
        "Please create a file called 'hello.py' with a simple hello world program",
        "Now can you search the web for 'Python best practices' and summarize what you find?",
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n📝 Message {i}: {message}")

        try:
            # Run the agent
            run = await agent.run(message, thread)

            # Stream the response
            print("🤖 Agent response:")
            stream = await run.get_stream()
            async for chunk in stream:
                print(chunk, end="", flush=True)
            print()  # New line after response
        except Exception as e:
            print(f"❌ Failed to run agent: {e}")
            
            # Check for specific error types
            error_str = str(e).lower()
            if "subscription plan" in error_str or "available models" in error_str:
                print("💡 Your current plan doesn't include access to the default model.")
                print("   The agent was created successfully, but you need to upgrade your plan")
                print("   or configure the agent to use an available model.")
            elif "permission" in error_str or "access denied" in error_str:
                print("💡 Access denied. Please check your plan permissions.")
            else:
                print("💡 Please check your configuration and try again.")
            break

    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
