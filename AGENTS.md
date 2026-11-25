# Agent notes for this repo

This file is for coding agents and maintainers changing the Python Langfuse workshop. Learners follow `docs/learner/`. Facilitators follow `docs/instructor/`.

The app is a Python port of [langfuse/langfuse-workshop](https://github.com/langfuse/langfuse-workshop). Do not fork, push, or open anything on that upstream repository. Alignment is recorded in `SYNC.md` and `.sync/upstream.json`.

## How to handle changes

`main` is the finished reference app plus the current docs. Learners do not start from `main` as a blank slate. They load a chapter with:

```bash
uv run python scripts/use_checkpoint.py 02-tracing
```

| Chapter | Snapshot directory | Milestone files |
| --- | --- | --- |
| `00-setup`, `01-base-app`, `02-tracing` | `checkpoints/00-setup` | Untraced `server.py`, `support_agent.py`, `tools.py` |
| `03-prompt-management` | `checkpoints/03-prompt-management` | Traced agent and tools, local `SYSTEM_PROMPT` only |
| `04-monitoring` through `08-wrap-up` | `checkpoints/reference` | Same bytes as `app/server.py`, `app/support_agent.py`, `app/tools.py` |

`checkpoints/reference/` must match those three files in `app/`. `uv run python scripts/use_checkpoint.py --check` fails when it does not. The `SYSTEM_PROMPT` region marked `checkpoint-sync:begin system-prompt` must be identical in every snapshot.

Shared behavior that every chapter relies on:

- The OpenAI SDK is already in place before tracing, so chapter 02 is only observability.
- Prompt fetch falls back to `SYSTEM_PROMPT` when Langfuse has no prompt.
- Monitoring, datasets, and experiments assume the root observation is `dad-it-support-chat-turn` and its input contains a `messages` array.
- Dataset items carry `idealAnswer` and `expectedBehavior`. `scripts/run_dataset.py` scores both with callbacks.
- `.env` is the source of truth. `app/env.py` loads it with override.

## Documentation

- Root `README.md` is the map: scope, modules, commands, environment variables.
- Learner lessons open with why the practice matters, then the goal, then the checkpoint command, then the steps.
- Do not recreate a second overview under `docs/learner/README.md`.
- Instructor notes stay in `docs/instructor/`. Maintainer-only sync rules stay here and in `SYNC.md`.

## Python equivalents to keep stable

| TypeScript workshop | This repo |
| --- | --- |
| `npm run dev` on port 3333 | `uv run python -m app.server` on port 3333 |
| `observeOpenAI(new OpenAI())` | `from langfuse.openai import OpenAI` |
| `observe(fn, { asType })` | `@observe(name=..., as_type=...)` |
| `LangfuseSpanProcessor` / `NodeSDK` | `get_client()`, `flush()`, `shutdown()` |
| `observeOpenAI(client, { langfusePrompt })` | `chat.completions.create(..., langfuse_prompt=prompt)` |
| `dataset.runExperiment` | `dataset.run_experiment` |
| `npm run prompt:publish` | `uv run python scripts/publish_prompt.py` |
| `npm run dataset:seed` / `dataset:run` | `scripts/seed_dataset.py` / `scripts/run_dataset.py` |
| `npm run langfuse:seed:error-analysis` | `scripts/seed_error_analysis.py` |
| `npm run langfuse:seed:topics` | `scripts/seed_topics_traces.py` (data in `scripts/topics_data.py`) |

## Before you finish

Run `uv run python scripts/run_workshop.py`. It must pass without secrets. Do not start the workshop server as a stand-in for that script unless you are checking the UI yourself, and do not put API keys into the repository.
