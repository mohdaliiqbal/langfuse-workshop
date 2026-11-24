---
title: "Workshop: Instructor Notes for Tracing"
description: "Facilitator notes for teaching Langfuse tracing in three layers: OpenAI generations, one agent root, and tool observations."
---

# 02 Tracing

Learner guide: [02 Tracing](../learner/02-tracing.md)

## Instructor notes

- Teach three layers: OpenAI generations, one agent root, then tool observations.
- Python equivalents of the TypeScript wrappers: `from langfuse.openai import OpenAI` instead of `observeOpenAI`, `@observe(name=..., as_type="agent"|"tool")` instead of `observe(fn, { asType })`, and `get_client()` plus `flush()` / `shutdown()` instead of `NodeSDK` and `LangfuseSpanProcessor`.
- Create the OpenAI client inside the decorated function so generations nest under the agent.
- User and session propagation is optional live. The `03-prompt-management` snapshot already includes `propagate_attributes`.

## Demo rhythm

1. Switch the OpenAI import and boot `get_client()` in `app/server.py`. One turn, separate generation traces.
2. Add `@observe` on `run_support_conversation`. One turn, nested generations.
3. Decorate the two tool helpers. One turn, full tree.

Restart the server between steps. This app does not watch files.
