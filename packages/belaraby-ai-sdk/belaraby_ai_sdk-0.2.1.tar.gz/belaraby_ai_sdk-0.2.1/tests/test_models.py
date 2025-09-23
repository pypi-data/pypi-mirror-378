"""Tests for data models."""



from ba.models import (
    AgentRun,
    AssistantMessage,
    BaseMessage,
    ContentObject,
    MessageType,
    Role,
    UserMessage,
)


class TestRole:
    """Test cases for Role enum."""

    def test_role_values(self):
        """Test Role enum has correct values."""
        assert Role.USER == "user"
        assert Role.ASSISTANT == "assistant"
        assert Role.SYSTEM == "system"


class TestMessageType:
    """Test cases for MessageType enum."""

    def test_message_type_values(self):
        """Test MessageType enum has correct values."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.TOOL == "tool"
        assert MessageType.STATUS == "status"
        assert MessageType.ASSISTANT_RESPONSE_END == "assistant_response_end"


class TestContentObject:
    """Test cases for ContentObject."""

    def test_content_object_creation(self):
        """Test ContentObject creation."""
        content = ContentObject(
            role=Role.USER, content="Hello, world!", tool_calls=None
        )

        assert content.role == Role.USER
        assert content.content == "Hello, world!"
        assert content.tool_calls is None

    def test_content_object_with_tool_calls(self):
        """Test ContentObject with tool calls."""
        tool_calls = [{"name": "test_tool", "args": {"param": "value"}}]
        content = ContentObject(
            role=Role.ASSISTANT,
            content="I'll help you with that.",
            tool_calls=tool_calls,
        )

        assert content.role == Role.ASSISTANT
        assert content.content == "I'll help you with that."
        assert content.tool_calls == tool_calls


class TestBaseMessage:
    """Test cases for BaseMessage."""

    def test_base_message_creation(self):
        """Test BaseMessage creation."""
        message = BaseMessage(
            message_id="msg-123",
            thread_id="thread-123",
            type=MessageType.USER,
            is_llm_message=True,
            metadata={"key": "value"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert message.message_id == "msg-123"
        assert message.thread_id == "thread-123"
        assert message.type == MessageType.USER
        assert message.is_llm_message is True
        assert message.metadata == {"key": "value"}
        assert message.created_at == "2024-01-01T00:00:00Z"
        assert message.updated_at == "2024-01-01T00:00:00Z"

    def test_base_message_default_metadata(self):
        """Test BaseMessage with default metadata."""
        message = BaseMessage(
            message_id="msg-123",
            thread_id="thread-123",
            type=MessageType.USER,
            is_llm_message=True,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert message.metadata == {}


class TestUserMessage:
    """Test cases for UserMessage."""

    def test_user_message_creation(self):
        """Test UserMessage creation."""
        message = UserMessage(
            message_id="msg-123",
            thread_id="thread-123",
            type=MessageType.USER,
            is_llm_message=True,
            content='{"role": "user", "content": "Hello!"}',
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert message.type == MessageType.USER
        assert message.content == '{"role": "user", "content": "Hello!"}'


class TestAssistantMessage:
    """Test cases for AssistantMessage."""

    def test_assistant_message_creation(self):
        """Test AssistantMessage creation."""
        content_obj = ContentObject(
            role=Role.ASSISTANT, content="Hello! How can I help you?"
        )

        message = AssistantMessage(
            message_id="msg-123",
            thread_id="thread-123",
            type=MessageType.ASSISTANT,
            is_llm_message=True,
            content=content_obj,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert message.type == MessageType.ASSISTANT
        assert message.content.role == Role.ASSISTANT
        assert message.content.content == "Hello! How can I help you?"


class TestAgentRun:
    """Test cases for AgentRun."""

    def test_agent_run_creation(self):
        """Test AgentRun creation."""
        agent_run = AgentRun(
            id="run-123",
            thread_id="thread-123",
            status="completed",
            started_at="2024-01-01T00:00:00Z",
            completed_at="2024-01-01T00:01:00Z",
            error=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
        )

        assert agent_run.id == "run-123"
        assert agent_run.thread_id == "thread-123"
        assert agent_run.status == "completed"
        assert agent_run.started_at == "2024-01-01T00:00:00Z"
        assert agent_run.completed_at == "2024-01-01T00:01:00Z"
        assert agent_run.error is None

    def test_agent_run_with_error(self):
        """Test AgentRun with error."""
        error_data = {"code": "TIMEOUT", "message": "Request timed out"}
        agent_run = AgentRun(
            id="run-123",
            thread_id="thread-123",
            status="failed",
            started_at="2024-01-01T00:00:00Z",
            completed_at=None,
            error=error_data,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
        )

        assert agent_run.status == "failed"
        assert agent_run.error == error_data
        assert agent_run.completed_at is None
