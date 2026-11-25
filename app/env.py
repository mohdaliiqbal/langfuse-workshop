"""Repository environment.

The workshop treats this repo's `.env` as the source of truth. Values already
exported in the shell do not override that file, matching the TypeScript
workshop's dotenv `override: true` behavior.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)


def _get(name: str, default: str = "") -> str:
    # An empty value counts as unset. GitHub Actions passes unset secrets as
    # empty strings, which would otherwise blank out the prompt and dataset names.
    return os.environ.get(name) or default


class Env:
    port: int = int(_get("PORT", "3333"))
    openai_api_key: str = _get("OPENAI_API_KEY")
    openai_model: str = _get("OPENAI_MODEL", "gpt-5.5-2026-04-23")
    langfuse_public_key: str = _get("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = _get("LANGFUSE_SECRET_KEY")
    langfuse_base_url: str = _get("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
    langfuse_prompt_name: str = _get("LANGFUSE_PROMPT_NAME", "dad-it-support-agent")
    langfuse_prompt_label: str = _get("LANGFUSE_PROMPT_LABEL", "production")
    workshop_prompt_variant: str = _get("WORKSHOP_PROMPT_VARIANT", "default")
    dataset_name: str = _get("DATASET_NAME", "dad-it-support-workshop")

    @property
    def langfuse_configured(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


env = Env()
