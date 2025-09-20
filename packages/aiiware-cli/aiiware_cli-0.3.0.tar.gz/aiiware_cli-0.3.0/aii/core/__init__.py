"""Core models and utilities for AII."""

from .environment import EnvironmentDetector, SystemEnvironmentDetector
from .exceptions import GitCommandError
from .models import (
    AIMode,
    AIRequest,
    AIResponse,
    ConversationHistory,
    ConversationMessage,
    EnvironmentContext,
    OSType,
    ProviderType,
    ShellType,
)
from .utils import debug_print

__all__ = [
    # Enums
    "AIMode",
    "OSType",
    "ShellType",
    "ProviderType",
    # Data classes
    "EnvironmentContext",
    "AIRequest",
    "AIResponse",
    "ConversationMessage",
    "ConversationHistory",
    # Environment detection
    "EnvironmentDetector",
    "SystemEnvironmentDetector",
    # Exceptions
    "GitCommandError",
    # Utilities
    "debug_print",
]
