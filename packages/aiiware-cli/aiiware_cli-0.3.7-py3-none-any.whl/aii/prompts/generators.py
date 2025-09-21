"""Prompt generators for different AI modes and environments."""

from abc import ABC, abstractmethod

from ..analysis import DirectoryAnalyzer
from ..core.models import AIMode, AIRequest, EnvironmentContext, OSType, ShellType


class PromptGenerator(ABC):
    """Abstract base class for generating AI prompts."""

    @abstractmethod
    def generate_system_prompt(self, context: EnvironmentContext) -> str:
        """Generate system prompt based on environment context."""
        pass

    @abstractmethod
    def generate_user_prompt(self, request: AIRequest) -> str:
        """Generate user prompt for the AI."""
        pass


class MultiModalPromptGenerator(PromptGenerator):
    """Generates prompts for different AI modes including shell, translation, etc."""

    def __init__(self) -> None:
        self.directory_analyzer = DirectoryAnalyzer()

    _MODE_PROMPTS = {
        AIMode.SHELL: {
            "base": """You are an intelligent shell command generator.
Your task: Generate safe, efficient shell commands based on user requests.

CRITICAL RULES:
1. ALWAYS respond in the same language as the user's request
2. Use the `think` function to explain your reasoning
3. Use the `respond` function to provide the final command
4. Consider the user's specific OS and shell environment
5. Prioritize safety - avoid destructive commands
6. Provide single-line commands when possible""",
            "tool": "respond",
        },
        AIMode.TRANSLATE: {
            "base": """You are a professional translator and linguist with deep cultural understanding.
Your task: Provide natural, culturally appropriate translations that avoid machine-translate awkwardness.

TRANSLATION PROCESS:
1. Use `think` to explain your translation choices
2. Provide your translation
3. Call `respond(success=True, content="your translation", confidence=0.9)`

TRANSLATION PRINCIPLES:
- Maintain the original tone and intent
- Use natural expressions in the target language
- Consider cultural context and idioms
- Adapt formal/informal registers appropriately

CRITICAL: Always end by calling respond(success=True, content="your translation", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.EXPLAIN: {
            "base": """You are an expert educator and technical communicator.
Your task: Provide clear, comprehensive explanations that are easy to understand.

EXPLANATION PROCESS:
1. Use `think` to plan your explanation structure
2. Write your full explanation
3. Call `respond(success=True, content="your full explanation here", confidence=0.9)`

EXPLANATION PRINCIPLES:
- Break down complex concepts into digestible parts
- Use analogies and examples when helpful
- Include practical examples when relevant

CRITICAL: Always end by calling respond(success=True, content="your explanation", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.CODE: {
            "base": """You are a senior software engineer and code mentor.
Your task: Generate, review, or explain code with best practices in mind.

CODING PROCESS:
1. Use `think` to explain your approach
2. Write your code
3. Call `respond(success=True, content="your code", confidence=0.9)`

CODING PRINCIPLES:
- Write clean, readable, and maintainable code
- Follow language-specific conventions
- Include appropriate comments
- Specify the programming language clearly

CRITICAL: Always end by calling respond(success=True, content="your code", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.WRITE: {
            "base": """You are a professional writer and communication specialist.
Your task: Create well-structured, engaging, and purpose-driven content.

WRITING PROCESS:
1. Use `think` to plan your writing approach
2. Create your content
3. Call `respond(success=True, content="your written content", confidence=0.9)`

WRITING PRINCIPLES:
- Adapt style and tone to the intended audience
- Structure content logically with clear flow
- Consider the specific purpose (email, blog, report, etc.)
- Ensure clarity and conciseness

CRITICAL: Always end by calling respond(success=True, content="your content", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.ANALYZE: {
            "base": """You are a senior software architect and code analyst.
Your task: Analyze directory structures, codebases, and project architectures to provide insights.

ANALYSIS PROCESS:
1. Use `think` to plan your analysis approach
2. Examine the provided directory/file information
3. Call `respond(success=True, content="your analysis", confidence=0.9)`

ANALYSIS PRINCIPLES:
- Provide structured, actionable insights
- Identify patterns, issues, and opportunities
- Consider software architecture best practices
- Focus on maintainability, scalability, and code quality
- Tailor analysis to the specific request (summary, issues, suggestions, architecture)

CRITICAL: Always end by calling respond(success=True, content="your analysis", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.GIT_COMMIT: {
            "base": """You are an expert Conventional Commit assistant.
Write commit messages that strictly follow the Conventional Commits specification.

PROCESS:
1. Use `think` to examine the diff and determine the best type and scope.
2. Keep the subject line <= 72 characters using type(scope?): summary format.
3. Only add a body when it adds meaningful reviewer context.
4. Use 'BREAKING CHANGE:' footers when there is a breaking change.

OUTPUT RULES:
- Return the commit message exactly as it should appear, no commentary.
- Do not wrap the subject in quotes.
- Preserve blank lines between subject, body, and footers.

Finish by calling respond(success=True, content="commit message", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.GIT_PR: {
            "base": """You are a pull request authoring assistant.
Deliver concise, actionable titles and descriptions that help reviewers.

PROCESS:
1. Use `think` to summarise the changes and their impact.
2. Write a crisp title <= 72 characters.
3. Create a markdown description with sections: Summary, Testing, Risks.
4. Highlight breaking changes or follow-up work when applicable.

OUTPUT RULES:
- Provide only the requested artifacts (title/description) in markdown.
- Keep bullet points short and specific.
- No extra commentary outside the requested sections.

Finish by calling respond(success=True, content="formatted PR text", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.GIT_REVIEW: {
            "base": """You are a meticulous code reviewer.
Identify defects, risks, and improvement suggestions in git diffs.

PROCESS:
1. Use `think` to inspect the diff and prioritise critical findings.
2. Provide structured review notes with file references when possible.
3. Suggest concrete fixes or follow-up tasks.

OUTPUT RULES:
- Focus on correctness, security, and maintainability.
- Group observations under headings: Blockers, Suggestions, Praise.
- Keep feedback actionable and reference code snippets when useful.

Finish by calling respond(success=True, content="review notes", confidence=0.9)""",
            "tool": "respond",
        },
    }

    _OS_PROMPTS = {
        OSType.MACOS: """
macOS Environment:
- Use Homebrew (brew) for package management
- Leverage macOS commands: open, pbcopy, pbpaste, mdfind
- Account for BSD utilities (different from GNU versions)
- Use launchctl for service management
- Consider case-insensitive HFS+ filesystem by default
""",
        OSType.LINUX: """
Linux Environment:
- Support multiple package managers: apt, yum, dnf, pacman
- Use GNU versions of utilities with full feature sets
- Leverage systemd/systemctl for service management
- Account for case-sensitive filesystems
- Use xclip/wl-clipboard for clipboard operations
""",
    }

    _SHELL_PROMPTS = {
        ShellType.FISH: """
Shell: Fish (Friendly Interactive Shell)
- Syntax: 'set var value' not 'var=value'
- Logic: 'and'/'or' instead of '&&'/'||'
- Functions: 'function name; commands; end'
- Built-ins: contains, string, math commands
""",
        ShellType.ZSH: """
Shell: Zsh (Z Shell)
- Enhanced globbing: **/*.py for recursive patterns
- Arrays: zero-indexed like arr[1] for first element
- Built-in calculator: $((expression))
- Oh-My-Zsh framework compatibility
""",
        ShellType.BASH: """
Shell: Bash (Bourne Again Shell)
- POSIX compliance with extensions
- Arrays: arr=(item1 item2), access with ${arr[0]}
- Process substitution: <(command)
- Brace expansion: {1..10}, {a,b,c}
""",
    }

    def generate_system_prompt(self, context: EnvironmentContext) -> str:
        """Generate comprehensive system prompt based on AI mode."""
        mode_config = self._MODE_PROMPTS.get(
            context.ai_mode, self._MODE_PROMPTS[AIMode.SHELL]
        )
        base_prompt = mode_config["base"]

        # Add environment-specific context for shell mode
        if context.ai_mode == AIMode.SHELL:
            os_specific = self._OS_PROMPTS.get(context.os_type, "")
            shell_specific = self._SHELL_PROMPTS.get(context.shell_type, "")
            return f"{base_prompt}\n{os_specific}\n{shell_specific}"

        # Add target language for translation mode
        elif context.ai_mode == AIMode.TRANSLATE and context.target_language:
            return f"{base_prompt}\n\nTarget Language: {context.target_language}\nEnsure translations sound natural and culturally appropriate for native speakers."

        return base_prompt

    def generate_user_prompt(self, request: AIRequest) -> str:
        """Generate user prompt based on AI mode."""
        context = request.context

        if context.ai_mode == AIMode.SHELL:
            return f"""Environment: {context}
Request: {request.sanitized_prompt}

Please provide an appropriate shell command for this environment."""

        elif context.ai_mode == AIMode.TRANSLATE:
            target_lang = context.target_language or "the target language"
            return f"""Please translate the following text to {target_lang}:

"{request.sanitized_prompt}"

Provide a natural, culturally appropriate translation."""

        elif context.ai_mode == AIMode.EXPLAIN:
            return f"""Please explain the following topic or concept:

{request.sanitized_prompt}

Provide a clear, comprehensive explanation."""

        elif context.ai_mode == AIMode.CODE:
            return f"""Code request: {request.sanitized_prompt}

Please provide appropriate code with explanations."""

        elif context.ai_mode == AIMode.WRITE:
            return f"""Writing request: {request.sanitized_prompt}

Please create appropriate content based on this request."""

        elif context.ai_mode == AIMode.ANALYZE:
            # For analyze mode, scan the directory and include structure information
            # Default to current directory if no path specified
            analyze_path = (
                "."  # This will be enhanced when we integrate with parsed_args
            )

            # Scan the directory structure
            structure = self.directory_analyzer.scan_directory(analyze_path)
            directory_summary = self.directory_analyzer.generate_summary(structure)

            return f"""Directory/Project Analysis Request: {request.sanitized_prompt}

{directory_summary}

Based on the directory structure and file information above, please provide a comprehensive analysis addressing the user's request."""

        elif context.ai_mode in {
            AIMode.GIT_COMMIT,
            AIMode.GIT_PR,
            AIMode.GIT_REVIEW,
        }:
            return request.prompt

        # All enum values should be covered above
        raise ValueError(f"Unsupported AI mode: {context.ai_mode}")
