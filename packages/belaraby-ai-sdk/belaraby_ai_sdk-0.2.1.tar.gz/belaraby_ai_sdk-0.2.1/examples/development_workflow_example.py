#!/usr/bin/env python3
"""
Development workflow example for BelArabyAI SDK.

This example demonstrates a complete development workflow using multiple tools:
1. Project setup and initialization
2. Code development and testing
3. Application deployment
4. Service exposure and monitoring
5. Continuous integration practices
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

    # Create a development agent with all development tools
    print("\n🤖 Creating Development Agent...")
    agent = await client.Agent.create(
        name="Full-Stack Developer",
        system_prompt="""You are a full-stack developer with expertise in:
        - Project setup and configuration
        - Code development and testing
        - Application deployment
        - Service exposure and monitoring
        - DevOps and CI/CD practices
        Always follow best practices for security, performance, and maintainability.""",
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
    print(f"✅ Agent created with ID: {agent._agent_id}")

    # Create a conversation thread
    print("\n💬 Creating conversation thread...")
    thread = await client.Thread.create("Development Workflow Demo")
    print(f"✅ Thread created with ID: {thread._thread_id}")

    # Development workflow phases
    phases = [
        {
            "title": "🏗️ Phase 1: Project Setup",
            "message": """Set up a complete Python web application project with the following requirements:
            1. Create a Flask application with proper structure
            2. Set up virtual environment and dependencies
            3. Create configuration files (requirements.txt, .env, .gitignore)
            4. Initialize git repository
            5. Create basic project documentation

            Project name: 'task-manager-api'
            Features needed: REST API for task management with CRUD operations""",
        },
        {
            "title": "💻 Phase 2: Core Development",
            "message": """Develop the core application:
            1. Create Flask application with proper structure
            2. Implement Task model with fields: id, title, description, status, created_at, updated_at
            3. Create REST API endpoints:
               - GET /tasks (list all tasks)
               - POST /tasks (create new task)
               - GET /tasks/<id> (get specific task)
               - PUT /tasks/<id> (update task)
               - DELETE /tasks/<id> (delete task)
            4. Add proper error handling and validation
            5. Include API documentation""",
        },
        {
            "title": "🧪 Phase 3: Testing",
            "message": """Set up comprehensive testing:
            1. Create unit tests for all API endpoints
            2. Add integration tests
            3. Create test fixtures and mock data
            4. Set up test database
            5. Add test coverage reporting
            6. Create test documentation""",
        },
        {
            "title": "🚀 Phase 4: Deployment Preparation",
            "message": """Prepare for deployment:
            1. Create Dockerfile for containerization
            2. Add docker-compose.yml for local development
            3. Create production configuration
            4. Set up environment variables
            5. Add health check endpoints
            6. Create deployment documentation""",
        },
        {
            "title": "🌐 Phase 5: Deployment",
            "message": """Deploy the application:
            1. Deploy the Flask application to a cloud platform
            2. Set up database (SQLite for demo, but mention production options)
            3. Configure environment variables
            4. Test the deployed application
            5. Set up monitoring and logging""",
        },
        {
            "title": "🔗 Phase 6: Service Exposure",
            "message": """Expose the service:
            1. Expose the deployed application to the internet
            2. Set up custom domain (if possible)
            3. Configure SSL/TLS
            4. Test public access
            5. Document the public API endpoints""",
        },
    ]

    for i, phase in enumerate(phases, 1):
        print(f"\n{'='*80}")
        print(f"Phase {i}: {phase['title']}")
        print(f"{'='*80}")

        # Add message to thread
        await thread.add_message(phase["message"])

        # Run the agent
        run = await agent.run(phase["message"], thread)

        # Stream the response
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()  # New line after response

    # Demonstrate additional development practices
    print(f"\n{'='*80}")
    print("🔧 Additional Development Practices")
    print(f"{'='*80}")

    additional_scenarios = [
        {
            "title": "📊 Code Quality",
            "message": "Set up code quality tools: linting (flake8/pylint), formatting (black), type checking (mypy), and security scanning (bandit).",
        },
        {
            "title": "🔄 CI/CD Pipeline",
            "message": "Create a CI/CD pipeline configuration for GitHub Actions that includes: testing, linting, security checks, and deployment.",
        },
        {
            "title": "📈 Monitoring & Logging",
            "message": "Implement comprehensive monitoring and logging: application logs, error tracking, performance metrics, and health checks.",
        },
        {
            "title": "🔒 Security Hardening",
            "message": "Implement security best practices: input validation, authentication, rate limiting, CORS configuration, and security headers.",
        },
        {
            "title": "📚 Documentation",
            "message": "Create comprehensive documentation: API documentation (OpenAPI/Swagger), deployment guide, development setup, and user guide.",
        },
    ]

    for scenario in additional_scenarios:
        print(f"\n🔧 {scenario['title']}")
        await thread.add_message(scenario["message"])

        run = await agent.run(scenario["message"], thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Demonstrate troubleshooting
    print(f"\n{'='*80}")
    print("🔍 Troubleshooting & Maintenance")
    print(f"{'='*80}")

    troubleshooting_scenarios = [
        "The application is running slowly. Help me identify performance bottlenecks and optimize the code.",
        "I'm getting database connection errors. Help me diagnose and fix the issue.",
        "The deployment failed. Help me troubleshoot the deployment process and fix the issues.",
        "Users are reporting 500 errors. Help me set up proper error handling and debugging.",
    ]

    for scenario in troubleshooting_scenarios:
        print(f"\n🔍 Troubleshooting: {scenario}")
        await thread.add_message(scenario)

        run = await agent.run(scenario, thread)
        print("🤖 Agent response:")
        stream = await run.get_stream()
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()

    # Get development summary
    print(f"\n{'='*80}")
    print("📊 Development Workflow Summary")
    print(f"{'='*80}")

    messages = await thread.get_messages()
    runs = await thread.get_agent_runs()

    print(f"📋 Total development tasks: {len(messages)}")
    print(f"🏃 Total agent runs: {len(runs)}")

    print("\n🛠️ Development phases completed:")
    phases_completed = [
        "Project Setup",
        "Core Development",
        "Testing",
        "Deployment Preparation",
        "Deployment",
        "Service Exposure",
        "Code Quality",
        "CI/CD Pipeline",
        "Monitoring & Logging",
        "Security Hardening",
        "Documentation",
        "Troubleshooting",
    ]

    for phase in phases_completed:
        print(f"  ✅ {phase}")

    print("\n📦 Technologies and tools used:")
    technologies = [
        "Flask (Python web framework)",
        "SQLite (Database)",
        "Docker (Containerization)",
        "Git (Version control)",
        "pytest (Testing)",
        "Black (Code formatting)",
        "Flake8 (Linting)",
        "MyPy (Type checking)",
        "Bandit (Security scanning)",
        "GitHub Actions (CI/CD)",
        "OpenAPI/Swagger (API documentation)",
    ]

    for tech in technologies:
        print(f"  - {tech}")

    # Clean up
    print(f"\n🗑️ Cleaning up thread {thread._thread_id}...")
    await client.Thread.delete(thread._thread_id)
    print("✅ Thread deleted")

    print("\n✅ Development workflow example completed!")


if __name__ == "__main__":
    asyncio.run(main())
