"""
NVIDIA NIM embedding provider.

Uses the free NVIDIA NIM API (integrate.api.nvidia.com) for embedding generation.
Model: nvidia/nemotron-3-embed-1b (1024 dimensions)
"""

import requests
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from notebookai.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class NVIDIANIMEmbeddingProvider(EmbeddingProvider):
    """NVIDIA NIM embedding provider using nemotron-3-embed-1b."""

    EMBEDDING_DIMENSION = 1024  # nemotron-3-embed-1b output dimension
    MODEL_NAME = "nvidia/nemotron-3-embed-1b"

    def __init__(self, api_url: str, api_key: str, model: str = MODEL_NAME):
        """
        Initialize NVIDIA NIM embedding provider.

        Args:
            api_url: Base URL for NIM API (e.g., https://integrate.api.nvidia.com/v1)
            api_key: NVIDIA NIM API key
            model: Model identifier (default: nemotron-3-embed-1b)
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.endpoint = f"{self.api_url}/embeddings"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed(self, texts: list[str]) -> dict:
        """
        Generate embeddings for texts using NVIDIA NIM API.

        Args:
            texts: List of strings to embed

        Returns:
            dict with 'embeddings', 'dimension', 'model'

        Raises:
            requests.RequestException: If API call fails after retries
        """
        if not texts:
            return {"embeddings": [], "dimension": self.EMBEDDING_DIMENSION, "model": self.model}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": texts,
            "model": self.model,
        }

        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            embeddings = [item["embedding"] for item in data.get("data", [])]

            logger.info(f"Generated embeddings for {len(texts)} texts via NVIDIA NIM")

            return {
                "embeddings": embeddings,
                "dimension": self.EMBEDDING_DIMENSION,
                "model": self.model,
            }

        except requests.RequestException as e:
            logger.error(f"Failed to generate embeddings via NVIDIA NIM: {e}")
            raise

    def get_dimension(self) -> int:
        """Return embedding dimension."""
        return self.EMBEDDING_DIMENSION

    def health_check(self) -> bool:
        """
        Verify NVIDIA NIM API is accessible.

        Returns:
            bool: True if API responds, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"input": ["test"], "model": self.model}

            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"Health check failed for NVIDIA NIM: {e}")
            return False
