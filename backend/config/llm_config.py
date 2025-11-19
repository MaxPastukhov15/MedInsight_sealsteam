"""LLM provider configuration."""

from typing import Dict, Any

# LLM parameters
LLM_TEMPERATURE: float = 0.3
LLM_MAX_TOKENS: int = 1024
LLM_TIMEOUT: int = 10

# Model names by provider
MODEL_NAMES: Dict[str, str] = {
    "ollama": "mistral:latest",
    "together": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "openai": "gpt-4-turbo-preview",
    "cohere": "command-r-plus",
}

# Provider-specific configurations
PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "ollama": {
        "temperature": LLM_TEMPERATURE,
        "num_predict": LLM_MAX_TOKENS,
    },
    "together": {
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    },
    "openai": {
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    },
    "cohere": {
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    },
}
