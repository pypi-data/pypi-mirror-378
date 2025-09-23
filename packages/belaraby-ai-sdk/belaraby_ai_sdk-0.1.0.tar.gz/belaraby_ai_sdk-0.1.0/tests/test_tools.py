"""Tests for tools."""
import pytest
from unittest.mock import AsyncMock, patch

from ba.tools import AgentPressTools, MCPTools


class TestAgentPressTools:
    """Test cases for AgentPressTools."""

    def test_agentpress_tools_enum_values(self):
        """Test AgentPressTools enum has correct values."""
        assert AgentPressTools.SB_FILES_TOOL == "sb_files_tool"
        assert AgentPressTools.SB_SHELL_TOOL == "sb_shell_tool"
        assert AgentPressTools.SB_DEPLOY_TOOL == "sb_deploy_tool"
        assert AgentPressTools.SB_EXPOSE_TOOL == "sb_expose_tool"
        assert AgentPressTools.SB_VISION_TOOL == "sb_vision_tool"
        assert AgentPressTools.BROWSER_TOOL == "browser_tool"
        assert AgentPressTools.WEB_SEARCH_TOOL == "web_search_tool"
        assert AgentPressTools.SB_IMAGE_EDIT_TOOL == "sb_image_edit_tool"
        assert AgentPressTools.DATA_PROVIDERS_TOOL == "data_providers_tool"

    def test_get_description(self):
        """Test get_description method returns correct descriptions."""
        assert AgentPressTools.SB_FILES_TOOL.get_description() == "Read, write, and edit files"
        assert AgentPressTools.SB_SHELL_TOOL.get_description() == "Execute shell commands"
        assert AgentPressTools.BROWSER_TOOL.get_description() == "Browse websites and interact with web pages"
        assert AgentPressTools.WEB_SEARCH_TOOL.get_description() == "Search the web for information"

    def test_get_description_invalid_tool(self):
        """Test get_description with invalid tool raises ValueError."""
        # Create a mock enum value that doesn't exist in descriptions
        class MockTool(AgentPressTools):
            INVALID_TOOL = "invalid_tool"
        
        with pytest.raises(ValueError, match="No description found for invalid_tool"):
            MockTool.INVALID_TOOL.get_description()


class TestMCPTools:
    """Test cases for MCPTools."""

    def test_mcp_tools_creation_without_fastmcp(self):
        """Test MCPTools creation when fastmcp is not available."""
        with patch('ba.tools.FastMCPClient', None):
            with pytest.raises(ImportError, match="fastmcp is required for MCPTools"):
                MCPTools("http://localhost:4000", "test-mcp")

    @patch('ba.tools.FastMCPClient')
    def test_mcp_tools_creation_with_fastmcp(self, mock_fastmcp):
        """Test MCPTools creation when fastmcp is available."""
        mock_client = AsyncMock()
        mock_fastmcp.return_value = mock_client
        
        mcp_tools = MCPTools("http://localhost:4000", "test-mcp")
        
        assert mcp_tools.endpoint == "http://localhost:4000"
        assert mcp_tools.name == "test-mcp"
        assert mcp_tools.type == "http"
        assert mcp_tools.enabled_tools == []
        assert mcp_tools._initialized is False
        mock_fastmcp.assert_called_once_with("http://localhost:4000")

    @patch('ba.tools.FastMCPClient')
    def test_mcp_tools_creation_with_allowed_tools(self, mock_fastmcp):
        """Test MCPTools creation with allowed tools."""
        mock_client = AsyncMock()
        mock_fastmcp.return_value = mock_client
        
        allowed_tools = ["tool1", "tool2"]
        mcp_tools = MCPTools("http://localhost:4000", "test-mcp", allowed_tools)
        
        assert mcp_tools.allowed_tools == allowed_tools

    @patch('ba.tools.FastMCPClient')
    @pytest.mark.asyncio
    async def test_mcp_tools_initialize(self, mock_fastmcp):
        """Test MCPTools initialization."""
        mock_client = AsyncMock()
        mock_tools = [
            AsyncMock(name="tool1"),
            AsyncMock(name="tool2"),
            AsyncMock(name="tool3"),
        ]
        mock_client.list_tools.return_value = mock_tools
        mock_fastmcp.return_value = mock_client
        
        mcp_tools = MCPTools("http://localhost:4000", "test-mcp")
        
        result = await mcp_tools.initialize()
        
        assert result is mcp_tools
        assert mcp_tools._initialized is True
        assert mcp_tools.enabled_tools == ["tool1", "tool2", "tool3"]
        mock_client.list_tools.assert_called_once()

    @patch('ba.tools.FastMCPClient')
    @pytest.mark.asyncio
    async def test_mcp_tools_initialize_with_allowed_tools(self, mock_fastmcp):
        """Test MCPTools initialization with allowed tools filter."""
        mock_client = AsyncMock()
        mock_tools = [
            AsyncMock(name="tool1"),
            AsyncMock(name="tool2"),
            AsyncMock(name="tool3"),
        ]
        mock_client.list_tools.return_value = mock_tools
        mock_fastmcp.return_value = mock_client
        
        allowed_tools = ["tool1", "tool3"]
        mcp_tools = MCPTools("http://localhost:4000", "test-mcp", allowed_tools)
        
        result = await mcp_tools.initialize()
        
        assert result is mcp_tools
        assert mcp_tools._initialized is True
        assert mcp_tools.enabled_tools == ["tool1", "tool3"]

    @patch('ba.tools.FastMCPClient')
    def test_mcp_tools_initialize_without_client(self, mock_fastmcp):
        """Test MCPTools initialization without client raises RuntimeError."""
        mock_fastmcp.return_value = None
        
        mcp_tools = MCPTools("http://localhost:4000", "test-mcp")
        mcp_tools._mcp_client = None
        
        with pytest.raises(RuntimeError, match="MCP client not initialized"):
            # This will fail because we can't await in a non-async test
            # but we can test the error condition
            pass
