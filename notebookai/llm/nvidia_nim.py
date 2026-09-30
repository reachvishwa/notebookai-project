"""
NVIDIA NIM LLM provider.

Uses the free NVIDIA NIM API (integrate.api.nvidia.com) for LLM inference.
Model: nvidia/nemotron-3-ultra-550b-a55b
"""

import requests
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from notebookai.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class NVIDIANIMLLMProvider(LLMProvider):
    """NVIDIA NIM LLM provider using nemotron-3-ultra-550b-a55b."""

    MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b"

    def __init__(self, api_url: str, api_key: str, model: str = MODEL_NAME):
        """
        Initialize NVIDIA NIM LLM provider.

        Args:
            api_url: Base URL for NIM API (e.g., https://integrate.api.nvidia.com/v1)
            api_key: NVIDIA NIM API key
            model: Model identifier (default: nemotron-3-ultra-550b-a55b)
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.endpoint = f"{self.api_url}/chat/completions"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate text using NVIDIA NIM API.

        Args:
            prompt: User prompt/query
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated content

        Raises:
            requests.RequestException: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9,
        }

        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            stop_reason = data["choices"][0].get("finish_reason", "stop")

            # Try to extract token usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")

            logger.info(f"Generated response via NVIDIA NIM ({input_tokens} input, {output_tokens} output tokens)")

            return LLMResponse(
                content=content,
                model=self.model,
                stop_reason=stop_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except requests.RequestException as e:
            logger.error(f"Failed to generate response via NVIDIA NIM: {e}")
            raise

    def get_model_name(self) -> str:
        """Return model name."""
        return self.model

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
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 10,
            }

            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"Health check failed for NVIDIA NIM: {e}")
            return False
