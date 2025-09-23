from typing import AsyncGenerator, Optional, List
from .api.threads import ThreadsClient
from .api.utils import stream_from_url
from .models import ChatMessage


class Thread:
    """A conversation thread for agent interactions."""
    
    def __init__(self, client: ThreadsClient, thread_id: str):
        self._client = client
        self._thread_id = thread_id

    async def add_message(self, message: str) -> str:
        """Add a message to the thread."""
        response = await self._client.add_message_to_thread(self._thread_id, message)
        return response.message_id

    async def delete_message(self, message_id: str) -> None:
        """Delete a message from the thread."""
        await self._client.delete_message_from_thread(self._thread_id, message_id)

    async def get_messages(self) -> List[ChatMessage]:
        """Get all messages in the thread."""
        response = await self._client.get_thread_messages(self._thread_id)
        return response.messages

    async def get_agent_runs(self) -> Optional[List["AgentRun"]]:
        """Get recent agent runs for this thread."""
        response = await self._client.get_thread(self._thread_id)
        if not response.recent_agent_runs:
            return None
        return [AgentRun(self, run.id) for run in response.recent_agent_runs]


class AgentRun:
    """An agent run within a thread."""
    
    def __init__(self, thread: Thread, agent_run_id: str):
        self._thread = thread
        self._agent_run_id = agent_run_id

    async def get_stream(self) -> AsyncGenerator[str, None]:
        """Get a streaming response from the agent run."""
        stream_url = self._thread._client.get_agent_run_stream_url(self._agent_run_id)
        stream = stream_from_url(stream_url, headers=self._thread._client.headers)
        return stream


class BAThread:
    """Thread management client."""
    
    def __init__(self, client: ThreadsClient):
        self._client = client

    async def create(self, name: Optional[str] = None) -> Thread:
        """Create a new thread."""
        thread_data = await self._client.create_thread(name)
        return Thread(self._client, thread_data.thread_id)

    async def get(self, thread_id: str) -> Thread:
        """Get an existing thread by ID."""
        return Thread(self._client, thread_id)

    async def delete(self, thread_id: str) -> None:
        """Delete a thread."""
        await self._client.delete_thread(thread_id)
