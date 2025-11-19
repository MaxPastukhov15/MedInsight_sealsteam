"""Together AI provider."""

from typing import Optional, Any, AsyncIterator
import httpx

from agent.llm_providers.base import BaseLLMProvider
from config.settings import settings
from monitoring.logging_config import logger


class TogetherProvider(BaseLLMProvider):
    """Together AI LLM provider."""

    def __init__(
        self,
        model_name: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize Together provider.

        Args:
            model_name: Together model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            api_key: Together API key
        """
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = api_key or settings.TOGETHER_API_KEY
        self.base_url = "https://api.together.xyz/v1"
        logger.info("together_provider_initialized", model=model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Together AI.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
            }

            headers = {"Authorization": f"Bearer {self.api_key}"}

            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            import json
                            chunk = json.loads(data)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
