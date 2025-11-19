"""OpenAI provider."""

from typing import Any, AsyncIterator, Optional

from agent.llm_providers.base import BaseLLMProvider
from config.settings import settings
from langchain_openai import ChatOpenAI
from monitoring.logging_config import logger


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            model_name: OpenAI model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            api_key: OpenAI API key
        """
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_key,
        )
        logger.info("openai_provider_initialized", model=model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.ainvoke(messages)
        return response.content

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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async for chunk in self.client.astream(messages):
            if chunk.content:
                yield chunk.content
