"""
LLM CLI Interface - Enhanced CLI interface with logging capabilities

This module provides an enhanced interface for CLI providers that captures both
the response and detailed logs from the CLI execution.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, NamedTuple
import asyncio
from pydantic import BaseModel
from .core import Conversation


class CliResponse(NamedTuple):
    """Response from CLI execution containing result, logs, and provider info"""
    value: str | BaseModel  # The actual response value
    output: str  # Complete log of CLI execution
    provider: str  # Name of the provider that was used


class LlmCli(ABC):
    """Abstract base class for CLI providers with logging capabilities"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def chat(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """
        Chat using CLI with logging capture

        Returns:
            CliResponse with value=response_string and output=execution_logs
        """
        pass

    async def chat_async(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """Async wrapper that offloads sync chat to a worker thread by default."""
        return await asyncio.to_thread(self.chat, conversation, force_json)

    @abstractmethod
    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """
        Chat with structured output using CLI with logging capture

        Returns:
            CliResponse with value=pydantic_model and output=execution_logs
        """
        pass

    async def chat_structured_async(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """Async wrapper that offloads sync structured chat by default."""
        return await asyncio.to_thread(self.chat_structured, conversation, schema, context_size)

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """Check if this CLI provider is available on the system"""
        pass

    @staticmethod
    @abstractmethod
    def capabilities() -> set[str]:
        """Return set of capabilities this CLI provider supports"""
        pass


class LlmCliMeta(LlmCli):
    """
    Meta-provider that round-robins through available CLI providers

    This provider cycles through available CLI providers using round-robin selection,
    starting from a random provider to distribute load evenly across providers.
    """

    def __init__(self):
        super().__init__("meta")
        self._providers: list[LlmCli] = []
        self._next_provider_index: int = 0
        self._load_available_providers()
        self._initialize_random_start()

    def _load_available_providers(self):
        """Load all available CLI providers"""
        from .llm_cli_codex import LlmCodexCli
        from .llm_cli_gemini import LlmGeminiCli
        from .llm_cli_claude import LlmClaudeCli

        provider_classes = [LlmCodexCli, LlmGeminiCli, LlmClaudeCli]

        for provider_class in provider_classes:
            if provider_class.is_available():
                try:
                    provider = provider_class()
                    self._providers.append(provider)
                except Exception as e:
                    # Log the error but continue with other providers
                    print(f"Warning: Failed to initialize {provider_class.__name__}: {e}")

    def _initialize_random_start(self):
        """Initialize with random starting provider to distribute load"""
        if self._providers:
            import random
            self._next_provider_index = random.randint(0, len(self._providers) - 1)

    def _get_next_provider(self) -> LlmCli:
        """Get next provider using round-robin selection"""
        if not self._providers:
            raise Exception("No CLI providers available")

        provider = self._providers[self._next_provider_index]
        self._next_provider_index = (self._next_provider_index + 1) % len(self._providers)
        return provider

    def chat(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """
        Use round-robin provider selection for chat
        """
        provider = self._get_next_provider()

        try:
            result = provider.chat(conversation, force_json)

            # Enhance output with provider selection info
            enhanced_output = f"=== Selected provider: {provider.provider_name} (round-robin) ===\n{result.output}"
            return CliResponse(value=result.value, output=enhanced_output, provider=provider.provider_name)

        except Exception as e:
            error_output = f"=== Provider {provider.provider_name} failed ===\nError: {e}"
            raise Exception(f"CLI provider {provider.provider_name} failed: {e}\n\nLog:\n{error_output}")

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """
        Use round-robin provider selection for structured chat
        """
        provider = self._get_next_provider()

        try:
            result = provider.chat_structured(conversation, schema, context_size)

            # Enhance output with provider selection info
            enhanced_output = f"=== Selected provider: {provider.provider_name} (round-robin) ===\n{result.output}"
            return CliResponse(value=result.value, output=enhanced_output, provider=provider.provider_name)

        except Exception as e:
            error_output = f"=== Provider {provider.provider_name} structured failed ===\nError: {e}"
            raise Exception(f"CLI provider {provider.provider_name} structured failed: {e}\n\nLog:\n{error_output}")

    @staticmethod
    def is_available() -> bool:
        """Meta provider is always available if any individual provider is available"""
        from .llm_cli_codex import LlmCodexCli
        from .llm_cli_gemini import LlmGeminiCli
        from .llm_cli_claude import LlmClaudeCli

        return any(cls.is_available() for cls in [LlmCodexCli, LlmGeminiCli, LlmClaudeCli])

    @staticmethod
    def capabilities() -> set[str]:
        """Return union of all available provider capabilities"""
        from .llm_cli_codex import LlmCodexCli
        from .llm_cli_gemini import LlmGeminiCli
        from .llm_cli_claude import LlmClaudeCli

        all_capabilities = set()
        for provider_class in [LlmCodexCli, LlmGeminiCli, LlmClaudeCli]:
            if provider_class.is_available():
                all_capabilities.update(provider_class.capabilities())

        return all_capabilities

    def get_available_providers(self) -> list[str]:
        """Get list of available provider names"""
        return [provider.provider_name for provider in self._providers]

    def get_next_provider_name(self) -> str:
        """Get the name of the provider that will be used for the next call"""
        if not self._providers:
            raise Exception("No CLI providers available")
        return self._providers[self._next_provider_index].provider_name
