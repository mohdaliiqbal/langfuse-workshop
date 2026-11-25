---
title: "Workshop: Instructor Notes for the Base App Tour"
description: "Facilitator notes for the base app chapter: chat UI, FastAPI routes, agent loop, and local tools."
---

# 01 Base App

Learner guide: [01 Base App](../learner/01-base-app.md)

## Instructor notes

- Nothing to build. Point at the three boundaries they will instrument: FastAPI route in `app/server.py`, the loop in `app/support_agent.py`, and the tools in `app/tools.py`.
- The base snapshot uses the official OpenAI SDK and local tool functions only.
- The chat page is vanilla HTML and JS in `app/static/`, not React. The `/api/chat` body is the same `{ messages, sessionId }` contract as the TypeScript app.

## Watch for

- Learners editing the prompt or tools here. Save edits for `02-tracing`.
- Confusion between the finished files on a fresh checkout and the untraced snapshot. `use_checkpoint.py reference` puts the finished app back.
