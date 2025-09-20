"""
LLM CLI Interface - Enhanced CLI interface with logging capabilities

This module provides an enhanced interface for CLI providers that captures both
the response and detailed logs from the CLI execution.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, Optional, NamedTuple
from pydantic import BaseModel
from .core import Conversation


class CliResponse(NamedTuple):
    """Response from CLI execution containing both result and logs"""
    value: str | BaseModel  # The actual response value
    output: str  # Complete log of CLI execution


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
    Meta-provider that aggregates all available CLI providers

    This provider automatically tries all available CLI providers and returns
    results from the first successful one, along with aggregated logs from all attempts.
    """

    def __init__(self):
        super().__init__("meta")
        self._providers: list[LlmCli] = []
        self._load_available_providers()

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

    def chat(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """
        Try chat with all available providers, return first success with aggregated logs
        """
        all_output = []
        last_error = None

        for provider in self._providers:
            try:
                all_output.append(f"=== Trying {provider.provider_name} ===")
                result = provider.chat(conversation, force_json)
                all_output.append(result.output)
                all_output.append(f"=== {provider.provider_name} succeeded ===")

                # Return first successful result with all logs
                aggregated_output = "\n".join(all_output)
                return CliResponse(value=result.value, output=aggregated_output)

            except Exception as e:
                all_output.append(f"=== {provider.provider_name} failed: {e} ===")
                last_error = e
                continue

        # If all providers failed
        aggregated_output = "\n".join(all_output)
        raise Exception(f"All CLI providers failed. Last error: {last_error}\n\nFull log:\n{aggregated_output}")

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """
        Try structured chat with all available providers, return first success with aggregated logs
        """
        all_output = []
        last_error = None

        for provider in self._providers:
            try:
                all_output.append(f"=== Trying {provider.provider_name} structured ===")
                result = provider.chat_structured(conversation, schema, context_size)
                all_output.append(result.output)
                all_output.append(f"=== {provider.provider_name} structured succeeded ===")

                # Return first successful result with all logs
                aggregated_output = "\n".join(all_output)
                return CliResponse(value=result.value, output=aggregated_output)

            except Exception as e:
                all_output.append(f"=== {provider.provider_name} structured failed: {e} ===")
                last_error = e
                continue

        # If all providers failed
        aggregated_output = "\n".join(all_output)
        raise Exception(f"All CLI providers failed for structured output. Last error: {last_error}\n\nFull log:\n{aggregated_output}")

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