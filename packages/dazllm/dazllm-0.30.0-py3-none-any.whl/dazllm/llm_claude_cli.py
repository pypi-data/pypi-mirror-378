"""
Claude CLI implementation for dazllm
Uses the claude command-line tool for LLM interactions
"""

import subprocess
import json
import re
from typing import Type, Optional
from pydantic import BaseModel
from jsonschema import validate, ValidationError

from .core import Llm, Conversation, ConfigurationError, DazLlmError


class LlmClaudeCli(Llm):
    """Claude CLI implementation"""

    def __init__(self, model: str):
        super().__init__(model)
        self.executable = self._find_executable()
        self._check_executable()

    @staticmethod
    def default_model() -> str:
        """Default model for Claude CLI"""
        return "claude-3-5-sonnet-20241022"

    @staticmethod
    def default_for_type(model_type: str) -> Optional[str]:
        """Get default model for a given type"""
        defaults = {
            "local_small": None,  # Claude doesn't have local models
            "local_medium": None,
            "local_large": None,
            "paid_cheap": "claude-3-5-haiku-20241022",
            "paid_best": "claude-3-5-sonnet-20241022",
        }
        return defaults.get(model_type)

    @staticmethod
    def capabilities() -> set[str]:
        """Return set of capabilities this provider supports"""
        return {"chat", "structured"}

    @staticmethod
    def supported_models() -> list[str]:
        """Return list of models this provider supports"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    @staticmethod
    def check_config():
        """Check if Claude CLI is properly configured"""
        try:
            result = subprocess.run(
                ["claude", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ConfigurationError(f"Claude CLI not accessible: {result.stderr}")
        except FileNotFoundError:
            raise ConfigurationError("Claude CLI not found. Please install claude CLI tool.")
        except subprocess.TimeoutExpired:
            raise ConfigurationError("Claude CLI timeout")
        except Exception as e:
            raise ConfigurationError(f"Claude CLI error: {e}") from e

    def _find_executable(self) -> str:
        """Find the claude executable"""
        import shutil
        executable = shutil.which("claude")
        if not executable:
            raise ConfigurationError("Claude CLI not found in PATH")
        return executable

    def _check_executable(self):
        """Ensure the executable is available and working"""
        try:
            result = subprocess.run(
                [self.executable, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ConfigurationError(f"Claude CLI check failed: {result.stderr}")
        except Exception as e:
            raise ConfigurationError(f"Cannot run Claude CLI: {e}") from e

    def _normalize_conversation(self, conversation: Conversation) -> list[str]:
        """Convert conversation to arguments for Claude CLI"""
        if isinstance(conversation, str):
            return [conversation]

        # For message list, create a structured prompt
        prompt_parts = []
        for msg in conversation:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"<system>{content}</system>")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"Human: {content}")

        return ["\n".join(prompt_parts)]

    def chat(self, conversation: Conversation, force_json: bool = False) -> str:
        """Chat using Claude CLI"""
        prompt_args = self._normalize_conversation(conversation)

        if force_json:
            prompt_args[-1] = f"{prompt_args[-1]}\n\nPlease respond with valid JSON only, no other text."

        try:
            # Use --print for non-interactive mode, --output-format text for plain text
            cmd = [
                self.executable,
                "--print",
                "--output-format", "text",
                "--dangerously-skip-permissions"  # For headless operation
            ]
            cmd.extend(prompt_args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise DazLlmError(f"Claude CLI error: {result.stderr}")

            response = result.stdout.strip()

            # If force_json, try to extract JSON from response
            if force_json:
                response = self._extract_json_string(response)

            return response

        except subprocess.TimeoutExpired:
            raise DazLlmError("Claude CLI timeout after 120 seconds")
        except Exception as e:
            raise DazLlmError(f"Claude CLI execution error: {e}") from e

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> BaseModel:
        """Chat with structured output using Pydantic schema"""
        schema_json = schema.model_json_schema()
        schema_str = json.dumps(schema_json, indent=2)

        # Build prompt with schema instructions
        prompt_args = self._normalize_conversation(conversation)
        structured_prompt = (
            f"{prompt_args[0]}\n\n"
            f"You must respond with valid JSON that matches the following schema exactly.\n"
            f"Output ONLY the JSON, no other text or explanation.\n"
            f"JSON Schema:\n{schema_str}"
        )

        attempts = 10
        last_error = None
        current_prompt = structured_prompt

        while attempts > 0:
            try:
                # Use --print for non-interactive mode
                cmd = [
                    self.executable,
                    "--print",
                    "--output-format", "text",
                    "--dangerously-skip-permissions",  # For headless operation
                    current_prompt
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    raise DazLlmError(f"Claude CLI error: {result.stderr}")

                response = result.stdout.strip()

                # Parse JSON from response
                parsed_json = self._extract_json(response)

                # Validate against schema
                validate(instance=parsed_json, schema=schema_json)

                # Create and return Pydantic model
                return schema(**parsed_json)

            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                current_prompt += (
                    f"\n\nThe previous response was not valid JSON. Error: {e}\n"
                    f"Please respond with ONLY valid JSON matching the schema."
                )
            except ValidationError as e:
                last_error = e
                current_prompt += (
                    f"\n\nThe JSON didn't match the schema. Error: {e}\n"
                    f"Please fix and return valid JSON matching the schema exactly."
                )
            except subprocess.TimeoutExpired:
                raise DazLlmError("Claude CLI timeout after 120 seconds")
            except Exception as e:
                raise DazLlmError(f"Claude CLI execution error: {e}") from e

            attempts -= 1

        raise DazLlmError(f"Failed to get valid structured response after multiple attempts. Last error: {last_error}")

    def _extract_json_string(self, text: str) -> str:
        """Extract JSON string from text (for force_json mode)"""
        # Try to find JSON in the response
        try:
            parsed = self._extract_json(text)
            return json.dumps(parsed)
        except (json.JSONDecodeError, ValueError):
            return text  # Return original if can't parse

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text with multiple fallback strategies"""
        # Strategy 1: Look for markdown code blocks
        if "```json" in text:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

        # Strategy 2: Look for any code blocks
        if "```" in text:
            match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

        # Strategy 3: Try to parse the entire text
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Strategy 4: Look for JSON-like structures
        json_patterns = [
            r'\{[^{}]*\}',  # Simple JSON object
            r'\{.*\}',      # Any JSON object
            r'\[.*\]',      # JSON array
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        # Strategy 5: Clean common prefixes and try again
        cleaned = text.strip()
        for prefix in ["Here is the JSON:", "JSON:", "Output:", "Result:", "Response:"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")

    def image(self, prompt: str, file_name: str, width: int = 1024, height: int = 1024) -> str:
        """Generate image using Claude CLI (not supported)"""
        raise DazLlmError("Image generation not supported by Claude CLI")

    def get_context_length(self) -> int:
        """Get the context length for Claude CLI models"""
        # Claude CLI uses the same models as the API, so use same context lengths
        context_lengths = {
            "claude-3-5-sonnet-20241022": 200000,    # 200K tokens
            "claude-3-5-sonnet-20240620": 200000,    # 200K tokens
            "claude-3-5-haiku-20241022": 200000,     # 200K tokens
            "claude-3-opus-20240229": 200000,        # 200K tokens
            "claude-3-sonnet-20240229": 200000,      # 200K tokens
            "claude-3-haiku-20240307": 200000,       # 200K tokens
            "claude-2.1": 200000,                    # 200K tokens
            "claude-2.0": 100000,                    # 100K tokens
            "claude-instant-1.2": 100000,            # 100K tokens
        }

        return context_lengths.get(self.model, 200000)  # Default to 200K


# Note: No embedded tests; integration tests live under tests/ and perform real calls.
