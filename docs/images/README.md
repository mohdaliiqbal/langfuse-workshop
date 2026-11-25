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

## Recaptured on 2026-11-25, second pass

These 6 monitoring files and 11 topics files were recaptured on 2026-11-25 in project `python-workshop-walkthrough`. Each is 1280×692, browser content only. The monitoring shots are the Python app's traces. The topics shots are the 200 traces from `scripts/seed_topics_traces.py`.

Monitoring:

- `monitoring/select-sample-observation.png`
- `monitoring/user-disagreement-conversation-history-mapping.png`
- `monitoring/user-disagreement-last-user-message-mapping.png`
- `monitoring/user-disagreement-test-evaluator.png` (the one-turn sample scores false: "There is no prior assistant response...")
- `monitoring/user-disagreement-execute-evaluator.png`
- `monitoring/user-frustration-target-root-observation.png` (ALL CAPS opens as a Code evaluator, with no variable mapping)

Topics:

- Setup: `topics/empty-setup.png`, `topics/setup-look-for-current.png`, `topics/select-traces-current.png`, `topics/review-current.png`, `topics/edit-map.png`
- Intent and Outcome: `topics/topic-map.png`, `topics/scatter.png`, `topics/result-treemap.png`, `topics/result-scatter.png`, `topics/insight-intent.png`, `topics/insight-issue-group.png`

`insight-issue-group.png` is the Outcome facet, group **Repeated Instructions Without Resolution** (30 traces), not an Issues tile.

## Topics that stay upstream

Four topics files stay as the upstream captures from `df8f386dd6594074ca31227b811c8472d377d595`. In the Python run, Sentiment and Issues still showed **Not enough analyzed traces yet** after more than 15 minutes, so those screens were not a populated map. The handoff also contained empty captures of these four, plus an Outcome scatter saved under `insight-issues.png`. Those files were not used.

- `topics/result-issues.png`
- `topics/result-sentiment.png`
- `topics/insight-sentiment.png`
- `topics/insight-issues.png`

`result-issues.png` and `insight-issues.png` are the same upstream bytes. `result-sentiment.png` and `insight-sentiment.png` are the same upstream bytes.

## Still the upstream captures

The monitoring screenshots that were not in either 2026-11-25 pass stay upstream: `default-evaluation-model.png`, Halo (`halo-cluster-annotations.png`, `halo-conversation-signals-prompt.png`), `failure-categories.png`, `user-frustration-dashboard.png`, and the unlinked `out-of-scope.png` / `out-of-scope-example.png`.

## Agent diagrams (Python, 2026-11-25)

`specs_illustration.png` (architecture) and `tracing/process_illustration.png` (the six steps of one turn) are diagrams, not screen captures, but they show what the app does, so they are redrawn from a real Python run instead of reusing the upstream art. The upstream versions said `gpt-4o`, `iPhone 11 · iOS 16.7.10`, and three LLM calls. The 2026-11-25 run of "How do I turn Bluetooth on?" (trace `917cb569feda6b3d5a6904b1a1300522` in `python-workshop-walkthrough`) showed `gpt-5.5-2026-04-23`, two `OpenAI-generation` calls (the first requests `get_support_context` and `search_help_library` together, the second writes the answer), `devices: ["iPhone 15"]`, and the 4-step `iphone-bluetooth` guide. Sources are `source/*.html` (styled with `app/static/colors.css`); re-render both with `uv run --with playwright python docs/images/source/render.py` and update the values if the app changes.

`AI-engineering-loop.png` and `monitoring/error-analysis-process.png` are concept diagrams with no app output in them. They stay as the upstream art.

## Langfuse UI captures that still show TypeScript-written traces

`monitoring/out-of-scope.png` and `monitoring/out-of-scope-example.png` are still the upstream captures. They are not linked from a lesson. The four topics files listed above also show the upstream project's traces, not this Python run.

`scripts/refresh_screenshots.py` is the refresh path for a later pass. It exits successfully and leaves the files in place when `LANGFUSE_PROJECT_URL` and a Playwright storage state (or email and password) are missing.
