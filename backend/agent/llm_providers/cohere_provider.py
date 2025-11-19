"""Cohere provider."""

from typing import Optional, Any, AsyncIterator
import httpx

from agent.llm_providers.base import BaseLLMProvider
from config.settings import settings
from monitoring.logging_config import logger


class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider."""

    def __init__(
        self,
        model_name: str = "command-r-plus",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize Cohere provider.

        Args:
            model_name: Cohere model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            api_key: Cohere API key
        """
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = api_key or settings.COHERE_API_KEY
        self.base_url = "https://api.cohere.ai/v1"
        logger.info("cohere_provider_initialized", model=model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Cohere.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            return result["generations"][0]["text"]

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Generate text with streaming.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Yields:
            Text chunks
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
            }

            headers = {"Authorization": f"Bearer {self.api_key}"}

            async with client.stream(
                "POST",
                f"{self.base_url}/generate",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "text" in chunk:
                            yield chunk["text"]
