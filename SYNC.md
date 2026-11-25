# Upstream sync

This repository is the Python port of [langfuse/langfuse-workshop](https://github.com/langfuse/langfuse-workshop). It is not a fork that pushes back upstream. Weekly syncs diff upstream from the commit recorded in [`.sync/upstream.json`](.sync/upstream.json).

| Field | Value |
| --- | --- |
| Upstream | https://github.com/langfuse/langfuse-workshop |
| Synced commit | `28996a20d39a82e511a8fd043fb26252495453e3` |
| Upstream date | 2026-11-23 |
| Sync date | 2026-11-24 |
| Subject | Revert "Nest tool observations under the generation that requested them" (#84) |

## How a weekly sync works

1. `git fetch` is not used against this repo's upstream remote. Clone or fetch `https://github.com/langfuse/langfuse-workshop.git` read-only and record `git rev-parse HEAD`.
2. Diff that tree against the SHA in `.sync/upstream.json` (`git diff <old> <new>` in the upstream clone).
3. For each changed learner lesson, script, or `src/` file, update the Python module in the mapping below. Keep the learning sequence. Use the current Langfuse Python SDK (`@observe`, `langfuse.openai.OpenAI`, `get_client()`, `propagate_attributes`, `dataset.run_experiment`) instead of translating TypeScript line by line.
4. Update checkpoint snapshots when a milestone file changed, then run `uv run python scripts/use_checkpoint.py --check`.
5. Run `uv run python scripts/run_workshop.py`. It must pass with no secrets. If secrets are available, also run the chapter scripts that those secrets unlock.
6. Refresh screenshots with `uv run python scripts/refresh_screenshots.py` when a Langfuse UI session is available. Otherwise leave the reused images and say so in [docs/images/README.md](docs/images/README.md).
7. Write the new SHA, date, and any mapping changes into this file and `.sync/upstream.json`. Open one pull request against `main`.

Do not open issues, pull requests, or pushes on `langfuse/langfuse-workshop`.

## Module map

| Upstream | Python | Status |
| --- | --- | --- |
| `docs/learner/00-setup.md` | `docs/learner/00-setup.md` | Ported. uv, port 3333, `use_checkpoint.py` |
| `docs/learner/01-base-app.md` | `docs/learner/01-base-app.md` | Ported. FastAPI and static UI instead of Express and React |
| `docs/learner/02-tracing.md` | `docs/learner/02-tracing.md` | Ported. Python SDK equivalents of `observeOpenAI`, `observe`, and the span processor |
| `docs/learner/03-prompt-management.md` | `docs/learner/03-prompt-management.md` | Ported. Prompt link via `langfuse_prompt=` on the OpenAI call (Python SDK 4) |
| `docs/learner/04-monitoring.md` | `docs/learner/04-monitoring.md` | Ported |
| `docs/learner/04-monitoring/error-analysis.md` | `docs/learner/04-monitoring/error-analysis.md` | Ported. Seed command is `scripts/seed_error_analysis.py` |
| `docs/learner/04-monitoring/capturing-signals.md` | `docs/learner/04-monitoring/capturing-signals.md` | Ported. UI evaluators unchanged. ALL CAPS still runs in Langfuse's TypeScript sandbox |
| `docs/learner/05-dataset.md` | `docs/learner/05-dataset.md` | Ported |
| `docs/learner/06-experiments.md` | `docs/learner/06-experiments.md` | Ported. `dataset.run_experiment` |
| `docs/learner/07-evaluation.md` | `docs/learner/07-evaluation.md` | Ported |
| `docs/learner/08-wrap-up.md` | `docs/learner/08-wrap-up.md` | Ported |
| `docs/instructor/*.md` | `docs/instructor/*.md` | Ported, with Python commands |
| `docs/preparation_and_materials/README.md` | `docs/preparation_and_materials/README.md` | Ported |
| `docs/images/**` | `docs/images/**` | Langfuse UI shots reused from this upstream SHA. `python-ui.png` is a new local capture of the Python chat page |
| `src/server/support-agent.ts` | `app/support_agent.py` | Ported |
| `src/server/tools.ts` | `app/tools.py` | Ported |
| `src/server/support-data.ts` | `app/support_data.py` | Ported |
| `src/server/index.ts` | `app/server.py` | Ported. One process on port 3333 |
| `src/server/env.ts`, `src/server/load-env.ts` | `app/env.py` | Ported, including dotenv override |
| `src/shared/types.ts` | `app/models.py` | Ported. JSON stays camelCase |
| `src/client/**` | `app/static/**` | Ported as HTML, CSS, and vanilla JS. Styles reused from upstream |
| `scripts/publish-prompt.ts` | `scripts/publish_prompt.py` | Ported, including `default`, `gentler`, and `error-analysis` |
| `scripts/seed-dataset.ts` | `scripts/seed_dataset.py` | Ported |
| `scripts/run-dataset.ts` | `scripts/run_dataset.py` | Ported. Decisions API via HTTP. Same judge prompt |
| `scripts/seed-error-analysis-traces.ts` | `scripts/seed_error_analysis.py`, `scripts/error_analysis_data.py` | Ported. Same 20 scenarios. Traces are written with the Python SDK instead of an OTEL replay |
| `scripts/seed-error-analysis-annotations.ts` | `scripts/seed_error_analysis_annotations.py` | Ported against the public API |
| `data/seed-dataset.json` | `data/seed-dataset.json` | Copied unchanged (25 items) |
| `checkpoint/*` git tags, `scripts/sync-checkpoints.sh` | `checkpoints/`, `scripts/use_checkpoint.py` | Python equivalent. No force-pushed tags |
| `.github/workflows/sync-checkpoints.yml` | `.github/workflows/workshop-smoke.yml` | Different job: smoke test on PRs and weekly, not tag sync |
| `package.json` scripts | `README.md` command table, `Makefile` | Ported |

## Intentionally not ported

| Upstream | Why |
| --- | --- |
| `scripts/synthetic-trace-seed.ts`, `scripts/langfuse-trace-seed-lib.ts`, `scripts/import-trace-seed-otel.ts` | They clone and replay an OpenTelemetry export. Learners never open them. The Python seed writes the same scenarios with the SDK. |
| `data/seed-traffic-followups-traces.json` | Template corpus for that OTEL replay only. About 50k lines, not used by a lesson. |
| `docs/storyline/WORKSHOP_STORYLINE.md` | Internal scratch with an empty failure-mode list and typos. The learner lessons replaced it. |
| `npm run dev` hot reload | The Python server is one process. Lessons say to restart it. |
| Previous DataStream / Gradio labs (`labs/00`–`labs/07`, `app/web.py`) | Those taught the pre-November 2026 workshop. They conflict with this loop, so they were removed rather than kept beside it. |

## Python-only pieces kept

- `uv`, `setup.sh`, and Python 3.14
- `scripts/run_workshop.py` and `make smoke`
- `scripts/refresh_screenshots.py`
- `.github/workflows/workshop-smoke.yml`
- Checkpoint snapshots instead of git tags, so the sync does not force-push this repo's tags
