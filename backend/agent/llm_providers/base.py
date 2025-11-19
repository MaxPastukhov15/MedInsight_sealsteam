"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> None:
        """Initialize LLM provider.

        Args:
            model_name: Name of the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from prompt.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Generate text with streaming.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Yields:
            Text chunks
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration.

        Returns:
            Configuration dict
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
