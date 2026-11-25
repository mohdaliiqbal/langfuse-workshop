# Screenshots

These images are the Langfuse Cloud UI and the workshop diagrams from the upstream TypeScript workshop:

https://github.com/langfuse/langfuse-workshop

They were copied at upstream commit `28996a20d39a82e511a8fd043fb26252495453e3` (2026-11-23). The UI views are not specific to TypeScript. This Python port uses the same trace name (`dad-it-support-chat-turn`), tool names (`get_support_context`, `search_help_library`), prompt name (`dad-it-support-agent`), and dataset name (`dad-it-support-workshop`), so the captured screens match the Python flow.

`sample_app.png` and `specs_illustration.png` show the upstream client. `python-ui.png` is a headless Chrome capture of this repo's page at `http://127.0.0.1:3333` during the 2026-11-24 sync (Specs greeting, suggestion chips, iPhone panel). Sending a chip was not captured: that calls OpenAI and no API key was available.

## Not refreshed in this sync

No Langfuse project URL or browser session was available, so none of the Cloud UI screenshots were regenerated. `scripts/refresh_screenshots.py` is the refresh path. It exits successfully and leaves these files in place when `LANGFUSE_PROJECT_URL` and a Playwright storage state (or email and password) are missing.

Diagrams that are not UI captures (`AI-engineering-loop.png`, `specs_illustration.png`, `tracing/process_illustration.png`, `monitoring/error-analysis-process.png`) do not need a Langfuse session.
