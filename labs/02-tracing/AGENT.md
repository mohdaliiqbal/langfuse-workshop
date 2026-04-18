# Lab 2: Basic Tracing — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 2" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through adding basic Langfuse tracing to `app/assistant.py` and `app/main.py`. Make changes one step at a time, explaining each one and verifying it in the Langfuse UI before moving on.

The attendee's `app/assistant.py` currently has no Langfuse imports. The app works — it just produces no observability data.

---

## Step 1 — Observe the root function

**Change**: Add `@observe()` to the `answer()` function in `app/assistant.py`.

```python
from langfuse import observe

@observe()
def answer(question: str, history: list[dict] | None = None) -> str:
    ...
```

**Run**: `python -m app.main` — ask one question, then quit.

**Verify in Langfuse**: Go to **Tracing** — you'll see the **observations table**, Langfuse's primary view in v4. An observation named `answer` should appear. Click it — you'll see the question as Input and the response as Output.

**Set up a saved view (do this once now)**: The observations table shows all operations. To focus on just the root `answer()` calls throughout the workshop, add a filter `name = "answer"` in the filter sidebar and click **Save view**, naming it `Workshop – answer calls`. This saves you from re-filtering every session.

**Explain**: Every call to `answer()` now creates an observation in Langfuse. The decorator captured the function arguments as input and the return value as output automatically. This is your observability foundation: without it, a wrong answer is a black box; with it, you can see exactly what prompt, context, and history the model received.

---

## Step 2 — Add a span for retrieval

**Change**: Extract the retrieval logic into a new `retrieve_context()` function decorated with `@observe()`. Call it from `answer()` instead of calling `retrieve()` and `format_context()` directly.

```python
@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)
```

Update `answer()` to call `retrieve_context(question)` and remove the direct calls to `retrieve()` and `format_context()`.

**Run**: Ask another question.

**Verify in Langfuse**: Open the observation. You should now see a tree with two nodes: `answer` at the top and `retrieve_context` nested beneath it. Click `retrieve_context` — its Input is the question and its Output is the formatted docs text that was injected into the prompt.

**Explain**: When one `@observe`-decorated function calls another, Langfuse automatically creates a parent-child relationship. This matters because "the model gave a wrong answer" is rarely a complete diagnosis — often it's "the retrieval step returned irrelevant context, so the model had nothing useful to work with." Seeing the retrieval output separately lets you tell those two failure modes apart instantly.

---

## Step 3 — Track the LLM call as a generation

**Change**: Extract the OpenAI call into a `call_llm()` function decorated with `@observe(as_type="generation")`. Call it from `answer()`.

```python
@observe(as_type="generation")
def call_llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content
```

**Run**: Ask another question.

**Verify in Langfuse**: The observation now has three nodes: `answer` → `retrieve_context` + `call_llm`. Click `call_llm` — its Input shows the **full messages array** sent to the model (system prompt, retrieved context, user question). This is the most important debugging view: if the model gave a wrong answer, you can see exactly what it was working with.

**Explain**: `as_type="generation"` marks this as an LLM call rather than a generic span. Langfuse uses this to display model name, token counts, and cost estimates. In production this is how you track spend per feature, per user, or per prompt version — not by guessing from billing dashboards but by querying observations directly.

---

## Step 4 — Flush on exit

**Change**: Add `flush()` to `app/main.py` so all traces are sent before the process exits.

```python
from langfuse import get_client

# At the end of main(), after the while loop:
get_client().flush()
```

**Explain**: Langfuse sends data in the background. In a short-lived script, the process can exit before all events are dispatched. `flush()` blocks until everything is sent.

---

## Completion check

Ask the attendee to run the app, ask 2-3 questions, then check Langfuse:

- [ ] Each question creates a new trace
- [ ] Each trace shows `answer` → `retrieve_context` + `call_llm` in the tree
- [ ] Clicking `call_llm` shows the full messages array as Input
- [ ] All traces appear after quitting the app

Once confirmed, tell the attendee they're ready for **Lab 3: Rich Instrumentation**.
