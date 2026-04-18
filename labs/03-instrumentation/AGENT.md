# Lab 3: Rich Instrumentation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 3" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "Please make sure you have a terminal window open in the workshop directory, and open the lab README in your browser for screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/03-instrumentation/README.md**
>
> I'll reference specific tasks in the README at each verification step."

---

## Your task

You are teaching Lab 3 as a live instructor. Make one change at a time, explain the concept, then ask the attendee to run the app and verify in Langfuse before moving on.

The attendee's app has `@observe` decorators from Lab 2. Now we enrich those traces with token usage, sessions, user IDs, trace naming, and environments.

---

## Step 1 — Switch to the Langfuse OpenAI drop-in

**Announce**: Right now the trace shows responses but no token counts or cost. A one-line import change fixes that.

**Make the change** — in `app/assistant.py`, replace the OpenAI import:

```python
# Before
from openai import OpenAI

# After
from langfuse.openai import OpenAI  # drop-in: auto-captures tokens, model, cost
```

Also change `@observe(as_type="generation")` on `call_llm()` to plain `@observe()`:

```python
@observe()  # plain span — the OpenAI wrapper creates the generation inside it
def call_llm(messages: list[dict]) -> str:
    ...
```

**Explain**: The `langfuse.openai` wrapper is a transparent proxy — it intercepts every `client.chat.completions.create()` call and records the model name, input tokens, output tokens, and estimated cost in USD. We change `call_llm` from `as_type="generation"` to a plain span because the wrapper now creates the generation automatically inside it — keeping `as_type="generation"` would create a duplicate nested generation.

**Terminal prompt**: "In your terminal, run the app and ask a question."

**Langfuse check**: "Open the `call_llm` node in your observation. You should now see model name, token counts, and an estimated cost in the detail panel."

📸 **See Task 3.1 in the lab README** for a screenshot showing token counts and cost on the generation.

**✋ Check in**: "Do you see token counts on the generation? What model and cost does it show?"

---

## Step 2 — Add session tracking

**Announce**: Right now each question is an isolated trace. Sessions group all turns of a conversation together — essential for replaying a full user interaction.

**Make the change** — update `answer()` in `app/assistant.py`:

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
    with propagate_attributes(session_id=session_id or str(uuid.uuid4())):
        context = retrieve_context(question)
        ...
```

Update `app/main.py` to generate a session ID at startup and pass it through:

```python
import uuid

session_id = str(uuid.uuid4())

# In the loop, update the answer() call:
response = answer(question, history, session_id=session_id)
```

**Explain**: Without sessions, a 10-turn conversation appears as 10 unrelated traces. With sessions, you can open **Sessions** in Langfuse and replay the entire conversation in order — exactly what a support team needs when a customer calls to complain. `propagate_attributes` attaches the session ID to the current trace context and all child spans automatically.

**Terminal prompt**: "Run the app and ask 3+ questions in one run."

**Langfuse check**: "In Langfuse, go to **Sessions**. You should see one session containing all questions from that run."

📸 **See Task 3.2 in the lab README** for a screenshot of the session view.

**✋ Check in**: "Do you see a session with multiple turns? Click it — can you see the full conversation in order?"

---

## Step 3 — Add user ID and trace metadata

**Announce**: Session IDs group conversations. User IDs link conversations to specific users — essential when someone reports a problem and you need to see everything they've asked.

**Make the change** — expand `propagate_attributes` in `answer()`:

```python
with propagate_attributes(
    session_id=session_id,
    user_id=user_id,
    tags=["workshop", "lab-3"],
    metadata={"app_version": "1.0.0"},
):
    ...
```

Update `app/main.py` to pass a user ID:

```python
user_id = "workshop-user-1"

response = answer(question, history, session_id=session_id, user_id=user_id)
```

**Explain**: `user_id` lets you filter Langfuse to show only one user's traces. In production, this is how you investigate a specific complaint — search the user ID and see every conversation they've had, every score they've received, every error that occurred. Tags are free-form labels useful for filtering across multiple pipelines.

**Terminal prompt**: "Run the app and ask a few questions."

**Langfuse check**: "In Langfuse, go to **Users**. You should see `workshop-user-1` listed with a trace count."

📸 **See Task 3.3 in the lab README** for a screenshot of the Users view.

**✋ Check in**: "Is `workshop-user-1` visible? What trace count does it show?"

---

## Step 4 — Name your traces

**Announce**: By default, traces are named after the function (`answer`). A meaningful name makes them identifiable at scale across multiple pipelines.

**Make the change** — add `trace_name` to `propagate_attributes`:

```python
with propagate_attributes(
    trace_name="support-question",
    session_id=session_id,
    user_id=user_id,
    tags=["workshop", "lab-3"],
    metadata={"app_version": "1.0.0"},
):
    ...
```

**Explain**: When you later add other pipelines (a summariser, a billing assistant, a search endpoint), filtering the observations table by `trace_name = "support-question"` shows each pipeline's performance separately. This prevents one noisy pipeline from drowning out quality signals from others.

**Terminal prompt**: "Run the app and ask a question."

**Langfuse check**: "Open the observation. The name at the top of the detail panel should show `support-question` instead of `answer`."

📸 **See Task 3.4 in the lab README** for a screenshot showing the renamed trace.

**✋ Check in**: "Does the observation show `support-question` as its name?"

---

## Step 5 — Set the tracing environment

**Announce**: Without environments, dev and production data mix together. One line in `.env` keeps them cleanly separated.

**Make the change** — add to the attendee's `.env` file:

```bash
LANGFUSE_TRACING_ENVIRONMENT=development
```

**Explain**: Every trace now carries an `environment` attribute. In production you'd set `LANGFUSE_TRACING_ENVIRONMENT=production`. Same project, same datasets — but you can filter the observations table to show only `development` traces. This prevents dev noise from inflating error rates or polluting dashboards the team watches in real time.

**Terminal prompt**: "Restart the app (so the `.env` change takes effect) and ask a question."

**Langfuse check**: "Use the **Environment** filter at the top of the observations table. Select `development` — only your workshop traces should appear."

📸 **See Task 3.5 in the lab README** for a screenshot of the environment filter.

**✋ Check in**: "Does the environment filter work? Are only development traces visible when you select it?"

---

## Completion check

- [ ] Generations show token counts and model name
- [ ] Traces are grouped under a Session in the Sessions view
- [ ] `workshop-user-1` appears in the Users view
- [ ] Traces are named `support-question`
- [ ] Traces are filterable by `environment = development`

"Excellent — you now have production-grade observability: cost tracking, session replay, user attribution, and environment separation. Ready for Lab 4: Prompt Management?"
