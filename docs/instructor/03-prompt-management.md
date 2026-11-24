---
title: "Workshop: Instructor Notes for Prompt Management"
description: "Facilitator notes for publishing a prompt, fetching it, and showing the Prompt badge on a generation."
---

# 03 Prompt Management

Learner guide: [03 Prompt Management](../learner/03-prompt-management.md)

## Instructor notes

- The teaching point is the trace-to-prompt loop. Every generation should link to the prompt version that produced it.
- Prefer the UI path first. `uv run python scripts/publish_prompt.py` is the same outcome.
- Keep `SYSTEM_PROMPT` as the fallback.
- In Python SDK 4 the prompt link is `langfuse_prompt=` on `chat.completions.create`, not a field of `propagate_attributes`. That call argument is the equivalent of `observeOpenAI(client, { langfusePrompt })`.

## Demo rhythm

1. Create `dad-it-support-agent` as a text prompt and label it `production`.
2. Fetch it with `get_client().get_prompt(name, label=...)`.
3. Use the fetched text as the system message and pass the prompt client into `propagate_attributes`.
