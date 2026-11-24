# Contributing

This is the Python port of the Langfuse workshop. Changes should stay aligned with [langfuse/langfuse-workshop](https://github.com/langfuse/langfuse-workshop) without pushing to that repository.

## Weekly sync

The procedure and the module map live in [SYNC.md](SYNC.md). The commit to diff from is [`.sync/upstream.json`](.sync/upstream.json).

In short: fetch upstream read-only, port what changed into the Python files in the mapping table, update the SHA, run the smoke test, and open one pull request against `main`.

## Checks

```bash
uv sync
uv run python scripts/run_workshop.py
uv run python scripts/use_checkpoint.py --check
```

`scripts/run_workshop.py` is also `make smoke`. It must pass with no API keys. When `OPENAI_API_KEY` or `LANGFUSE_*` are missing it skips the live steps and exits 0. When the Langfuse keys are present it calls the projects API and still does not spend an OpenAI request.

GitHub Actions runs the same command on pull requests and every Monday. Missing repository secrets are empty and the live steps skip. Do not make that workflow fail just because secrets are unset.

## Checkpoints

Learner-facing code changes that belong to a chapter also belong in `checkpoints/`. After editing `app/server.py`, `app/support_agent.py`, or `app/tools.py` on the finished app, copy those files to `checkpoints/reference/`. If the untraced or pre-prompt snapshots should change too, edit `checkpoints/00-setup/` and `checkpoints/03-prompt-management/` and keep the `SYSTEM_PROMPT` block identical. `scripts/use_checkpoint.py --check` enforces that.

## Screenshots

`docs/images/` is reused from upstream unless a Langfuse UI change makes a figure wrong. `scripts/refresh_screenshots.py` recaptures a subset when `LANGFUSE_PROJECT_URL` and a Playwright login are available. It exits 0 and leaves the images in place when they are not.

## Secrets

Do not commit `.env` or real API keys. `.env.example` lists every variable the lessons and scripts read.
