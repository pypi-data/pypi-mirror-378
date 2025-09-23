"""Synthetica: Generate synthetic datasets using LLMs from schemas."""

from .generator import SyntheticDataGenerator
from .schema import DataSchema, FieldSchema, FieldType
from .uploader import HuggingFaceUploader

__version__ = "0.1.0"
__all__ = ["SyntheticDataGenerator", "DataSchema", "FieldSchema", "FieldType", "HuggingFaceUploader"]