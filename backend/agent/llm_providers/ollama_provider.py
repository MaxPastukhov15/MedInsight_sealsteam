"""Ollama LLM provider."""

from typing import Optional, Any, AsyncIterator
import httpx

from agent.llm_providers.base import BaseLLMProvider
from config.settings import settings
from monitoring.logging_config import logger


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(
        self,
        model_name: str = "mistral:latest",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        base_url: Optional[str] = None,
    ) -> None:
        """Initialize Ollama provider.

        Args:
            model_name: Ollama model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            base_url: Ollama API base URL
        """
        super().__init__(model_name, temperature, max_tokens)
        self.base_url = base_url or settings.LLM_BASE_URL
        logger.info(
            "ollama_provider_initialized",
            model=model_name,
            base_url=self.base_url,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Ollama.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "ollama_generate_complete",
                model=self.model_name,
                tokens=len(result.get("response", "").split()),
            )

            return result.get("response", "")

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
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }

            if system_prompt:
                payload["system"] = system_prompt

            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
