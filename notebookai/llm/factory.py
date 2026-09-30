"""
Factory for creating LLM provider instances based on configuration.
"""

import logging
from notebookai.llm.base import LLMProvider

logger = logging.getLogger(__name__)


def create_llm_provider(settings) -> LLMProvider:
    """
    Instantiate the configured LLM provider.

    Args:
        settings: Configuration object from notebookai.config

    Returns:
        LLMProvider instance (NVIDIA NIM, OpenAI, or Anthropic)

    Raises:
        ValueError: If provider is not recognized or required keys are missing
    """
    provider_name = settings.llm_provider.lower()

    if provider_name == "nvidia_nim":
        if not settings.nvidia_nim_api_key:
            raise ValueError("NVIDIA_NIM_API_KEY not set in environment")

        from notebookai.llm.nvidia_nim import NVIDIANIMLLMProvider

        logger.info(f"Initializing NVIDIA NIM LLM provider: {settings.nvidia_nim_llm_model}")
        return NVIDIANIMLLMProvider(
            api_url=settings.nvidia_nim_llm_url,
            api_key=settings.nvidia_nim_api_key,
            model=settings.nvidia_nim_llm_model,
        )

    elif provider_name == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        from notebookai.llm.openai import OpenAILLMProvider

        logger.info(f"Initializing OpenAI LLM provider: {settings.openai_llm_model}")
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_llm_model,
        )

    elif provider_name == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        from notebookai.llm.anthropic import AnthropicLLMProvider

        logger.info(f"Initializing Anthropic LLM provider: {settings.anthropic_llm_model}")
        return AnthropicLLMProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_llm_model,
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. "
            "Supported: 'nvidia_nim', 'openai', 'anthropic'"
        )
