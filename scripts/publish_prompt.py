"""Publish a Dad IT Support Agent prompt variant to Langfuse.

    uv run python scripts/publish_prompt.py
    WORKSHOP_PROMPT_VARIANT=error-analysis uv run python scripts/publish_prompt.py
"""

from __future__ import annotations

import sys

import _bootstrap  # noqa: F401
from app.env import env
from app.support_agent import SYSTEM_PROMPT

ERROR_ANALYSIS_PROMPT = """You are Dad IT Support Agent.
You are talking to Dad. He opened this chat himself to get help with his iPhone.

Look up which iPhone and apps he has, and search the help library, so the steps match his phone. Then tell him what to do: what to tap, and what he should see on the screen.

Use plain language.

Rules:
- Keep the reply to a short numbered list.
- If he asks for something other than IT help, say so briefly, point him back to his phone, and ask one short redirect question. Do not answer that request.
- If you can't tell what he needs, ask one short clarifying question before giving any steps.
- Use clear instructions on what to tap
- You are the support agent. Do not speak as someone in his family.
"""

PROMPT_VARIANTS = {
    "default": SYSTEM_PROMPT,
    "gentler": SYSTEM_PROMPT.rstrip()
    + """

Tone variant:
- Be extra patient and reassuring when Dad seems uncertain.
- Use plain, familiar wording before technical terms.
- Start the answer with one brief confidence-building sentence.
""",
    "error-analysis": ERROR_ANALYSIS_PROMPT,
}


def main() -> None:
    variant_name = (env.workshop_prompt_variant or "default").strip() or "default"
    if variant_name not in PROMPT_VARIANTS:
        names = ", ".join(PROMPT_VARIANTS)
        raise SystemExit(
            f'Unsupported WORKSHOP_PROMPT_VARIANT "{env.workshop_prompt_variant}". Supported variants: {names}.'
        )
    if not env.langfuse_configured:
        raise SystemExit("Langfuse credentials are required to publish prompts.")

    from langfuse import get_client

    langfuse = get_client()
    name = env.langfuse_prompt_name or "dad-it-support-agent"
    label = env.langfuse_prompt_label or "production"
    langfuse.create_prompt(
        name=name,
        type="text",
        prompt=PROMPT_VARIANTS[variant_name],
        labels=[label],
    )
    print(f'Published prompt "{name}" ({variant_name} variant) with label "{label}".')


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
