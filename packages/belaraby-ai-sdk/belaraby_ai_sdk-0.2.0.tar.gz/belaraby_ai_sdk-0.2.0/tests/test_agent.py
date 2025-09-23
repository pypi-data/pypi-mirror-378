"""Tests for agent functionality."""

from unittest.mock import MagicMock

import pytest

from ba.agent import Agent, BAAgent
from ba.api.agents import AgentCreateRequest, AgentUpdateRequest
from ba.tools import AgentPressTools, MCPTools


class TestAgent:
    """Test cases for Agent class."""

    @pytest.fixture
    def mock_agent(self, mock_agents_client):
        """Create a mock agent instance."""
        return Agent(mock_agents_client, "agent-123", "anthropic/claude-sonnet-4")

    @pytest.mark.asyncio
    async def test_agent_update_with_mcp_tools(self, mock_agent):
        """Test agent update with MCP tools."""
        mock_tool = MagicMock()
        mock_tool.name = "test-tool"
        mock_tool.type = "http"
        mock_tool.endpoint = "http://localhost:4000"
        mock_tool.enabled_tools = ["tool1", "tool2"]

        await mock_agent.update(
            name="Updated Agent",
            system_prompt="Updated prompt",
            mcp_tools=[mock_tool],
            allowed_tools=["tool1"],
        )

        mock_agent._client.update_agent.assert_called_once()
        call_args = mock_agent._client.update_agent.call_args
        assert call_args[0][0] == "agent-123"
        assert isinstance(call_args[0][1], AgentUpdateRequest)
        assert call_args[0][1].name == "Updated Agent"
        assert call_args[0][1].system_prompt == "Updated prompt"

    @pytest.mark.asyncio
    async def test_agent_update_with_agentpress_tools(self, mock_agent):
        """Test agent update with AgentPress tools."""
        agentpress_tool = AgentPressTools.SB_FILES_TOOL

        await mock_agent.update(
            name="Updated Agent",
            mcp_tools=[agentpress_tool],
            allowed_tools=["sb_files_tool"],
        )

        mock_agent._client.update_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_update_without_tools(self, mock_agent):
        """Test agent update without tools."""
        mock_details = MagicMock()
        mock_details.agentpress_tools = {}
        mock_details.custom_mcps = []
        mock_agent._client.get_agent.return_value = mock_details

        await mock_agent.update(name="Updated Agent")

        mock_agent._client.update_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_details(self, mock_agent):
        """Test getting agent details."""
        mock_details = MagicMock()
        mock_agent._client.get_agent.return_value = mock_details

        result = await mock_agent.details()

        assert result is mock_details
        mock_agent._client.get_agent.assert_called_once_with("agent-123")

    @pytest.mark.asyncio
    async def test_agent_run(self, mock_agent, mock_threads_client):
        """Test agent run."""
        from ba.thread import Thread

        thread = Thread(mock_threads_client, "thread-123")
        mock_response = MagicMock()
        mock_response.agent_run_id = "run-123"
        mock_threads_client.start_agent.return_value = mock_response

        result = await mock_agent.run("Hello, world!", thread)

        assert result._agent_run_id == "run-123"
        assert result._thread is thread
        mock_threads_client.add_message_to_thread.assert_called_once_with(
            "thread-123", "Hello, world!"
        )
        mock_threads_client.start_agent.assert_called_once()


class TestBAAgent:
    """Test cases for BAAgent class."""

    @pytest.fixture
    def mock_ba_agent(self, mock_agents_client):
        """Create a mock BAAgent instance."""
        return BAAgent(mock_agents_client)

    @pytest.mark.asyncio
    async def test_create_agent_with_mcp_tools(self, mock_ba_agent):
        """Test creating agent with MCP tools."""

        # Create a real MCPTools instance for testing
        mcp_tool = MCPTools(
            endpoint="http://localhost:4000",
            name="test-tool",
            allowed_tools=["tool1", "tool2"],
        )

        mock_response = MagicMock()
        mock_response.agent_id = "agent-123"
        mock_ba_agent._client.create_agent.return_value = mock_response

        result = await mock_ba_agent.create(
            name="Test Agent",
            system_prompt="You are a helpful assistant.",
            mcp_tools=[mcp_tool],
            allowed_tools=["tool1"],
        )

        assert isinstance(result, Agent)
        assert result._agent_id == "agent-123"
        mock_ba_agent._client.create_agent.assert_called_once()
        call_args = mock_ba_agent._client.create_agent.call_args
        assert isinstance(call_args[0][0], AgentCreateRequest)

    @pytest.mark.asyncio
    async def test_create_agent_with_agentpress_tools(self, mock_ba_agent):
        """Test creating agent with AgentPress tools."""
        agentpress_tool = AgentPressTools.SB_FILES_TOOL

        mock_response = MagicMock()
        mock_response.agent_id = "agent-123"
        mock_ba_agent._client.create_agent.return_value = mock_response

        result = await mock_ba_agent.create(
            name="Test Agent",
            system_prompt="You are a helpful assistant.",
            mcp_tools=[agentpress_tool],
            allowed_tools=["sb_files_tool"],
        )

        assert isinstance(result, Agent)
        assert result._agent_id == "agent-123"

    @pytest.mark.asyncio
    async def test_create_agent_without_tools(self, mock_ba_agent):
        """Test creating agent without tools."""
        mock_response = MagicMock()
        mock_response.agent_id = "agent-123"
        mock_ba_agent._client.create_agent.return_value = mock_response

        result = await mock_ba_agent.create(
            name="Test Agent", system_prompt="You are a helpful assistant."
        )

        assert isinstance(result, Agent)
        assert result._agent_id == "agent-123"

    @pytest.mark.asyncio
    async def test_create_agent_with_unknown_tool_type(self, mock_ba_agent):
        """Test creating agent with unknown tool type raises ValueError."""
        unknown_tool = "unknown_tool"

        with pytest.raises(ValueError, match="Unknown tool type"):
            await mock_ba_agent.create(
                name="Test Agent",
                system_prompt="You are a helpful assistant.",
                mcp_tools=[unknown_tool],
            )

    @pytest.mark.asyncio
    async def test_get_agent(self, mock_ba_agent):
        """Test getting an existing agent."""
        mock_response = MagicMock()
        mock_response.agent_id = "agent-123"
        mock_ba_agent._client.get_agent.return_value = mock_response

        result = await mock_ba_agent.get("agent-123")

        assert isinstance(result, Agent)
        assert result._agent_id == "agent-123"
        mock_ba_agent._client.get_agent.assert_called_once_with("agent-123")
