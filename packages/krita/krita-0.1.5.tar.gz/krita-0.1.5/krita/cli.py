"""Command-line interface for Synthetica."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track

from .generator import SyntheticDataGenerator
from .schema import DataSchema
from .uploader import HuggingFaceUploader

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    """Synthetica: Generate synthetic datasets using LLMs."""
    setup_logging(verbose)


@main.command()
@click.argument("schema_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "jsonl"]), default="json", help="Output format")
@click.option("--provider", "-p", type=click.Choice(["openai", "anthropic"]), default="openai", help="LLM provider")
@click.option("--model", "-m", help="LLM model to use")
@click.option("--api-key", "-k", help="API key for LLM provider")
@click.option("--batch-size", "-b", type=int, default=10, help="Batch size for generation")
def generate(
    schema_file: str,
    output: Optional[str],
    format: str,
    provider: str,
    model: Optional[str],
    api_key: Optional[str],
    batch_size: int,
) -> None:
    """Generate synthetic data from a schema file."""
    try:
        with open(schema_file, "r") as f:
            if schema_file.endswith(".yaml") or schema_file.endswith(".yml"):
                schema_data = yaml.safe_load(f)
            else:
                schema_data = json.load(f)

        schema = DataSchema.from_dict(schema_data)
        console.print(f"[green]Loaded schema:[/green] {schema.name}")
        console.print(f"[blue]Fields:[/blue] {len(schema.fields)}")
        console.print(f"[blue]Samples to generate:[/blue] {schema.num_samples}")

    except Exception as e:
        console.print(f"[red]Error loading schema:[/red] {e}")
        sys.exit(1)

    try:
        generator = SyntheticDataGenerator(
            llm_provider=provider,
            llm_model=model,
            api_key=api_key,
            batch_size=batch_size,
        )

        console.print(f"[yellow]Generating data with {provider}...[/yellow]")
        data = generator.generate(schema)

        console.print(f"[green]Generated {len(data)} samples[/green]")

        if output:
            if format == "json":
                generator.save_to_json(data, output)
            else:
                generator.save_to_jsonl(data, output)
            console.print(f"[green]Saved to:[/green] {output}")
        else:
            console.print(json.dumps(data[:3], indent=2))
            if len(data) > 3:
                console.print(f"... and {len(data) - 3} more samples")

    except Exception as e:
        console.print(f"[red]Generation failed:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.argument("repo_id")
@click.option("--token", "-t", help="Hugging Face token")
@click.option("--description", "-d", help="Dataset description")
@click.option("--private", is_flag=True, help="Make dataset private")
@click.option("--tags", help="Comma-separated tags")
def upload(
    data_file: str,
    repo_id: str,
    token: Optional[str],
    description: Optional[str],
    private: bool,
    tags: Optional[str],
) -> None:
    """Upload synthetic data to Hugging Face Hub."""
    try:
        with open(data_file, "r") as f:
            if data_file.endswith(".jsonl"):
                data = [json.loads(line) for line in f]
            else:
                data = json.load(f)

        console.print(f"[blue]Loaded {len(data)} samples[/blue]")

    except Exception as e:
        console.print(f"[red]Error loading data:[/red] {e}")
        sys.exit(1)

    try:
        uploader = HuggingFaceUploader(token=token)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        console.print(f"[yellow]Uploading to {repo_id}...[/yellow]")
        url = uploader.upload_dataset(
            data=data,
            repo_id=repo_id,
            description=description,
            tags=tag_list,
            private=private,
        )

        console.print(f"[green]Dataset uploaded:[/green] {url}")

    except Exception as e:
        console.print(f"[red]Upload failed:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("output_file", type=click.Path())
def init_schema(output_file: str) -> None:
    """Create a sample schema file."""
    sample_schema = {
        "name": "sample_dataset",
        "description": "A sample dataset for demonstration",
        "num_samples": 100,
        "context": "Generate realistic data for testing purposes",
        "fields": [
            {
                "name": "id",
                "type": "uuid",
                "description": "Unique identifier",
                "required": True,
            },
            {
                "name": "name",
                "type": "name",
                "description": "Full name of a person",
                "required": True,
                "examples": ["John Doe", "Jane Smith", "Alex Johnson"],
            },
            {
                "name": "email",
                "type": "email",
                "description": "Email address",
                "required": True,
            },
            {
                "name": "age",
                "type": "number",
                "description": "Age in years",
                "required": True,
                "constraints": {"min": 18, "max": 80},
            },
            {
                "name": "description",
                "type": "description",
                "description": "Brief personal description",
                "required": False,
            },
        ],
    }

    try:
        if output_file.endswith(".yaml") or output_file.endswith(".yml"):
            with open(output_file, "w") as f:
                yaml.dump(sample_schema, f, default_flow_style=False, indent=2)
        else:
            with open(output_file, "w") as f:
                json.dump(sample_schema, f, indent=2)

        console.print(f"[green]Sample schema created:[/green] {output_file}")
        console.print("[blue]Edit the schema and run:[/blue] synthetica generate schema.yaml")

    except Exception as e:
        console.print(f"[red]Error creating schema:[/red] {e}")
        sys.exit(1)


@main.command()
def list_providers() -> None:
    """List available LLM providers and models."""
    providers = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
    }

    console.print("[bold]Available LLM Providers:[/bold]")
    for provider, models in providers.items():
        console.print(f"\n[green]{provider}:[/green]")
        for model in models:
            console.print(f"  • {model}")

    console.print("\n[blue]Usage:[/blue] synthetica generate --provider openai --model gpt-4 schema.yaml")


if __name__ == "__main__":
    main()