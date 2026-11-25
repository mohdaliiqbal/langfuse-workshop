---
title: "Workshop: Instructor Notes for Setup"
description: "Facilitator notes for setup: keep learners on the checkpoint snapshot, verify the local port and credentials, and leave evaluator configuration for monitoring."
---

# 00 Setup

Learner guide: [00 Setup](../learner/00-setup.md)

## Instructor notes

- Recommend **Langfuse Cloud**, not self-hosted. This workshop is about current Cloud features.
- Confirm Halo is visible. If AI Features are off, only an owner or admin can turn them on under **Organization Settings → General → AI Features**.
- Learners load the untraced app with `uv run python scripts/use_checkpoint.py 00-setup`. That snapshot matches `01-base-app`. It is not the finished reference in `app/` on a fresh clone. A fresh clone is the finished app, so say the checkpoint command out loud before they edit.
- The UI is at `http://127.0.0.1:3333`. One Python process serves the page and the API. There is no Vite reload. After a code edit they restart `uv run python -m app.server`.
- `app/env.py` loads `.env` with override, so stale exported keys from another project do not win. Tell them to edit `.env`.
- EU host: `LANGFUSE_BASE_URL=https://cloud.langfuse.com`. US host: `https://us.cloud.langfuse.com`.
- Do not front-load **Project Settings → LLM Connections**. Learners add the OpenAI connection in [section 4.2 Detect topics and issues](../learner/04-monitoring/topics.md). [Section 4.3 Capturing signals](../learner/04-monitoring/capturing-signals.md) reuses that connection and picks **5.6 Luna** for the disagreement judge. Someone who skips topics adds the connection at the start of capturing signals.
- Node is only for `npx langfuse-cli` and the skill installer. The app runs without it.
