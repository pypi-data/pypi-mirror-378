#!/usr/bin/env python3
"""
Error handling example for BelArabyAI SDK.

This example demonstrates how to:
1. Handle various error conditions
2. Validate inputs
3. Gracefully handle API errors
4. Provide meaningful error messages
"""

import asyncio
import os
from belarabyai import BelArabyAI, AgentPressTools, MCPTools


async def main():
    """Main example function demonstrating error handling."""
    
    # Example 1: Invalid API key
    print("🚫 Example 1: Invalid API key")
    try:
        client = BelArabyAI(api_key="")
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
    
    try:
        client = BelArabyAI(api_key=None)
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")

    # Example 2: MCP tools without fastmcp
    print("\n🚫 Example 2: MCP tools without fastmcp dependency")
    try:
        # This will fail if fastmcp is not installed
        mcp_tools = MCPTools("http://localhost:4000", "test")
    except ImportError as e:
        print(f"✅ Caught expected error: {e}")
        print("💡 Install fastmcp: pip install fastmcp")

    # Example 3: Valid API key (if available)
    api_key = os.getenv("BELARABYAI_API_KEY")
    if api_key:
        print(f"\n✅ Example 3: Using valid API key")
        client = BelArabyAI(api_key=api_key)
        
        try:
            # Try to create an agent with invalid tools
            print("🚫 Testing invalid tool configuration...")
            agent = await client.Agent.create(
                name="Test Agent",
                system_prompt="Test prompt",
                mcp_tools=["invalid_tool_type"]  # This should fail
            )
        except ValueError as e:
            print(f"✅ Caught expected error: {e}")
        
        try:
            # Try to get a non-existent agent
            print("🚫 Testing non-existent agent retrieval...")
            agent = await client.Agent.get("non-existent-agent-id")
        except Exception as e:
            print(f"✅ Caught expected error: {e}")
        
        try:
            # Try to get a non-existent thread
            print("🚫 Testing non-existent thread retrieval...")
            thread = await client.Thread.get("non-existent-thread-id")
        except Exception as e:
            print(f"✅ Caught expected error: {e}")
        
        # Example 4: Graceful error handling in conversation
        print("\n✅ Example 4: Graceful error handling in conversation")
        try:
            # Create a valid agent
            agent = await client.Agent.create(
                name="Error Handling Agent",
                system_prompt="You are a helpful assistant.",
                mcp_tools=[AgentPressTools.SB_FILES_TOOL]
            )
            
            # Create a thread
            thread = await client.Thread.create("Error Handling Demo")
            
            # Try to run agent with empty message
            print("🚫 Testing empty message...")
            try:
                run = await agent.run("", thread)
                stream = await run.get_stream()
                async for chunk in stream:
                    print(chunk, end="")
                print()
            except Exception as e:
                print(f"✅ Caught error with empty message: {e}")
            
            # Clean up
            await client.Thread.delete(thread._thread_id)
            print("✅ Cleaned up resources")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    else:
        print("\n⚠️  Example 3: Skipped - No API key provided")
        print("💡 Set BELARABYAI_API_KEY environment variable to test with real API")

    # Example 5: Input validation
    print("\n✅ Example 5: Input validation examples")
    
    # Test AgentPressTools description
    try:
        desc = AgentPressTools.SB_FILES_TOOL.get_description()
        print(f"✅ Valid tool description: {desc}")
    except Exception as e:
        print(f"❌ Error getting tool description: {e}")
    
    # Test invalid tool (this would fail if we had an invalid enum)
    print("✅ All error handling examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
