
from .api.agents import (
    AgentCreateRequest,
    AgentPress_ToolConfig,
    AgentsClient,
    AgentUpdateRequest,
    CustomMCP,
    MCPConfig,
)
from .api.threads import AgentStartRequest
from .thread import AgentRun, Thread
from .tools import AgentPressTools, BAMCPTools, MCPTools


class Agent:
    def __init__(
        self,
        client: AgentsClient,
        agent_id: str,
        model: str = "openrouter/moonshotai/kimi-k2",
    ):
        self._client = client
        self._agent_id = agent_id
        self._model = model

    async def update(
        self,
        name: str | None = None,
        system_prompt: str | None = None,
        mcp_tools: list[BAMCPTools] | None = None,
        allowed_tools: list[str] | None = None,
    ) -> None:
        """Update agent configuration."""
        if mcp_tools:
            agentpress_tools = {}
            custom_mcps: list[CustomMCP] = []
            for tool in mcp_tools:
                if isinstance(tool, AgentPressTools):
                    is_enabled = tool.value in allowed_tools if allowed_tools else True
                    agentpress_tools[tool] = AgentPress_ToolConfig(
                        enabled=is_enabled, description=tool.get_description()
                    )
                elif isinstance(tool, MCPTools):
                    is_enabled = tool.name in allowed_tools if allowed_tools else True
                    custom_mcps.append(
                        CustomMCP(
                            name=tool.name,
                            type=tool.type,
                            config=MCPConfig(url=tool.endpoint),
                            enabled_tools=tool.enabled_tools if is_enabled else [],
                        )
                    )
        else:
            agent_details = await self.details()
            agentpress_tools = agent_details.agentpress_tools or {}
            custom_mcps = agent_details.custom_mcps or []
            if allowed_tools:
                for tool in agentpress_tools:
                    if tool.value not in allowed_tools:
                        agentpress_tools[tool].enabled = False
                for mcp in custom_mcps:
                    mcp.enabled_tools = allowed_tools

        await self._client.update_agent(
            self._agent_id,
            AgentUpdateRequest(
                name=name,
                system_prompt=system_prompt,
                custom_mcps=custom_mcps,
                agentpress_tools=agentpress_tools,
            ),
        )

    async def details(self):
        response = await self._client.get_agent(self._agent_id)
        return response

    async def run(
        self,
        prompt: str,
        thread: Thread,
        model: str | None = None,
    ):
        await thread.add_message(prompt)
        response = await thread._client.start_agent(
            thread._thread_id,
            AgentStartRequest(
                agent_id=self._agent_id,
                model_name=model or self._model,
            ),
        )
        return AgentRun(thread, response.agent_run_id)


class BAAgent:
    def __init__(self, client: AgentsClient):
        self._client = client

    async def create(
        self,
        name: str,
        system_prompt: str,
        mcp_tools: list[BAMCPTools] = None,
        allowed_tools: list[str] | None = None,
    ) -> "Agent":
        """Create a new agent."""
        if mcp_tools is None:
            mcp_tools = []

        agentpress_tools = {}
        custom_mcps: list[CustomMCP] = []

        for tool in mcp_tools:
            if isinstance(tool, AgentPressTools):
                is_enabled = tool.value in allowed_tools if allowed_tools else True
                agentpress_tools[tool] = AgentPress_ToolConfig(
                    enabled=is_enabled, description=tool.get_description()
                )
            elif isinstance(tool, MCPTools):
                is_enabled = tool.name in allowed_tools if allowed_tools else True
                custom_mcps.append(
                    CustomMCP(
                        name=tool.name,
                        type=tool.type,
                        config=MCPConfig(url=tool.endpoint),
                        enabled_tools=tool.enabled_tools if is_enabled else [],
                    )
                )
            else:
                raise ValueError(f"Unknown tool type: {type(tool)}")

        agent = await self._client.create_agent(
            AgentCreateRequest(
                name=name,
                system_prompt=system_prompt,
                custom_mcps=custom_mcps,
                agentpress_tools=agentpress_tools,
            )
        )

        return Agent(self._client, agent.agent_id)

    async def get(self, agent_id: str) -> "Agent":
        """Get an existing agent by ID."""
        agent = await self._client.get_agent(agent_id)
        return Agent(self._client, agent.agent_id)
