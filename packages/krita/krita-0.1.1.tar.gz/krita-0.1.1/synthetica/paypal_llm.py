"""Generic OpenAI-compatible LLM provider for custom inference endpoints."""

import json
import logging
from typing import Optional

import requests

from .llm import LLMProvider

logger = logging.getLogger(__name__)


class CustomOpenAIProvider(LLMProvider):
    """Generic OpenAI-compatible LLM provider for custom endpoints."""

    def __init__(
        self,
        endpoint_url: str,
        model: str,
        api_key: Optional[str] = None,
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        """
        Initialize custom OpenAI-compatible LLM provider.

        Args:
            endpoint_url: The inference endpoint URL (e.g., https://api.example.com/v1/chat/completions)
            model: Model name to use
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.endpoint_url = endpoint_url
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Generate text using custom OpenAI-compatible endpoint.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            logger.info(f"Making request to {self.endpoint_url}")
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if not content:
                    # Fallback to text field if content is empty
                    content = result["choices"][0].get("text", "")
                return content
            else:
                logger.error(f"Unexpected response format: {result}")
                raise ValueError("No choices found in response")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Custom LLM generation failed: {e}")
            raise


def get_custom_openai_provider(**kwargs) -> CustomOpenAIProvider:
    """Get custom OpenAI-compatible LLM provider."""
    return CustomOpenAIProvider(**kwargs)