"""
Anthropic LLM provider.

Fallback provider using Anthropic's Claude API.
"""

from anthropic import Anthropic
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from notebookai.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicLLMProvider(LLMProvider):
    """Anthropic LLM provider using Claude."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-1"):
        """
        Initialize Anthropic LLM provider.

        Args:
            api_key: Anthropic API key
            model: Model identifier (default: claude-opus-4-1)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate text using Anthropic API.

        Args:
            prompt: User prompt/query
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )

            content = response.content[0].text
            stop_reason = response.stop_reason

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            logger.info(f"Generated response via Anthropic ({input_tokens} input, {output_tokens} output tokens)")

            return LLMResponse(
                content=content,
                model=self.model,
                stop_reason=stop_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except Exception as e:
            logger.error(f"Failed to generate response via Anthropic: {e}")
            raise

    def get_model_name(self) -> str:
        """Return model name."""
        return self.model

    def health_check(self) -> bool:
        """
        Verify Anthropic API is accessible.

        Returns:
            bool: True if API responds, False otherwise
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return response is not None

        except Exception as e:
            logger.warning(f"Health check failed for Anthropic: {e}")
            return False
