"""
OpenAI LLM provider.

Fallback provider using OpenAI's chat completion API.
"""

from openai import OpenAI, APIError
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from notebookai.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI LLM provider.

        Args:
            api_key: OpenAI API key
            model: Model identifier (default: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
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
        Generate text using OpenAI API.

        Args:
            prompt: User prompt/query
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated content

        Raises:
            APIError: If API call fails
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            stop_reason = response.choices[0].finish_reason

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            logger.info(f"Generated response via OpenAI ({input_tokens} input, {output_tokens} output tokens)")

            return LLMResponse(
                content=content,
                model=self.model,
                stop_reason=stop_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except APIError as e:
            logger.error(f"Failed to generate response via OpenAI: {e}")
            raise

    def get_model_name(self) -> str:
        """Return model name."""
        return self.model

    def health_check(self) -> bool:
        """
        Verify OpenAI API is accessible.

        Returns:
            bool: True if API responds, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
            )
            return response is not None

        except Exception as e:
            logger.warning(f"Health check failed for OpenAI: {e}")
            return False
