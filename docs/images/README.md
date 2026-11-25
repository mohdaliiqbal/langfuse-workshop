# Screenshots

The diagrams and the Langfuse Cloud UI shots that have not been recaptured come from the upstream TypeScript workshop:

https://github.com/langfuse/langfuse-workshop

They were copied at upstream commit `28996a20d39a82e511a8fd043fb26252495453e3` (2026-11-23). This Python port uses the same trace name (`dad-it-support-chat-turn`), tool names (`get_support_context`, `search_help_library`), prompt name (`dad-it-support-agent`), and dataset name (`dad-it-support-workshop`).

`sample_app.png` and `specs_illustration.png` show the upstream client. `python-ui.png` (Specs greeting, suggestion chips, iPhone panel) and `python-ui-answer.png` (the Bluetooth chip answered by the model) are headless Chrome captures of this repo's page at `http://127.0.0.1:3333`, taken during the 2026-11-25 live walkthrough with real OpenAI and Langfuse keys.

## Recaptured on 2026-11-25

These 13 files were recaptured on 2026-11-25 from a live Python run in the `python-workshop-walkthrough` project. The traces were written by the Python SDK, so generations are named `OpenAI-generation`.

- `tracing/02-tracing-step-1.png`
- `tracing/02-tracing-step-2.png`
- `tracing/02-tracing-step-3.png`
- `prompt-management/03-prompt-management-published-prompt.png`
- `prompt-management/03-prompt-management-prompt-badge.png`
- `datasets/05-dataset-items.png`
- `evaluate-a-change/side-by-side-runs.png`
- `monitoring/home-dashboard.png`
- `monitoring/add-to-annotation-queue.png`
- `monitoring/filter-traces-by-evaluator-score.png`
- `monitoring/user-disagreement-config.png`
- `monitoring/user-disagrees-example.png`
- `monitoring/all-caps-example.png`

`tracing/02-tracing-step-2.png` and `tracing/02-tracing-step-3.png` are the same finished trace: the `dad-it-support-chat-turn` root, two `OpenAI-generation` rows, `get_support_context`, and `search_help_library`. `monitoring/user-disagrees-example.png` and `monitoring/all-caps-example.png` are the same trace, showing both the disagreement score and the all-caps score.

## Still the upstream captures

The remaining monitoring screenshots are still the upstream captures: the evaluator wizard steps, Halo, failure categories, the frustration dashboard, and out-of-scope.

Diagrams that are not UI captures (`AI-engineering-loop.png`, `specs_illustration.png`, `tracing/process_illustration.png`, `monitoring/error-analysis-process.png`) do not need a Langfuse session.

`scripts/refresh_screenshots.py` is the refresh path for a later pass. It exits successfully and leaves the files in place when `LANGFUSE_PROJECT_URL` and a Playwright storage state (or email and password) are missing.
