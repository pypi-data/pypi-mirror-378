#!/usr/bin/env python3
"""
aii - AI Intelligence: Multi-Modal AI Assistant

A powerful multi-modal AI assistant that serves as your intelligent companion for
translation, explanation, coding, writing, and shell automation - powered by multiple AI providers.

Features:
- Multi-Provider Support: Choose between Google Gemini, Anthropic Claude, and OpenAI GPT models 🆕
- Multi-Modal AI: Supports 5 different AI modes (shell, translate, explain, code, write)
- Natural Language Interface: Use intuitive commands like `aii translate "hello" to Spanish`
- Smart Environment Detection: Auto-detects your OS (macOS/Linux) and shell (bash, zsh, fish, etc.)
- Context-Aware: Provides culturally appropriate translations and OS-specific commands
- Safe Execution: Only prompts for execution on shell commands, not explanations or translations
- High-Quality Output: Shows confidence levels and provides detailed reasoning
- Secure: Uses environment variables for API keys with helpful setup guidance
- Model Selection: Choose specific models for different use cases and performance needs 🆕
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Import memory management from new module
from aii.analysis import DirectoryAnalyzer

# Import core models from new module
from aii.core import (
    AIMode,
    AIRequest,
    AIResponse,
    EnvironmentContext,
    GitCommandError,
    OSType,
    ProviderType,
    ShellType,
    SystemEnvironmentDetector,
)
from aii.git import GitRepository
from aii.memory import ContextMemoryManager
from aii.prompts import MultiModalPromptGenerator
from aii.providers import AIGenerator
from aii.response import ResponseHandler

# Version information dynamically loaded from package metadata
from aii.version import __description__, __version__

# GitCommandError is imported from aii.core


class AiiApplication:
    """Main application class for the aii tool."""

    def __init__(self) -> None:
        self.detector = SystemEnvironmentDetector()
        self.prompt_generator = MultiModalPromptGenerator()
        self.response_handler = ResponseHandler()
        self.context_memory = ContextMemoryManager()
        self.directory_analyzer = DirectoryAnalyzer()
        self.generator: AIGenerator | None = None

    def _get_api_key(self) -> str:
        """Get API key from environment with helpful error message."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY environment variable is required.")
            print("💡 Setup: export GEMINI_API_KEY=your_api_key_here")
            print("🔗 Get key: https://aistudio.google.com/apikey")
            sys.exit(1)
        return api_key

    def _ensure_generator(self) -> AIGenerator:
        """Lazily create the shared AI generator."""
        if not self.generator:
            api_key = self._get_api_key()
            self.generator = AIGenerator(api_key, self.prompt_generator)
        return self.generator

    def _parse_target_language(self, prompt: str) -> tuple[str, str | None]:
        """Parse target language from translate mode prompt."""
        # Look for patterns like "to Spanish", "into French", etc.
        import re

        # Common patterns for language specification
        patterns = [
            r"\b(?:to|into|in)\s+(\w+)$",  # "to Spanish", "into French"
            r"^(\w+):\s*(.+)",  # "Spanish: hello world"
            r"\b--(\w+)\b",  # "--spanish"
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                if pattern.startswith("^"):  # Language prefix pattern
                    return match.group(2).strip(), match.group(1).title()
                else:
                    # Remove the language specification from prompt
                    cleaned_prompt = re.sub(
                        pattern, "", prompt, flags=re.IGNORECASE
                    ).strip()
                    return cleaned_prompt, match.group(1).title()

        return prompt, None

    def _create_environment_context(
        self, args: argparse.Namespace
    ) -> EnvironmentContext:
        """Create environment context from arguments and detection."""
        # Determine AI mode
        ai_mode = (
            AIMode(args.mode) if hasattr(args, "mode") and args.mode else AIMode.SHELL
        )

        # For shell mode, detect OS and shell
        if ai_mode == AIMode.SHELL:
            if args.os:
                os_type = OSType(args.os)
                is_detected = False
            else:
                os_type = self.detector.detect_os()
                is_detected = True

            if args.shell:
                shell_type = ShellType(args.shell)
                if is_detected:
                    is_detected = False
            else:
                shell_type = self.detector.detect_shell()
        else:
            # For non-shell modes, use defaults
            os_type = OSType.UNKNOWN
            shell_type = ShellType.BASH
            is_detected = True

        # Handle target language for translation
        target_language = None
        if ai_mode == AIMode.TRANSLATE and hasattr(args, "target_language"):
            target_language = args.target_language

        # Handle provider and model selection
        provider_type = ProviderType.GOOGLE  # Default
        if hasattr(args, "provider") and args.provider:
            provider_type = ProviderType(args.provider)

        model_name = None
        if hasattr(args, "model") and args.model:
            model_name = args.model

        return EnvironmentContext(
            os_type=os_type,
            shell_type=shell_type,
            ai_mode=ai_mode,
            is_detected=is_detected,
            target_language=target_language,
            provider_type=provider_type,
            model_name=model_name,
        )

    def _create_git_context(
        self, args: argparse.Namespace, mode: AIMode
    ) -> EnvironmentContext:
        """Create environment context for git-focused modes."""
        provider = (
            ProviderType(args.provider)
            if getattr(args, "provider", None)
            else ProviderType.GOOGLE
        )
        model_name = getattr(args, "model", None)

        return EnvironmentContext(
            os_type=OSType.UNKNOWN,
            shell_type=ShellType.BASH,
            ai_mode=mode,
            is_detected=True,
            provider_type=provider,
            model_name=model_name,
        )

    @staticmethod
    def _truncate_text(text: str, char_limit: int = 12000) -> str:
        """Truncate large blobs while noting omitted content."""
        if len(text) <= char_limit:
            return text
        slice_end = char_limit
        truncated = text[:slice_end]
        omitted = len(text) - slice_end
        return f"{truncated}\n\n[truncated {omitted} additional characters]"

    def _display_git_output(self, heading: str, response: AIResponse) -> bool:
        """Render AI output for git-oriented commands."""
        if not response.success:
            error = response.error_message or "AI generation failed."
            print(f"❌ {error}")
            return False

        if not response.content:
            print("❌ No content generated")
            return False

        print(f"{heading}\n")
        print(response.content.strip())

        if response.explanation:
            print(f"\n📝 Additional Info: {response.explanation}")

        print(f"\n🎯 Confidence: {response.confidence:.1%}")
        return True

    def _handle_git_commit(self, args: argparse.Namespace, guidance: str) -> int:
        """Generate Conventional Commit message for staged changes."""
        if not args.generate_message:
            print("❌ Error: --generate-message is required in commit mode")
            print("💡 Usage: aii commit --generate-message [optional guidance]")
            return 1

        repo = GitRepository()
        if not repo.is_repository():
            print("❌ Error: Git repository not detected in current directory")
            return 1

        try:
            diff = repo.get_staged_diff()
        except GitCommandError as err:
            print(f"❌ Git error: {err}")
            return 1

        if not diff.strip():
            print(
                "❌ Error: No staged changes found. Stage files before generating a commit message"
            )
            return 1

        stats = repo.get_staged_stats()
        status = repo.get_status_short()
        branch = repo.get_current_branch() or "unknown"
        root = repo.get_root() or str(Path.cwd())

        stats_block = (
            stats.strip() if stats and stats.strip() else "(no staged summary)"
        )
        status_block = (
            status.strip() if status and status.strip() else "(clean working tree)"
        )
        guidance_block = (
            guidance.strip() if guidance.strip() else "No additional guidance provided."
        )
        truncated_diff = self._truncate_text(diff)

        prompt = (
            "Generate a Conventional Commit message for the staged changes below.\n"
            f"Repository root: {root}\n"
            f"Current branch: {branch}\n"
            "\nGit status (--short --branch):\n"
            f"{status_block}\n"
            "\nStaged diff summary:\n"
            f"{stats_block}\n"
            "\nAdditional author guidance:\n"
            f"{guidance_block}\n"
            "\nStaged diff:\n"
            f"{truncated_diff}\n"
        )

        context = self._create_git_context(args, AIMode.GIT_COMMIT)
        request = AIRequest(prompt=prompt, context=context, require_confirmation=False)
        generator = self._ensure_generator()
        response = generator.generate(request)

        if response.content:
            original_message = response.content.strip()
        else:
            original_message = ""

        if original_message:
            response.content = (
                f"{original_message}\n\n"
                "🤖 Generated with [aii](https://pypi.org/project/a2py/)\n\n"
                "Co-Authored-By: aii <aii@aiiware.com>"
            )

        if not self._display_git_output("📝 Suggested commit message:", response):
            return 1

        return 0

    def _handle_git_pr(self, args: argparse.Namespace, guidance: str) -> int:
        """Generate pull request title/description from local changes."""
        repo = GitRepository()
        if not repo.is_repository():
            print("❌ Error: Git repository not detected in current directory")
            return 1

        generate_title = bool(args.pr_title)
        generate_description = bool(args.pr_description)

        if not (generate_title or generate_description):
            generate_title = True
            generate_description = True

        base = args.pr_base or repo.guess_default_base()
        branch = repo.get_current_branch() or "unknown"
        root = repo.get_root() or str(Path.cwd())

        try:
            diff = repo.get_diff_between(base, "HEAD")
            stats = repo.get_diff_stats_between(base, "HEAD")
        except GitCommandError as err:
            print(f"❌ Git error: {err}")
            return 1

        if not diff.strip():
            print(
                "❌ Error: No differences found between HEAD and base. Commit changes before drafting a PR"
            )
            return 1

        try:
            commits = repo.get_log_since(base, limit=10)
        except GitCommandError:
            commits = ""

        status = repo.get_status_short()
        status_block = (
            status.strip() if status and status.strip() else "(clean working tree)"
        )
        stats_block = stats.strip() if stats and stats.strip() else "(no diff summary)"
        commits_block = (
            commits.strip() if commits and commits.strip() else "(no new commits)"
        )
        guidance_block = (
            guidance.strip() if guidance.strip() else "No additional guidance provided."
        )
        requested_parts = []
        if generate_title:
            requested_parts.append("Provide a single `Title:` line <= 72 characters.")
        if generate_description:
            requested_parts.append(
                "Include a `Description:` section with Markdown subsections Summary, Testing, and Risks."
            )

        requested_text = "\n".join(f"- {part}" for part in requested_parts)
        truncated_diff = self._truncate_text(diff, char_limit=20000)

        prompt = (
            "Create the requested pull request materials for the changes below.\n"
            f"Repository root: {root}\n"
            f"Current branch: {branch}\n"
            f"Comparison base: {base}\n"
            "\nRequested output:\n"
            f"{requested_text}\n"
            "\nGit status (--short --branch):\n"
            f"{status_block}\n"
            "\nDiff summary:\n"
            f"{stats_block}\n"
            "\nCommits since base:\n"
            f"{commits_block}\n"
            "\nAdditional author guidance:\n"
            f"{guidance_block}\n"
            "\nDiff:\n"
            f"{truncated_diff}\n"
        )

        context = self._create_git_context(args, AIMode.GIT_PR)
        request = AIRequest(prompt=prompt, context=context, require_confirmation=False)
        generator = self._ensure_generator()
        response = generator.generate(request)

        heading = (
            "📝 Pull request draft:"
            if generate_description
            else "📝 Pull request title:"
        )
        if not self._display_git_output(heading, response):
            return 1
        return 0

    def _handle_git_review(self, args: argparse.Namespace, guidance: str) -> int:
        """Run AI-powered review on a git revision range."""
        repo = GitRepository()
        if not repo.is_repository():
            print("❌ Error: Git repository not detected in current directory")
            return 1

        range_expr = args.review_changes or "HEAD~1"

        try:
            if ".." in range_expr:
                diff = repo.get_diff_range(range_expr)
                stats = repo.get_diff_range_stats(range_expr)
                range_label = range_expr
            else:
                diff = repo.get_diff_between(range_expr, "HEAD")
                stats = repo.get_diff_stats_between(range_expr, "HEAD")
                range_label = f"{range_expr}..HEAD"
        except GitCommandError as err:
            print(f"❌ Git error: {err}")
            return 1

        if not diff.strip():
            print(f"❌ Error: No changes found for revision range '{range_expr}'")
            return 1

        status = repo.get_status_short()
        status_block = (
            status.strip() if status and status.strip() else "(clean working tree)"
        )
        stats_block = stats.strip() if stats and stats.strip() else "(no diff summary)"
        guidance_block = (
            guidance.strip()
            if guidance.strip()
            else "Focus on correctness, testing gaps, and architectural risks."
        )
        branch = repo.get_current_branch() or "unknown"
        root = repo.get_root() or str(Path.cwd())
        truncated_diff = self._truncate_text(diff, char_limit=15000)

        prompt = (
            "Perform a code review for the git diff below.\n"
            f"Repository root: {root}\n"
            f"Current branch: {branch}\n"
            f"Revision range: {range_label}\n"
            "\nGit status (--short --branch):\n"
            f"{status_block}\n"
            "\nDiff summary:\n"
            f"{stats_block}\n"
            "\nReviewer guidance:\n"
            f"{guidance_block}\n"
            "\nDiff:\n"
            f"{truncated_diff}\n"
        )

        context = self._create_git_context(args, AIMode.GIT_REVIEW)
        request = AIRequest(prompt=prompt, context=context, require_confirmation=False)
        generator = self._ensure_generator()
        response = generator.generate(request)

        if not self._display_git_output("🧾 Review notes:", response):
            return 1
        return 0

    def _setup_argument_parser(self) -> argparse.ArgumentParser:
        """Setup comprehensive argument parser."""
        parser = argparse.ArgumentParser(
            prog="aii",
            description="🧠 AI Intelligence: Multi-Modal AI Assistant",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
🌟 Examples:
  # Shell Commands (default mode)
  aii print hello world                    # Generate shell command (Google)
  aii --os mac install docker             # Force macOS mode
  aii -m -s fish list python files        # macOS + Fish shell

  # Multi-Provider Support 🆕
  aii --provider google translate "Hello" to Spanish    # Google Gemini (default)
  aii --provider anthropic explain "quantum physics"    # Anthropic Claude
  aii --provider openai code "Python web scraper"       # OpenAI GPT
  aii -p openai write "professional email"             # Short form

  # Model Selection 🆕
  aii --model gemini-2.0-flash "list files"            # Specific Google model
  aii --provider anthropic --model claude-3-5-sonnet-latest "write essay"
  aii --provider openai --model gpt-4o "explain AI"    # Specific OpenAI model

  # Translation Mode (natural syntax)
  aii translate "Hello world" to Spanish   # Natural language detection
  aii translate "Good morning" --to French # With explicit target language
  aii trans "Bonjour" to English          # Short form

  # Explain Mode (natural syntax)
  aii explain "How does Docker work?"      # Natural explanation
  aii explain "Machine learning algorithms" # Complex topics
  aii exp "Why is the sky blue?"           # Short form

  # Code Mode (natural syntax)
  aii code "Python function to sort list"  # Generate code
  aii code "Fix this JavaScript bug"       # Debug help
  aii coding "React component for login"   # Alternative form

  # Writing Mode (natural syntax)
  aii write "Professional email declining meeting" # Generate content
  aii write "Blog post intro about AI"     # Creative writing
  aii writing "Cover letter for dev role"  # Alternative form

  # Context Memory System 🆕
  aii --continue "Follow up on our previous discussion"          # Continue latest conversation
  aii --continue 20250916_220719_dbdcbd0c "What about performance?" # Continue specific conversation
  aii --clear-context "Start fresh conversation"                 # Clear context
  aii --show-history                                             # Show conversation history

🔧 Setup:
  export GEMINI_API_KEY=your_gemini_key       # Required for Google provider
  export ANTHROPIC_API_KEY=your_anthropic_key # Required for Anthropic provider
  export OPENAI_API_KEY=your_openai_key       # Required for OpenAI provider

🔗 More info: https://pypi.org/project/a2py
            """.strip(),
        )

        # Mode selection
        parser.add_argument(
            "--mode",
            choices=[mode.value for mode in AIMode],
            default="shell",
            help="AI operation mode (default: shell)",
        )

        # Mode shortcuts
        parser.add_argument(
            "--translate",
            "-t",
            action="store_const",
            const="translate",
            dest="mode",
            help="Translation mode shortcut",
        )

        parser.add_argument(
            "--explain",
            "-e",
            action="store_const",
            const="explain",
            dest="mode",
            help="Explanation mode shortcut",
        )

        parser.add_argument(
            "--code",
            "-c",
            action="store_const",
            const="code",
            dest="mode",
            help="Code generation mode shortcut",
        )

        parser.add_argument(
            "--write",
            "-w",
            action="store_const",
            const="write",
            dest="mode",
            help="Writing mode shortcut",
        )

        parser.add_argument(
            "--analyze",
            "-a",
            action="store_const",
            const="analyze",
            dest="mode",
            help="Directory analysis mode shortcut",
        )

        # Provider selection options
        parser.add_argument(
            "--provider",
            "-p",
            choices=[provider.value for provider in ProviderType],
            default="google",
            help="AI provider to use (default: google)",
        )

        parser.add_argument(
            "--model",
            help="Specific model to use (e.g., gemini-2.0-flash, claude-3-5-sonnet-latest)",
        )

        # Translation-specific options
        parser.add_argument(
            "--to", dest="target_language", help="Target language for translation mode"
        )

        # Shell-specific options (only relevant for shell mode)
        parser.add_argument(
            "--os",
            "-o",
            choices=[os.value for os in OSType if os != OSType.UNKNOWN],
            help="Override OS detection (mac/linux) - shell mode only",
        )

        parser.add_argument(
            "--shell",
            "-s",
            choices=[shell.value for shell in ShellType],
            help="Override shell detection - shell mode only",
        )

        parser.add_argument(
            "-m",
            "--mac",
            action="store_const",
            const="mac",
            dest="os",
            help="Shorthand for --os mac",
        )

        parser.add_argument(
            "-l",
            "--linux",
            action="store_const",
            const="linux",
            dest="os",
            help="Shorthand for --os linux",
        )

        # Context Memory options
        parser.add_argument(
            "--continue",
            nargs="?",
            const="latest",
            metavar="CONVERSATION_ID",
            help="Continue conversation with context memory. Use 'latest' (default) or specify conversation ID",
        )

        parser.add_argument(
            "--clear-context",
            action="store_true",
            help="Clear current conversation context and start fresh",
        )

        parser.add_argument(
            "--show-history",
            action="store_true",
            help="Show conversation history and exit",
        )

        # Directory Analysis options
        parser.add_argument(
            "--path",
            help="Directory path to analyze (default: current directory)",
        )

        parser.add_argument(
            "--summary",
            action="store_true",
            help="Generate project summary (analyze mode only)",
        )

        parser.add_argument(
            "--issues",
            action="store_true",
            help="Identify code issues and problems (analyze mode only)",
        )

        parser.add_argument(
            "--suggestions",
            action="store_true",
            help="Provide improvement suggestions (analyze mode only)",
        )

        parser.add_argument(
            "--architecture",
            action="store_true",
            help="Analyze project architecture (analyze mode only)",
        )

        # Git integration options
        parser.add_argument(
            "--generate-message",
            action="store_true",
            help="Generate Conventional Commit message (commit mode only)",
        )

        parser.add_argument(
            "--title",
            action="store_true",
            dest="pr_title",
            help="Generate pull request title (pr mode only)",
        )

        parser.add_argument(
            "--description",
            action="store_true",
            dest="pr_description",
            help="Generate pull request description (pr mode only)",
        )

        parser.add_argument(
            "--base",
            dest="pr_base",
            help="Base branch for pull request diff (pr mode only)",
        )

        parser.add_argument(
            "--changes",
            dest="review_changes",
            help="Revision or range to review (review mode only)",
        )

        # General options
        parser.add_argument(
            "--version",
            action="version",
            version=f"aii {__version__} - {__description__}",
        )

        parser.add_argument(
            "prompt", nargs="*", help="Your request in natural language"
        )

        return parser

    def _detect_mode_from_prompt(
        self, prompt_words: list[str]
    ) -> tuple[str | None, list[str]]:
        """Detect mode from first word of prompt and return mode and remaining words."""
        if not prompt_words:
            return None, prompt_words

        # Handle case where prompt_words contains multi-word strings (from quotes)
        # Split the first element to get the actual first word
        first_element = prompt_words[0]
        if " " in first_element:
            # Split the first element into words
            words = first_element.split()
            first_word = words[0].lower()
            # Reconstruct the prompt_words with the split first element
            remaining_first_element = " ".join(words[1:]) if len(words) > 1 else ""
            reconstructed_prompt = []
            if remaining_first_element:
                reconstructed_prompt.append(remaining_first_element)
            reconstructed_prompt.extend(prompt_words[1:])
        else:
            first_word = first_element.lower()
            reconstructed_prompt = prompt_words[1:]

        mode_mapping = {
            "translate": "translate",
            "trans": "translate",
            "explain": "explain",
            "exp": "explain",
            "what": "explain",
            "what's": "explain",
            "what're": "explain",
            "why": "explain",
            "how": "explain",
            "when": "explain",
            "where": "explain",
            "who": "explain",
            "code": "code",
            "coding": "code",
            "implement": "code",
            "build": "code",
            "create": "code",
            "write": "write",
            "writing": "write",
            "analyze": "analyze",
            "analysis": "analyze",
            "audit": "analyze",
            "review": "git_review",
            "commit": "git_commit",
            "pr": "git_pr",
            "pull": "git_pr",
            "gitreview": "git_review",
            "shell": "shell",
            "cmd": "shell",
            "command": "shell",
        }

        detected_mode = mode_mapping.get(first_word)
        if detected_mode:
            return detected_mode, reconstructed_prompt

        return None, prompt_words

    def run(self, args: list[str] | None = None) -> int:
        """Main application entry point."""
        parser = self._setup_argument_parser()
        if hasattr(parser, "parse_intermixed_args"):
            parsed_args = parser.parse_intermixed_args(args)
        else:
            parsed_args = parser.parse_args(args)

        # Handle context memory flags that don't require prompt
        if hasattr(parsed_args, "show_history") and parsed_args.show_history:
            self.context_memory.show_history()
            return 0

        if hasattr(parsed_args, "clear_context") and parsed_args.clear_context:
            self.context_memory.clear_current_conversation()
            print("🧹 Conversation context cleared - starting fresh!")
            if not parsed_args.prompt:  # If no prompt provided, just clear and exit
                return 0

        # Handle case where --continue argument might contain the prompt
        continue_arg = getattr(parsed_args, "continue", None)
        if continue_arg and continue_arg not in ["latest"] and not parsed_args.prompt:
            # The argument after --continue is likely the prompt, not a conversation ID
            # Check if it looks like a conversation ID (timestamp format)
            if not (
                len(continue_arg) >= 15
                and "_" in continue_arg
                and continue_arg.replace("_", "").replace("-", "").isalnum()
            ):
                # It's probably a prompt, not a conversation ID
                parsed_args.prompt = [continue_arg]
                setattr(parsed_args, "continue", "latest")

        prompt_words = parsed_args.prompt or []

        # Always try to detect mode from current prompt, even when continuing conversation
        detected_mode, remaining_words = self._detect_mode_from_prompt(prompt_words)

        if detected_mode and (not parsed_args.mode or parsed_args.mode == "shell"):
            parsed_args.mode = detected_mode
            prompt_words = remaining_words
        elif not parsed_args.mode:
            parsed_args.mode = "shell"  # Default mode

        prompt_text = " ".join(prompt_words)
        parsed_args.prompt = prompt_words

        # Dispatch git-focused modes early
        if parsed_args.mode == "git_commit":
            return self._handle_git_commit(parsed_args, prompt_text)
        if parsed_args.mode == "git_pr":
            return self._handle_git_pr(parsed_args, prompt_text)
        if parsed_args.mode == "git_review":
            return self._handle_git_review(parsed_args, prompt_text)

        # Check if we need a prompt for the remaining operations
        if not prompt_words:
            if hasattr(parsed_args, "continue") and getattr(
                parsed_args, "continue", False
            ):
                print(
                    "❌ Error: --continue requires a prompt to continue the conversation"
                )
                print('💡 Usage: aii --continue "your follow-up question"')
                print("📚 To see conversation history: aii --show-history")
            else:
                print("❌ Error: Please provide a prompt for AI processing")
            return 1

        # Handle translation mode language parsing
        if parsed_args.mode == "translate" and not parsed_args.target_language:
            # Try to parse target language from prompt
            cleaned_prompt, detected_language = self._parse_target_language(prompt_text)
            if detected_language:
                prompt_text = cleaned_prompt
                parsed_args.target_language = detected_language

        # Create request context
        context = self._create_environment_context(parsed_args)

        # Handle conversation context
        conversation_id = None
        if hasattr(parsed_args, "continue") and getattr(parsed_args, "continue", False):
            # Continue specified conversation or latest
            target_conversation = getattr(parsed_args, "continue")

            if self.context_memory.continue_conversation(target_conversation):
                conversation_id = self.context_memory.get_current_conversation_id()
                if target_conversation == "latest":
                    print(f"🔄 Continuing latest conversation: {conversation_id}")
                else:
                    print(f"🔄 Continuing conversation: {target_conversation}")
            else:
                if target_conversation == "latest":
                    print(
                        "🔄 No previous conversation found - starting new conversation"
                    )
                else:
                    print(
                        f"❌ Conversation '{target_conversation}' not found - starting new conversation"
                    )
                conversation_id = self.context_memory.start_new_conversation()
        else:
            # Start new conversation (but don't announce it)
            conversation_id = self.context_memory.start_new_conversation()

        # Enhance request with conversation context
        enhanced_prompt = prompt_text
        if conversation_id:
            context_lines = self.context_memory.get_conversation_context(
                conversation_id
            )
            if context_lines:
                context_str = "\n".join(context_lines)
                enhanced_prompt = f"""Previous conversation context:
{context_str}

Current request: {prompt_text}

Please respond to the current request, taking into account the conversation history above."""

        request = AIRequest(prompt=enhanced_prompt, context=context)

        # Show context info
        print(f"🔍 Context: {context}")
        if hasattr(parsed_args, "continue") and getattr(parsed_args, "continue", False):
            context_lines = (
                self.context_memory.get_conversation_context(conversation_id)
                if conversation_id
                else []
            )
            if context_lines:
                print(
                    f"💬 Using {len(context_lines) // 2} previous messages for context"
                )
        print(f"📝 Request: {prompt_text}\n")

        # Generate AI response
        generator = self._ensure_generator()
        response = generator.generate(request)

        # Save to conversation history
        if conversation_id and response.success:
            self.context_memory.add_message_to_conversation(
                conversation_id, prompt_text, response, context
            )

        # Display response
        self.response_handler.display_response(response)

        if not response.success:
            return 1

        # Handle execution ONLY for shell commands
        if response.mode == AIMode.SHELL and response.content:
            if self.response_handler.prompt_for_execution(response):
                return self.response_handler.execute_command(response.content)

        return 0


def main() -> int:
    """Application entry point."""
    try:
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


def main_translate() -> int:
    """Entry point for aiit command (translation shortcut)."""
    try:
        # Insert -t at the beginning of arguments
        sys.argv.insert(1, "-t")
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
