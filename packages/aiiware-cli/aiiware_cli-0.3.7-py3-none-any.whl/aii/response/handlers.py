"""Response handlers for different AI modes."""

import os

from ..core.models import AIMode, AIResponse

try:
    from typing import assert_never  # Python 3.11+
except ImportError:
    from typing_extensions import assert_never  # Python 3.10  # noqa: UP035


def debug_print(message: str) -> None:
    """Print debug message if DEBUG environment variable is set."""
    if os.getenv("AII_DEBUG"):
        print(f"[DEBUG] {message}")


class ResponseHandler:
    """Handles AI response display and execution for different modes."""

    @staticmethod
    def display_response(response: AIResponse) -> None:
        """Display AI response based on mode."""
        debug_print(f"display_response() received mode: {response.mode}")
        debug_print(
            f"response.mode == AIMode.EXPLAIN: {response.mode == AIMode.EXPLAIN}"
        )
        debug_print(f"response.mode == AIMode.SHELL: {response.mode == AIMode.SHELL}")

        if not response.success:
            print(f"❌ Failed: {response.error_message}")
            return

        if not response.content:
            print("❌ No content generated")
            return

        # Mode-specific display
        if response.mode == AIMode.SHELL:
            print(f"💡 Generated Command: {response.content}")
        elif response.mode == AIMode.TRANSLATE:
            print("🌐 Translation:")
            print(response.content)
        elif response.mode == AIMode.EXPLAIN:
            print("🎓 Explanation:")
            print(response.content)
        elif response.mode == AIMode.CODE:
            print("💻 Generated Code:")
            print(response.content)
        elif response.mode == AIMode.WRITE:
            print("✍️  Generated Content:")
            print(response.content)
        elif response.mode == AIMode.ANALYZE:
            print("🔍 Analysis Report:")
            print(response.content)
        elif response.mode == AIMode.GIT_COMMIT:
            print("📝 Suggested commit message:")
            print(response.content)
        elif response.mode == AIMode.GIT_PR:
            print("📝 Pull request draft:")
            print(response.content)
        elif response.mode == AIMode.GIT_REVIEW:
            print("🧾 Review notes:")
            print(response.content)

        else:
            assert_never(response.mode)

        # Show explanation if available
        if response.explanation:
            print(f"\n📝 Additional Info: {response.explanation}")

        # Show confidence
        print(f"\n🎯 Confidence: {response.confidence:.1%}")

    @staticmethod
    def prompt_for_execution(response: AIResponse) -> bool:
        """Prompt user for execution confirmation (shell commands only)."""
        if not response.is_executable or not response.content:
            return False

        if not response.is_safe_to_execute:
            print("\n⚠️  WARNING: This command may be potentially dangerous!")

        try:
            choice = input("\n🚀 Execute this command? [y/N]: ").strip().lower()
            return choice in ["y", "yes"]
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled by user")
            return False

    @staticmethod
    def execute_command(command: str) -> int:
        """Execute the command and return exit code."""
        try:
            return os.system(command)  # nosec B605 - needed for shell execution
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return 1
