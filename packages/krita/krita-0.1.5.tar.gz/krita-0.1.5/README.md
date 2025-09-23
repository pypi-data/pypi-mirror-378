# Krita

Generate synthetic datasets using LLMs from schemas. Upload to Hugging Face.

## Quick Start

```bash
pip install krita
krita generate schema.yaml --output dataset.json
```

```python
from krita import SyntheticDataGenerator, DataSchema, FieldType

schema = DataSchema(
    name="reviews",
    num_samples=100,
    fields=[
        {"name": "product", "type": FieldType.TITLE, "required": True},
        {"name": "rating", "type": FieldType.NUMBER, "constraints": {"min": 1, "max": 5}},
        {"name": "review", "type": FieldType.REVIEW, "required": True}
    ]
)

generator = SyntheticDataGenerator(llm_provider="openai")
data = generator.generate(schema)
```

## Features

- **Schema-driven**: Define data structure with types, constraints, examples
- **Multiple LLMs**: OpenAI, Anthropic, custom OpenAI-compatible endpoints
- **Custom endpoints**: Ollama, vLLM, enterprise deployments
- **Validation**: Ensures data matches schema
- **Hugging Face**: Direct upload with metadata
- **Multiple formats**: JSON, CSV, Parquet output

## Custom Endpoints

Use any OpenAI-compatible API:

```python
generator = SyntheticDataGenerator(
    llm_provider="openai",
    base_url="https://your-api.com/v1",  # Your endpoint
    llm_model="your-model",
    api_key="your-key"
)
```

**Examples:**
- Ollama: `base_url="http://localhost:11434/v1"`
- vLLM: `base_url="https://your-vllm.com/v1"`
- Enterprise: `base_url="https://internal-ai.company.com/v1"`

## Schema Format

```yaml
name: "user_profiles"
description: "User profile data"
num_samples: 500
fields:
  - name: "name"
    type: "name"
    required: true
  - name: "email"
    type: "email"
    required: true
  - name: "age"
    type: "number"
    constraints: {min: 18, max: 80}
```

## Field Types

**Built-in**: `text`, `name`, `email`, `phone`, `address`, `date`, `number`, `boolean`, `uuid`, `category`, `url`, `json`, `title`, `description`, `review`

**Custom**: Define domain-specific types:

```yaml
fields:
  - name: "diagnosis"
    type: "icd_code"  # Custom type
    custom_type_definition: "ICD-10 diagnosis with code and description"
    examples: ["E11.9 - Type 2 diabetes mellitus"]
```

## CLI

```bash
krita init-schema schema.yaml        # Create template
krita generate schema.yaml           # Generate data
krita upload data.json user/dataset  # Upload to HF
```

## Configuration

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export HF_TOKEN="your-token"
```

## License

MIT