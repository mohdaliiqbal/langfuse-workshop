"""Create the hosted eval dataset from data/seed-dataset.json.

    uv run python scripts/seed_dataset.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from app.env import env

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if not env.langfuse_configured:
        raise SystemExit("Langfuse credentials are required to seed a dataset.")

    from langfuse import get_client

    items = json.loads((ROOT / "data" / "seed-dataset.json").read_text())
    langfuse = get_client()
    try:
        langfuse.create_dataset(
            name=env.dataset_name,
            description="Starter workshop dataset for the Dad IT Support Agent",
            metadata={"source": "repo-seed", "workshop": "langfuse-dad-it-support"},
        )
    except Exception as exc:
        if not any(
            token in str(exc).lower()
            for token in ("exists", "duplicate", "already", "409", "conflict")
        ):
            raise

    for item in items:
        langfuse.create_dataset_item(
            dataset_name=env.dataset_name,
            id=item["id"],
            input=item["input"],
            expected_output=item["expectedOutput"],
            metadata=item["metadata"],
        )
    langfuse.flush()
    print(f'Seeded dataset "{env.dataset_name}" with {len(items)} items.')


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
