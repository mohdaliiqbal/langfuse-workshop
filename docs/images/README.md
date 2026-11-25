# Screenshots

The diagrams and the Langfuse Cloud UI shots that have not been recaptured come from the upstream TypeScript workshop:

https://github.com/langfuse/langfuse-workshop

They were copied at upstream commit `28996a20d39a82e511a8fd043fb26252495453e3` (2026-11-23). This Python port uses the same trace name (`dad-it-support-chat-turn`), tool names (`get_support_context`, `search_help_library`), prompt name (`dad-it-support-agent`), and dataset name (`dad-it-support-workshop`).

Every image of the app itself is from this Python app. `sample_app.png` (1440x900, greeting state, same framing as the upstream file it replaces) was recaptured on 2026-11-25 with headless Chrome from `http://127.0.0.1:3333`; no doc links it, but it is kept under the upstream name. `python-ui.png` (Specs greeting, suggestion chips, iPhone panel) and `python-ui-answer.png` (the Bluetooth chip answered by the model) are headless Chrome captures of this repo's page at `http://127.0.0.1:3333`, taken during the 2026-11-25 live walkthrough with real OpenAI and Langfuse keys.

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

## Topics (reused from upstream `df8f386`)

The 15 files in `topics/` were copied unchanged from upstream commit `df8f386dd6594074ca31227b811c8472d377d595` (2026-11-25, "Add the topics lab to monitoring (#82)"). Topics is a Langfuse product feature, so the wizard and the result screens look the same whichever SDK wrote the traces, and the Python seed sends the same 200 scenarios. They were not recaptured from the Python walkthrough project: the setup wizard, the LLM connection, and the analysis run are UI mutations, and the result tiles are model-named, so a recapture would not match the lesson text word for word anyway.

- Setup: `empty-setup.png`, `setup-look-for-current.png`, `select-traces-current.png`, `review-current.png`, `edit-map.png`
- Results: `topic-map.png`, `scatter.png`, `result-treemap.png`, `result-scatter.png`, `result-issues.png`, `result-sentiment.png`
- Insights: `insight-intent.png`, `insight-sentiment.png`, `insight-issue-group.png`, `insight-issues.png`

Some are byte-identical upstream too (`result-issues.png` = `insight-issues.png`, `result-sentiment.png` = `insight-sentiment.png`). `edit-map.png`, `topic-map.png`, and `scatter.png` are not referenced by the lesson; they are kept because upstream ships them.

## Agent diagrams (Python, 2026-11-25)

`specs_illustration.png` (architecture) and `tracing/process_illustration.png` (the six steps of one turn) are diagrams, not screen captures, but they show what the app does, so they are redrawn from a real Python run instead of reusing the upstream art. The upstream versions said `gpt-4o`, `iPhone 11 · iOS 16.7.10`, and three LLM calls. The 2026-11-25 run of "How do I turn Bluetooth on?" (trace `917cb569feda6b3d5a6904b1a1300522` in `python-workshop-walkthrough`) showed `gpt-5.5-2026-04-23`, two `OpenAI-generation` calls (the first requests `get_support_context` and `search_help_library` together, the second writes the answer), `devices: ["iPhone 15"]`, and the 4-step `iphone-bluetooth` guide. Sources are `source/*.html` (styled with `app/static/colors.css`); re-render both with `uv run --with playwright python docs/images/source/render.py` and update the values if the app changes.

`AI-engineering-loop.png` and `monitoring/error-analysis-process.png` are concept diagrams with no app output in them. They stay as the upstream art.

## Langfuse UI captures that still show TypeScript-written traces

These upstream captures show Langfuse's UI, not the app, but the traces in them came from the TypeScript app: `OpenAI.chat` generation names (Python writes `OpenAI-generation`), `gpt-4.1-mini`, or JS SDK metadata (`scope.name: langfuse-sdk`, `scope.version: 5.3.0`). Recapturing them needs the Langfuse UI and evaluator-wizard mutations:

- `monitoring/select-sample-observation.png`, `monitoring/user-frustration-target-root-observation.png`
- `monitoring/user-disagreement-conversation-history-mapping.png`, `monitoring/user-disagreement-last-user-message-mapping.png`, `monitoring/user-disagreement-test-evaluator.png`, `monitoring/user-disagreement-execute-evaluator.png`
- `monitoring/out-of-scope.png`, `monitoring/out-of-scope-example.png` (not linked from a lesson)

`monitoring/user-frustration-target-root-observation.png` also shows the ALL CAPS evaluator's TypeScript, which is correct: Langfuse runs code evaluators in its TypeScript sandbox.

`scripts/refresh_screenshots.py` is the refresh path for a later pass. It exits successfully and leaves the files in place when `LANGFUSE_PROJECT_URL` and a Playwright storage state (or email and password) are missing.
