"""Tests for schema validation."""

import pytest
from pydantic import ValidationError

from synthetica.schema import DataSchema, FieldSchema, FieldType


def test_field_schema_creation():
    """Test basic field schema creation."""
    field = FieldSchema(
        name="email",
        type=FieldType.EMAIL,
        description="User email address",
        required=True
    )
    assert field.name == "email"
    assert field.type == FieldType.EMAIL
    assert field.required is True


def test_field_schema_with_examples():
    """Test field schema with examples."""
    field = FieldSchema(
        name="category",
        type=FieldType.CATEGORY,
        examples=["tech", "health", "finance"]
    )
    assert field.examples == ["tech", "health", "finance"]


def test_field_schema_empty_examples():
    """Test that empty examples list becomes None."""
    field = FieldSchema(
        name="test",
        type=FieldType.TEXT,
        examples=[]
    )
    assert field.examples is None


def test_data_schema_creation():
    """Test basic data schema creation."""
    fields = [
        FieldSchema(name="id", type=FieldType.UUID, required=True),
        FieldSchema(name="name", type=FieldType.NAME, required=True),
        FieldSchema(name="email", type=FieldType.EMAIL, required=True)
    ]

    schema = DataSchema(
        name="test_dataset",
        description="Test dataset",
        fields=fields,
        num_samples=10
    )

    assert schema.name == "test_dataset"
    assert schema.description == "Test dataset"
    assert len(schema.fields) == 3
    assert schema.num_samples == 10


def test_data_schema_unique_field_names():
    """Test that field names must be unique."""
    fields = [
        FieldSchema(name="id", type=FieldType.UUID),
        FieldSchema(name="id", type=FieldType.TEXT)  # Duplicate name
    ]

    with pytest.raises(ValidationError):
        DataSchema(
            name="test",
            description="Test",
            fields=fields
        )


def test_data_schema_no_fields():
    """Test that at least one field is required."""
    with pytest.raises(ValidationError):
        DataSchema(
            name="test",
            description="Test",
            fields=[]
        )


def test_data_schema_to_prompt():
    """Test schema to prompt conversion."""
    fields = [
        FieldSchema(
            name="name",
            type=FieldType.NAME,
            description="Person's name",
            examples=["John Doe", "Jane Smith"]
        ),
        FieldSchema(
            name="age",
            type=FieldType.NUMBER,
            constraints={"min": 18, "max": 65}
        )
    ]

    schema = DataSchema(
        name="people",
        description="People dataset",
        fields=fields,
        num_samples=5,
        context="Generate diverse people"
    )

    prompt = schema.to_prompt()
    assert "People dataset" in prompt
    assert "name (name): Person's name" in prompt
    assert "examples: John Doe, Jane Smith" in prompt
    assert "constraints: min=18, max=65" in prompt
    assert "Generate diverse people" in prompt


def test_data_schema_from_dict():
    """Test creating schema from dictionary."""
    data = {
        "name": "test_dataset",
        "description": "Test dataset",
        "num_samples": 10,
        "fields": [
            {
                "name": "id",
                "type": "uuid",
                "required": True
            },
            {
                "name": "name",
                "type": "name",
                "required": True
            }
        ]
    }

    schema = DataSchema.from_dict(data)
    assert schema.name == "test_dataset"
    assert len(schema.fields) == 2
    assert schema.fields[0].name == "id"
    assert schema.fields[0].type == FieldType.UUID