from typing import Optional, Union, Dict, Any, List
from enum import Enum
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
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class BaseMessage(BaseModel):
    """Base message class."""
    message_id: str
    thread_id: str
    type: MessageType
    is_llm_message: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)
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
    content: Dict[str, Union[str, Any]]  # role: "user", content: JSON string of ToolExecutionResult


class StatusMessage(BaseMessage):
    """Status message."""
    type: MessageType = MessageType.STATUS
    content: Dict[str, Any]  # status_type and other fields


class AssistantResponseEndMessage(BaseMessage):
    """Assistant response end message."""
    type: MessageType = MessageType.ASSISTANT_RESPONSE_END
    content: Dict[str, Any]  # model, usage, etc.


ChatMessage = Union[
    UserMessage,
    AssistantMessage,
    ToolResultMessage,
    StatusMessage,
    AssistantResponseEndMessage,
]


class AgentRun(BaseModel):
    """Agent run information."""
    id: str
    thread_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
