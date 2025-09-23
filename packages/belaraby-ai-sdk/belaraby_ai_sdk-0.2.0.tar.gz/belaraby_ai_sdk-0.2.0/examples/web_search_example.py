#!/usr/bin/env python3
"""
Web Search Example for BelArabyAI SDK
=====================================

This example demonstrates comprehensive web search capabilities using the WEB_SEARCH_TOOL:

🎯 What This Example Covers:
- Basic web search operations
- Advanced research tasks
- Information gathering and verification
- Source validation and fact-checking
- Data extraction and summarization
- Multi-source research workflows

🛠️ Tools Demonstrated:
- WEB_SEARCH_TOOL: Web search and information retrieval
- BROWSER_TOOL: Web page browsing and interaction
- SB_FILES_TOOL: Saving search results and reports

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Get API key from: https://belaraby.ai/settings/api-keys
3. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/web_search_example.py

💡 Key Learning Points:
- How to create research-focused agents
- Web search query optimization
- Information synthesis and analysis
- Source verification techniques
- Research workflow automation
- Data extraction and processing

🔧 Use Cases:
- Market research and competitive analysis
- Academic research and fact-checking
- News monitoring and analysis
- Content research and curation
- Business intelligence gathering
- Customer research and insights
- Technical documentation research

🔍 Search Scenarios Covered:
1. Basic Web Search - Simple information queries
2. Research Tasks - Complex multi-step research
3. Information Gathering - Comprehensive data collection
4. Source Verification - Fact-checking and validation
5. Data Extraction - Structured data collection
6. Summarization - Information synthesis

⚠️ Important Notes:
- Web search results may vary over time
- Always verify information from multiple sources
- Respect website terms of service and robots.txt
- Consider rate limiting for extensive searches
- Be mindful of copyright and fair use policies
- Validate information before using in production
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

    # Create a web research agent
    print("\n🤖 Creating Web Research Agent...")
    agent = await client.Agent.create(
        name="Web Research Expert",
        system_prompt="""You are a web research expert. You can:
        - Search the web for information
        - Browse websites and extract relevant data
        - Summarize findings from multiple sources
        - Provide citations and sources
        - Verify information from multiple sources
        - Extract key insights and trends
        Always provide accurate information with proper citations.""",
        mcp_tools=[AgentPressTools.WEB_SEARCH_TOOL, AgentPressTools.BROWSER_TOOL],
        allowed_tools=["web_search_tool", "browser_tool"],
    )
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Web Research Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Web search scenarios
    scenarios = [
        {
            "title": "🔍 Basic Information Search",
            "message": "Search for information about 'Python 3.12 new features' and provide a comprehensive summary of the key improvements.",
        },
        {
            "title": "📊 Market Research",
            "message": "Research the current state of AI/ML frameworks in 2024. Compare TensorFlow, PyTorch, and JAX. Include market share, adoption rates, and key differences.",
        },
        {
            "title": "🌐 Technology Trends",
            "message": "Search for the latest trends in web development for 2024. Focus on frontend frameworks, backend technologies, and deployment strategies.",
        },
        {
            "title": "📚 Educational Resources",
            "message": "Find the best online resources for learning machine learning. Include free courses, tutorials, and documentation from reputable sources.",
        },
        {
            "title": "🔬 Scientific Research",
            "message": "Research recent developments in quantum computing. Focus on practical applications, current limitations, and future prospects.",
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

    # Demonstrate specific search techniques
    print(f"\n{'='*60}")
    print("🎯 Advanced Search Techniques")
    print(f"{'='*60}")

    advanced_scenarios = [
        {
            "title": "📈 Comparative Analysis",
            "message": "Compare the performance of different Python web frameworks (Flask, Django, FastAPI) based on recent benchmarks and real-world usage.",
        },
        {
            "title": "🔍 Fact Checking",
            "message": "Verify the claim that 'Python is the most popular programming language in 2024'. Search for multiple sources and provide evidence.",
        },
        {
            "title": "📋 Best Practices Research",
            "message": "Research best practices for API design in 2024. Include REST vs GraphQL, authentication methods, and documentation standards.",
        },
        {
            "title": "🌍 Global Trends",
            "message": "Research how different countries are approaching AI regulation and policy in 2024. Compare approaches from US, EU, and Asia.",
        },
    ]

    for scenario in advanced_scenarios:
        print(f"\n🎯 {scenario['title']}")
        await thread.add_message(scenario["message"])

        run = await agent.run(scenario["message"], thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate real-time information gathering
    print(f"\n{'='*60}")
    print("⏰ Real-time Information Gathering")
    print(f"{'='*60}")

    realtime_scenarios = [
        "Search for the latest news about artificial intelligence breakthroughs in the last 30 days",
        "Find recent updates about major tech companies' AI initiatives (Google, Microsoft, OpenAI, Anthropic)",
        "Research current job market trends for AI/ML engineers and data scientists",
    ]

    for scenario in realtime_scenarios:
        print(f"\n⏰ Real-time: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate data extraction and summarization
    print(f"\n{'='*60}")
    print("📊 Data Extraction and Summarization")
    print(f"{'='*60}")

    extraction_scenarios = [
        "Search for Python package statistics on PyPI and summarize the most popular packages",
        "Research GitHub's State of the Octoverse report and extract key insights about developer trends",
        "Find information about cloud computing market share and summarize the competitive landscape",
    ]

    for scenario in extraction_scenarios:
        print(f"\n📊 Extraction: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get conversation summary
    print(f"\n{'='*60}")
    print("📊 Research Summary")
    print(f"{'='*60}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total research queries: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n📝 Research topics covered:")
    research_topics = [
        "Python 3.12 features",
        "AI/ML frameworks comparison",
        "Web development trends",
        "Educational resources",
        "Quantum computing developments",
        "Web framework performance",
        "API design best practices",
        "AI regulation policies",
        "Tech company AI initiatives",
        "Job market trends",
        "Package statistics",
        "Developer trends",
        "Cloud computing market",
    ]

    for topic in research_topics:
        print(f"  - {topic}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Web search example completed!")


if __name__ == "__main__":
    asyncio.run(main())
