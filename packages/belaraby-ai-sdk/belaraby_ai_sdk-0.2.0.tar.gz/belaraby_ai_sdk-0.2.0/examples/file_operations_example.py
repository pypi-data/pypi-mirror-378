#!/usr/bin/env python3
"""
File Operations Example for BelArabyAI SDK
==========================================

This example demonstrates comprehensive file system operations using the SB_FILES_TOOL:

🎯 What This Example Covers:
- File and directory creation
- Reading and writing files
- File searching and organization
- Batch file operations
- Error handling for file operations

🛠️ Tools Demonstrated:
- SB_FILES_TOOL: Complete file system access and manipulation

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Get API key from: https://belaraby.ai/settings/api-keys
3. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/file_operations_example.py

💡 Key Learning Points:
- How to create agents specialized for file operations
- File system navigation and manipulation
- Batch operations for efficiency
- Error handling for file system operations
- Organizing complex file operations

🔧 Use Cases:
- Automated file management systems
- Content creation and organization
- Data processing pipelines
- Backup and synchronization tools
- Document management systems

⚠️ Important Notes:
- The agent has full file system access
- Be careful with file deletion operations
- Consider file permissions and security
- Test operations in a safe environment first
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

    # Create a file management agent
    print("\n🤖 Creating File Management Agent...")
    agent = await client.Agent.create(
        name="File Operations Expert",
        system_prompt="""You are a file operations expert. You can:
        - Create, read, update, and delete files
        - Create and manage directories
        - Search for files by name or content
        - Organize files efficiently
        - Perform batch operations
        Always be careful with file operations and provide clear feedback.""",
        mcp_tools=[AgentPressTools.SB_FILES_TOOL],
        allowed_tools=["sb_files_tool"],
    )
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("File Operations Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # File operations scenarios
    scenarios = [
        {
            "title": "📁 Creating Project Structure",
            "message": "Create a complete project structure for a Python web application called 'myapp' with the following structure:\n- myapp/\n  - src/\n    - __init__.py\n    - main.py\n    - models/\n      - __init__.py\n    - views/\n      - __init__.py\n  - tests/\n    - __init__.py\n    - test_main.py\n  - requirements.txt\n  - README.md\n  - .gitignore",
        },
        {
            "title": "📝 Creating Configuration Files",
            "message": "Create configuration files for the project:\n1. requirements.txt with Flask, pytest, and requests\n2. README.md with project description and setup instructions\n3. .gitignore with Python-specific ignores",
        },
        {
            "title": "💻 Writing Application Code",
            "message": "Create the main application files:\n1. src/main.py - A simple Flask web application with a home route\n2. src/models/user.py - A simple User model class\n3. tests/test_main.py - Basic tests for the Flask app",
        },
        {
            "title": "🔍 File Search and Organization",
            "message": "Search for all Python files in the project and create a summary of the codebase structure. Also, check if there are any TODO comments in the code.",
        },
        {
            "title": "📊 Project Analysis",
            "message": "Analyze the project structure and provide recommendations for improvement. Check for any missing files or best practices.",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['title']}")
        print(f"{'='*60}")

        # Add message to thread
        await thread.add_message(scenario["message"])

        # Run the agent
        run = await agent.run(scenario["message"], thread)

        # Stream the response
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()  # New line after response

    # Demonstrate file reading
    print(f"\n{'='*60}")
    print("📖 Reading Created Files")
    print(f"{'='*60}")

    read_scenarios = [
        "Read the contents of src/main.py and explain what it does",
        "Read the requirements.txt file and list all dependencies",
        "Read the README.md file and provide a summary",
    ]

    for scenario in read_scenarios:
        print(f"\n📝 Reading: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate file modification
    print(f"\n{'='*60}")
    print("✏️ Modifying Files")
    print(f"{'='*60}")

    modify_scenarios = [
        "Add error handling to the Flask application in src/main.py",
        "Update the README.md to include installation and usage instructions",
        "Add more dependencies to requirements.txt (like Flask-CORS and python-dotenv)",
    ]

    for scenario in modify_scenarios:
        print(f"\n✏️ Modifying: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate cleanup
    print(f"\n{'='*60}")
    print("🗑️ Cleanup Operations")
    print(f"{'='*60}")

    cleanup_scenarios = [
        "Create a backup of all important files before cleanup",
        "Remove test files and temporary files",
        "Create a final project summary",
    ]

    for scenario in cleanup_scenarios:
        print(f"\n🗑️ Cleanup: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get conversation summary
    print(f"\n{'='*60}")
    print("📊 Conversation Summary")
    print(f"{'='*60}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total messages: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n📝 Message types:")
    message_types = {}
    for msg in messages:
        message_types[msg.type] = message_types.get(msg.type, 0) + 1

    for msg_type, count in message_types.items():
        print(f"  - {msg_type}: {count}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ File operations example completed!")


if __name__ == "__main__":
    asyncio.run(main())
