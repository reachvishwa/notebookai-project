"""
OpenAI embedding provider.

Fallback provider using OpenAI's embedding API.
Model: text-embedding-3-small (1536 dimensions)
"""

from openai import OpenAI, APIError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from notebookai.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small."""

    EMBEDDING_DIMENSION = 1536  # text-embedding-3-small output dimension
    MODEL_NAME = "text-embedding-3-small"

    def __init__(self, api_key: str, model: str = MODEL_NAME):
        """
        Initialize OpenAI embedding provider.

        Args:
            api_key: OpenAI API key
            model: Model identifier (default: text-embedding-3-small)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        # Determine dimension based on model
        self.dimension = 1536 if "3-small" in model else 3072

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed(self, texts: list[str]) -> dict:
        """
        Generate embeddings for texts using OpenAI API.

        Args:
            texts: List of strings to embed

        Returns:
            dict with 'embeddings', 'dimension', 'model'

        Raises:
            APIError: If API call fails after retries
        """
        if not texts:
            return {"embeddings": [], "dimension": self.dimension, "model": self.model}

        try:
            response = self.client.embeddings.create(input=texts, model=self.model)

            embeddings = [item.embedding for item in response.data]

            logger.info(f"Generated embeddings for {len(texts)} texts via OpenAI")

            return {
                "embeddings": embeddings,
                "dimension": self.dimension,
                "model": self.model,
            }

        except APIError as e:
            logger.error(f"Failed to generate embeddings via OpenAI: {e}")
            raise

    def get_dimension(self) -> int:
        """Return embedding dimension."""
        return self.dimension

    def health_check(self) -> bool:
        """
        Verify OpenAI API is accessible.

        Returns:
            bool: True if API responds, False otherwise
        """
        try:
            response = self.client.embeddings.create(input=["test"], model=self.model)
            return response is not None

        except Exception as e:
            logger.warning(f"Health check failed for OpenAI: {e}")
            return False
