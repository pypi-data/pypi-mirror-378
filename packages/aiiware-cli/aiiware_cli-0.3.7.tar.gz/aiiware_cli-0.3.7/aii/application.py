"""Main AII application class."""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .analysis import DirectoryAnalyzer
from .core import (
    AIMode,
    AIRequest,
    AIResponse,
    EnvironmentContext,
    OSType,
    ProviderType,
    ShellType,
    SystemEnvironmentDetector,
)
from .git import GitRepository
from .memory import ContextMemoryManager
from .prompts import MultiModalPromptGenerator
from .providers import AIGenerator
from .response import ResponseHandler
from .version import __description__, __version__

MODE_COMMANDS: dict[str, str] = {
    "shell": "shell",
    "sh": "shell",
    "translate": "translate",
    "trans": "translate",
    "explain": "explain",
    "exp": "explain",
    "code": "code",
    "write": "write",
    "analyze": "analyze",
    "analysis": "analyze",
    "commit": "git_commit",
    "pr": "git_pr",
    "pull": "git_pr",
    "review": "git_review",
    "gitreview": "git_review",
}


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
            os_type = self.detector.detect_os()
            shell_type = self.detector.detect_shell()
            is_detected = True
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

    def run(self, args: list[str] | None = None) -> int:
        """Entry point that supports hierarchical commands with smart fallback."""
        arg_list = list(args) if args is not None else sys.argv[1:]

        if not arg_list:
            return self._run_legacy([])

        legacy_prefix: list[str] = []
        idx = 0
        while idx < len(arg_list):
            token = arg_list[idx]
            if token in {"--help", "-h", "--version", "-v"}:
                return self._run_legacy(arg_list)
            if token in {"-p", "--provider", "--model", "--to", "--mode"}:
                if idx + 1 >= len(arg_list):
                    return self._run_legacy(arg_list)
                legacy_prefix.extend(arg_list[idx : idx + 2])
                idx += 2
                continue
            break

        remaining = arg_list[idx:]
        if not remaining:
            return self._run_legacy(legacy_prefix)

        command = remaining[0].lower()

        if command == "run":
            return self._handle_run_alias(remaining[1:], legacy_prefix)

        if command == "convo":
            return self._handle_convo_command(remaining[1:], legacy_prefix)

        if command == "git":
            return self._handle_git_command(remaining[1:], legacy_prefix)

        mode = MODE_COMMANDS.get(command)
        if mode:
            return self._run_mode_command(mode, remaining[1:], legacy_prefix)

        return self._run_legacy(legacy_prefix + remaining)

    def _handle_run_alias(self, args: list[str], legacy_prefix: list[str]) -> int:
        """Handle the legacy `aii run …` alias."""
        if not args:
            return self._run_legacy(legacy_prefix)

        mode = MODE_COMMANDS.get(args[0].lower())
        if mode:
            return self._run_mode_command(mode, args[1:], legacy_prefix)

        return self._run_legacy(legacy_prefix + args)

    def _run_mode_command(
        self, mode: str, remaining_args: list[str], legacy_prefix: list[str]
    ) -> int:
        """Execute a specific AI mode command."""
        forwarded = list(legacy_prefix)
        forwarded.extend(["--mode", mode])
        forwarded.extend(remaining_args)
        if mode == "git_commit" and "--generate-message" not in forwarded:
            forwarded.append("--generate-message")
        return self._run_legacy(forwarded)

    def _handle_convo_command(self, args: list[str], legacy_prefix: list[str]) -> int:
        """Handle conversation-specific subcommands."""
        convo_parser = argparse.ArgumentParser(
            prog="aii convo", description="Conversation management commands"
        )
        subparsers = convo_parser.add_subparsers(dest="action")
        subparsers.required = True

        subparsers.add_parser("history", help="Show recent conversations")
        subparsers.add_parser(
            "clear", help="Clear the currently active conversation context"
        )

        continue_parser = subparsers.add_parser(
            "continue", help="Continue a previous conversation"
        )
        continue_parser.add_argument("conversation_id", nargs="?", default="latest")
        continue_parser.add_argument("prompt", nargs=argparse.REMAINDER)

        new_parser = subparsers.add_parser("new", help="Start a new conversation")
        new_parser.add_argument("prompt", nargs=argparse.REMAINDER)

        show_parser = subparsers.add_parser(
            "show", help="Display recent messages from a conversation"
        )
        show_parser.add_argument("conversation_id", nargs="?", default="latest")
        show_parser.add_argument(
            "--count",
            type=int,
            default=3,
            help="Number of recent messages to display (default: 3)",
        )

        namespace = convo_parser.parse_args(args)

        if namespace.action == "history":
            self.context_memory.show_history()
            return 0

        if namespace.action == "clear":
            self.context_memory.clear_current_conversation()
            print("🧹 Conversation context cleared - starting fresh!")
            return 0

        if namespace.action == "show":
            convo_id = namespace.conversation_id
            if convo_id == "latest":
                convo_id = self.context_memory.get_current_conversation_id()
                if not convo_id:
                    conversations = self.context_memory.list_conversations(limit=1)
                    convo_id = conversations[0]["id"] if conversations else None
            if not convo_id:
                print("📭 No conversation history found.")
                return 0

            messages = self.context_memory.get_recent_messages(
                convo_id, max(1, namespace.count)
            )
            if not messages:
                print(f"📭 Conversation '{convo_id}' has no messages yet.")
                return 0

            print(
                f"🗒️ Conversation {convo_id} — showing last {len(messages)} message(s):"
            )
            print("=" * 60)
            for msg in messages:
                timestamp = datetime.fromtimestamp(msg.timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                print(f"[{timestamp}] User: {msg.request}")
                print(f"[{timestamp}] Assistant: {msg.response}\n")
            return 0

        if namespace.action == "continue":
            forwarded = list(legacy_prefix)
            forwarded.extend(["--continue", namespace.conversation_id])
            forwarded.extend(namespace.prompt or [])
            return self._run_legacy(forwarded)

        if namespace.action == "new":
            forwarded = list(legacy_prefix)
            forwarded.append("--new")
            forwarded.extend(namespace.prompt or [])
            return self._run_legacy(forwarded)

        return 0

    def _handle_git_command(self, args: list[str], legacy_prefix: list[str]) -> int:
        """Handle git-related subcommands."""
        git_parser = argparse.ArgumentParser(
            prog="aii git", description="Git-integrated AI helpers"
        )
        subparsers = git_parser.add_subparsers(dest="action")
        subparsers.required = True

        commit_parser = subparsers.add_parser(
            "commit", help="Generate Conventional Commit messages"
        )
        commit_parser.add_argument("--generate-message", action="store_true")
        commit_parser.add_argument("--provider", "-p")
        commit_parser.add_argument("--model")
        commit_parser.add_argument("prompt", nargs="*")

        pr_parser = subparsers.add_parser(
            "pr", help="Draft pull request titles and descriptions"
        )
        pr_parser.add_argument("--title", action="store_true")
        pr_parser.add_argument("--description", action="store_true")
        pr_parser.add_argument("--base", dest="pr_base")
        pr_parser.add_argument("--provider", "-p")
        pr_parser.add_argument("--model")
        pr_parser.add_argument("prompt", nargs="*")

        review_parser = subparsers.add_parser(
            "review", help="Review diff ranges with AI assistance"
        )
        review_parser.add_argument("--changes", dest="review_changes")
        review_parser.add_argument("--provider", "-p")
        review_parser.add_argument("--model")
        review_parser.add_argument("prompt", nargs="*")

        namespace, extra = git_parser.parse_known_args(args)

        if namespace.action == "commit":
            forwarded = list(legacy_prefix)
            forwarded.extend(["--mode", "git_commit"])
            forwarded.extend(extra)
            if namespace.provider:
                forwarded.extend(["--provider", namespace.provider])
            if namespace.model:
                forwarded.extend(["--model", namespace.model])
            if namespace.generate_message:
                forwarded.append("--generate-message")
            forwarded.extend(namespace.prompt or [])
            return self._run_legacy(forwarded)

        if namespace.action == "pr":
            forwarded = list(legacy_prefix)
            forwarded.extend(["--mode", "git_pr"])
            forwarded.extend(extra)
            if namespace.provider:
                forwarded.extend(["--provider", namespace.provider])
            if namespace.model:
                forwarded.extend(["--model", namespace.model])
            if namespace.title:
                forwarded.append("--title")
            if namespace.description:
                forwarded.append("--description")
            if namespace.pr_base:
                forwarded.extend(["--base", namespace.pr_base])
            forwarded.extend(namespace.prompt or [])
            return self._run_legacy(forwarded)

        if namespace.action == "review":
            forwarded = list(legacy_prefix)
            forwarded.extend(["--mode", "git_review"])
            forwarded.extend(extra)
            if namespace.provider:
                forwarded.extend(["--provider", namespace.provider])
            if namespace.model:
                forwarded.extend(["--model", namespace.model])
            if namespace.review_changes:
                forwarded.extend(["--changes", namespace.review_changes])
            forwarded.extend(namespace.prompt or [])
            return self._run_legacy(forwarded)

        return 0

    @staticmethod
    def _append_git_signature(response: AIResponse) -> None:
        """Append branded signature to git commit messages."""
        signature = "\n\n🤖 Generated by aii - https://pypi.org/project/aiiware-cli"
        if not response.content:
            return
        if signature.strip() in response.content:
            return
        response.content = response.content.rstrip() + signature

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="AI Intelligence: Multi-modal AI assistant for translation, explanation, coding, writing, and shell automation"
        )

        # Add version argument
        parser.add_argument(
            "--version",
            action="version",
            version=f"aii {__version__} - {__description__}",
        )

        # Mode selection (exclusive group)
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "-s",
            "--shell",
            dest="mode",
            action="store_const",
            const="shell",
            help="Shell command mode (default)",
        )
        mode_group.add_argument(
            "-c",
            "--code",
            dest="mode",
            action="store_const",
            const="code",
            help="Coding assistance mode",
        )
        mode_group.add_argument(
            "-w",
            "--write",
            dest="mode",
            action="store_const",
            const="write",
            help="Writing assistance mode",
        )
        mode_group.add_argument(
            "-t",
            "--translate",
            dest="mode",
            action="store_const",
            const="translate",
            help="Translation mode",
        )
        mode_group.add_argument(
            "-e",
            "--explain",
            dest="mode",
            action="store_const",
            const="explain",
            help="Explanation mode",
        )
        mode_group.add_argument(
            "-a",
            "--analyze",
            dest="mode",
            action="store_const",
            const="analyze",
            help="Analysis mode",
        )
        mode_group.add_argument(
            "--mode",
            dest="mode",
            choices=[mode.value for mode in AIMode],
            help=argparse.SUPPRESS,
        )

        # Translation options
        parser.add_argument(
            "--to",
            dest="target_language",
            help="Target language for translation",
        )

        # AI provider options
        parser.add_argument(
            "--provider",
            "-p",
            choices=[provider.value for provider in ProviderType],
            help="AI provider to use",
        )
        parser.add_argument(
            "--model",
            help="Specific model to use",
        )

        # Context management
        parser.add_argument(
            "--continue",
            "-C",
            nargs="?",
            const="latest",
            dest="continue_id",
            metavar="CONVERSATION_ID",
            help="Continue previous conversation (use optional ID or default to latest)",
        )
        parser.add_argument(
            "--new",
            "-N",
            action="store_true",
            help="Start a new conversation",
        )
        parser.add_argument(
            "--show-history",
            action="store_true",
            help="Show recent conversation history and exit",
        )
        parser.add_argument(
            "--clear-context",
            action="store_true",
            help="Clear current conversation context",
        )

        # Analysis options
        parser.add_argument(
            "--path",
            type=str,
            help="Path to analyze (for analyze mode)",
        )
        parser.add_argument(
            "--architecture",
            type=str,
            help="Architecture description (for analyze mode)",
        )

        # Image analysis
        parser.add_argument(
            "--image",
            "-i",
            type=str,
            help="Include image for analysis",
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

        # Prompt
        parser.add_argument(
            "prompt",
            nargs="*",
            help="The prompt or question to process",
        )

        return parser

    def _handle_special_commands(self, args: argparse.Namespace) -> int | None:
        """Handle special commands that don't require AI generation."""
        if not args.prompt:
            # Allow empty prompts for git commit with --generate-message
            if hasattr(args, "generate_message") and args.generate_message:
                return None
            print("❌ Error: No prompt provided")
            return 1

        prompt_text = " ".join(args.prompt)

        # Handle version command
        if prompt_text.lower() in ["version", "--version", "-v"]:
            print(f"aii {__version__} - {__description__}")
            return 0

        return None

    def _run_legacy(self, args: list[str]) -> int:
        """Execute the legacy flat CLI parsing path."""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Conversation history utilities that do not require prompts
        if getattr(parsed_args, "show_history", False):
            self.context_memory.show_history()
            return 0

        if getattr(parsed_args, "clear_context", False):
            self.context_memory.clear_current_conversation()
            print("🧹 Conversation context cleared - starting fresh!")
            if not parsed_args.prompt and not getattr(parsed_args, "continue_id", None):
                return 0

        # Handle special commands first
        special_result = self._handle_special_commands(parsed_args)
        if special_result is not None:
            return special_result

        # Join prompt arguments
        prompt_text = " ".join(parsed_args.prompt)

        # Detect mode from prompt if not set by flags
        detected_mode = None
        if not hasattr(parsed_args, "mode") or not parsed_args.mode:
            detected_mode, modified_prompt_words = self._detect_mode_from_prompt(
                parsed_args.prompt
            )
            if detected_mode:
                # Update the parsed args with detected mode
                parsed_args.mode = detected_mode
                # Update prompt_text with modified words (without the mode word)
                prompt_text = " ".join(modified_prompt_words)

        # Handle conversation context before generating the request
        conversation_id = self.context_memory.get_current_conversation_id()
        continue_target = getattr(parsed_args, "continue_id", None)
        continued_successfully = False

        if continue_target:
            if self.context_memory.continue_conversation(continue_target):
                conversation_id = self.context_memory.get_current_conversation_id()
                continued_successfully = True
                if conversation_id:
                    if continue_target == "latest":
                        print(f"🔄 Continuing latest conversation: {conversation_id}")
                    else:
                        print(f"🔄 Continuing conversation: {continue_target}")
                    if not getattr(parsed_args, "mode", None):
                        last_mode = self.context_memory.get_last_message_mode(
                            conversation_id
                        )
                        if last_mode:
                            parsed_args.mode = last_mode
            else:
                print(
                    f"❌ Conversation '{continue_target}' not found - starting new conversation"
                )
                conversation_id = self.context_memory.start_new_conversation()
                print(f"🆕 Started new conversation: {conversation_id}")
        elif getattr(parsed_args, "new", False):
            conversation_id = self.context_memory.start_new_conversation()
            print(f"🆕 Started new conversation: {conversation_id}")
        elif not conversation_id:
            conversation_id = self.context_memory.start_new_conversation()

        context = self._create_environment_context(parsed_args)

        # Handle translation mode target language parsing
        if context.ai_mode == AIMode.TRANSLATE:
            target_language = None
            if parsed_args.target_language:
                target_language = parsed_args.target_language
            else:
                # Try to parse target language from prompt
                prompt_text, parsed_language = self._parse_target_language(prompt_text)
                if parsed_language:
                    target_language = parsed_language

            # Create new context with target language if different
            if target_language and target_language != context.target_language:
                context = EnvironmentContext(
                    os_type=context.os_type,
                    shell_type=context.shell_type,
                    ai_mode=context.ai_mode,
                    is_detected=context.is_detected,
                    target_language=target_language,
                    provider_type=context.provider_type,
                    model_name=context.model_name,
                )

        # Handle analysis mode
        if context.ai_mode == AIMode.ANALYZE:
            analysis_path = Path(parsed_args.path) if parsed_args.path else Path.cwd()
            try:
                if analysis_path.is_file():
                    # Analyze a specific file
                    with open(analysis_path, encoding="utf-8") as f:
                        file_content = f.read()
                    prompt_text = f"File Analysis ({analysis_path}):\n{file_content}\n\nUser Request: {prompt_text}"
                else:
                    # Analyze a directory
                    analysis = self.directory_analyzer.analyze_directory(analysis_path)
                    prompt_text = f"Directory Analysis ({analysis_path}):\n{analysis}\n\nUser Request: {prompt_text}"

                if parsed_args.architecture:
                    prompt_text = f"Architecture Context: {parsed_args.architecture}\n\n{prompt_text}"
            except Exception as e:
                print(f"⚠️  Warning: Could not analyze {analysis_path}: {e}")

        # Handle image analysis
        if parsed_args.image:
            image_path = Path(parsed_args.image)
            if not image_path.exists():
                print(f"❌ Error: Image file not found: {image_path}")
                return 1

            # Add image to prompt (the prompt generator will handle it)
            prompt_text = f"[IMAGE: {image_path}]\n{prompt_text}"

        # Handle git commit mode
        if (
            hasattr(parsed_args, "mode")
            and parsed_args.mode == "git_commit"
            and hasattr(parsed_args, "generate_message")
            and parsed_args.generate_message
        ):

            repo = GitRepository()
            if not repo.is_repository():
                print("❌ Error: Git repository not detected in current directory")
                return 1

            try:
                diff = repo.get_staged_diff()
            except Exception as err:
                print(f"❌ Git error: {err}")
                return 1

            if not diff.strip():
                print(
                    "❌ Error: No staged changes found. Stage files before generating a commit message"
                )
                print("💡 Use: git add <files> to stage changes")
                return 1

            # Create enhanced prompt for commit message generation
            guidance = (
                prompt_text
                if prompt_text.strip()
                else "Generate a comprehensive commit message with proper conventional commit format"
            )
            enhanced_commit_prompt = f"""Analyze the following git diff and generate a Conventional Commit message.

Guidance: {guidance}

Git diff of staged changes:
```diff
{diff}
```

Please generate:
1. A concise commit message following Conventional Commits format (type(scope): description)
2. Use appropriate types: feat, fix, refactor, docs, style, test, chore, perf, ci, revert
3. Keep the subject line under 72 characters
4. Include a body if the changes are complex and need explanation
5. Focus on WHY the changes were made, not just WHAT was changed"""

            prompt_text = enhanced_commit_prompt

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
        if continued_successfully:
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

        if context.ai_mode == AIMode.GIT_COMMIT and response.success:
            self._append_git_signature(response)

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
        if context.ai_mode == AIMode.GIT_COMMIT and response.content:
            commit_exit = self._prompt_commit_confirmation(response.content)
            if commit_exit is not None:
                return commit_exit

        if response.mode == AIMode.SHELL and response.content:
            if self.response_handler.prompt_for_execution(response):
                return self.response_handler.execute_command(response.content)

        return 0

    def _prompt_commit_confirmation(self, commit_message: str) -> int | None:
        """Ask user whether to create a git commit with the generated message."""
        if not commit_message.strip():
            return None

        if not sys.stdin.isatty():
            print("ℹ️ Skipping automatic git commit in non-interactive environment.")
            return None

        try:
            user_input = input("\n💾 Commit this message now? [y/N]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Commit cancelled by user.")
            return 130

        if user_input.lower() not in {"y", "yes"}:
            print("ℹ️ Commit skipped.")
            return None

        return self._execute_git_commit(commit_message)

    def _execute_git_commit(self, commit_message: str) -> int:
        """Run `git commit` with the provided message."""
        repo = GitRepository()
        if not repo.is_repository():
            print("❌ Error: Git repository not detected; cannot create commit.")
            return 1

        message_parts = [
            part.strip()
            for part in commit_message.strip().split("\n\n")
            if part.strip()
        ]
        if not message_parts:
            print("❌ Error: Generated commit message is empty; aborting commit.")
            return 1

        command = ["git", "commit"]
        for part in message_parts:
            command.extend(["-m", part])

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Commit created successfully.")
            return 0

        stderr = (result.stderr or "").strip()
        if stderr:
            print(f"❌ git commit failed: {stderr}")
        else:
            print("❌ git commit failed.")
        return result.returncode


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
