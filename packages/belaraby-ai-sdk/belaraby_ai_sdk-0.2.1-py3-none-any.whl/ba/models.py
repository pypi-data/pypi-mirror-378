from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Message roles in the conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Types of messages in the conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    STATUS = "status"
    ASSISTANT_RESPONSE_END = "assistant_response_end"


class ContentObject(BaseModel):
    """Content object for messages."""

    role: Role
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class BaseMessage(BaseModel):
    """Base message class."""

    message_id: str
    thread_id: str
    type: MessageType
    is_llm_message: bool
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class UserMessage(BaseMessage):
    """User message."""

    type: MessageType = MessageType.USER
    content: str  # JSON string of ContentObject


class AssistantMessage(BaseMessage):
    """Assistant message."""

    type: MessageType = MessageType.ASSISTANT
    content: ContentObject


class ToolResultMessage(BaseMessage):
    """Tool result message."""

    type: MessageType = MessageType.TOOL
    content: dict[
        str, str | Any
    ]  # role: "user", content: JSON string of ToolExecutionResult


class StatusMessage(BaseMessage):
    """Status message."""

    type: MessageType = MessageType.STATUS
    content: dict[str, Any]  # status_type and other fields


class AssistantResponseEndMessage(BaseMessage):
    """Assistant response end message."""

    type: MessageType = MessageType.ASSISTANT_RESPONSE_END
    content: dict[str, Any]  # model, usage, etc.


ChatMessage = (
    UserMessage
    | AssistantMessage
    | ToolResultMessage
    | StatusMessage
    | AssistantResponseEndMessage
)


class AgentRun(BaseModel):
    """Agent run information."""

    id: str
    thread_id: str
    status: str
    started_at: str | None = None
    completed_at: str | None = None
    error: dict[str, Any] | None = None
    created_at: str
    updated_at: str
