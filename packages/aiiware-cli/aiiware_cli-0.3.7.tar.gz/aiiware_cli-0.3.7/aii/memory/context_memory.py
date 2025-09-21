"""Context memory management for conversation history."""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.models import (
    AIResponse,
    ConversationHistory,
    ConversationMessage,
    EnvironmentContext,
)
from ..core.utils import debug_print


class ContextMemoryManager:
    """Manages conversation history and context memory."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize context memory manager."""
        if base_dir is None:
            base_dir = Path.home() / ".aii"
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "history"
        self.current_conversation_file = self.base_dir / "current_conversation"

        # Ensure directories exist
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Current conversation ID (None means no active conversation)
        self._current_conversation_id: str | None = None

        # Load current conversation ID if exists
        self._load_current_conversation_id()

    def _load_current_conversation_id(self) -> None:
        """Load the current conversation ID from file."""
        try:
            if self.current_conversation_file.exists():
                self._current_conversation_id = (
                    self.current_conversation_file.read_text().strip()
                )
                # Validate conversation exists
                if not self._get_conversation_file(
                    self._current_conversation_id
                ).exists():
                    self._current_conversation_id = None
                    self.current_conversation_file.unlink(missing_ok=True)
        except Exception:
            self._current_conversation_id = None

    def _save_current_conversation_id(self, conversation_id: str | None) -> None:
        """Save the current conversation ID to file."""
        if conversation_id:
            self.current_conversation_file.write_text(conversation_id)
        else:
            self.current_conversation_file.unlink(missing_ok=True)
        self._current_conversation_id = conversation_id

    def _get_conversation_file(self, conversation_id: str) -> Path:
        """Get the file path for a conversation."""
        return self.history_dir / f"{conversation_id}.json"

    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def start_new_conversation(self) -> str:
        """Start a new conversation and return the conversation ID."""
        conversation_id = self._generate_conversation_id()
        now = time.time()

        # Create new conversation history
        history = ConversationHistory(
            conversation_id=conversation_id,
            created_at=now,
            last_updated=now,
            messages=[],
        )

        # Save to file
        self._save_conversation(history)

        # Set as current conversation
        self._save_current_conversation_id(conversation_id)

        return conversation_id

    def get_current_conversation_id(self) -> str | None:
        """Get the current conversation ID."""
        return self._current_conversation_id

    def clear_current_conversation(self) -> None:
        """Clear the current conversation context."""
        self._save_current_conversation_id(None)

    def continue_conversation(self, conversation_id: str) -> bool:
        """Continue a specific conversation by ID. Returns True if conversation exists."""
        if conversation_id == "latest":
            # Use current conversation if available
            current_id = self.get_current_conversation_id()
            if current_id:
                return True
            else:
                # Find most recent conversation
                conversations = self.list_conversations(limit=1)
                if conversations:
                    latest_id = conversations[0]["id"]
                    self._save_current_conversation_id(latest_id)
                    return True
                return False
        else:
            # Try to continue specific conversation ID
            if self._load_conversation(conversation_id):
                self._save_current_conversation_id(conversation_id)
                return True
            return False

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists."""
        if conversation_id == "latest":
            current_id = self.get_current_conversation_id()
            if current_id:
                return True
            conversations = self.list_conversations(limit=1)
            return len(conversations) > 0
        else:
            return self._load_conversation(conversation_id) is not None

    def _save_conversation(self, history: ConversationHistory) -> None:
        """Save conversation history to file."""
        file_path = self._get_conversation_file(history.conversation_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            debug_print(f"Failed to save conversation: {e}")

    def _load_conversation(self, conversation_id: str) -> ConversationHistory | None:
        """Load conversation history from file."""
        file_path = self._get_conversation_file(conversation_id)
        try:
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                return ConversationHistory.from_dict(data)
        except Exception as e:
            debug_print(f"Failed to load conversation: {e}")
        return None

    def add_message_to_conversation(
        self,
        conversation_id: str,
        request: str,
        response: AIResponse,
        context: EnvironmentContext,
    ) -> None:
        """Add a message to the conversation history."""
        # Load existing conversation or create new one
        history = self._load_conversation(conversation_id)
        if not history:
            now = time.time()
            history = ConversationHistory(
                conversation_id=conversation_id,
                created_at=now,
                last_updated=now,
                messages=[],
            )

        # Create message
        message = ConversationMessage(
            timestamp=time.time(),
            request=request,
            response=response.content or "",
            context={
                "mode": context.ai_mode.value,
                "provider": context.provider_type.value,
                "model": context.model_name,
                "os_type": context.os_type.value,
                "shell_type": context.shell_type.value,
                "target_language": context.target_language,
                "confidence": response.confidence,
            },
            success=response.success,
            mode=context.ai_mode.value,
        )

        # Add message and update timestamp
        history.messages.append(message)
        history.last_updated = time.time()

        # Save conversation
        self._save_conversation(history)

    def get_conversation_context(
        self, conversation_id: str, max_messages: int = 5
    ) -> list[str]:
        """Get recent conversation context for prompting."""
        history = self._load_conversation(conversation_id)
        if not history:
            return []

        # Get last N messages
        recent_messages = history.messages[-max_messages:] if history.messages else []

        context_lines = []
        for msg in recent_messages:
            context_lines.append(f"User: {msg.request}")
            context_lines.append(f"Assistant: {msg.response}")

        return context_lines

    def get_recent_messages(
        self, conversation_id: str, limit: int = 5
    ) -> list[ConversationMessage]:
        """Return the last `limit` messages for display purposes."""
        history = self._load_conversation(conversation_id)
        if not history or not history.messages:
            return []
        return history.messages[-limit:]

    def list_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent conversations with metadata."""
        conversations = []

        # Find all conversation files
        for file_path in self.history_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                conversations.append(
                    {
                        "id": data["conversation_id"],
                        "created_at": datetime.fromtimestamp(
                            data["created_at"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "last_updated": datetime.fromtimestamp(
                            data["last_updated"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "message_count": len(data.get("messages", [])),
                        "is_current": data["conversation_id"]
                        == self._current_conversation_id,
                    }
                )
            except Exception:
                continue

        # Sort by last_updated (most recent first) and limit
        conversations.sort(key=lambda x: x["last_updated"], reverse=True)
        return conversations[:limit]

    def show_history(self) -> None:
        """Display conversation history in a user-friendly format."""
        conversations = self.list_conversations()

        if not conversations:
            print("📭 No conversation history found.")
            return

        print("📚 Recent Conversations:")
        print("=" * 60)

        for conv in conversations:
            current_marker = "🔄 " if conv["is_current"] else "   "
            print(f"{current_marker}{conv['id']}")
            print(f"     Created: {conv['created_at']}")
            print(f"     Updated: {conv['last_updated']}")
            print(f"     Messages: {conv['message_count']}")
            print()

    def get_last_message_mode(self, conversation_id: str) -> str | None:
        """Return the mode of the most recent message in a conversation."""
        history = self._load_conversation(conversation_id)
        if history and history.messages:
            return history.messages[-1].mode
        return None
