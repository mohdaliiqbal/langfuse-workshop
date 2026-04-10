# Lab 3: Rich Instrumentation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 3" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through enriching their traces with token usage, session tracking, user IDs, and trace naming. All changes are in `app/assistant.py` and `app/main.py`.

The attendee's app already has `@observe` decorators from Lab 2.

---

## Step 1 — Switch to the Langfuse OpenAI drop-in

**Change**: Replace the OpenAI import at the top of `app/assistant.py`:

```python
# Before
from openai import OpenAI

# After
from langfuse.openai import OpenAI  # drop-in: auto-captures tokens, model, cost
```

Also change `@observe(as_type="generation")` on `call_llm()` to plain `@observe()` — the OpenAI wrapper now creates the generation automatically, so keeping `as_type="generation"` would produce a duplicate nested generation.

```python
@observe()  # plain span — openai wrapper creates the generation inside it
def call_llm(messages: list[dict]) -> str:
    ...
```

**Run**: Ask a question.

**Verify in Langfuse**: Open the trace and click the generation node inside `call_llm`. You should now see **model name**, **token counts** (input/output/total), and an estimated **cost in USD** — all captured automatically with no extra code.

**Explain**: The `langfuse.openai` wrapper intercepts every `client.chat.completions.create()` call and records the full generation metadata. This works for any OpenAI-compatible API including Anthropic Claude (just change `api_key` and `base_url`).

---

## Step 2 — Add session tracking

**Change**: Update `answer()` in `app/assistant.py` to accept a `session_id` parameter and propagate it via `propagate_attributes`. Also remove the `get_client` import if unused.

```python
import uuid
from langfuse import observe, propagate_attributes

@observe()
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> str:
    with propagate_attributes(
        trace_name="support-question",
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
        tags=["workshop"],
        metadata={"app_version": "1.0.0"},
    ):
        context = retrieve_context(question)
        ...
```

**Change**: Update `app/main.py` to generate a `session_id` at startup and pass it to `answer()`:

```python
import uuid
from langfuse import get_client

session_id = str(uuid.uuid4())
user_id = "workshop-user-1"

# In the loop, update the answer() call:
response = answer(question, history, session_id=session_id, user_id=user_id)
```

**Run**: Ask 3+ questions in one run of the app.

**Verify in Langfuse**:
1. Go to **Sessions** — you should see a session containing all the questions from that run grouped together
2. Go to **Users** — you should see `workshop-user-1` listed with a trace count
3. Open any trace — it should now be named `support-question` instead of `answer`

**Explain**: Session IDs group all turns of a conversation so you can replay the full interaction. User IDs let you filter all traces for a specific user — essential when a customer reports a problem. The trace name makes traces identifiable at scale.

---

## Step 3 — Set the tracing environment

**Change**: Add one line to the attendee's `.env` file:

```bash
LANGFUSE_TRACING_ENVIRONMENT=development
```

**Run**: Ask a question.

**Verify in Langfuse**: Use the **Environment** filter at the top of the Traces table — select `development` and confirm only the workshop traces appear.

**Explain**: In production you'd set `LANGFUSE_TRACING_ENVIRONMENT=production`. Same project, same prompts, same datasets — but traces from different environments are cleanly separated. This prevents dev noise from polluting production dashboards and score analytics.

---

## Completion check

- [ ] Generations show token counts and model name
- [ ] Multiple questions from one run appear grouped in Sessions
- [ ] `workshop-user-1` appears in the Users view
- [ ] Traces are named `support-question`
- [ ] Traces are filterable by `environment = development`

Once confirmed, tell the attendee they're ready for **Lab 4: Prompt Management**.
