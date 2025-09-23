"""Test configuration and fixtures."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from ba.ba import BASdk
from ba.tools import AgentPressTools, MCPTools


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_api_url():
    """Mock API URL for testing."""
    return "https://test.belaraby.ai"


@pytest.fixture
def mock_agents_client():
    """Mock agents client."""
    client = AsyncMock()
    client.create_agent = AsyncMock()
    client.get_agent = AsyncMock()
    client.update_agent = AsyncMock()
    return client


@pytest.fixture
def mock_threads_client():
    """Mock threads client."""
    client = AsyncMock()
    client.create_thread = AsyncMock()
    client.get_thread = AsyncMock()
    client.delete_thread = AsyncMock()
    client.add_message_to_thread = AsyncMock()
    client.delete_message_from_thread = AsyncMock()
    client.get_thread_messages = AsyncMock()
    client.start_agent = AsyncMock()
    client.get_agent_run_stream_url = MagicMock()
    client.headers = {"Authorization": "Bearer test-key"}
    return client


@pytest.fixture
def mock_sdk(mock_api_key, mock_api_url, mock_agents_client, mock_threads_client):
    """Mock SDK instance."""
    sdk = BASdk(mock_api_key, mock_api_url)
    sdk._agents_client = mock_agents_client
    sdk._threads_client = mock_threads_client
    return sdk


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "agent_id": "agent-123",
        "name": "Test Agent",
        "system_prompt": "You are a helpful assistant.",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_thread_data():
    """Sample thread data for testing."""
    return {
        "thread_id": "thread-123",
        "name": "Test Thread",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "message_id": "msg-123",
        "thread_id": "thread-123",
        "type": "user",
        "content": "Hello, world!",
        "is_llm_message": True,
        "metadata": {},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
