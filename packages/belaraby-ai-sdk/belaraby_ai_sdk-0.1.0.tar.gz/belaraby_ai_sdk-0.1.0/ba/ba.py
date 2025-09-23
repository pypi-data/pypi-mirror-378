from typing import Optional
from .api import agents, threads
from .agent import BAAgent
from .thread import BAThread
from .tools import AgentPressTools, MCPTools


class BASdk:
    """
    BelArabyAI SDK main client.
    
    This is the main entry point for interacting with the BelArabyAI platform.
    It provides access to agents and threads for creating and managing AI workers.
    
    Args:
        api_key: Your BelArabyAI API key
        api_url: Base URL for the BelArabyAI API (default: "https://belaraby.ai")
    """
    
    def __init__(self, api_key: str, api_url: str = "https://belaraby.ai"):
        if not api_key:
            raise ValueError("API key is required")
        
        self._api_key = api_key
        self._api_url = api_url
        self._agents_client = agents.create_agents_client(api_url, api_key)
        self._threads_client = threads.create_threads_client(api_url, api_key)

        self.Agent = BAAgent(self._agents_client)
        self.Thread = BAThread(self._threads_client)
    
    @property
    def api_key(self) -> str:
        """Get the API key (masked for security)."""
        return f"{self._api_key[:8]}...{self._api_key[-4:]}" if len(self._api_key) > 12 else "***"
    
    @property
    def api_url(self) -> str:
        """Get the API URL."""
        return self._api_url
