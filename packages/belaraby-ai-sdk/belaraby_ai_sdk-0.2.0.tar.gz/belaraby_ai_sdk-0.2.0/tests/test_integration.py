"""Integration tests for the SDK."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ba.api.agents import AgentUpdateRequest
from ba.ba import BASdk
from ba.tools import AgentPressTools, MCPTools


class TestSDKIntegration:
    """Integration tests for the complete SDK workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test a complete workflow from SDK creation to agent execution."""
        # Mock all the API clients
        mock_agents_client = AsyncMock()
        mock_threads_client = AsyncMock()

        # Mock agent creation response
        mock_agent_response = MagicMock()
        mock_agent_response.agent_id = "agent-123"
        mock_agents_client.create_agent.return_value = mock_agent_response

        # Mock thread creation response
        mock_thread_response = MagicMock()
        mock_thread_response.thread_id = "thread-123"
        mock_threads_client.create_thread.return_value = mock_thread_response

        # Mock message addition response
        mock_message_response = MagicMock()
        mock_message_response.message_id = "msg-123"
        mock_threads_client.add_message_to_thread.return_value = mock_message_response

        # Mock agent start response
        mock_start_response = MagicMock()
        mock_start_response.agent_run_id = "run-123"
        mock_threads_client.start_agent.return_value = mock_start_response

        # Mock stream URL
        mock_threads_client.get_agent_run_stream_url = MagicMock(
            return_value="http://example.com/stream"
        )
        mock_threads_client.headers = {"Authorization": "Bearer test-key"}

        # Mock stream response
        async def mock_stream():
            yield "Hello! "
            yield "How can I "
            yield "help you?"

        with (
            patch("ba.ba.agents.create_agents_client", return_value=mock_agents_client),
            patch(
                "ba.ba.threads.create_threads_client", return_value=mock_threads_client
            ),
            patch(
                "ba.thread.stream_from_url", return_value=mock_stream()
            ),
        ):

            # Initialize SDK
            sdk = BASdk("test-api-key")

            # Create agent with tools
            agent = await sdk.Agent.create(
                name="Test Assistant",
                system_prompt="You are a helpful AI assistant.",
                mcp_tools=[AgentPressTools.SB_FILES_TOOL],
                allowed_tools=["sb_files_tool"],
            )

            # Create thread
            thread = await sdk.Thread.create("Test Conversation")

            # Run agent
            run = await agent.run("Hello, how are you?", thread)

            # Stream response
            stream = await run.get_stream()
            response_chunks = []
            async for chunk in stream:
                response_chunks.append(chunk)

            # Verify the workflow
            assert agent._agent_id == "agent-123"
            assert thread._thread_id == "thread-123"
            assert run._agent_run_id == "run-123"
            assert "".join(response_chunks) == "Hello! How can I help you?"

            # Verify API calls were made
            mock_agents_client.create_agent.assert_called_once()
            mock_threads_client.create_thread.assert_called_once()
            mock_threads_client.add_message_to_thread.assert_called_once()
            mock_threads_client.start_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_tools_integration(self):
        """Test MCP tools integration."""
        # Mock MCP client
        mock_mcp_client = AsyncMock()
        mock_tools = [
            MagicMock(),
            MagicMock(),
        ]
        mock_tools[0].name = "get_weather"
        mock_tools[1].name = "send_email"
        mock_mcp_client.list_tools.return_value = mock_tools

        with patch("ba.tools.FastMCPClient", return_value=mock_mcp_client):
            # Create MCP tools
            mcp_tools = MCPTools(
                endpoint="http://localhost:4000",
                name="weather-mcp",
                allowed_tools=["get_weather"],
            )

            # Initialize tools
            await mcp_tools.initialize()

            # Verify initialization
            assert mcp_tools._initialized is True
            assert mcp_tools.enabled_tools == ["get_weather"]
            assert "send_email" not in mcp_tools.enabled_tools

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in the SDK."""
        # Test invalid API key
        with pytest.raises(ValueError, match="API key is required"):
            BASdk("")

        # Test MCP tools without fastmcp
        with patch("ba.tools.FastMCPClient", None):
            with pytest.raises(ImportError, match="fastmcp is required"):
                MCPTools("http://localhost:4000", "test-mcp")

    @pytest.mark.asyncio
    async def test_agent_update_workflow(self):
        """Test agent update workflow."""
        mock_agents_client = AsyncMock()
        mock_threads_client = AsyncMock()

        # Mock agent details response
        mock_details = MagicMock()
        mock_details.agentpress_tools = {
            AgentPressTools.SB_FILES_TOOL: MagicMock(enabled=True),
            AgentPressTools.SB_SHELL_TOOL: MagicMock(enabled=True),
        }
        mock_details.custom_mcps = []
        mock_agents_client.get_agent.return_value = mock_details

        with (
            patch("ba.ba.agents.create_agents_client", return_value=mock_agents_client),
            patch(
                "ba.ba.threads.create_threads_client", return_value=mock_threads_client
            ),
        ):

            from ba.agent import Agent

            agent = Agent(mock_agents_client, "agent-123")

            # Update agent with new allowed tools
            await agent.update(name="Updated Agent", allowed_tools=["sb_files_tool"])

            # Verify update was called
            mock_agents_client.update_agent.assert_called_once()
            call_args = mock_agents_client.update_agent.call_args
            assert call_args[0][0] == "agent-123"
            assert isinstance(call_args[0][1], AgentUpdateRequest)
            assert call_args[0][1].name == "Updated Agent"
