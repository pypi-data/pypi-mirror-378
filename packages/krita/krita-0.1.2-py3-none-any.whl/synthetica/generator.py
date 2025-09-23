"""Core synthetic data generator."""

import json
import logging
from typing import Any, Dict, List, Optional

from .llm import LLMProvider, get_llm_provider, parse_json_response
from .schema import DataSchema

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generate synthetic datasets using LLMs."""

    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        batch_size: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the synthetic data generator.

        Args:
            llm_provider: LLM provider to use ('openai' or 'anthropic')
            llm_model: Specific model to use (optional)
            api_key: API key for the LLM provider (optional if set via env)
            base_url: Custom base URL for OpenAI-compatible endpoints (optional)
            batch_size: Number of samples to generate per LLM call
            max_retries: Maximum number of retries for failed generations
        """
        kwargs = {"api_key": api_key}
        if llm_model:
            kwargs["model"] = llm_model
        if base_url:
            kwargs["base_url"] = base_url

        self.llm = get_llm_provider(llm_provider, **kwargs)
        self.batch_size = batch_size
        self.max_retries = max_retries

    def generate(self, schema: DataSchema) -> List[Dict[str, Any]]:
        """
        Generate synthetic data based on the provided schema.

        Args:
            schema: Data schema defining the structure and constraints

        Returns:
            List of generated data samples
        """
        total_samples = schema.num_samples
        generated_data = []

        while len(generated_data) < total_samples:
            remaining = min(self.batch_size, total_samples - len(generated_data))
            batch_schema = DataSchema(
                name=schema.name,
                description=schema.description,
                fields=schema.fields,
                num_samples=remaining,
                context=schema.context,
            )

            try:
                batch_data = self._generate_batch(batch_schema)
                generated_data.extend(batch_data)
                logger.info(f"Generated {len(batch_data)} samples ({len(generated_data)}/{total_samples})")
            except Exception as e:
                logger.error(f"Failed to generate batch: {e}")
                if len(generated_data) == 0:
                    raise
                break

        return generated_data[:total_samples]

    def _generate_batch(self, schema: DataSchema) -> List[Dict[str, Any]]:
        """Generate a batch of synthetic data."""
        prompt = self._create_generation_prompt(schema)

        for attempt in range(self.max_retries):
            try:
                response = self.llm.generate(prompt, max_tokens=4000)
                data = parse_json_response(response)

                if not data:
                    raise ValueError("Empty response from LLM")

                validated_data = self._validate_and_clean_data(data, schema)
                return validated_data

            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise

        raise RuntimeError("All generation attempts failed")

    def _create_generation_prompt(self, schema: DataSchema) -> str:
        """Create generation prompt from schema."""
        base_prompt = schema.to_prompt()

        additional_instructions = [
            "",
            f"Generate exactly {schema.num_samples} samples.",
            "Ensure all required fields are present in each sample.",
            "Make the data realistic and diverse.",
            "Return only valid JSON - no additional text or formatting.",
            "",
            "Example format:",
            "[",
            "  {",
            f'    "{schema.fields[0].name}": "example_value",',
            f'    "{schema.fields[1].name if len(schema.fields) > 1 else "field2"}": "example_value"',
            "  }",
            "]",
        ]

        return base_prompt + "\n" + "\n".join(additional_instructions)

    def _validate_and_clean_data(
        self, data: List[Dict[str, Any]], schema: DataSchema
    ) -> List[Dict[str, Any]]:
        """Validate and clean generated data."""
        required_fields = {field.name for field in schema.fields if field.required}
        all_fields = {field.name for field in schema.fields}

        cleaned_data = []
        for item in data:
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dict item: {item}")
                continue

            missing_required = required_fields - set(item.keys())
            if missing_required:
                logger.warning(f"Skipping item missing required fields: {missing_required}")
                continue

            extra_fields = set(item.keys()) - all_fields
            if extra_fields:
                logger.info(f"Removing extra fields: {extra_fields}")
                item = {k: v for k, v in item.items() if k in all_fields}

            cleaned_data.append(item)

        return cleaned_data

    def save_to_json(self, data: List[Dict[str, Any]], filepath: str) -> None:
        """Save generated data to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_to_jsonl(self, data: List[Dict[str, Any]], filepath: str) -> None:
        """Save generated data to JSONL file."""
        with open(filepath, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")