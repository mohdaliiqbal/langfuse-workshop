# Lab 2: Rich Tracing — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 2" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Run `pwd` via Bash to get the workshop directory path. Then tell the attendee (substituting the actual path):

> "Before we begin, please do two things:
> 1. Open a new terminal window and navigate to the workshop directory:
>    ```bash
>    cd /path/to/workshop   ← replace with the actual path from pwd
>    ```
> 2. Open the lab README in your browser — it has all the screenshots for reference: **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/02-tracing/README.md**
>
> Keep both open as we go. I'll tell you exactly which task and step to look at for each screenshot."

---

## Your task

You are teaching Lab 2 as a live instructor. We're going straight for **rich** tracing — nested observations, cost/token/latency capture, and a meaningful trace name — all in this one lab. Make one code change at a time, explain why, then ask the attendee to verify before continuing.

The attendee's `app/assistant.py` has no Langfuse imports. The app works — it just produces no observability data.

---

## Step 0 — Tour the application code

**Announce**: Before we add any observability, let's understand what we're working with. Read `app/assistant.py` and `app/knowledge_base.py` — then walk the attendee through the structure.

Read the files now and explain to the attendee:

> "Here's how the app is structured:
>
> **`app/web.py`** — the entry point. It runs a Gradio web server that serves the chat UI at http://localhost:7860, calls `answer()`, and passes the response back to the browser.
>
> **`app/assistant.py`** — the brain. The current `answer()` does everything inline: retrieves docs, builds the messages array, calls OpenAI, returns the response. We'll split it into three named functions so each step shows up as its own node in the trace.
>
> **`app/knowledge_base.py`** — a simple in-memory store with DataStream product docs. A keyword-based `retrieve()` returns the top matches; `format_context()` joins them into the text block we inject into the prompt.
>
> The flow is: **user question → retrieve docs → build messages → call LLM → return answer**. That's exactly the structure your trace will reflect once we're done."

**✋ Check in**: "Does the structure make sense? Any questions before we start adding instrumentation?"

Wait for their reply before continuing.

---

## Step 1 — Add nested observations with a meaningful trace name

**Announce**: We'll add three `@observe` decorators in one pass — one for the root, one for retrieval, one for the LLM call. We'll also give the root a real name (`support-question`) right away, so traces are identifiable from the very first one you log. No half-instrumented intermediate state.

**Make the change** — in `app/assistant.py`, add the import, extract `retrieve_context()` and `call_llm()` from the inline body, and decorate all three. Final state:

```python
# app/assistant.py — at the top:
from langfuse import observe

# Add these two new functions above answer():
@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)


@observe()
def call_llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


# Replace the existing answer() with this — give the trace a real name via @observe(name=...):
@observe(name="support-question")
def answer(question: str, history: list[dict] | None = None) -> str:
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

**Show the diff**: Point out the three new decorators, the two new functions, and the `name="support-question"` on the root.

> **Note for attendees**: `app/knowledge_base.py` does NOT need any Langfuse imports — it's a plain data file.

**Explain**: `@observe()` intercepts each function call and records its name, inputs, return value, and timing. When one decorated function calls another, Langfuse nests them automatically — so you get a tree (`support-question` → `retrieve_context` + `call_llm`) instead of three unrelated entries. Naming the root explicitly from the start matters: at scale you'll have multiple pipelines logging traces, and `support-question` is far more useful in a filter than the function name `answer`.

**Terminal prompt**: "Save the file — Gradio will reload automatically. Ask one question in the browser, then check Langfuse."

> If the app isn't running: `uv run gradio app/web.py`, then open http://localhost:7860

**Langfuse check**: "In Langfuse, go to **Tracing** → **Traces**. You should see a new trace named `support-question`. Click it — the left panel shows a tree with `support-question` at the top and `retrieve_context` + `call_llm` nested beneath it."

📸 **See Task 2.1 in the lab README** for screenshots of the nested trace tree and the per-node detail view.

**✋ Check in**: "Do you see the trace named `support-question` with the two child nodes? Click `call_llm` — what does its Input show?"

Wait for their answer before continuing.

---

## Step 2 — Capture cost, tokens, and the generation type

**Announce**: The trace shows what each step received and returned, but the LLM call doesn't yet show model, token counts, or cost. One import change fixes that.

**Make the change** — in `app/assistant.py`, replace the OpenAI import:

```python
# Before
from openai import OpenAI

# After
from langfuse.openai import OpenAI  # drop-in: auto-captures tokens, model, cost
```

That's it. Don't touch `call_llm()` — keep it as a plain `@observe()`. The wrapper creates the generation observation automatically inside it.

**Explain**: `langfuse.openai` is a transparent proxy — every `client.chat.completions.create()` call gets intercepted and recorded as a **generation** observation with model name, input/output tokens, and estimated cost in USD. Generations are a distinct observation type (different icon in the UI) and this is where cost dashboards, per-model comparisons, and token budgets all come from. You'd reach the same result by hand-recording usage on a manual generation, but the wrapper is one line and never drifts out of date.

**Terminal prompt**: "Save the file — Gradio reloads automatically. Ask a question in the browser."

**Langfuse check**: "Open the new trace. Inside `call_llm` you now see a nested **generation** node — click it. The top bar shows the model name (e.g. `gpt-4o-mini`), input + output token counts, total tokens, and estimated cost. The left panel also shows latency for every node."

📸 **See Task 2.2 in the lab README** for a screenshot showing the generation with tokens and cost.

**✋ Check in**: "Do you see the generation with token counts and a cost figure? What model and cost did it record?"

---

## Step 3 — Confirm everything is flowing

**Announce**: With three decorators and one import change you now have nested observations, observation types (span vs. generation), cost, tokens, latency, and a meaningful trace name — that's rich tracing.

**Terminal prompt**: "Ask 2–3 more questions in the browser."

**Explain**: Langfuse batches and sends trace data asynchronously in the background. With the web server running continuously, this happens automatically — no manual flush needed. In Lab 7, the offline eval scripts are short-lived and will call `get_client().flush()` explicitly before exiting — that's the scenario flush is designed for.

**✋ Check in**: "Are all your traces showing up with full input, output, tokens, and cost? Does anything look cut off?"

---

## Completion check

- [ ] Each question creates a trace named `support-question` in the Traces table
- [ ] Each trace has `support-question` → `retrieve_context` + `call_llm` nested
- [ ] `call_llm` contains a generation node with model name, token counts, and cost
- [ ] Latency is visible on every node

"Great work — you've added rich, production-grade tracing in a single lab. Ready for Lab 3, where we attach this to real conversations and environments?"
