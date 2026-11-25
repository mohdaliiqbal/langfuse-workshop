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
- Do not skip the `update_current_span(input=request.model_dump(mode="json", by_alias=True, exclude_none=True))` line in Step 2. Without it the Python root input is `{"args": [...], "kwargs": {}}` in snake_case, and the 4.3 evaluator mapping **Input → messages** finds nothing.
- User and session propagation is optional live. The `03-prompt-management` snapshot already includes `propagate_attributes`.
- Tracing environment is an appendix, not a fourth live step. Leave `LANGFUSE_TRACING_ENVIRONMENT` unset unless a learner wants laptop traces separated from a deployed app. Unset traces land in `default`. The app never sets a tracing environment. If they set the variable, the Traces filter and the 4.3 sample-observation filter have to use that same value. Do not tell them to filter the sample panel to `production`.

## Demo rhythm

1. Switch the OpenAI import and boot `get_client()` in `app/server.py`. One turn, separate generation traces.
2. Add `@observe` on `run_support_conversation` and the root-input line. One turn, nested generations, and the request body as the root input.
3. Decorate the two tool helpers. One turn, full tree.

Restart the server between steps. This app does not watch files.
