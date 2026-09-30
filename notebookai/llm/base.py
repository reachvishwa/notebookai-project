"""
Abstract base class for LLM providers.

All LLM implementations (NVIDIA NIM, OpenAI, Anthropic) inherit from this.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Standardized LLM response format."""

    content: str  # Generated text
    model: str  # Model used
    stop_reason: Optional[str] = None  # 'stop', 'length', 'error', etc.
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate text using the LLM.

        Args:
            prompt: User prompt/query
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            LLMResponse with generated content and metadata
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Return the model name/identifier.

        Returns:
            str: Model name
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify the LLM provider is accessible and working.

        Returns:
            bool: True if provider is healthy, False otherwise
        """
        pass
