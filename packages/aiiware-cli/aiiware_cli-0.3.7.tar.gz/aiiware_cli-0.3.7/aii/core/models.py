"""Core data models and enums for AII."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class OSType(Enum):
    """Supported operating systems."""

    MACOS = "mac"
    LINUX = "linux"
    UNKNOWN = "unknown"


class ShellType(Enum):
    """Supported shell types."""

    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    CSH = "csh"
    TCSH = "tcsh"
    KSH = "ksh"
    DASH = "dash"
    SH = "sh"


class AIMode(Enum):
    """Supported AI operation modes."""

    SHELL = "shell"
    TRANSLATE = "translate"
    EXPLAIN = "explain"
    CODE = "code"
    WRITE = "write"
    ANALYZE = "analyze"
    GIT_COMMIT = "git_commit"
    GIT_PR = "git_pr"
    GIT_REVIEW = "git_review"


class ProviderType(Enum):
    """Supported AI provider types."""

    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass(frozen=True)
class EnvironmentContext:
    """Immutable context about the user's environment."""

    os_type: OSType
    shell_type: ShellType
    ai_mode: AIMode
    is_detected: bool = True
    confidence: float = 1.0
    target_language: str | None = None
    provider_type: ProviderType = ProviderType.GOOGLE  # Default to Google
    model_name: str | None = None

    def __str__(self) -> str:
        provider_info = f"{self.provider_type.value}"
        if self.model_name:
            provider_info += f":{self.model_name}"

        if self.ai_mode == AIMode.SHELL:
            status = "detected" if self.is_detected else "overridden"
            return f"{self.os_type.value}/{self.shell_type.value} ({status}) • {provider_info}"
        elif self.ai_mode == AIMode.TRANSLATE and self.target_language:
            return f"translate to {self.target_language} • {provider_info}"
        else:
            return f"{self.ai_mode.value} mode • {provider_info}"


@dataclass(frozen=True)
class AIRequest:
    """Immutable request for AI processing."""

    prompt: str
    context: EnvironmentContext
    require_confirmation: bool = True

    @property
    def sanitized_prompt(self) -> str:
        """Get sanitized version of the prompt."""
        return " ".join(self.prompt.split())


@dataclass
class AIResponse:
    """Response containing AI-generated content and metadata."""

    success: bool
    content: str | None = None
    explanation: str | None = None
    error_message: str | None = None
    confidence: float = 0.0
    mode: AIMode = AIMode.SHELL

    @property
    def is_safe_to_execute(self) -> bool:
        """Check if content appears safe to execute (for shell commands only)."""
        if self.mode != AIMode.SHELL or not self.content:
            return False

        dangerous_patterns = ["rm -rf", "sudo rm", "format", "mkfs", ":(){"]
        return not any(
            pattern in self.content.lower() for pattern in dangerous_patterns
        )

    @property
    def is_executable(self) -> bool:
        """Check if this response type supports execution (shell commands only)."""
        return self.mode == AIMode.SHELL and bool(self.content)


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""

    timestamp: float
    request: str
    response: str
    context: dict[str, Any]
    success: bool
    mode: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationMessage:
        """Create from dictionary from JSON deserialization."""
        return cls(**data)


@dataclass
class ConversationHistory:
    """Represents a conversation history."""

    conversation_id: str
    created_at: float
    last_updated: float
    messages: list[ConversationMessage]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "messages": [msg.to_dict() for msg in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationHistory:
        """Create from dictionary from JSON deserialization."""
        messages = [
            ConversationMessage.from_dict(msg) for msg in data.get("messages", [])
        ]
        return cls(
            conversation_id=data["conversation_id"],
            created_at=data["created_at"],
            last_updated=data["last_updated"],
            messages=messages,
        )
