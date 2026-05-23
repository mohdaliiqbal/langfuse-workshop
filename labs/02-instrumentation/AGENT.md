# Lab 2: Instrumentation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 2" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Run `pwd` via Bash to get the workshop directory path. Then tell the attendee (substituting the actual path):

> "Before we begin, please do two things:
> 1. Open a new terminal window and navigate to the workshop directory:
>    ```bash
>    cd /path/to/workshop   ← replace with the actual path from pwd
>    ```
> 2. Open the lab README in your browser — it has all the screenshots for reference: **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/02-instrumentation/README.md**
>
> Keep both open as we go. I'll tell you exactly which task and step to look at for each screenshot."

---

## Your task

You are teaching Lab 2 as a live instructor. This lab folds basic tracing and rich instrumentation together. There are five tasks — the first is a deliberately tiny win (one import, one decorator, one trace) so the attendee sees the feedback loop before anything else. Each task after that adds one capability. Make one change at a time, show what changed, explain why, then ask the attendee to verify in Langfuse before continuing.

The attendee's `app/assistant.py` has no Langfuse imports. The app works — it just produces no observability data.

---

## Step 0 — Tour the application code

**Announce**: Before we add any observability, let's understand what we're working with. Read `app/assistant.py` and `app/knowledge_base.py` — then walk the attendee through the structure.

Read the files now and explain to the attendee:

> "Here's how the app is structured:
>
> **`app/web.py`** — the entry point. It runs a Gradio web server that serves the chat UI at http://localhost:7860, calls `answer()`, and passes the response back to the browser.
>
> **`app/assistant.py`** — the brain. It has one function today:
> - `answer(question, history)` — retrieves docs, builds the messages array, calls OpenAI, returns the response.
>
> **`app/knowledge_base.py`** — a simple in-memory store with DataStream product docs and a keyword-scored `retrieve()` function.
>
> The app works end-to-end right now — you can ask questions and get answers. What it's missing is any visibility into what's happening inside. That's what this lab adds."

**✋ Check in**: "Does the structure make sense? Any questions before we start adding instrumentation?"

Wait for their reply before continuing.

---

## Task 2.1 — Your first trace

**Announce**: Smallest possible change first — one import, one decorator, no refactoring. The goal is to confirm the feedback loop: file change → Gradio reload → ask a question → see a trace appear in Langfuse. Everything else builds on that.

**Make the change** — in `app/assistant.py`, add the Langfuse import at the top and decorate the existing `answer()` function:

```python
# app/assistant.py — add the import alongside the existing imports:
from langfuse import observe

# Add @observe() directly above answer() — DO NOT change the function body:
@observe()
def answer(question: str, history: list[dict] | None = None) -> str:
    # ... existing code unchanged ...
```

**Show the diff**: Point out that nothing inside `answer()` changed — only the import and the one-line decorator above it.

**Explain**: `@observe()` is an interceptor. It captures the function's name (`answer`), its inputs (the question and history), its return value (the response string), and its duration — and sends all of that to Langfuse as one observation. Zero changes to your business logic. This is the foundation; the next task adds detail.

> **Saved view (one-time setup):** In Langfuse, go to **Tracing**, add the filter `name = "answer"` and click **Save view** as `Workshop – answer calls`. We'll rename the trace in Task 2.2 — for now this filter lets you find your work easily.

**Terminal prompt**: "Save the file — Gradio will reload automatically. Ask one question in the browser. If the app isn't running yet: `uv run gradio app/web.py`, then open http://localhost:7860."

**Langfuse check**: "In Langfuse, open your **Workshop – answer calls** saved view. You should see one row for the question you just asked. Click it — the detail panel shows your question as **Input** and the assistant's reply as **Output**, plus the duration."

📸 **See Task 2.1 in the lab README** for screenshots of the observations table and the detail view.

**✋ Check in**: "Can you see the observation? Open it — does the Input show your exact question?"

Wait for their answer before continuing.

---

## Task 2.2 — Split the pipeline, capture tokens, and name the trace

**Announce**: Now the bigger step. We'll split the pipeline into traced steps so retrieval and the LLM call show up separately, swap to Langfuse's drop-in OpenAI wrapper so tokens and cost are captured automatically, and rename the trace to `support-question` so it's identifiable at scale.

**Make the change** — replace the contents of `app/assistant.py` with:

```python
import os
from langfuse.openai import OpenAI  # drop-in: auto-captures tokens, model, cost
from langfuse import observe, propagate_attributes
from app.knowledge_base import retrieve, format_context

client = OpenAI()

SYSTEM_PROMPT = """You are a helpful customer support assistant for DataStream, a real-time data pipeline platform.

Your role is to help users with questions about DataStream's features, pricing, troubleshooting, and best practices.

Guidelines:
- Be concise and direct. Answer the question asked.
- Use the provided documentation context when available.
- If the answer is not in the context, say so honestly rather than guessing.
- For technical issues, provide actionable steps.
- Maintain a friendly, professional tone.
"""


@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)


@observe()  # plain span — the openai wrapper creates the generation inside it
def call_llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


@observe(name="support-question")
def answer(question: str, history: list[dict] | None = None) -> str:
    with propagate_attributes(trace_name="support-question"):
        context = retrieve_context(question)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        return call_llm(messages)
```

**Explain**: Three changes are layered on top of the Task 2.1 baseline.

1. **The pipeline is now a tree.** Extracting `retrieve_context()` and `call_llm()` as their own `@observe`-decorated functions gives you a parent-child tree per trace. Seeing the retrieval output separately from the LLM call lets you tell "the retrieval returned irrelevant context" apart from "the model ignored the context" — instantly.
2. **Token counts and cost are captured automatically.** Importing `OpenAI` from `langfuse.openai` instead of `openai` wraps every `client.chat.completions.create()` call so the model name, input/output tokens, and an estimated USD cost flow into Langfuse with no extra code. `call_llm` uses a plain `@observe()` because the wrapper creates the generation inside it; `as_type="generation"` would create a duplicate.
3. **The trace has a meaningful name.** `@observe(name="support-question")` plus `propagate_attributes(trace_name="support-question")` set the observation label and the trace-level name. At scale, filtering by `name = "support-question"` separates this pipeline's traces from others (summarisers, billing assistants, search endpoints).

> **Update your saved view:** change the filter from `name = "answer"` to `name = "support-question"` (or create a new saved view called `Workshop – support-question`).

**Terminal prompt**: "Save the file — Gradio reloads automatically. Ask one question in the browser."

**Langfuse check**: "Open the new observation. You should see:
> - A tree with `support-question` at the top and `retrieve_context` + `call_llm` nested beneath it
> - On the `call_llm` node, a model name, input/output token counts, and an estimated USD cost
> - The trace title at the top of the panel shows `support-question` (not `answer`)"

📸 **See Task 2.2 in the lab README** for screenshots of the tree, the token-instrumented generation, and the named trace.

**✋ Check in**: "Can you see all three nodes? Click `call_llm` — what model, token counts, and cost does Langfuse show?"

Wait for their answer before continuing.

---

## Task 2.3 — Group conversation turns into sessions

**Announce**: Right now each question is an isolated trace. Sessions group all turns of a conversation together — essential for replaying a full user interaction.

**Make the change** — update the imports and `answer()` in `app/assistant.py`:

```python
# add to imports at the top:
import uuid

# replace answer() with:
@observe(name="support-question")
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
) -> str:
    with propagate_attributes(
        trace_name="support-question",
        session_id=session_id or str(uuid.uuid4()),
    ):
        context = retrieve_context(question)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        return call_llm(messages)
```

> **Web app**: `app/web.py` already passes `session_id` automatically once the parameter exists in `answer()`'s signature — no changes to `web.py` needed. Each browser tab gets its own session ID.

**Explain**: Without sessions, a 10-turn conversation appears as 10 unrelated traces. With sessions, you can open **Sessions** in Langfuse and replay the entire conversation in order — exactly what a support team needs when a customer calls to complain. `propagate_attributes` attaches the session ID to the current trace context and all child spans automatically.

**Terminal prompt**: "Save the file — Gradio reloads automatically. Ask 3+ questions in the same browser tab."

**Langfuse check**: "In Langfuse, go to **Sessions**. You should see one session containing all questions from that tab."

📸 **See Task 2.3 in the lab README** for a screenshot of the session view.

> **If Sessions is empty**: check that `session_id` is declared in `answer()`'s signature — `app/web.py` only passes it if the parameter exists. Wait a few seconds and refresh; traces are sent asynchronously.

**✋ Check in**: "Do you see a session with multiple turns? Click it — can you see the full conversation in order?"

---

## Task 2.4 — Add user ID, tags, and metadata

**Announce**: Session IDs group conversations. User IDs link conversations to specific users — essential when someone reports a problem and you need to see everything they've asked.

**Make the change** — expand `propagate_attributes` in `answer()` in `app/assistant.py`:

```python
@observe(name="support-question")
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
        tags=["workshop", "lab-2"],
        metadata={"app_version": "1.0.0"},
    ):
        context = retrieve_context(question)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        return call_llm(messages)
```

> **Web app**: once `answer()` accepts `user_id`, `app/web.py` passes `"workshop-user-1"` automatically — no changes to `web.py` needed.

**Explain**: `user_id` lets you filter Langfuse to show only one user's traces. In production, this is how you investigate a specific complaint — search the user ID and see every conversation they've had, every score they've received, every error that occurred. Tags are free-form labels useful for filtering across multiple pipelines.

**Terminal prompt**: "Save the file — Gradio reloads automatically. Ask a few questions in the browser."

**Langfuse check**: "In Langfuse, go to **Users**. You should see `workshop-user-1` listed with a trace count."

📸 **See Task 2.4 in the lab README** for a screenshot of the Users view.

**✋ Check in**: "Is `workshop-user-1` visible? What trace count does it show?"

---

## Task 2.5 — Set the tracing environment

**Announce**: Without environments, dev and production data mix together. This is already configured — let's verify it's active.

**Check** — open the attendee's `.env` file and confirm this line is already there (it was copied from `.env.example` during setup):

```bash
LANGFUSE_TRACING_ENVIRONMENT=development
```

If it's missing, add it now. Otherwise, no change needed.

**Explain**: Every trace now carries an `environment` attribute. In production you'd set `LANGFUSE_TRACING_ENVIRONMENT=production`. Same project, same datasets — but you can filter the observations table to show only `development` traces. This prevents dev noise from inflating error rates or polluting dashboards the team watches in real time.

**Terminal prompt**: "Restart the app (so the `.env` is loaded fresh) and ask a question."

**Langfuse check**: "Use the **Environment** filter at the top of the observations table. Select `development` — only your workshop traces should appear."

📸 **See Task 2.5 in the lab README** for a screenshot of the environment filter.

**✋ Check in**: "Does the environment filter work? Are only development traces visible when you select it?"

---

## Completion check

- [ ] Each question creates a trace named `support-question` in the saved view
- [ ] The trace has `support-question` → `retrieve_context` + `call_llm` as nested nodes
- [ ] The generation shows model, token counts, and estimated cost
- [ ] Multi-turn conversations group under a Session in the Sessions view
- [ ] `workshop-user-1` appears in the Users view
- [ ] The Environment filter shows only `development` traces

"Excellent — you now have production-grade observability: a named, fully traced pipeline with cost tracking, session replay, user attribution, and environment separation. Ready for Lab 3: Prompt Management?"
