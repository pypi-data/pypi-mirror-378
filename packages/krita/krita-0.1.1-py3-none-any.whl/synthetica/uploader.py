"""Upload synthetic datasets to Hugging Face Hub."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HuggingFaceUploader:
    """Upload datasets to Hugging Face Hub."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the uploader.

        Args:
            token: Hugging Face token (optional if set via env)
        """
        try:
            from datasets import Dataset
            from huggingface_hub import HfApi
        except ImportError:
            raise ImportError("datasets and huggingface-hub packages are required")

        self.token = token
        self.api = HfApi(token=token)

    def upload_dataset(
        self,
        data: List[Dict[str, Any]],
        repo_id: str,
        dataset_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        private: bool = False,
        commit_message: Optional[str] = None,
    ) -> str:
        """
        Upload dataset to Hugging Face Hub.

        Args:
            data: Generated dataset
            repo_id: Repository ID (username/dataset-name)
            dataset_name: Name of the dataset
            description: Dataset description
            tags: Dataset tags
            private: Whether the dataset should be private
            commit_message: Commit message for the upload

        Returns:
            URL of the uploaded dataset
        """
        from datasets import Dataset

        if not data:
            raise ValueError("Cannot upload empty dataset")

        dataset = Dataset.from_list(data)

        try:
            self.api.create_repo(
                repo_id=repo_id,
                repo_type="dataset",
                private=private,
                exist_ok=True,
            )
            logger.info(f"Repository {repo_id} created/verified")
        except Exception as e:
            logger.warning(f"Repository creation failed (may already exist): {e}")

        try:
            dataset.push_to_hub(
                repo_id=repo_id,
                token=self.token,
                commit_message=commit_message or f"Upload synthetic dataset with {len(data)} samples",
            )
            logger.info(f"Dataset uploaded successfully to {repo_id}")
        except Exception as e:
            logger.error(f"Failed to upload dataset: {e}")
            raise

        self._upload_metadata(
            repo_id=repo_id,
            dataset_name=dataset_name or repo_id.split("/")[-1],
            description=description,
            tags=tags,
            num_samples=len(data),
        )

        return f"https://huggingface.co/datasets/{repo_id}"

    def _upload_metadata(
        self,
        repo_id: str,
        dataset_name: str,
        description: Optional[str],
        tags: Optional[List[str]],
        num_samples: int,
    ) -> None:
        """Upload dataset metadata (README.md)."""
        readme_content = self._generate_readme(
            dataset_name=dataset_name,
            description=description,
            tags=tags or [],
            num_samples=num_samples,
        )

        try:
            self.api.upload_file(
                path_or_fileobj=readme_content.encode("utf-8"),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message="Add dataset metadata",
                token=self.token,
            )
            logger.info("Dataset metadata uploaded")
        except Exception as e:
            logger.warning(f"Failed to upload metadata: {e}")

    def _generate_readme(
        self,
        dataset_name: str,
        description: Optional[str],
        tags: List[str],
        num_samples: int,
    ) -> str:
        """Generate README content for the dataset."""
        tag_list = tags + ["synthetic", "generated"] if tags else ["synthetic", "generated"]
        tags_yaml = "\n".join(f"- {tag}" for tag in tag_list)

        readme = f"""---
dataset_info:
  features:
  - name: data
    dtype: string
  config_name: default
  data_files:
  - split: train
    path: data/train-*
  default: true
task_categories:
- text-generation
language:
- en
tags:
{tags_yaml}
size_categories:
- 1K<n<10K
---

# {dataset_name}

{description or 'Synthetic dataset generated with Synthetica.'}

## Dataset Details

- **Number of samples**: {num_samples:,}
- **Generated with**: [Synthetica](https://github.com/yourusername/synthetica)
- **License**: MIT

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{dataset_name}")
```

## Citation

If you use this dataset, please cite:

```bibtex
@misc{{{dataset_name.replace('-', '_')},
  title={{{dataset_name}}},
  author={{Generated with Synthetica}},
  year={{2024}},
  url={{https://huggingface.co/datasets/{dataset_name}}}
}}
```
"""
        return readme

    def save_dataset_locally(
        self,
        data: List[Dict[str, Any]],
        output_dir: str,
        format: str = "json",
    ) -> str:
        """
        Save dataset locally in various formats.

        Args:
            data: Generated dataset
            output_dir: Output directory
            format: Output format ('json', 'jsonl', 'csv', 'parquet')

        Returns:
            Path to saved file
        """
        from datasets import Dataset
        import os

        os.makedirs(output_dir, exist_ok=True)
        dataset = Dataset.from_list(data)

        if format == "json":
            filepath = os.path.join(output_dir, "dataset.json")
            dataset.to_json(filepath)
        elif format == "jsonl":
            filepath = os.path.join(output_dir, "dataset.jsonl")
            dataset.to_json(filepath, lines=True)
        elif format == "csv":
            filepath = os.path.join(output_dir, "dataset.csv")
            dataset.to_csv(filepath)
        elif format == "parquet":
            filepath = os.path.join(output_dir, "dataset.parquet")
            dataset.to_parquet(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Dataset saved locally to {filepath}")
        return filepath