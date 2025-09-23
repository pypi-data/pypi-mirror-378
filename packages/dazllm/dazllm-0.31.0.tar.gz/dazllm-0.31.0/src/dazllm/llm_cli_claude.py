"""
Claude CLI Provider with logging capabilities

Extends the original LlmClaudeCli to implement the new LlmCli interface
with comprehensive logging capture using Claude's built-in debug features.
"""

import subprocess
import json
from typing import Type
from pydantic import BaseModel

from .llm_cli_interface import LlmCli, CliResponse
from .llm_claude_cli import LlmClaudeCli as OriginalLlmClaudeCli
from .core import Conversation, ConfigurationError


class LlmClaudeCli(LlmCli):
    """Claude CLI provider with enhanced logging"""

    def __init__(self):
        super().__init__("claude")
        self._original = OriginalLlmClaudeCli("claude:claude-3-5-sonnet-20241022")

    def chat(self, conversation: Conversation, force_json: bool = False) -> CliResponse:
        """Chat with Claude CLI capturing full execution logs"""
        prompt_args = self._original._normalize_conversation(conversation)

        if force_json:
            prompt_args[-1] = f"{prompt_args[-1]}\n\nPlease respond with valid JSON only, no other text."

        try:
            # Use --debug for comprehensive logging, --print for non-interactive mode
            cmd = [
                self._original.executable,
                "--debug",
                "--print",
                "--output-format", "text",
                "--dangerously-skip-permissions"
            ]
            cmd.extend(prompt_args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            # Compile comprehensive log
            execution_log = []
            execution_log.append("Claude CLI Execution Log")
            # Don't log full prompt
            execution_log.append(
                "Command: claude --debug --print [options] [prompt]"
            )
            execution_log.append(f"Return code: {result.returncode}")

            # Add debug output from stderr
            if result.stderr:
                execution_log.append("\n=== Debug Output ===")
                # Filter and limit debug output
                debug_lines = result.stderr.split('\n')
                filtered_debug = []
                for line in debug_lines:
                    # Include relevant debug information
                    if any(keyword in line for keyword in [
                        '[DEBUG]', 'Creating shell', 'Applying permission',
                        'Tool execution', 'API call', 'File operation',
                        'Error:', 'Warning:'
                    ]):
                        filtered_debug.append(line)

                # Limit to most relevant debug lines
                execution_log.extend(filtered_debug[:25])

            if result.returncode != 0:
                execution_log.append(
                    f"\nError: Command failed with return code {result.returncode}"
                )
                raise Exception(f"Claude CLI error: {result.stderr}")

            response = result.stdout.strip()

            if force_json:
                response = self._original._extract_json_string(response)

            execution_log.append(f"\nFinal response length: {len(response)}")
            execution_log.append(f"Response preview: {response[:100]}...")

            log_output = "\n".join(execution_log)
            return CliResponse(value=response, output=log_output, provider=self.provider_name)

        except Exception as e:
            error_msg = f"Claude CLI execution error: {e}"
            log_output = (
                "Claude CLI Execution Log\n"
                "Command: claude --debug --print [options] [prompt]\n"
                f"Error: {error_msg}"
            )
            raise Exception(f"{error_msg}\n\nLog:\n{log_output}")

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> CliResponse:
        """Chat with structured output capturing execution logs"""
        execution_log = []
        execution_log.append("=== Claude CLI Structured Output ===")
        execution_log.append(f"Schema: {schema.__name__}")
        execution_log.append(f"Schema fields: {list(schema.model_fields.keys())}")

        try:
            # Build the structured prompt like the original
            schema_json = schema.model_json_schema()
            schema_str = json.dumps(schema_json, indent=2)

            prompt_args = self._original._normalize_conversation(conversation)
            structured_prompt = (
                f"{prompt_args[0]}\n\n"
                f"IMPORTANT: You must provide a JSON response that exactly matches this schema:\n"
                f"{schema_str}\n\n"
                f"CRITICAL INSTRUCTIONS:\n"
                f"1. Start your response with any explanations, logs, or working notes\n"
                f"2. Then add the marker: === RESULT JSON START ===\n"
                f"3. Provide ONLY the valid JSON matching the schema\n"
                f"4. End with the marker: === RESULT JSON END ===\n"
                f"5. Everything between the markers must be valid JSON with no other text\n\n"
                f"Example format:\n"
                f"[Your working notes and explanations here]\n"
                f"=== RESULT JSON START ===\n"
                f"{{\"field\": \"value\"}}\n"
                f"=== RESULT JSON END ==="
            )

            execution_log.append("\n=== Schema Definition ===")
            if len(schema_str) > 200:
                execution_log.append(f"Schema JSON: {schema_str[:200]}...")
            else:
                execution_log.append(f"Schema JSON: {schema_str}")

            # Use our enhanced chat method to get the response with logging
            chat_result = self.chat(structured_prompt, force_json=False)
            execution_log.append("\n=== Console Output ===")
            execution_log.append(chat_result.output)

            # Extract JSON from response
            response_text = chat_result.value
            execution_log.append("\n=== Processing Response ===")

            # Try to extract JSON with markers first
            parsed_json = None
            start_marker = "=== RESULT JSON START ==="
            end_marker = "=== RESULT JSON END ==="

            if start_marker in response_text and end_marker in response_text:
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.find(end_marker)
                json_str = response_text[start_idx:end_idx].strip()
                execution_log.append("Found JSON between markers")
                if len(json_str) > 200:
                    execution_log.append(f"Extracted JSON: {json_str[:200]}...")
                else:
                    execution_log.append(f"Extracted JSON: {json_str}")

                try:
                    parsed_json = json.loads(json_str)
                except json.JSONDecodeError as e:
                    execution_log.append(f"Failed to parse marked JSON: {e}")

            # If no markers or parse failed, fall back to extraction
            if parsed_json is None:
                execution_log.append("Falling back to JSON extraction")
                parsed_json = self._original._extract_json(response_text)

            # Validate against schema
            from jsonschema import validate
            validate(instance=parsed_json, schema=schema_json)
            result = schema(**parsed_json)

            execution_log.append("\n=== Validation: PASSED ===")
            execution_log.append(f"Result: {result.model_dump()}")

            log_output = "\n".join(execution_log)
            return CliResponse(value=result, output=log_output, provider=self.provider_name)

        except Exception as e:
            execution_log.append("\n=== ERROR ===")
            execution_log.append(str(e))
            log_output = "\n".join(execution_log)
            raise Exception(f"Claude CLI structured execution error: {e}\n\nLog:\n{log_output}")

    @staticmethod
    def is_available() -> bool:
        """Check if Claude CLI is available"""
        try:
            OriginalLlmClaudeCli.check_config()
            return True
        except ConfigurationError:
            return False

    @staticmethod
    def capabilities() -> set[str]:
        """Return capabilities of Claude CLI"""
        return OriginalLlmClaudeCli.capabilities()
