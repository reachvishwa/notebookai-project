"""
Factory for creating embedding provider instances based on configuration.
"""

import logging
from notebookai.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


def create_embedding_provider(settings) -> EmbeddingProvider:
    """
    Instantiate the configured embedding provider.

    Args:
        settings: Configuration object from notebookai.config

    Returns:
        EmbeddingProvider instance (NVIDIA NIM or OpenAI)

    Raises:
        ValueError: If provider is not recognized or required keys are missing
    """
    provider_name = settings.embedding_provider.lower()

    if provider_name == "nvidia_nim":
        if not settings.nvidia_nim_api_key:
            raise ValueError("NVIDIA_NIM_API_KEY not set in environment")

        from notebookai.embeddings.nvidia_nim import NVIDIANIMEmbeddingProvider

        logger.info(f"Initializing NVIDIA NIM embedding provider: {settings.nvidia_nim_embedding_model}")
        return NVIDIANIMEmbeddingProvider(
            api_url=settings.nvidia_nim_embedding_url,
            api_key=settings.nvidia_nim_api_key,
            model=settings.nvidia_nim_embedding_model,
        )

    elif provider_name == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        from notebookai.embeddings.openai import OpenAIEmbeddingProvider

        logger.info(f"Initializing OpenAI embedding provider: {settings.openai_embedding_model}")
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )

    else:
        raise ValueError(
            f"Unknown embedding provider: {provider_name}. "
            "Supported: 'nvidia_nim', 'openai'"
        )
