"""AI content generation with multi-provider support."""

import os
import sys
from typing import TYPE_CHECKING, Any

from ..core.models import (
    AIMode,
    AIRequest,
    AIResponse,
    EnvironmentContext,
    ProviderType,
)
from ..core.utils import debug_print
from ..prompts import PromptGenerator

# Pydantic AI imports are optional so tests and lightweight setups can run without them
if TYPE_CHECKING:
    from pydantic_ai import Agent as AgentType
    from pydantic_ai.models.anthropic import AnthropicModel as AnthropicModelType
    from pydantic_ai.models.google import GoogleModel as GoogleModelType
    from pydantic_ai.models.openai import OpenAIChatModel as OpenAIChatModelType
    from pydantic_ai.providers.anthropic import (
        AnthropicProvider as AnthropicProviderType,
    )
    from pydantic_ai.providers.google import GoogleProvider as GoogleProviderType
    from pydantic_ai.providers.openai import OpenAIProvider as OpenAIProviderType
else:  # pragma: no cover - typing fallback when dependency missing
    AgentType = Any
    AnthropicModelType = Any
    GoogleModelType = Any
    OpenAIChatModelType = Any
    AnthropicProviderType = Any
    GoogleProviderType = Any
    OpenAIProviderType = Any

AgentClass: Any
AnthropicModelClass: Any
GoogleModelClass: Any
OpenAIChatModelClass: Any
AnthropicProviderClass: Any
GoogleProviderClass: Any
OpenAIProviderClass: Any

try:
    from pydantic_ai import Agent as _AgentClass
    from pydantic_ai.models.anthropic import AnthropicModel as _AnthropicModelClass
    from pydantic_ai.models.google import GoogleModel as _GoogleModelClass
    from pydantic_ai.models.openai import OpenAIChatModel as _OpenAIChatModelClass
    from pydantic_ai.providers.anthropic import (
        AnthropicProvider as _AnthropicProviderClass,
    )
    from pydantic_ai.providers.google import GoogleProvider as _GoogleProviderClass
    from pydantic_ai.providers.openai import OpenAIProvider as _OpenAIProviderClass

    AgentClass = _AgentClass
    AnthropicModelClass = _AnthropicModelClass
    GoogleModelClass = _GoogleModelClass
    OpenAIChatModelClass = _OpenAIChatModelClass
    AnthropicProviderClass = _AnthropicProviderClass
    GoogleProviderClass = _GoogleProviderClass
    OpenAIProviderClass = _OpenAIProviderClass
    _PYDANTIC_AI_IMPORT_ERROR: Exception | None = None
except ModuleNotFoundError as exc:
    AgentClass = None
    AnthropicModelClass = None
    GoogleModelClass = None
    OpenAIChatModelClass = None
    AnthropicProviderClass = None
    GoogleProviderClass = None
    OpenAIProviderClass = None
    _PYDANTIC_AI_IMPORT_ERROR = exc


def _ensure_pydantic_ai_available() -> None:
    """Ensure optional pydantic_ai dependency is available before use."""
    if AgentClass is None or GoogleModelClass is None or GoogleProviderClass is None:
        message = (
            "pydantic_ai is required for AI generation. Install it with "
            "`uv add pydantic-ai` and include provider extras as needed."
        )
        raise RuntimeError(message) from _PYDANTIC_AI_IMPORT_ERROR


class AIGenerator:
    """Main class for AI-powered content generation across multiple modes."""

    def __init__(self, api_key: str, prompt_generator: PromptGenerator):
        self.api_key = api_key
        self.prompt_generator = prompt_generator
        self._agents: dict[str, AgentType] = {}

    def _get_agent(self, context: EnvironmentContext) -> AgentType:
        """Get or create agent for specific environment context."""
        _ensure_pydantic_ai_available()
        assert AgentClass is not None
        assert GoogleModelClass is not None
        assert GoogleProviderClass is not None

        # Create cache key based on mode, provider, and relevant context
        provider_key = f"{context.provider_type.value}"
        if context.model_name:
            provider_key += f"_{context.model_name}"

        if context.ai_mode == AIMode.SHELL:
            cache_key = f"shell_{context.os_type.value}_{context.shell_type.value}_{provider_key}"
        elif context.ai_mode == AIMode.TRANSLATE:
            cache_key = f"translate_{context.target_language or 'auto'}_{provider_key}"
        else:
            cache_key = f"{context.ai_mode.value}_general_{provider_key}"

        if cache_key not in self._agents:
            system_prompt = self.prompt_generator.generate_system_prompt(context)

            # Create provider and model based on context
            if context.provider_type == ProviderType.ANTHROPIC:
                anthropic_api_key = self._get_anthropic_api_key()
                assert AnthropicProviderClass is not None
                assert AnthropicModelClass is not None
                anthropic_provider = AnthropicProviderClass(api_key=anthropic_api_key)
                model_name = context.model_name or "claude-3-5-sonnet-latest"
                agent = AgentClass(
                    model=AnthropicModelClass(model_name, provider=anthropic_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )
            elif context.provider_type == ProviderType.OPENAI:
                openai_api_key = self._get_openai_api_key()
                assert OpenAIProviderClass is not None
                assert OpenAIChatModelClass is not None
                openai_provider = OpenAIProviderClass(api_key=openai_api_key)
                model_name = context.model_name or "gpt-4o"
                agent = AgentClass(
                    model=OpenAIChatModelClass(model_name, provider=openai_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )
            else:  # Default to Google
                google_provider = GoogleProviderClass(api_key=self.api_key)
                model_name = context.model_name or "gemini-2.0-flash"
                agent = AgentClass(
                    model=GoogleModelClass(model_name, provider=google_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )

            self._setup_agent_tools(agent, context.ai_mode)
            self._agents[cache_key] = agent

        return self._agents[cache_key]

    def _get_anthropic_api_key(self) -> str:
        """Get Anthropic API key from environment."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print(
                "❌ Error: ANTHROPIC_API_KEY environment variable is required for Anthropic provider."
            )
            print("💡 Setup: export ANTHROPIC_API_KEY=your_api_key_here")
            print("🔗 Get key: https://console.anthropic.com/settings/keys")
            sys.exit(1)
        return api_key

    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print(
                "❌ Error: OPENAI_API_KEY environment variable is required for OpenAI provider."
            )
            print("💡 Setup: export OPENAI_API_KEY=your_api_key_here")
            print("🔗 Get key: https://platform.openai.com/account/api-keys")
            sys.exit(1)
        return api_key

    def _setup_agent_tools(self, agent: AgentType, mode: AIMode) -> None:
        """Setup tools for the agent based on mode."""
        debug_print(f"Setting up agent tools for mode: {mode}")

        @agent.tool_plain
        def think(reasoning: str) -> None:
            """Communicate reasoning to the user."""
            if mode == AIMode.TRANSLATE:
                print(f"🌐 Translation Logic: {reasoning}\n")
            elif mode == AIMode.EXPLAIN:
                print(f"🎓 Explanation Structure: {reasoning}\n")
            elif mode == AIMode.CODE:
                print(f"💻 Code Planning: {reasoning}\n")
            elif mode == AIMode.WRITE:
                print(f"✍️  Writing Strategy: {reasoning}\n")
            else:
                print(f"🤔 AII Thinking: {reasoning}\n")

        @agent.tool_plain
        def respond(
            success: bool,
            content: str,
            explanation: str | None = None,
            confidence: float = 0.8,
        ) -> AIResponse:
            """Provide the final response with your generated content.

            Args:
                success: Always set to True when providing content
                content: Your main response (translation, explanation, code, etc.)
                explanation: Optional additional context or notes
                confidence: Your confidence in the response (0.0-1.0)
            """
            debug_print(f"respond() called with mode: {mode}")
            response = AIResponse(
                success=success,
                content=content,
                explanation=explanation,
                error_message=None,
                confidence=confidence,
                mode=mode,
            )
            debug_print(f"Created response with mode: {response.mode}")
            return response

    async def generate_async(self, request: AIRequest) -> AIResponse:
        """Generate content asynchronously."""
        agent = self._get_agent(request.context)
        user_prompt = self.prompt_generator.generate_user_prompt(request)

        try:
            result = await agent.run(user_prompt)
            response = result.output
            assert isinstance(
                response, AIResponse
            ), f"Expected AIResponse, got {type(response)}"
            return response
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"AI generation failed: {str(e)}",
                mode=request.context.ai_mode,
            )

    def generate(self, request: AIRequest) -> AIResponse:
        """Generate content synchronously."""
        agent = self._get_agent(request.context)
        user_prompt = self.prompt_generator.generate_user_prompt(request)

        try:
            result = agent.run_sync(user_prompt)
            response = result.output
            assert isinstance(
                response, AIResponse
            ), f"Expected AIResponse, got {type(response)}"
            debug_print(f"Agent returned response with mode: {response.mode}")

            # Force the mode to match the request context if it doesn't match
            if response.mode != request.context.ai_mode:
                debug_print(
                    f"Mode mismatch! Expected {request.context.ai_mode}, got {response.mode}"
                )
                debug_print("Creating new response with correct mode...")
                corrected_response = AIResponse(
                    success=response.success,
                    content=response.content,
                    explanation=response.explanation,
                    error_message=response.error_message,
                    confidence=response.confidence,
                    mode=request.context.ai_mode,
                )
                debug_print(
                    f"New response created with mode: {corrected_response.mode}"
                )
                return corrected_response

            return response
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"AI generation failed: {str(e)}",
                mode=request.context.ai_mode,
            )
