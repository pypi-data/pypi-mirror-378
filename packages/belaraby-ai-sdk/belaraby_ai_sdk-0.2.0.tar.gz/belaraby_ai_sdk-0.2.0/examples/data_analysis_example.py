#!/usr/bin/env python3
"""
Data Analysis Example for BelArabyAI SDK
========================================

This example demonstrates comprehensive data analysis capabilities using the DATA_PROVIDERS_TOOL:

🎯 What This Example Covers:
- Data collection from various sources
- Statistical analysis and computation
- Data visualization and charting
- Pattern recognition and insights
- Automated report generation
- Advanced analytical techniques

🛠️ Tools Demonstrated:
- DATA_PROVIDERS_TOOL: Access to structured data sources
- SB_FILES_TOOL: Data file management and storage
- WEB_SEARCH_TOOL: External data collection

📋 Prerequisites:
1. Install the SDK: pip install belaraby-ai-sdk
2. Get API key from: https://belaraby.ai/settings/api-keys
3. Set environment variable: export BELARABYAI_API_KEY="your-key"

🚀 Running This Example:
python examples/data_analysis_example.py

💡 Key Learning Points:
- How to create data analysis agents
- Data collection and preprocessing
- Statistical analysis techniques
- Visualization and reporting
- Error handling for data operations
- Performance optimization for large datasets

🔧 Use Cases:
- Business intelligence and reporting
- Market research and analysis
- Scientific data analysis
- Financial data processing
- Customer analytics
- Performance monitoring
- Predictive modeling

📊 Analysis Scenarios Covered:
1. Basic Data Analysis - Simple statistical operations
2. Advanced Analytics - Complex analytical techniques
3. Data Visualization - Chart and graph generation
4. Report Generation - Automated report creation
5. Performance Optimization - Efficient data processing

⚠️ Important Notes:
- Data analysis can be computationally intensive
- Consider data privacy and security requirements
- Validate data sources and quality
- Monitor resource usage for large datasets
- Test with sample data before production use
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

    # Create a data analysis agent
    print("\n🤖 Creating Data Analysis Agent...")
    try:
        agent = await client.Agent.create(
            name="Data Analysis Expert",
            system_prompt="""You are a data analysis expert with capabilities in:
            - Data collection and web scraping
            - Statistical analysis and modeling
            - Data visualization and reporting
            - Pattern recognition and insights
            - Data cleaning and preprocessing
            - Report generation and presentation
            Always provide clear, actionable insights with proper statistical backing.""",
            mcp_tools=[
                AgentPressTools.WEB_SEARCH_TOOL,
                AgentPressTools.DATA_PROVIDERS_TOOL,
                AgentPressTools.SB_FILES_TOOL,
            ],
            allowed_tools=["web_search_tool", "data_providers_tool", "sb_files_tool"],
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
    thread = await client.Thread.create("Data Analysis Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Data analysis scenarios
    scenarios = [
        {
            "title": "📊 Market Research Analysis",
            "message": """Conduct a comprehensive market research analysis:
            1. Research current market trends in the AI/ML industry
            2. Analyze competitor data and market positioning
            3. Identify growth opportunities and threats
            4. Create a market size estimation
            5. Generate insights on customer preferences

            Provide statistical analysis with data sources and methodology.""",
        },
        {
            "title": "📈 Financial Data Analysis",
            "message": """Analyze financial data and trends:
            1. Research stock market performance for tech companies
            2. Analyze cryptocurrency trends and volatility
            3. Study economic indicators and their impact
            4. Create investment recommendations based on data
            5. Generate risk assessment and portfolio analysis

            Include statistical measures, correlations, and predictive insights.""",
        },
        {
            "title": "🌐 Social Media Analytics",
            "message": """Perform social media data analysis:
            1. Analyze trending topics and hashtags
            2. Study engagement patterns and user behavior
            3. Identify influencer trends and reach
            4. Analyze sentiment around specific topics
            5. Create social media strategy recommendations

            Provide quantitative analysis with engagement metrics.""",
        },
        {
            "title": "🔬 Scientific Data Analysis",
            "message": """Conduct scientific data analysis:
            1. Research recent scientific publications and findings
            2. Analyze research trends in specific fields
            3. Identify collaboration patterns among researchers
            4. Study citation patterns and impact factors
            5. Generate insights on emerging research areas

            Include statistical significance and confidence intervals.""",
        },
        {
            "title": "🏢 Business Intelligence",
            "message": """Perform business intelligence analysis:
            1. Analyze industry performance metrics
            2. Study customer behavior and preferences
            3. Identify operational efficiency opportunities
            4. Create competitive benchmarking analysis
            5. Generate strategic recommendations

            Provide actionable insights with data-driven recommendations.""",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['title']}")
        print(f"{'='*60}")

        # Add message to thread
        await thread.add_message(scenario["message"])

        # Run the agent
        try:
            run = await agent.run(scenario["message"], thread)

            # Stream the response
            print("🤖 Agent response:")
            stream = await run.get_stream()
            async for chunk in stream:
                print(chunk, end="", flush=True)
            print()  # New line after response
        except Exception as e:
            print(f"❌ Failed to run agent: {e}")
            error_str = str(e).lower()
            if "subscription plan" in error_str or "available models" in error_str:
                print("💡 Your current plan doesn't include access to the default model.")
                print("   The agent was created successfully, but you need to upgrade your plan")
                print("   or configure the agent to use an available model.")
                print("   Continuing with the next scenario...")
            elif "permission" in error_str or "access denied" in error_str:
                print("💡 Access denied. Please check your plan permissions.")
                print("   Continuing with the next scenario...")
            else:
                print("💡 Please check your configuration and try again.")
                print("   Continuing with the next scenario...")
            continue

    # Demonstrate specific analysis techniques
    print(f"\n{'='*60}")
    print("🔬 Advanced Analysis Techniques")
    print(f"{'='*60}")

    technique_scenarios = [
        {
            "title": "📊 Statistical Analysis",
            "message": "Demonstrate advanced statistical analysis techniques: descriptive statistics, inferential statistics, hypothesis testing, correlation analysis, and regression analysis.",
        },
        {
            "title": "📈 Time Series Analysis",
            "message": "Explain time series analysis methods: trend analysis, seasonal decomposition, forecasting, and anomaly detection.",
        },
        {
            "title": "🎯 Predictive Modeling",
            "message": "Guide through predictive modeling: data preprocessing, feature selection, model training, validation, and performance evaluation.",
        },
        {
            "title": "🔍 Pattern Recognition",
            "message": "Demonstrate pattern recognition techniques: clustering analysis, classification, association rules, and anomaly detection.",
        },
        {
            "title": "📊 Data Visualization",
            "message": "Create effective data visualizations: charts, graphs, dashboards, and interactive visualizations for different data types.",
        },
    ]

    for scenario in technique_scenarios:
        print(f"\n🔬 {scenario['title']}")
        await thread.add_message(scenario["message"])

        try:
            run = await agent.run(scenario["message"], thread)
            print("🤖 Agent response:")
            stream = await run.get_stream()
            async for chunk in stream:
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"❌ Failed to run agent: {e}")
            error_str = str(e).lower()
            if "subscription plan" in error_str or "available models" in error_str:
                print("💡 Your current plan doesn't include access to the default model.")
                print("   Continuing with the next technique...")
            elif "permission" in error_str or "access denied" in error_str:
                print("💡 Access denied. Please check your plan permissions.")
                print("   Continuing with the next technique...")
            else:
                print("💡 Please check your configuration and try again.")
                print("   Continuing with the next technique...")
            continue

    # Demonstrate data collection and processing
    print(f"\n{'='*60}")
    print("📥 Data Collection & Processing")
    print(f"{'='*60}")

    collection_scenarios = [
        "Set up a data collection pipeline for gathering market research data from multiple sources.",
        "Create a web scraping strategy for collecting competitor pricing data and product information.",
        "Design a data validation and cleaning process for ensuring data quality and consistency.",
        "Implement a data storage and organization system for managing large datasets efficiently.",
        "Create automated data processing workflows for regular analysis and reporting.",
    ]

    for i, scenario in enumerate(collection_scenarios, 1):
        print(f"\n📥 Collection {i}: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate report generation
    print(f"\n{'='*60}")
    print("📋 Report Generation")
    print(f"{'='*60}")

    report_scenarios = [
        "Generate a comprehensive market analysis report with executive summary, methodology, findings, and recommendations.",
        "Create a financial performance dashboard with key metrics, trends, and visualizations.",
        "Produce a social media analytics report with engagement metrics, audience insights, and content recommendations.",
        "Develop a scientific research summary with key findings, statistical analysis, and future research directions.",
        "Create a business intelligence report with operational metrics, competitive analysis, and strategic recommendations.",
    ]

    for i, scenario in enumerate(report_scenarios, 1):
        print(f"\n📋 Report {i}: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate real-world applications
    print(f"\n{'='*60}")
    print("🌍 Real-World Applications")
    print(f"{'='*60}")

    application_scenarios = [
        "Design a customer analytics system for an e-commerce platform to track user behavior and optimize conversion rates.",
        "Create a supply chain analytics solution for monitoring inventory levels, demand forecasting, and optimization.",
        "Develop a healthcare analytics system for patient data analysis, treatment effectiveness, and outcome prediction.",
        "Build a marketing analytics platform for campaign performance tracking, ROI analysis, and customer segmentation.",
        "Design a financial risk assessment system for credit scoring, fraud detection, and investment analysis.",
    ]

    for i, scenario in enumerate(application_scenarios, 1):
        print(f"\n🌍 Application {i}: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get analysis summary
    print(f"\n{'='*60}")
    print("📊 Data Analysis Summary")
    print(f"{'='*60}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total analysis tasks: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n📊 Analysis types covered:")
    analysis_types = [
        "Market Research Analysis",
        "Financial Data Analysis",
        "Social Media Analytics",
        "Scientific Data Analysis",
        "Business Intelligence",
        "Statistical Analysis",
        "Time Series Analysis",
        "Predictive Modeling",
        "Pattern Recognition",
        "Data Visualization",
        "Data Collection & Processing",
        "Report Generation",
    ]

    for analysis_type in analysis_types:
        print(f"  ✅ {analysis_type}")

    print("\n🔬 Analysis techniques demonstrated:")
    techniques = [
        "Descriptive Statistics",
        "Inferential Statistics",
        "Hypothesis Testing",
        "Correlation Analysis",
        "Regression Analysis",
        "Trend Analysis",
        "Seasonal Decomposition",
        "Forecasting",
        "Anomaly Detection",
        "Clustering Analysis",
        "Classification",
        "Association Rules",
        "Feature Selection",
        "Model Validation",
        "Performance Evaluation",
    ]

    for technique in techniques:
        print(f"  - {technique}")

    print("\n🌍 Application domains covered:")
    domains = [
        "E-commerce Analytics",
        "Supply Chain Management",
        "Healthcare Analytics",
        "Marketing Analytics",
        "Financial Risk Assessment",
        "Customer Behavior Analysis",
        "Competitive Intelligence",
        "Research Analytics",
        "Social Media Intelligence",
        "Market Research",
    ]

    for domain in domains:
        print(f"  - {domain}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Data analysis example completed!")


if __name__ == "__main__":
    asyncio.run(main())
