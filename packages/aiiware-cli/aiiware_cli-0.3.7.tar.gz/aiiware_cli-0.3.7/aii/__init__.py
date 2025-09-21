"""AII - AI Intelligence Multi-Modal Assistant."""

# Core models and enums - maintain backward compatibility
# Memory management
# Analysis tools
from .analysis import DirectoryAnalyzer

# Import AiiApplication and main functions from the application module
from .application import AiiApplication, main, main_translate
from .core import (
    AIMode,
    AIRequest,
    AIResponse,
    ConversationHistory,
    ConversationMessage,
    EnvironmentContext,
    EnvironmentDetector,
    GitCommandError,
    OSType,
    ProviderType,
    ShellType,
    SystemEnvironmentDetector,
)

# Git integration
from .git import GitRepository
from .memory import ContextMemoryManager

# Prompt generation
from .prompts import MultiModalPromptGenerator, PromptGenerator

# AI providers
from .providers import AIGenerator

# Response handling
from .response import ResponseHandler

# Version information dynamically loaded from package metadata
from .version import __description__, __version__


# For direct access (compatibility with existing tests)
def __getattr__(name: str) -> object:
    # Import debug_print from response module for backward compatibility
    if name == "debug_print":
        try:
            from .response.handlers import debug_print

            return debug_print
        except ImportError:

            def _placeholder_debug_print(message: str) -> None:
                pass

            return _placeholder_debug_print

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Maintain exact same exports as original single file for backward compatibility
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
    # Main application and version
    "__version__",
    "__description__",
    "AiiApplication",
    # Analysis tools
    "DirectoryAnalyzer",
    # Git integration
    "GitRepository",
    # Memory management
    "ContextMemoryManager",
    # Prompt generation
    "MultiModalPromptGenerator",
    "PromptGenerator",
    # AI providers
    "AIGenerator",
    # Response handling
    "ResponseHandler",
    # Entry points
    "main",
    "main_translate",
]
