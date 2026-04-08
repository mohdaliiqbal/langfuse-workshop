# Lab 2: Rich Instrumentation

## Concept

Basic tracing tells you *what* happened. Rich instrumentation tells you *who*, *how much*, and *why*.

In production, you need to answer questions like:
- Which user triggered this trace? (user tracking)
- Was this part of a multi-turn conversation? (sessions)
- How many tokens did this cost? (usage tracking)
- What version of the app generated this? (release tracking)
- Why did this particular trace fail? (metadata)

Langfuse supports all of this through **trace attributes** and **propagated context**.

### Key concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| `user_id` | Link traces to users | `"user_42"` |
| `session_id` | Group traces from one conversation | `"conv_abc123"` |
| `tags` | Filter traces in the UI | `["production", "v2"]` |
| `metadata` | Attach arbitrary data | `{"ab_variant": "A"}` |
| `usage_details` | Token counts for cost tracking | `{"input_tokens": 120, "output_tokens": 45}` |
| `version` | Track app/prompt versions | `"1.2.0"` |

---

## What You'll Build

Extend the instrumented assistant from Lab 1 to capture:
1. Token usage and model details on generations
2. Session IDs so multi-turn conversations group together
3. User IDs on every trace
4. Custom metadata and version tags

---

## Tasks

### Task 2.1 — Capture token usage on generations

Open `app/assistant.py`. The `client = OpenAI()` line at the top is where the OpenAI client is created. Currently it records input/output text but not token counts. Langfuse can display cost estimates, but only if it knows the token usage.

The simplest way to enable this is Langfuse's **drop-in OpenAI replacement** — a one-line import change that wraps the OpenAI client and automatically captures token usage, model name, and cost for every call, with no other code changes needed.

Replace the OpenAI import at the top of `app/assistant.py`:

```python
# Before
from openai import OpenAI

# After
from langfuse.openai import OpenAI
```

That's it. The `call_llm()` function stays exactly as it is. Langfuse intercepts every `client.chat.completions.create()` call and records the model, token counts, and estimated cost automatically.

> **Note**: This drop-in also works alongside `@observe`. The `@observe(as_type="generation")` decorator on `call_llm()` creates the span in the trace hierarchy, while the OpenAI wrapper fills in the token and cost details.

Ask a question and verify token counts appear in the Langfuse generation detail view.

---

### Task 2.2 — Add session tracking

Right now each question creates an independent trace. But your app supports multi-turn conversations — logically, all turns of a conversation should be grouped.

Langfuse uses a `session_id` for this. Pass it via `propagate_attributes`:

```python
import uuid
from langfuse import observe, propagate_attributes

@observe()
def answer(question: str, history: list[dict] | None = None, session_id: str | None = None) -> str:
    with propagate_attributes(session_id=session_id or str(uuid.uuid4())):
        context = retrieve_context(question)
        ...
```

Update `app/main.py` to generate a session ID at startup and pass it through:

```python
import uuid
session_id = str(uuid.uuid4())

# In the loop:
response = answer(question, history, session_id=session_id)
```

Ask a few questions in one session. In Langfuse, go to **Sessions** — all questions from that run should be grouped together.

---

### Task 2.3 — Add user ID and trace metadata

In a real app you'd have authenticated users. Simulate this by hardcoding a user ID and passing it as trace metadata:

```python
from langfuse import observe, propagate_attributes

@observe()
def answer(question: str, history: list[dict] | None = None, session_id: str | None = None, user_id: str | None = None) -> str:
    with propagate_attributes(
        session_id=session_id,
        user_id=user_id,
        tags=["workshop", "lab-2"],
        metadata={"app_version": "1.0.0"},
    ):
        ...
```

Update `app/main.py` to pass a `user_id` (e.g., `"workshop-user-1"`).

---

### Task 2.4 — Name your traces

By default, traces use the function name. Give the root trace a meaningful name using `trace_name`:

```python
with propagate_attributes(
    trace_name="support-question",
    session_id=session_id,
    user_id=user_id,
):
    ...
```

---

## Checkpoint

Ask several questions across a session. In Langfuse:

- [ ] Generations show token counts (input + output)
- [ ] Generations show the model name
- [ ] Traces are grouped under a Session in the Sessions view
- [ ] Traces show `user_id` and `tags` in the detail view
- [ ] Traces are named `"support-question"` instead of `"answer"`

---

## Why This Matters

With user IDs and sessions, you can:
- Filter all traces for a specific user who reported a bug
- See the full conversation history for a support case
- Measure per-user token spend
- Identify users having bad experiences

With token usage, you can:
- Build cost dashboards (cost per user, per feature, per day)
- Set budget alerts
- Compare cost across model versions

---

## Solution

See [`solution.py`](./solution.py) for the complete implementation.
