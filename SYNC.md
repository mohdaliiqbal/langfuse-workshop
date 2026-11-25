# Upstream sync

This repository is the Python port of [langfuse/langfuse-workshop](https://github.com/langfuse/langfuse-workshop). It is not a fork that pushes back upstream. Weekly syncs diff upstream from the commit recorded in [`.sync/upstream.json`](.sync/upstream.json).

| Field | Value |
| --- | --- |
| Upstream | https://github.com/langfuse/langfuse-workshop |
| Synced commit | `df8f386dd6594074ca31227b811c8472d377d595` |
| Upstream date | 2026-11-25 |
| Sync date | 2026-11-25 |
| Subject | Add the topics lab to monitoring (#82) |

## How a weekly sync works

1. `git fetch` is not used against this repo's upstream remote. Clone or fetch `https://github.com/langfuse/langfuse-workshop.git` read-only and record `git rev-parse HEAD`.
2. Diff that tree against the SHA in `.sync/upstream.json` (`git diff <old> <new>` in the upstream clone).
3. For each changed learner lesson, script, or `src/` file, update the Python module in the mapping below. Keep the learning sequence. Use the current Langfuse Python SDK (`@observe`, `langfuse.openai.OpenAI`, `get_client()`, `propagate_attributes`, `dataset.run_experiment`) instead of translating TypeScript line by line.
4. Update checkpoint snapshots when a milestone file changed, then run `uv run python scripts/use_checkpoint.py --check`.
5. Run `uv run python scripts/run_workshop.py`. It must pass with no secrets. If secrets are available, also run it with `--live` and run the chapter scripts that those secrets unlock.
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
| `docs/learner/04-monitoring/topics.md` | `docs/learner/04-monitoring/topics.md` | Ported. Seed command is `scripts/seed_topics_traces.py`; laptop context lives in `app/support_data.py` |
| `docs/learner/04-monitoring/capturing-signals.md` | `docs/learner/04-monitoring/capturing-signals.md` | Ported. UI evaluators unchanged. ALL CAPS still runs in Langfuse's TypeScript sandbox |
| `docs/learner/05-dataset.md` | `docs/learner/05-dataset.md` | Ported |
| `docs/learner/06-experiments.md` | `docs/learner/06-experiments.md` | Ported. `dataset.run_experiment` |
| `docs/learner/07-evaluation.md` | `docs/learner/07-evaluation.md` | Ported |
| `docs/learner/08-wrap-up.md` | `docs/learner/08-wrap-up.md` | Ported |
| `docs/instructor/*.md` | `docs/instructor/*.md` | Ported, with Python commands |
| `docs/preparation_and_materials/README.md` | `docs/preparation_and_materials/README.md` | Ported |
| `docs/images/**` | `docs/images/**` | Diagrams, the monitoring shots that were not recaptured, and all 15 `topics/` shots are upstream captures (`topics/` from `df8f386`). Thirteen Langfuse UI screenshots were recaptured on 2026-11-25 from a live Python run. `python-ui.png` and `python-ui-answer.png` are local captures of the Python chat page |
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
| `scripts/seed-topics-traces.ts` | `scripts/seed_topics_traces.py`, `scripts/topics_data.py` | Ported. Same 200 scenarios in the same order (the deterministic shuffle reproduces the TypeScript float math). Sent to the Langfuse OTel endpoint with explicit timestamps instead of an OTEL template replay, because Topics needs traces spread over the last five days |
| `scripts/seed-error-analysis-annotations.ts` | `scripts/seed_error_analysis_annotations.py` | Ported against the public API |
| `data/seed-dataset.json` | `data/seed-dataset.json` | Copied unchanged (25 items) |
| `checkpoint/*` git tags, `scripts/sync-checkpoints.sh` | `checkpoints/`, `scripts/use_checkpoint.py` | Python equivalent. No force-pushed tags |
| `.github/workflows/sync-checkpoints.yml` | `.github/workflows/workshop-smoke.yml` | Different job: smoke test on PRs and weekly, not tag sync |
| `package.json` scripts | `README.md` command table, `Makefile` | Ported |

## Intentionally not ported

| Upstream | Why |
| --- | --- |
| `scripts/synthetic-trace-seed.ts`, `scripts/langfuse-trace-seed-lib.ts`, `scripts/import-trace-seed-otel.ts` | They clone and replay an OpenTelemetry export. Learners never open them. The Python seeds write the same scenarios themselves. The `anchorMs` option added in `df8f386` is covered by `topics_data.timestamps()`. |
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

## Python-only adaptations to preserve on sync

Weekly syncs must keep the pieces below. They are deliberate differences from upstream, taken from attendee feedback in [PR #9](https://github.com/mohdaliiqbal/langfuse-workshop/pull/9) (`f1fba023`, Annabell Schaefer).

### Tracing environment

Upstream teaches user and session IDs as an appendix and does not mention `LANGFUSE_TRACING_ENVIRONMENT`. The feedback asked for a way to keep laptop traces out of a deployed app's stream. This port keeps the upstream chapter order and the three tracing steps. It adds:

- The "Tracing environment" appendix in [docs/learner/02-tracing.md](docs/learner/02-tracing.md)
- The instructor note in [docs/instructor/02-tracing.md](docs/instructor/02-tracing.md)
- A commented `LANGFUSE_TRACING_ENVIRONMENT` line in `.env.example`
- The optional row in the root README environment table

The variable stays unset in the workshop defaults. Traces still use Langfuse's default environment, and chapter 4.3 still tells learners to filter the sample observation to `production` when that panel shows another environment. When porting a new upstream `02-tracing.md`, keep this appendix.

### Root input shape

The Python SDK's `@observe` records a function's input as `{"args": [...], "kwargs": {}}`, and the pydantic request dumps in snake_case. The TypeScript `observe(...)` records the single argument, so upstream's root input is the `{ sessionId, userId, messages }` request body. The 4.3 evaluator mappings (**Input → messages**) and the error-analysis seed depend on that shape.

This port adds one `update_current_span(input=request.model_dump(mode="json", by_alias=True, exclude_none=True))` line at the top of `run_support_conversation` in `app/support_agent.py`, `checkpoints/reference/`, and `checkpoints/03-prompt-management/`, and teaches it in Step 2 of [docs/learner/02-tracing.md](docs/learner/02-tracing.md). `scripts/run_workshop.py --live` fails if the root input loses that shape. Keep the line when porting a new upstream `support-agent.ts` or `02-tracing.md`.

### Feedback from that PR that stays dropped

The same PR reworked the old DataStream labs. Those files are gone, and the ideas that would replace an upstream chapter stay dropped. Do not revive them on a later sync.

| Feedback | Where the current workshop stands |
| --- | --- |
| Lab 02 collapses tracing into one pass and names the trace on the first observation | Chapter 02 still builds the trace in three steps: OpenAI generations, then the `dad-it-support-chat-turn` agent root, then tool spans. That end state already has the drop-in client, the nested observations, and the trace name. |
| Lab 03 becomes its own Sessions & Environments chapter, and drops `tags` and `trace_name` from `propagate_attributes` | Chapter 03 stays prompt management. User, session, trace name, and tags are already set in the tracing appendix and in `app/support_agent.py`. |
| Lab 05 aims both evaluators at out-of-scope detection, adds an SDK `in-scope` judge, and adds a task for thumbs-versus-judge disagreement | Chapter 4.3 stays on Detect User Disagreement and the ALL CAPS evaluator. The chat UI has no thumbs control. Out-of-scope replies are an error-analysis failure and a dataset case, scored offline by `behavior_match`. |
| Lab 07 removes the script judge and scores dataset runs only with a platform LLM-as-a-judge | Chapter 06 still scores `behavior_match` and `correctness` inside `dataset.run_experiment`. The lesson keeps platform evaluators out of this chapter. Chapter 07 already reads the low-scoring items, publishes the error-analysis prompt, and compares the two runs. |
| Lab folder rename, solution files, and the old root workshop-flow tables | `labs/` is not part of this tree. No lesson links to it. |
