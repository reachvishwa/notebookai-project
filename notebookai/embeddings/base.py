"""
Abstract base class for embedding providers.

All embedding implementations (NVIDIA NIM, OpenAI, etc.) inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Optional


class EmbeddingProvider(ABC):
    """Abstract base class for text embedding providers."""

    @abstractmethod
    def embed(self, texts: list[str]) -> dict:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of strings to embed

        Returns:
            dict with keys:
                - 'embeddings': list of embedding vectors (list[list[float]])
                - 'dimension': int (embedding dimension, e.g., 1024 for nemotron)
                - 'model': str (model name used)
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Return the embedding dimension for this provider.

        Returns:
            int: Embedding dimension (e.g., 1024 for nemotron-3-embed-1b)
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify the provider is accessible and working.

        Returns:
            bool: True if provider is healthy, False otherwise
        """
        pass
