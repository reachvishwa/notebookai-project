"""Embedding providers for NotebookAI."""

from notebookai.embeddings.base import EmbeddingProvider
from notebookai.embeddings.factory import create_embedding_provider

__all__ = ["EmbeddingProvider", "create_embedding_provider"]
