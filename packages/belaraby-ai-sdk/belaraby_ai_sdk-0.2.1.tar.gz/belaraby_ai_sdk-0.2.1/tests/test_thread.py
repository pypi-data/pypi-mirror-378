"""Tests for thread functionality."""

from unittest.mock import MagicMock, patch

import pytest

from ba.thread import AgentRun, BAThread, Thread


class TestThread:
    """Test cases for Thread class."""

    @pytest.fixture
    def mock_thread(self, mock_threads_client):
        """Create a mock thread instance."""
        return Thread(mock_threads_client, "thread-123")

    @pytest.mark.asyncio
    async def test_add_message(self, mock_thread):
        """Test adding a message to thread."""
        mock_response = MagicMock()
        mock_response.message_id = "msg-123"
        mock_thread._client.add_message_to_thread.return_value = mock_response

        result = await mock_thread.add_message("Hello, world!")

        assert result == "msg-123"
        mock_thread._client.add_message_to_thread.assert_called_once_with(
            "thread-123", "Hello, world!"
        )

    @pytest.mark.asyncio
    async def test_delete_message(self, mock_thread):
        """Test deleting a message from thread."""
        await mock_thread.delete_message("msg-123")

        mock_thread._client.delete_message_from_thread.assert_called_once_with(
            "thread-123", "msg-123"
        )

    @pytest.mark.asyncio
    async def test_get_messages(self, mock_thread):
        """Test getting thread messages."""
        mock_messages = [
            MagicMock(message_id="msg-1"),
            MagicMock(message_id="msg-2"),
        ]
        mock_response = MagicMock()
        mock_response.messages = mock_messages
        mock_thread._client.get_thread_messages.return_value = mock_response

        result = await mock_thread.get_messages()

        assert result == mock_messages
        mock_thread._client.get_thread_messages.assert_called_once_with("thread-123")

    @pytest.mark.asyncio
    async def test_get_agent_runs_with_runs(self, mock_thread):
        """Test getting agent runs when runs exist."""
        mock_runs = [
            MagicMock(id="run-1"),
            MagicMock(id="run-2"),
        ]
        mock_response = MagicMock()
        mock_response.recent_agent_runs = mock_runs
        mock_thread._client.get_thread.return_value = mock_response

        result = await mock_thread.get_agent_runs()

        assert result is not None
        assert len(result) == 2
        assert all(isinstance(run, AgentRun) for run in result)
        assert result[0]._agent_run_id == "run-1"
        assert result[1]._agent_run_id == "run-2"

    @pytest.mark.asyncio
    async def test_get_agent_runs_without_runs(self, mock_thread):
        """Test getting agent runs when no runs exist."""
        mock_response = MagicMock()
        mock_response.recent_agent_runs = None
        mock_thread._client.get_thread.return_value = mock_response

        result = await mock_thread.get_agent_runs()

        assert result is None


class TestAgentRun:
    """Test cases for AgentRun class."""

    @pytest.fixture
    def mock_agent_run(self, mock_thread):
        """Create a mock agent run instance."""
        return AgentRun(mock_thread, "run-123")

    @pytest.mark.asyncio
    async def test_get_stream(self, mock_agent_run):
        """Test getting stream from agent run."""
        mock_stream_url = "http://example.com/stream"
        mock_threads_client = mock_agent_run._thread._client
        mock_threads_client.get_agent_run_stream_url.return_value = mock_stream_url

        # Mock the stream_from_url function
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"

        with patch("ba.thread.stream_from_url") as mock_stream_from_url:
            mock_stream_from_url.return_value = mock_stream()

            stream = await mock_agent_run.get_stream()

            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            assert chunks == ["chunk1", "chunk2", "chunk3"]
            mock_threads_client.get_agent_run_stream_url.assert_called_once_with(
                "run-123"
            )


class TestBAThread:
    """Test cases for BAThread class."""

    @pytest.fixture
    def mock_ba_thread(self, mock_threads_client):
        """Create a mock BAThread instance."""
        return BAThread(mock_threads_client)

    @pytest.mark.asyncio
    async def test_create_thread(self, mock_ba_thread):
        """Test creating a new thread."""
        mock_response = MagicMock()
        mock_response.thread_id = "thread-123"
        mock_ba_thread._client.create_thread.return_value = mock_response

        result = await mock_ba_thread.create("Test Thread")

        assert isinstance(result, Thread)
        assert result._thread_id == "thread-123"
        mock_ba_thread._client.create_thread.assert_called_once_with("Test Thread")

    @pytest.mark.asyncio
    async def test_create_thread_without_name(self, mock_ba_thread):
        """Test creating a thread without name."""
        mock_response = MagicMock()
        mock_response.thread_id = "thread-123"
        mock_ba_thread._client.create_thread.return_value = mock_response

        result = await mock_ba_thread.create()

        assert isinstance(result, Thread)
        assert result._thread_id == "thread-123"
        mock_ba_thread._client.create_thread.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_get_thread(self, mock_ba_thread):
        """Test getting an existing thread."""
        result = await mock_ba_thread.get("thread-123")

        assert isinstance(result, Thread)
        assert result._thread_id == "thread-123"

    @pytest.mark.asyncio
    async def test_delete_thread(self, mock_ba_thread):
        """Test deleting a thread."""
        await mock_ba_thread.delete("thread-123")

        mock_ba_thread._client.delete_thread.assert_called_once_with("thread-123")
