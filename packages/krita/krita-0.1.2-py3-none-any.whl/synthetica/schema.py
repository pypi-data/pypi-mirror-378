"""Schema definition and validation for synthetic data generation."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class FieldType(str, Enum):
    """Built-in field types for synthetic data generation."""

    TEXT = "text"
    EMAIL = "email"
    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"
    DATE = "date"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    JSON = "json"
    URL = "url"
    UUID = "uuid"
    DESCRIPTION = "description"
    REVIEW = "review"
    TITLE = "title"
    CUSTOM = "custom"  # Indicates a custom user-defined type


class FieldSchema(BaseModel):
    """Schema for a single field in the dataset."""

    name: str = Field(..., description="Name of the field")
    type: Union[FieldType, str] = Field(..., description="Type of the field (built-in or custom)")
    description: Optional[str] = Field(None, description="Description of the field")
    examples: Optional[List[str]] = Field(None, description="Example values for the field")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints for the field")
    required: bool = Field(True, description="Whether the field is required")
    custom_type_definition: Optional[str] = Field(None, description="Definition for custom field types")

    @validator("examples")
    def validate_examples(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) == 0:
            return None
        return v

    @validator("custom_type_definition")
    def validate_custom_type_definition(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate that custom types have definitions."""
        field_type = values.get("type")

        # If type is a string and not a known built-in type, require custom_type_definition
        if isinstance(field_type, str):
            try:
                FieldType(field_type)
                # It's a built-in type
                if field_type == FieldType.CUSTOM and not v:
                    raise ValueError("custom_type_definition is required when type is 'custom'")
            except ValueError:
                # It's a custom type string, require definition
                if not v:
                    raise ValueError(f"custom_type_definition is required for custom type '{field_type}'")

        return v

    def get_type_display(self) -> str:
        """Get display string for the field type."""
        if isinstance(self.type, FieldType):
            return self.type.value
        return str(self.type)

    def is_custom_type(self) -> bool:
        """Check if this field uses a custom type."""
        if isinstance(self.type, str):
            try:
                field_type = FieldType(self.type)
                return field_type == FieldType.CUSTOM
            except ValueError:
                return True  # Custom string type
        return self.type == FieldType.CUSTOM


class DataSchema(BaseModel):
    """Schema for the entire dataset."""

    name: str = Field(..., description="Name of the dataset")
    description: str = Field(..., description="Description of the dataset")
    fields: List[FieldSchema] = Field(..., description="List of field schemas")
    num_samples: int = Field(100, description="Number of samples to generate", ge=1)
    context: Optional[str] = Field(None, description="Additional context for generation")

    @validator("fields")
    def validate_fields(cls, v: List[FieldSchema]) -> List[FieldSchema]:
        if len(v) == 0:
            raise ValueError("At least one field is required")

        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Field names must be unique")

        return v

    def to_prompt(self) -> str:
        """Convert schema to a prompt for LLM generation."""
        prompt_parts = [
            f"Generate synthetic data for: {self.description}",
            f"Dataset name: {self.name}",
            "",
            "Fields to generate:",
        ]

        for field in self.fields:
            # Use the display type for built-in types or custom type name
            type_display = field.get_type_display()
            field_desc = f"- {field.name} ({type_display})"

            if field.description:
                field_desc += f": {field.description}"

            # Add custom type definition if present
            if field.custom_type_definition:
                field_desc += f" - {field.custom_type_definition}"

            if field.examples:
                field_desc += f" (examples: {', '.join(field.examples[:3])})"

            if field.constraints:
                constraints_str = ", ".join(f"{k}={v}" for k, v in field.constraints.items())
                field_desc += f" [constraints: {constraints_str}]"

            prompt_parts.append(field_desc)

        if self.context:
            prompt_parts.extend(["", f"Additional context: {self.context}"])

        # Add specific instructions for custom types
        custom_fields = [f for f in self.fields if f.is_custom_type()]
        if custom_fields:
            prompt_parts.extend([
                "",
                "Custom field types:",
            ])
            for field in custom_fields:
                prompt_parts.append(f"- {field.name}: {field.custom_type_definition}")

        prompt_parts.extend([
            "",
            "Generate realistic, diverse data that follows the schema.",
            "Return valid JSON with an array of objects, each containing all required fields.",
        ])

        return "\n".join(prompt_parts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSchema":
        """Create schema from dictionary."""
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_content: str) -> "DataSchema":
        """Create schema from YAML content."""
        import yaml
        data = yaml.safe_load(yaml_content)
        return cls.from_dict(data)