#!/usr/bin/env python3
"""
Advanced Agent Management Example for BelArabyAI SDK
====================================================

This example demonstrates sophisticated agent management patterns for complex applications:

🎯 What This Example Covers:
- Creating multiple specialized agents for different tasks
- Managing agent configurations and settings
- Switching between agents based on context
- Agent lifecycle management and optimization
- Bulk operations and agent orchestration
- Error handling for multi-agent scenarios

🛠️ Tools Demonstrated:
- SB_FILES_TOOL: File management operations
- SB_VISION_TOOL: Image processing capabilities
- WEB_SEARCH_TOOL: Web research and information gathering
- SB_SHELL_TOOL: System command execution
- BROWSER_TOOL: Web browsing and interaction

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Get API key from: https://belaraby.ai/settings/api-keys
3. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/advanced_agent_management.py

💡 Key Learning Points:
- How to design specialized agents for specific domains
- Agent configuration management and updates
- Multi-agent workflow orchestration
- Resource optimization and agent reuse
- Error handling in complex agent scenarios
- Performance monitoring and optimization

🔧 Agent Types Demonstrated:
1. File Management Agent - File system operations
2. Image Processing Agent - Image analysis and manipulation
3. Web Research Agent - Information gathering and research
4. Development Agent - Code generation and deployment
5. Data Analysis Agent - Data processing and visualization

🏗️ Architecture Patterns:
- Specialized Agent Design - Each agent has a specific purpose
- Agent Registry Pattern - Centralized agent management
- Context Switching - Dynamic agent selection
- Resource Pooling - Efficient agent reuse
- Error Isolation - Independent agent failure handling

⚠️ Important Notes:
- Agent creation is subject to plan limits
- Consider resource usage with multiple agents
- Implement proper error handling for agent failures
- Monitor agent performance and optimize as needed
- Plan for agent lifecycle management in production
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

    # Create multiple specialized agents
    print("\n🤖 Creating specialized agents...")

    agents = {}

    # 1. File Management Agent
    print("📁 Creating File Management Agent...")
    try:
        file_agent = await client.Agent.create(
            name="File Manager",
            system_prompt="""You are a file management expert. You can:
            - Create, read, update, and delete files
            - Organize files into directories
            - Search for files by name or content
            - Provide file system recommendations
            Always be careful with file operations and ask for confirmation before deleting files.""",
            mcp_tools=[AgentPressTools.SB_FILES_TOOL, AgentPressTools.SB_SHELL_TOOL],
            allowed_tools=["sb_files_tool", "sb_shell_tool"],
        )
        agents["file_manager"] = file_agent
        print(f"✅ File Manager created with ID: {file_agent._agent_id}")
    except Exception as e:
        print(f"❌ Failed to create File Management Agent: {e}")
        error_str = str(e).lower()
        if "agent_limit_exceeded" in error_str or "maximum of" in error_str:
            print("💡 You've reached the agent limit for your current plan.")
            print("   Please upgrade your plan or delete unused agents to create new ones.")
            return
        else:
            print("💡 Please check your configuration and try again.")
            return

    # 2. Web Research Agent
    print("🌐 Creating Web Research Agent...")
    web_agent = await client.Agent.create(
        name="Web Researcher",
        system_prompt="""You are a web research specialist. You can:
        - Search the web for information
        - Browse websites and extract relevant data
        - Summarize findings from multiple sources
        - Provide citations and sources
        Always verify information from multiple sources when possible.""",
        mcp_tools=[AgentPressTools.WEB_SEARCH_TOOL, AgentPressTools.BROWSER_TOOL],
        allowed_tools=["web_search_tool", "browser_tool"],
    )
    agents["web_researcher"] = web_agent
    print(f"✅ Web Researcher created with ID: {web_agent._agent_id}")

    # 3. Image Processing Agent
    print("🖼️ Creating Image Processing Agent...")
    try:
        image_agent = await client.Agent.create(
            name="Image Processor",
            system_prompt="""You are an image processing expert. You can:
            - Analyze and understand images
            - Edit and manipulate images
            - Extract information from visual content
            - Provide image optimization recommendations
            Always respect image rights and provide appropriate disclaimers.""",
            mcp_tools=[AgentPressTools.SB_VISION_TOOL, AgentPressTools.SB_IMAGE_EDIT_TOOL],
            allowed_tools=["sb_vision_tool", "sb_image_edit_tool"],
        )
        agents["image_processor"] = image_agent
        print(f"✅ Image Processor created with ID: {image_agent._agent_id}")
    except Exception as e:
        print(f"❌ Failed to create Image Processing Agent: {e}")
        error_str = str(e).lower()
        if "agent_limit_exceeded" in error_str or "maximum of" in error_str:
            print("💡 You've reached the agent limit for your current plan.")
            print("   Continuing with the agents that were created successfully...")
        else:
            print("💡 Please check your configuration and try again.")

    # 4. Development Agent
    print("💻 Creating Development Agent...")
    try:
        dev_agent = await client.Agent.create(
            name="Development Assistant",
            system_prompt="""You are a software development assistant. You can:
            - Write and debug code
            - Deploy applications
            - Manage development environments
            - Provide coding best practices
            Always follow security best practices and test code thoroughly.""",
            mcp_tools=[
                AgentPressTools.SB_FILES_TOOL,
                AgentPressTools.SB_SHELL_TOOL,
                AgentPressTools.SB_DEPLOY_TOOL,
                AgentPressTools.SB_EXPOSE_TOOL,
            ],
            allowed_tools=[
                "sb_files_tool",
                "sb_shell_tool",
                "sb_deploy_tool",
                "sb_expose_tool",
            ],
        )
        agents["developer"] = dev_agent
        print(f"✅ Development Assistant created with ID: {dev_agent._agent_id}")
    except Exception as e:
        print(f"❌ Failed to create Development Agent: {e}")
        error_str = str(e).lower()
        if "agent_limit_exceeded" in error_str or "maximum of" in error_str:
            print("💡 You've reached the agent limit for your current plan.")
            print("   Continuing with the agents that were created successfully...")
        else:
            print("💡 Please check your configuration and try again.")

    # Create a shared conversation thread
    print("\n💬 Creating shared conversation thread...")
    thread = await client.Thread.create("Multi-Agent Collaboration")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Demonstrate agent switching
    print("\n🔄 Demonstrating agent switching...")

    # Scenario 1: File operations
    print("\n📁 Scenario 1: File Operations")
    await thread.add_message(
        "I need to create a project structure for a Python web application"
    )

    run1 = await file_agent.run(
        "Create a project structure for a Python web application with Flask", thread
    )
    print("File Manager response:")
    stream1 = await run1.get_stream()
    async for chunk in stream1:
        print(chunk, end="", flush=True)
    print()

    # Scenario 2: Web research
    print("\n🌐 Scenario 2: Web Research")
    await thread.add_message("Research the latest trends in Python web frameworks")

    run2 = await web_agent.run(
        "Research the latest trends in Python web frameworks for 2024", thread
    )
    print("Web Researcher response:")
    stream2 = await run2.get_stream()
    async for chunk in stream2:
        print(chunk, end="", flush=True)
    print()

    # Scenario 3: Development
    print("\n💻 Scenario 3: Development")
    await thread.add_message("Help me deploy the application")

    run3 = await dev_agent.run(
        "Help me deploy a Flask application with best practices", thread
    )
    print("Development Assistant response:")
    stream3 = await run3.get_stream()
    async for chunk in stream3:
        print(chunk, end="", flush=True)
    print()

    # Demonstrate agent updates
    print("\n🔄 Demonstrating agent updates...")

    # Update the file manager to be more cautious
    print("📝 Updating File Manager to be more cautious...")
    await file_agent.update(
        name="Cautious File Manager",
        system_prompt="""You are a very cautious file management expert. You can:
        - Create, read, update, and delete files
        - Organize files into directories
        - Search for files by name or content
        - Provide file system recommendations
        ALWAYS ask for explicit confirmation before any destructive operations.
        ALWAYS create backups before modifying important files.""",
        allowed_tools=["sb_files_tool"],  # Remove shell access for safety
    )
    print("✅ File Manager updated")

    # Test the updated agent
    print("\n🧪 Testing updated File Manager...")
    run4 = await file_agent.run("Create a backup of all important files", thread)
    print("Updated File Manager response:")
    stream4 = await run4.get_stream()
    async for chunk in stream4:
        print(chunk, end="", flush=True)
    print()

    # Demonstrate bulk operations
    print("\n📊 Demonstrating bulk operations...")

    # Get all messages
    messages = await thread.get_messages()
    print(f"📋 Thread has {len(messages)} messages")

    # Get all agent runs
    runs = await thread.get_agent_runs()
    print(f"🏃 Found {len(runs)} agent runs")

    # Display agent summary
    print("\n📊 Agent Summary:")
    for name, agent in agents.items():
        print(f"  - {name}: {agent._agent_id}")

    # Clean up - delete all agents and thread
    print("\n🗑️ Cleaning up...")

    for name, _agent in agents.items():
        print(f"Deleting {name}...")
        # Note: Agent deletion would require API support
        # await client.Agent.delete(agent._agent_id)

    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Advanced agent management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
