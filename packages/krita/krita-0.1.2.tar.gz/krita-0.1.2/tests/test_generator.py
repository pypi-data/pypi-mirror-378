"""Tests for synthetic data generator."""

import json
from unittest.mock import Mock, patch

import pytest

from synthetica.generator import SyntheticDataGenerator
from synthetica.schema import DataSchema, FieldSchema, FieldType


@pytest.fixture
def sample_schema():
    """Sample schema for testing."""
    fields = [
        FieldSchema(name="id", type=FieldType.UUID, required=True),
        FieldSchema(name="name", type=FieldType.NAME, required=True),
        FieldSchema(name="email", type=FieldType.EMAIL, required=True)
    ]

    return DataSchema(
        name="test_dataset",
        description="Test dataset",
        fields=fields,
        num_samples=5
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return json.dumps([
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        {
            "id": "987fcdeb-51e2-47d8-9c6b-123456789abc",
            "name": "Jane Smith",
            "email": "jane.smith@example.com"
        }
    ])


class TestSyntheticDataGenerator:
    """Test the SyntheticDataGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        with patch("synthetica.generator.get_llm_provider") as mock_provider:
            mock_provider.return_value = Mock()

            generator = SyntheticDataGenerator(
                llm_provider="openai",
                llm_model="gpt-3.5-turbo",
                batch_size=5
            )

            assert generator.batch_size == 5
            assert generator.max_retries == 3
            mock_provider.assert_called_once_with("openai", api_key=None, model="gpt-3.5-turbo")

    def test_generate_batch(self, sample_schema, mock_llm_response):
        """Test batch generation."""
        with patch("synthetica.generator.get_llm_provider") as mock_provider:
            mock_llm = Mock()
            mock_llm.generate.return_value = mock_llm_response
            mock_provider.return_value = mock_llm

            generator = SyntheticDataGenerator()
            result = generator._generate_batch(sample_schema)

            assert len(result) == 2
            assert result[0]["name"] == "John Doe"
            assert result[1]["email"] == "jane.smith@example.com"

    def test_validate_and_clean_data(self, sample_schema):
        """Test data validation and cleaning."""
        with patch("synthetica.generator.get_llm_provider") as mock_provider:
            mock_provider.return_value = Mock()

            generator = SyntheticDataGenerator()

            # Test data with extra field
            dirty_data = [
                {
                    "id": "123",
                    "name": "John",
                    "email": "john@example.com",
                    "extra_field": "should_be_removed"
                }
            ]

            cleaned = generator._validate_and_clean_data(dirty_data, sample_schema)
            assert len(cleaned) == 1
            assert "extra_field" not in cleaned[0]
            assert cleaned[0]["name"] == "John"

    def test_validate_missing_required_field(self, sample_schema):
        """Test validation when required field is missing."""
        with patch("synthetica.generator.get_llm_provider") as mock_provider:
            mock_provider.return_value = Mock()

            generator = SyntheticDataGenerator()

            # Missing required 'email' field
            data_missing_field = [
                {
                    "id": "123",
                    "name": "John"
                    # email is missing
                }
            ]

            cleaned = generator._validate_and_clean_data(data_missing_field, sample_schema)
            assert len(cleaned) == 0  # Should be filtered out

    def test_create_generation_prompt(self, sample_schema):
        """Test prompt generation."""
        with patch("synthetica.generator.get_llm_provider") as mock_provider:
            mock_provider.return_value = Mock()

            generator = SyntheticDataGenerator()
            prompt = generator._create_generation_prompt(sample_schema)

            assert "test_dataset" in prompt
            assert "Test dataset" in prompt
            assert "Generate exactly 5 samples" in prompt
            assert "id" in prompt
            assert "name" in prompt
            assert "email" in prompt