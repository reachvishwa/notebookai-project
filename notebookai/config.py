"""
Configuration module for NotebookAI.

Loads environment variables and provides factory functions for
instantiating embedding and LLM providers.
"""

import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_vector_dimension: int = Field(default=1024, alias="SUPABASE_VECTOR_DIMENSION")

    # Embedding Provider
    embedding_provider: Literal["nvidia_nim", "openai"] = Field(
        default="nvidia_nim", alias="EMBEDDING_PROVIDER"
    )
    nvidia_nim_embedding_url: str = Field(
        default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_NIM_EMBEDDING_URL"
    )
    nvidia_nim_embedding_model: str = Field(
        default="nvidia/nemotron-3-embed-1b", alias="NVIDIA_NIM_EMBEDDING_MODEL"
    )
    nvidia_nim_api_key: str = Field(default="", alias="NVIDIA_NIM_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")

    # LLM Provider
    llm_provider: Literal["nvidia_nim", "openai", "anthropic"] = Field(
        default="nvidia_nim", alias="LLM_PROVIDER"
    )
    nvidia_nim_llm_url: str = Field(
        default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_NIM_LLM_URL"
    )
    nvidia_nim_llm_model: str = Field(
        default="nvidia/nemotron-3-ultra-550b-a55b", alias="NVIDIA_NIM_LLM_MODEL"
    )
    openai_llm_model: str = Field(default="gpt-4o-mini", alias="OPENAI_LLM_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_llm_model: str = Field(default="claude-opus-4-1", alias="ANTHROPIC_LLM_MODEL")

    # Application
    chunk_size: int = Field(default=1500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    max_upload_size_mb: int = Field(default=50, alias="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: str = Field(default="pdf,docx,txt,md", alias="ALLOWED_FILE_TYPES")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    debug: bool = Field(default=False, alias="DEBUG")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_max_upload_bytes(self) -> int:
        """Return max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    def get_allowed_file_types(self) -> list[str]:
        """Return list of allowed file types."""
        return [ft.strip() for ft in self.allowed_file_types.split(",")]


# Global settings instance
settings = Settings()


def get_embedding_provider():
    """
    Factory function to instantiate the configured embedding provider.

    Returns:
        EmbeddingProvider instance (NVIDIA NIM or OpenAI)
    """
    from notebookai.embeddings.factory import create_embedding_provider

    return create_embedding_provider(settings)


def get_llm_provider():
    """
    Factory function to instantiate the configured LLM provider.

    Returns:
        LLMProvider instance (NVIDIA NIM, OpenAI, or Anthropic)
    """
    from notebookai.llm.factory import create_llm_provider

    return create_llm_provider(settings)


if __name__ == "__main__":
    # Print loaded config (mask sensitive values)
    print("Configuration loaded:")
    print(f"  Embedding Provider: {settings.embedding_provider}")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  Supabase URL: {settings.supabase_url[:50]}...")
    print(f"  Chunk Size: {settings.chunk_size}")
    print(f"  Retrieval Top-K: {settings.retrieval_top_k}")
