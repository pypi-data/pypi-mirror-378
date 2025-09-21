"""
Codex CLI Provider with logging capabilities

Extends the original LlmCodexCli to implement the new LlmCli interface
with comprehensive logging capture.
"""

import subprocess
from typing import Type
from pydantic import BaseModel

from .llm_cli_interface import LlmCli, CliResponse
from .llm_codex_cli import LlmCodexCli as OriginalLlmCodexCli
from .core import Conversation, ConfigurationError


class LlmCodexCli(LlmCli):
    """Codex CLI provider with enhanced logging"""

    def __init__(self):
        super().__init__("codex")
        self._original = OriginalLlmCodexCli("codex:default")

    def chat(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """Chat with Codex CLI capturing full execution logs"""
        prompt = self._original._normalize_conversation(conversation)

        if force_json:
            prompt = f"{prompt}\n\nPlease respond with valid JSON only, no other text."

        try:
            # Execute with debug output capture
            cmd = [self._original.executable, "exec", prompt]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            # Codex doesn't have detailed debug logs, so we create our own
            execution_log = []
            execution_log.append("Codex CLI Execution Log")
            execution_log.append(f"Command: {' '.join(cmd)}")
            execution_log.append(f"Return code: {result.returncode}")

            if result.stderr:
                execution_log.append(f"Stderr: {result.stderr}")

            execution_log.append(f"Raw stdout length: {len(result.stdout)}")

            if result.returncode != 0:
                execution_log.append(f"Error: Command failed with return code {result.returncode}")
                raise Exception(f"Codex CLI error: {result.stderr}")

            response = result.stdout.strip()

            if force_json:
                response = self._original._extract_json_string(response)

            execution_log.append(f"Final response length: {len(response)}")
            execution_log.append(f"Response preview: {response[:100]}...")

            log_output = "\n".join(execution_log)
            return CliResponse(value=response, output=log_output, provider=self.provider_name)

        except Exception as e:
            error_msg = f"Codex CLI execution error: {e}"
            log_output = f"Codex CLI Execution Log\nCommand: {' '.join(cmd)}\nError: {error_msg}"
            raise Exception(f"{error_msg}\n\nLog:\n{log_output}")

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """Chat with structured output capturing execution logs"""
        try:
            # Use the original implementation to get the structured result
            result = self._original.chat_structured(conversation, schema, context_size)

            # Create detailed log
            execution_log = []
            execution_log.append("Codex CLI Structured Output Execution Log")
            execution_log.append(f"Schema: {schema.__name__}")
            execution_log.append(f"Schema fields: {list(schema.model_fields.keys())}")
            execution_log.append(f"Conversation type: {type(conversation).__name__}")

            if isinstance(conversation, list):
                execution_log.append(f"Conversation length: {len(conversation)} messages")
            else:
                execution_log.append(f"Conversation length: {len(str(conversation))} chars")

            execution_log.append("Attempts made: Up to 10 (codex implementation)")
            execution_log.append(f"Final result type: {type(result).__name__}")
            execution_log.append(f"Final result: {result.model_dump()}")

            log_output = "\n".join(execution_log)
            return CliResponse(value=result, output=log_output, provider=self.provider_name)

        except Exception as e:
            error_msg = f"Codex CLI structured execution error: {e}"
            log_output = f"Codex CLI Structured Output Execution Log\nSchema: {schema.__name__}\nError: {error_msg}"
            raise Exception(f"{error_msg}\n\nLog:\n{log_output}")

    @staticmethod
    def is_available() -> bool:
        """Check if Codex CLI is available"""
        try:
            OriginalLlmCodexCli.check_config()
            return True
        except ConfigurationError:
            return False

    @staticmethod
    def capabilities() -> set[str]:
        """Return capabilities of Codex CLI"""
        return OriginalLlmCodexCli.capabilities()
