#!/usr/bin/env python3
"""
Conversation management example for BelArabyAI SDK.

This example demonstrates how to:
1. Manage conversation threads
2. Add and delete messages
3. Retrieve conversation history
4. Handle multiple agent runs
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

    # Create an agent
    print("\n🤖 Creating agent...")
    try:
        agent = await client.Agent.create(
            name="Conversation Manager",
            system_prompt="You are a helpful assistant that can help with various tasks.",
            mcp_tools=[AgentPressTools.SB_FILES_TOOL, AgentPressTools.WEB_SEARCH_TOOL],
        )
        print(f"✅ Agent created with ID: {agent._agent_id}")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        error_str = str(e).lower()
        if "agent_limit_exceeded" in error_str or "maximum of" in error_str:
            print("💡 You've reached the agent limit for your current plan.")
            print("   Please upgrade your plan or delete unused agents to create new ones.")
        elif "authentication required" in error_str or "redirected to" in error_str:
            print("💡 This usually means your API key is invalid or expired.")
            print("   Please check your BELARABYAI_API_KEY environment variable.")
        else:
            print("💡 Please check your API key and try again.")
        return

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Conversation Management Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Add initial messages
    print("\n📝 Adding messages to thread...")
    message_ids = []

    messages = [
        "Hello! I need help with a project.",
        "Can you help me create a simple web page?",
        "What are the best practices for web development?",
    ]

    for message in messages:
        message_id = await thread.add_message(message)
        message_ids.append(message_id)
        print(f"✅ Added message: {message[:50]}... (ID: {message_id})")

    # Get all messages
    print("\n📋 Retrieving conversation history...")
    all_messages = await thread.get_messages()
    print(f"✅ Found {len(all_messages)} messages in thread")

    for i, msg in enumerate(all_messages, 1):
        # Handle different content types
        if isinstance(msg.content, str):
            content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
        elif isinstance(msg.content, dict):
            content_preview = str(msg.content)[:50] + "..."
        else:
            content_preview = str(msg.content)[:50] + "..."
        print(f"  {i}. [{msg.type}] {content_preview}")

    # Run agent on first message
    print("\n🤖 Running agent on first message...")
    try:
        run1 = await agent.run(messages[0], thread)

        print("Agent response:")
        stream1 = await run1.get_stream()
        async for chunk in stream1:
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"❌ Failed to run agent: {e}")
        error_str = str(e).lower()
        if "subscription plan" in error_str or "available models" in error_str:
            print("💡 Your current plan doesn't include access to the default model.")
            print("   The agent was created successfully, but you need to upgrade your plan")
            print("   or configure the agent to use an available model.")
        elif "permission" in error_str or "access denied" in error_str:
            print("💡 Access denied. Please check your plan permissions.")
        else:
            print("💡 Please check your configuration and try again.")
        return

    # Get agent runs
    print("\n📊 Retrieving agent runs...")
    runs = await thread.get_agent_runs()
    if runs:
        print(f"✅ Found {len(runs)} agent runs")
        for i, run in enumerate(runs, 1):
            print(f"  {i}. Run ID: {run._agent_run_id}")
    else:
        print("ℹ️  No agent runs found")

    # Delete a message
    if message_ids:
        print(f"\n🗑️  Deleting message {message_ids[0]}...")
        await thread.delete_message(message_ids[0])
        print("✅ Message deleted")

    # Get updated messages
    print("\n📋 Retrieving updated conversation history...")
    updated_messages = await thread.get_messages()
    print(f"✅ Now {len(updated_messages)} messages in thread")

    # Update agent
    print("\n🔄 Updating agent...")
    await agent.update(
        name="Updated Conversation Manager",
        system_prompt="You are an updated helpful assistant with enhanced capabilities.",
        allowed_tools=["sb_files_tool"],  # Only allow file operations
    )
    print("✅ Agent updated")

    # Run updated agent
    print("\n🤖 Running updated agent...")
    run2 = await agent.run("Can you help me with file operations?", thread)

    print("Updated agent response:")
    stream2 = await run2.get_stream()
    async for chunk in stream2:
        print(chunk, end="", flush=True)
    print()

    # Clean up - delete the thread
    print(f"\n🗑️  Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Conversation management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
