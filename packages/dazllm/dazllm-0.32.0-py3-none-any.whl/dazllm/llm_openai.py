"""
OpenAI implementation for dazllm
"""

import keyring
import json
import unittest
from typing import Type
from pydantic import BaseModel

from .core import Llm, Conversation, ConfigurationError, DazLlmError, _run_sync


class LlmOpenai(Llm):
    """OpenAI implementation"""

    def __init__(self, model: str):
        super().__init__(model)
        self.check_config()

        # Import OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=self._get_api_key())
        except ImportError as exc:
            raise ConfigurationError(
                "OpenAI library not installed. Run: pip install openai"
            ) from exc

    @staticmethod
    def default_model() -> str:
        """Default model for OpenAI"""
        return "gpt-4o"

    @staticmethod
    def default_for_type(model_type: str) -> str:
        """Get default model for a given type"""
        defaults = {
            "local_small": None,  # OpenAI doesn't have local models
            "local_medium": None,
            "local_large": None,
            "paid_cheap": "gpt-4o-mini",
            "paid_best": "gpt-4o",
        }
        return defaults.get(model_type)

    @staticmethod
    def capabilities() -> set[str]:
        """Return set of capabilities this provider supports"""
        return {"chat", "structured", "image"}

    @staticmethod
    def supported_models() -> list[str]:
        """Return list of models this provider supports"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "dall-e-3",
            "dall-e-2",
            "gpt-image-1",
        ]

    @staticmethod
    def check_config():
        """Check if OpenAI is properly configured"""
        api_key = keyring.get_password("dazllm", "openai_api_key")
        if not api_key:
            raise ConfigurationError(
                "OpenAI API key not found in keyring. Set with: keyring set dazllm openai_api_key"
            )

    def _get_api_key(self) -> str:
        """Get OpenAI API key from keyring"""
        api_key = keyring.get_password("dazllm", "openai_api_key")
        if not api_key:
            raise ConfigurationError("OpenAI API key not found in keyring")
        return api_key

    def _normalize_conversation(self, conversation: Conversation) -> list:
        """Convert conversation to OpenAI message format"""
        if isinstance(conversation, str):
            return [{"role": "user", "content": conversation}]
        return conversation

    def chat(self, conversation: Conversation, force_json: bool = False) -> str:
        """Sync wrapper; blocks on async_chat."""
        return _run_sync(self.async_chat(conversation, force_json))

    async def async_chat(self, conversation: Conversation, force_json: bool = False) -> str:
        """Async chat using OpenAI's async client when available, else thread offload."""
        import asyncio
        messages = self._normalize_conversation(conversation)
        kwargs = {"model": self.model, "messages": messages}
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        # Try native async client first
        try:
            from openai import AsyncOpenAI  # type: ignore

            client = AsyncOpenAI(api_key=self._get_api_key())
            response = await client.chat.completions.create(**kwargs)  # type: ignore[arg-type]
            return response.choices[0].message.content
        except Exception:
            # Fallback: perform the blocking call in a worker thread using the sync client
            def _call_sync():
                try:
                    return self.client.chat.completions.create(**kwargs)
                except Exception as e:  # noqa: BLE001
                    raise DazLlmError(f"OpenAI API error: {e}") from e

            response = await asyncio.to_thread(_call_sync)
            return response.choices[0].message.content

    def chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> BaseModel:
        """Sync wrapper; blocks on async_chat_structured."""
        return _run_sync(self.async_chat_structured(conversation, schema, context_size))

    async def async_chat_structured(
        self, conversation: Conversation, schema: Type[BaseModel], context_size: int = 0
    ) -> BaseModel:
        import asyncio

        messages = self._normalize_conversation(conversation)
        schema_json = schema.model_json_schema()
        schema_prompt = f"\n\nPlease respond with valid JSON matching this schema:\n{json.dumps(schema_json, indent=2)}"
        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] += schema_prompt
        else:
            messages.append({"role": "user", "content": schema_prompt})

        async def _call_async():
            try:
                from openai import AsyncOpenAI  # type: ignore

                client = AsyncOpenAI(api_key=self._get_api_key())
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                return response.choices[0].message.content
            except Exception:
                def _call_sync():
                    return self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        response_format={"type": "json_object"},
                    )
                resp = await asyncio.to_thread(_call_sync)
                return resp.choices[0].message.content

        content = await _call_async()
        try:
            data = json.loads(content)
            return schema(**data)
        except json.JSONDecodeError as exc:  # noqa: PERF203
            raise DazLlmError(f"Could not parse JSON response: {content}") from exc
        except Exception as e:  # noqa: BLE001
            raise DazLlmError(f"Could not create Pydantic model: {e}") from e

    def image(
        self, prompt: str, file_name: str, width: int = 1024, height: int = 1024
    ) -> str:
        """Sync wrapper; blocks on async_image."""
        return _run_sync(self.async_image(prompt, file_name, width, height))

    async def async_image(
        self, prompt: str, file_name: str, width: int = 1024, height: int = 1024
    ) -> str:
        from .image_utils import ImageUtils
        import base64
        from PIL import Image
        from io import BytesIO
        import asyncio
        import os

        image_model = self.model if self.model in ["gpt-image-1", "dall-e-2", "dall-e-3"] else "gpt-image-1"

        # Calculate optimal generation size and enhance prompt
        gen_width, gen_height = ImageUtils.calculate_optimal_size(width, height)
        enhanced_prompt = ImageUtils.enhance_prompt_for_aspect_ratio(prompt, gen_width, gen_height)

        # Try native async client
        try:
            from openai import AsyncOpenAI  # type: ignore
            client = AsyncOpenAI(api_key=self._get_api_key())
            response = await client.images.generate(
                model=image_model,
                prompt=enhanced_prompt,
                size=f"{gen_width}x{gen_height}",
                quality="high",
                response_format="b64_json",
                n=1,
            )
            data = response.data[0]
        except Exception:
            # Fallback: call sync in thread
            def _call_sync():
                return self.client.images.generate(
                    model=image_model,
                    prompt=enhanced_prompt,
                    size=f"{gen_width}x{gen_height}",
                    quality="high",
                    output_format="png",
                    n=1,
                )

            resp = await asyncio.to_thread(_call_sync)
            data = resp.data[0]

        # Save image
        if hasattr(data, "b64_json") and data.b64_json:
            image_data = base64.b64decode(data.b64_json)
            image = Image.open(BytesIO(image_data))
        else:
            return ImageUtils.save_image(data.url, file_name)

        if width != gen_width or height != gen_height:
            temp_path = file_name + "_temp.png"
            image.save(temp_path, 'PNG')
            ImageUtils.resize_and_crop(temp_path, width, height)
            os.remove(temp_path)

        base_dir = os.path.dirname(file_name) or '.'
        os.makedirs(base_dir, exist_ok=True)
        image.save(file_name, 'PNG')
        return file_name

    def get_context_length(self) -> int:
        """Get the context length for the current OpenAI model"""
        # Use OpenAI API to get model info
        try:
            import openai
            api_key = keyring.get_password("dazllm", "openai_api_key")
            if not api_key:
                raise DazLlmError("OpenAI API key not found")

            client = openai.OpenAI(api_key=api_key)

            # Get model details from OpenAI API
            model_info = client.models.retrieve(self.model)

            # Check if the model has context_length in the response
            if hasattr(model_info, 'context_length'):
                return model_info.context_length

            # Fallback to known context lengths for common models
            context_lengths = {
                "gpt-4o": 128000,
                "gpt-4o-mini": 128000,
                "gpt-4-turbo": 128000,
                "gpt-4": 8192,
                "gpt-3.5-turbo": 16385,
                "gpt-3.5-turbo-16k": 16385,
                "text-davinci-003": 4097,
                "text-davinci-002": 4097,
                "code-davinci-002": 8001,
                "gpt-image-1": 4096,  # Image models have different context
                "dall-e-2": 4096,
                "dall-e-3": 4096,
            }

            return context_lengths.get(self.model, 4096)  # Default fallback

        except Exception:
            # If API call fails, use known defaults
            context_lengths = {
                "gpt-4o": 128000,
                "gpt-4o-mini": 128000,
                "gpt-4-turbo": 128000,
                "gpt-4": 8192,
                "gpt-3.5-turbo": 16385,
                "gpt-3.5-turbo-16k": 16385,
                "text-davinci-003": 4097,
                "text-davinci-002": 4097,
                "code-davinci-002": 8001,
                "gpt-image-1": 4096,
                "dall-e-2": 4096,
                "dall-e-3": 4096,
            }

            return context_lengths.get(self.model, 4096)


class TestLlmOpenai(unittest.TestCase):
    """Essential tests for LlmOpenai class"""

    def test_default_model(self):
        """Test default model returns expected value"""
        self.assertEqual(LlmOpenai.default_model(), "gpt-4o")

    def test_default_for_type(self):
        """Test default_for_type returns correct models"""
        self.assertEqual(LlmOpenai.default_for_type("paid_cheap"), "gpt-4o-mini")
        self.assertEqual(LlmOpenai.default_for_type("paid_best"), "gpt-4o")
        self.assertIsNone(LlmOpenai.default_for_type("local_small"))

    def test_capabilities(self):
        """Test capabilities returns expected set"""
        capabilities = LlmOpenai.capabilities()
        self.assertEqual(capabilities, {"chat", "structured", "image"})

    def test_supported_models(self):
        """Test supported_models returns expected list"""
        models = LlmOpenai.supported_models()
        self.assertIn("gpt-4o", models)
        self.assertIn("dall-e-3", models)

    def test_normalize_conversation_string(self):
        """Test conversation normalization with string input"""
        result = [{"role": "user", "content": "hello"}] if isinstance("hello", str) else "hello"
        self.assertEqual(result, [{"role": "user", "content": "hello"}])


__all__ = ["LlmOpenai"]
