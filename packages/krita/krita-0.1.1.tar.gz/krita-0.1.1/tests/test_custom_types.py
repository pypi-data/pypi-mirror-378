"""Tests for custom field types functionality."""

import pytest
from pydantic import ValidationError

from synthetica.schema import DataSchema, FieldSchema, FieldType


class TestCustomFieldTypes:
    """Test custom field types functionality."""

    def test_custom_type_with_enum_value(self):
        """Test custom type using FieldType.CUSTOM enum value."""
        field = FieldSchema(
            name="medical_condition",
            type=FieldType.CUSTOM,
            description="Medical condition",
            custom_type_definition="A medical condition or diagnosis",
            examples=["diabetes", "hypertension"]
        )

        assert field.name == "medical_condition"
        assert field.type == FieldType.CUSTOM
        assert field.is_custom_type() is True
        assert field.get_type_display() == "custom"
        assert field.custom_type_definition == "A medical condition or diagnosis"

    def test_custom_type_with_string_value(self):
        """Test custom type using a custom string value."""
        field = FieldSchema(
            name="skill_level",
            type="programming_skill",
            description="Programming skill level",
            custom_type_definition="A programming skill with proficiency level",
            examples=["Python - Expert", "JavaScript - Intermediate"]
        )

        assert field.name == "skill_level"
        assert field.type == "programming_skill"
        assert field.is_custom_type() is True
        assert field.get_type_display() == "programming_skill"
        assert field.custom_type_definition == "A programming skill with proficiency level"

    def test_builtin_type_validation(self):
        """Test that built-in types work normally."""
        field = FieldSchema(
            name="email",
            type=FieldType.EMAIL,
            description="Email address",
            required=True
        )

        assert field.name == "email"
        assert field.type == FieldType.EMAIL
        assert field.is_custom_type() is False
        assert field.get_type_display() == "email"
        assert field.custom_type_definition is None

    def test_custom_type_requires_definition(self):
        """Test that custom types require a definition."""
        with pytest.raises(ValidationError, match="custom_type_definition is required"):
            FieldSchema(
                name="custom_field",
                type=FieldType.CUSTOM,
                description="Custom field without definition"
            )

    def test_custom_string_type_requires_definition(self):
        """Test that custom string types require a definition."""
        with pytest.raises(ValidationError, match="custom_type_definition is required"):
            FieldSchema(
                name="custom_field",
                type="custom_string_type",
                description="Custom field without definition"
            )

    def test_builtin_type_string_works(self):
        """Test that built-in types work when specified as strings."""
        field = FieldSchema(
            name="user_name",
            type="name",  # String version of built-in type
            description="User's name"
        )

        assert field.name == "user_name"
        assert field.type == "name"
        assert field.is_custom_type() is False
        assert field.get_type_display() == "name"

    def test_schema_with_mixed_types(self):
        """Test schema with both built-in and custom types."""
        fields = [
            FieldSchema(
                name="id",
                type=FieldType.UUID,
                required=True
            ),
            FieldSchema(
                name="email",
                type="email",
                required=True
            ),
            FieldSchema(
                name="skill",
                type="programming_skill",
                custom_type_definition="Programming skill with experience level",
                examples=["Python - 5 years"]
            ),
            FieldSchema(
                name="medical_info",
                type=FieldType.CUSTOM,
                custom_type_definition="Medical information including conditions and medications",
                required=False
            )
        ]

        schema = DataSchema(
            name="mixed_types_test",
            description="Test schema with mixed field types",
            fields=fields,
            num_samples=5
        )

        assert schema.name == "mixed_types_test"
        assert len(schema.fields) == 4

        # Check that the schema identifies custom fields correctly
        custom_fields = [f for f in schema.fields if f.is_custom_type()]
        assert len(custom_fields) == 2
        assert custom_fields[0].name == "skill"
        assert custom_fields[1].name == "medical_info"

    def test_prompt_generation_with_custom_types(self):
        """Test that prompt generation includes custom type definitions."""
        fields = [
            FieldSchema(
                name="name",
                type=FieldType.NAME,
                required=True
            ),
            FieldSchema(
                name="skill",
                type="programming_skill",
                description="Programming skill",
                custom_type_definition="Programming language and proficiency level",
                examples=["Python - Expert"]
            ),
            FieldSchema(
                name="certification",
                type=FieldType.CUSTOM,
                description="Professional certification",
                custom_type_definition="Professional certification with issuing body and expiration date"
            )
        ]

        schema = DataSchema(
            name="developer_profiles",
            description="Developer profile data",
            fields=fields,
            num_samples=3
        )

        prompt = schema.to_prompt()

        # Check that the prompt includes custom type information
        assert "Custom field types:" in prompt
        assert "skill: Programming language and proficiency level" in prompt
        assert "certification: Professional certification with issuing body and expiration date" in prompt
        assert "programming_skill" in prompt
        assert "Programming skill - Programming language and proficiency level" in prompt

    def test_custom_type_with_constraints(self):
        """Test custom types with constraints."""
        field = FieldSchema(
            name="risk_score",
            type="risk_rating",
            description="Risk assessment score",
            custom_type_definition="Risk score from 1-10 with category and justification",
            constraints={"format": "X/10 (Category): Justification", "range": "1-10"},
            examples=["7/10 (High): Volatile conditions"]
        )

        assert field.constraints["format"] == "X/10 (Category): Justification"
        assert field.constraints["range"] == "1-10"
        assert field.is_custom_type() is True

    def test_schema_from_dict_with_custom_types(self):
        """Test creating schema from dictionary with custom types."""
        data = {
            "name": "custom_test",
            "description": "Test custom types from dict",
            "num_samples": 5,
            "fields": [
                {
                    "name": "id",
                    "type": "uuid",
                    "required": True
                },
                {
                    "name": "skill_level",
                    "type": "programming_expertise",
                    "description": "Programming expertise level",
                    "custom_type_definition": "Programming skill with years of experience",
                    "examples": ["Python - 5 years", "Java - 3 years"],
                    "required": True
                },
                {
                    "name": "certification",
                    "type": "custom",
                    "description": "Professional certification",
                    "custom_type_definition": "Professional certification with details",
                    "required": False
                }
            ]
        }

        schema = DataSchema.from_dict(data)
        assert schema.name == "custom_test"
        assert len(schema.fields) == 3

        # Check custom fields
        skill_field = schema.fields[1]
        assert skill_field.type == "programming_expertise"
        assert skill_field.is_custom_type() is True

        cert_field = schema.fields[2]
        assert cert_field.type == "custom"
        assert cert_field.is_custom_type() is True