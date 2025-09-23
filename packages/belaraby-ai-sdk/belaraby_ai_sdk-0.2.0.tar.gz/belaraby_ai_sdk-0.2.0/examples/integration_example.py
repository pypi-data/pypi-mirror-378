#!/usr/bin/env python3
"""
Integration example for BelArabyAI SDK.

This example demonstrates integration with external services and APIs:
1. Database integration
2. External API integration
3. Cloud service integration
4. Third-party tool integration
5. Custom service integration
"""

import asyncio
import os

from ba.ba import BASdk
from ba.tools import AgentPressTools, MCPTools


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

    # Create an integration agent
    print("\n🤖 Creating Integration Agent...")
    agent = await client.Agent.create(
        name="Integration Specialist",
        system_prompt="""You are an integration specialist with expertise in:
        - Database integration and management
        - External API integration
        - Cloud service integration
        - Third-party tool integration
        - Custom service integration
        - Data synchronization and ETL processes
        Always provide secure, scalable, and maintainable integration solutions.""",
        mcp_tools=[
            AgentPressTools.SB_FILES_TOOL,
            AgentPressTools.SB_SHELL_TOOL,
            AgentPressTools.WEB_SEARCH_TOOL,
            AgentPressTools.DATA_PROVIDERS_TOOL,
        ],
        allowed_tools=[
            "sb_files_tool",
            "sb_shell_tool",
            "web_search_tool",
            "data_providers_tool",
        ],
    )
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Integration Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Integration scenarios
    scenarios = [
        {
            "title": "🗄️ Database Integration",
            "message": """Set up comprehensive database integration:
            1. Design database schema for a customer management system
            2. Create connection configurations for different database types (PostgreSQL, MySQL, SQLite)
            3. Implement CRUD operations with proper error handling
            4. Set up database migrations and versioning
            5. Create data validation and sanitization
            6. Implement connection pooling and performance optimization

            Include security best practices and backup strategies.""",
        },
        {
            "title": "🌐 External API Integration",
            "message": """Design external API integration patterns:
            1. REST API integration with authentication (API keys, OAuth, JWT)
            2. GraphQL API integration and query optimization
            3. Webhook handling and event processing
            4. Rate limiting and retry mechanisms
            5. API versioning and backward compatibility
            6. Error handling and fallback strategies

            Provide examples for popular APIs (GitHub, Stripe, SendGrid, etc.).""",
        },
        {
            "title": "☁️ Cloud Service Integration",
            "message": """Implement cloud service integration:
            1. AWS services integration (S3, Lambda, RDS, DynamoDB)
            2. Google Cloud integration (Storage, Functions, BigQuery)
            3. Azure services integration (Blob Storage, Functions, Cosmos DB)
            4. Container orchestration (Docker, Kubernetes)
            5. Serverless function deployment
            6. Cloud monitoring and logging

            Include cost optimization and security considerations.""",
        },
        {
            "title": "🔧 Third-Party Tool Integration",
            "message": """Integrate with third-party tools:
            1. CRM systems (Salesforce, HubSpot, Pipedrive)
            2. Project management tools (Jira, Trello, Asana)
            3. Communication platforms (Slack, Discord, Microsoft Teams)
            4. Analytics tools (Google Analytics, Mixpanel, Amplitude)
            5. Payment processors (Stripe, PayPal, Square)
            6. Email services (SendGrid, Mailgun, AWS SES)

            Focus on authentication, data synchronization, and error handling.""",
        },
        {
            "title": "🔄 Data Synchronization",
            "message": """Create data synchronization solutions:
            1. Real-time data synchronization patterns
            2. Batch processing and ETL pipelines
            3. Data transformation and mapping
            4. Conflict resolution strategies
            5. Data quality monitoring and validation
            6. Incremental sync and change detection

            Include performance optimization and monitoring.""",
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

    # Demonstrate specific integration patterns
    print(f"\n{'='*60}")
    print("🔗 Specific Integration Patterns")
    print(f"{'='*60}")

    pattern_scenarios = [
        {
            "title": "🔐 Authentication Patterns",
            "message": "Implement various authentication patterns: API key management, OAuth 2.0 flow, JWT token handling, session management, and multi-factor authentication.",
        },
        {
            "title": "📊 Data Pipeline Design",
            "message": "Design data pipelines: data ingestion, transformation, validation, storage, and delivery. Include error handling, monitoring, and alerting.",
        },
        {
            "title": "🔄 Event-Driven Architecture",
            "message": "Implement event-driven integration: message queues, event streaming, webhook processing, and real-time data synchronization.",
        },
        {
            "title": "🛡️ Security Integration",
            "message": "Integrate security measures: encryption, secure communication, access control, audit logging, and compliance requirements.",
        },
        {
            "title": "📈 Monitoring & Observability",
            "message": "Set up monitoring and observability: metrics collection, logging, tracing, alerting, and performance monitoring.",
        },
    ]

    for scenario in pattern_scenarios:
        print(f"\n🔗 {scenario['title']}")
        await thread.add_message(scenario["message"])

        run = await agent.run(scenario["message"], thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate custom MCP tool integration
    print(f"\n{'='*60}")
    print("🛠️ Custom MCP Tool Integration")
    print(f"{'='*60}")

    try:
        # Create custom MCP tools for different services
        print("🔧 Setting up custom MCP tools...")

        # Example: Database MCP tool
        _db_tools = MCPTools(
            endpoint="http://localhost:4001/mcp/",  # Database service
            name="database-service",
            allowed_tools=[
                "query_database",
                "create_table",
                "insert_data",
                "update_data",
                "delete_data",
            ],
        )

        # Example: External API MCP tool
        _api_tools = MCPTools(
            endpoint="http://localhost:4002/mcp/",  # API service
            name="api-service",
            allowed_tools=[
                "make_request",
                "handle_webhook",
                "process_response",
                "manage_auth",
            ],
        )

        # Example: Cloud service MCP tool
        _cloud_tools = MCPTools(
            endpoint="http://localhost:4003/mcp/",  # Cloud service
            name="cloud-service",
            allowed_tools=[
                "upload_file",
                "deploy_function",
                "manage_resources",
                "monitor_services",
            ],
        )

        print("✅ Custom MCP tools configured")

        # Demonstrate integration with custom tools
        integration_scenarios = [
            "Create a database integration using the database MCP tool for user management",
            "Set up API integration using the API MCP tool for external service communication",
            "Implement cloud integration using the cloud MCP tool for file storage and processing",
        ]

        for scenario in integration_scenarios:
            print(f"\n🛠️ Custom Integration: {scenario}")
            await thread.add_message(scenario)

            run = await agent.run(scenario, thread)
            print("🤖 Agent response:")
            stream = await run.get_stream()
            async for chunk in stream:
                print(chunk, end="", flush=True)
            print()

    except ImportError:
        print("⚠️ Custom MCP tools require fastmcp: pip install fastmcp")
    except Exception as e:
        print(f"⚠️ Custom MCP tools setup failed: {e}")
        print("💡 Make sure your MCP servers are running on the specified ports")

    # Demonstrate real-world integration scenarios
    print(f"\n{'='*60}")
    print("🌍 Real-World Integration Scenarios")
    print(f"{'='*60}")

    realworld_scenarios = [
        "Design a complete e-commerce integration system connecting inventory management, payment processing, shipping, and customer service.",
        "Create a healthcare data integration platform connecting electronic health records, lab systems, and patient portals.",
        "Build a financial services integration hub connecting banking systems, payment processors, and regulatory reporting systems.",
        "Design a manufacturing integration system connecting ERP, MES, quality management, and supply chain systems.",
        "Create a media and entertainment integration platform connecting content management, distribution, analytics, and monetization systems.",
    ]

    for i, scenario in enumerate(realworld_scenarios, 1):
        print(f"\n🌍 Scenario {i}: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate troubleshooting and maintenance
    print(f"\n{'='*60}")
    print("🔧 Integration Troubleshooting")
    print(f"{'='*60}")

    troubleshooting_scenarios = [
        "Integration is failing due to API rate limits. Help me implement proper rate limiting and retry mechanisms.",
        "Database connections are timing out. Guide me through connection pooling and timeout configuration.",
        "Data synchronization is inconsistent. Help me implement proper conflict resolution and data validation.",
        "External API changes are breaking our integration. Help me implement versioning and backward compatibility.",
        "Integration performance is slow. Guide me through optimization techniques and monitoring setup.",
    ]

    for scenario in troubleshooting_scenarios:
        print(f"\n🔧 Troubleshooting: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get integration summary
    print(f"\n{'='*60}")
    print("📊 Integration Summary")
    print(f"{'='*60}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total integration tasks: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n🔗 Integration types covered:")
    integration_types = [
        "Database Integration",
        "External API Integration",
        "Cloud Service Integration",
        "Third-Party Tool Integration",
        "Data Synchronization",
        "Authentication Patterns",
        "Data Pipeline Design",
        "Event-Driven Architecture",
        "Security Integration",
        "Monitoring & Observability",
        "Custom MCP Tool Integration",
        "Real-World Scenarios",
        "Troubleshooting & Maintenance",
    ]

    for integration_type in integration_types:
        print(f"  ✅ {integration_type}")

    print("\n🛠️ Integration technologies covered:")
    technologies = [
        "PostgreSQL, MySQL, SQLite",
        "REST APIs, GraphQL",
        "AWS, Google Cloud, Azure",
        "Docker, Kubernetes",
        "Salesforce, HubSpot",
        "Jira, Trello, Asana",
        "Slack, Discord, Teams",
        "Google Analytics, Mixpanel",
        "Stripe, PayPal, Square",
        "SendGrid, Mailgun",
        "OAuth 2.0, JWT",
        "Message Queues, Webhooks",
        "ETL Pipelines",
        "Monitoring & Logging",
    ]

    for tech in technologies:
        print(f"  - {tech}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Integration example completed!")


if __name__ == "__main__":
    asyncio.run(main())
