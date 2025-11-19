"""LLM provider factory.

Фабрика для создания LLM провайдеров.
Поддерживает: Ollama (local), Together AI, OpenAI, Cohere.
Использование:
    provider = get_llm_provider()  # использует LLM_PROVIDER из .env
    provider = get_llm_provider("ollama", "mistral:latest")
    response = await provider.generate("Hello, world!")
"""

from typing import Optional

from agent.llm_providers.base import BaseLLMProvider
from agent.llm_providers.cohere_provider import CohereProvider
from agent.llm_providers.ollama_provider import OllamaProvider
from agent.llm_providers.openai_provider import OpenAIProvider
from agent.llm_providers.together_provider import TogetherProvider
from config.llm_config import MODEL_NAMES, PROVIDER_CONFIGS
from config.settings import settings
from monitoring.logging_config import logger


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers = {
        "ollama": OllamaProvider,
        "together": TogetherProvider,
        "openai": OpenAIProvider,
        "cohere": CohereProvider,
    }

    @classmethod
    def create(
        cls,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ) -> BaseLLMProvider:
        """Create LLM provider instance."""
        provider_name = provider_name or settings.LLM_PROVIDER

        if provider_name not in cls._providers:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {list(cls._providers.keys())}"
            )

        default_model = MODEL_NAMES.get(provider_name)
        config = PROVIDER_CONFIGS.get(provider_name, {})
        final_model = model_name or default_model
        final_config = {**config, **kwargs}

        logger.info(
            "creating_llm_provider",
            provider=provider_name,
            model=final_model,
        )

        provider_class = cls._providers[provider_name]
        return provider_class(model_name=final_model, **final_config)


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs,
) -> BaseLLMProvider:
    """Get LLM provider instance."""
    return LLMProviderFactory.create(provider_name, model_name, **kwargs)
