from enum import Enum

from pydantic import BaseModel, ConfigDict

try:
    from fastmcp import Client as FastMCPClient
except ImportError:
    # Handle case where fastmcp is not installed
    FastMCPClient = None


class MCPTools(BaseModel):
    """MCP (Model Context Protocol) tools configuration."""

    endpoint: str
    name: str
    allowed_tools: list[str] | None = None
    type: str = "http"
    enabled_tools: list[str] = []
    _initialized: bool = False
    _mcp_client: object | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        endpoint: str,
        name: str,
        allowed_tools: list[str] | None = None,
        **kwargs,
    ):
        if FastMCPClient is None:
            raise ImportError(
                "fastmcp is required for MCPTools. Install it with: pip install fastmcp"
            )

        super().__init__(
            endpoint=endpoint, name=name, allowed_tools=allowed_tools, **kwargs
        )
        self._mcp_client = FastMCPClient(endpoint)

    async def initialize(self) -> "MCPTools":
        """Initialize the MCP client and discover available tools."""
        if self._mcp_client is None:
            raise RuntimeError("MCP client not initialized")

        async with self._mcp_client:
            tools = await self._mcp_client.list_tools()

        if self.allowed_tools:
            self.enabled_tools = [
                tool.name for tool in tools if tool.name in self.allowed_tools
            ]
        else:
            self.enabled_tools = [tool.name for tool in tools]

        self._initialized = True
        return self


class AgentPressTools(str, Enum):
    """Built-in AgentPress tools available for agents."""

    SB_FILES_TOOL = "sb_files_tool"
    SB_SHELL_TOOL = "sb_shell_tool"
    SB_DEPLOY_TOOL = "sb_deploy_tool"
    SB_EXPOSE_TOOL = "sb_expose_tool"
    SB_VISION_TOOL = "sb_vision_tool"
    BROWSER_TOOL = "browser_tool"
    WEB_SEARCH_TOOL = "web_search_tool"
    SB_IMAGE_EDIT_TOOL = "sb_image_edit_tool"
    DATA_PROVIDERS_TOOL = "data_providers_tool"

    def get_description(self) -> str:
        """Get the description for this tool."""
        descriptions = {
            "sb_files_tool": "Read, write, and edit files",
            "sb_shell_tool": "Execute shell commands",
            "sb_deploy_tool": "Deploy web applications",
            "sb_expose_tool": "Expose local services to the internet",
            "sb_vision_tool": "Analyze and understand images",
            "browser_tool": "Browse websites and interact with web pages",
            "web_search_tool": "Search the web for information",
            "sb_image_edit_tool": "Edit and manipulate images",
            "data_providers_tool": "Access structured data from various providers",
        }

        desc = descriptions.get(self.value)
        if not desc:
            raise ValueError(f"No description found for {self.value}")
        return desc


# Type alias for all supported tool types
BAMCPTools = AgentPressTools | MCPTools
