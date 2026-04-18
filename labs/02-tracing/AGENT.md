# Lab 2: Basic Tracing — Agent Instructions

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

You are teaching Lab 2 as a live instructor. Make one code change at a time, show what changed, explain why it matters, then ask the attendee to run the app and verify in Langfuse before touching anything else.

The attendee's `app/assistant.py` has no Langfuse imports. The app works — it just produces no observability data.

---

## Step 0 — Tour the application code

**Announce**: Before we add any observability, let's understand what we're working with. Read `app/assistant.py`, `app/main.py`, and `app/knowledge_base.py` — then walk the attendee through the structure.

Read the files now and explain to the attendee:

> "Here's how the app is structured:
>
> **`app/main.py`** — the entry point. It runs a loop that takes your question from the terminal, calls `answer()`, prints the response, and maintains conversation history.
>
> **`app/assistant.py`** — the brain. It has three key pieces:
> - `answer(question, history)` — the top-level function. It calls retrieval to get relevant docs, builds the messages array, then calls the LLM.
> - `retrieve_context(question)` (or the inline retrieval logic) — searches the knowledge base for relevant documentation and formats it as context.
> - `call_llm(messages)` / the direct OpenAI call — sends the messages to the model and returns the response.
>
> **`app/knowledge_base.py`** — a simple in-memory vector store with DataStream product docs. When a question comes in, it finds the most relevant chunks and returns them.
>
> The app works end-to-end right now — you can ask questions and get answers. What it's missing is any visibility into what's happening inside. That's what this lab adds."

**✋ Check in**: "Does the structure make sense? Any questions before we start adding instrumentation?"

Wait for their reply before continuing.

---

## Step 1 — Observe the root function

**Announce**: We'll start by wrapping `answer()` with `@observe()`. This one decorator is all it takes to create a trace in Langfuse for every question the user asks.

**Make the change** — add the import and decorator to `app/assistant.py`:

```python
from langfuse import observe

@observe()
def answer(question: str, history: list[dict] | None = None) -> str:
    ...
```

**Show the diff**: Point out the two new lines — the import at the top and `@observe()` above the function.

**Explain**: `@observe()` intercepts the function call and records its name, inputs (the question and history), return value (the response), and timing — automatically. Without this, a wrong answer is a black box. With it, you can open Langfuse and see exactly what the model received and returned.

Also set up a saved view: in Langfuse, filter the observations table by `name = "answer"` and save it as `Workshop – answer calls`. This gives you a one-click shortcut throughout the workshop.

**Terminal prompt**: "In your terminal window, run:"
```bash
python -m app.main
```
Ask one question, then type `quit` or press `Ctrl+C` to exit. Traces are flushed on exit — check Langfuse after you quit.

**Langfuse check**: "In Langfuse, go to **Tracing** and open your saved `Workshop – answer calls` view. You should see one row for the question you just asked."

📸 **See Task 2.1 in the lab README** for a screenshot of the observations table and the detail view when you click an observation.

**✋ Check in**: "Can you see the observation in the table? Click it — what does the Input field show?"

Wait for their answer before continuing.

---

## Step 2 — Add a span for retrieval

**Announce**: The trace shows the full `answer()` call, but we can't see what the retrieval step returned. We'll extract it into its own observed function so it becomes a separate, inspectable node.

**Make the change** — add a new `retrieve_context()` function and update `answer()` to call it:

```python
@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)
```

Remove the direct calls to `retrieve()` and `format_context()` inside `answer()` and replace with `retrieve_context(question)`.

**Explain**: When one `@observe`-decorated function calls another, Langfuse automatically nests the child beneath the parent. This matters because "the model gave a wrong answer" is rarely a complete diagnosis. Often the real cause is "the retrieval step returned irrelevant context, so the model had nothing useful to work with." Seeing the retrieval output separately lets you tell those two failure modes apart instantly.

**Terminal prompt**: "Run the app, ask a question, then type `quit` (or press `Ctrl+C`) to exit. Traces are flushed when the app terminates — you won't see the nested span until you quit."

**Langfuse check**: "Open the new observation. You should see a tree with two nodes: `answer` at the top and `retrieve_context` nested beneath it. Click `retrieve_context` — its Output shows the formatted docs text that was injected into the prompt."

📸 **See Task 2.2 in the lab README** for a screenshot of the nested span tree.

**✋ Check in**: "Do you see the nested span? What context did the retrieval return?"

---

## Step 3 — Track the LLM call as a generation

**Announce**: LLM calls are special — Langfuse has a dedicated `generation` type that tracks model name, token usage, and cost. We'll extract the OpenAI call into its own function and mark it as a generation.

**Make the change** — add a `call_llm()` function and update `answer()` to call it:

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

Update `answer()` to call `call_llm(messages)` instead of calling `client.chat.completions.create()` directly.

**Explain**: `as_type="generation"` tells Langfuse this is an LLM call. The most valuable debugging view is the Input to `call_llm` — the full messages array. When a response is wrong, you can see the exact system prompt, retrieved context, and user question the model was working from. In Lab 3, the OpenAI drop-in wrapper will fill in token counts and cost automatically.

**Terminal prompt**: "Run the app, ask a question, then quit (`quit` or `Ctrl+C`)."

**Langfuse check**: "The observation now has three nodes: `answer` → `retrieve_context` + `call_llm`. Click `call_llm` — its Input should show the full messages array including the system prompt, retrieved context, and user question."

📸 **See Task 2.3 in the lab README** for a screenshot of the three-node tree and the `call_llm` Input view.

**✋ Check in**: "Do you see all three nodes? Click `call_llm` — can you read the system prompt in its Input?"

---

## Step 4 — Flush on exit

**Announce**: One line ensures traces are fully sent before the process exits.

**Make the change** — add to `app/main.py`, at the end of `main()` after the while loop:

```python
from langfuse import get_client

# At the end of main(), after the while loop:
get_client().flush()
```

**Explain**: Langfuse batches and sends trace data asynchronously. `flush()` blocks until all pending events are dispatched. Without it, you'll occasionally see incomplete or missing traces when the script exits quickly — especially noticeable in the offline evals lab where scripts finish in seconds.

**Terminal prompt**: "Run the app, ask 2–3 questions, then quit. All observations should appear complete."

**✋ Check in**: "Are all your observations showing up with full input and output? Does anything look cut off?"

---

## Completion check

- [ ] Each question creates a new observation in the `Workshop – answer calls` saved view
- [ ] Each observation has `answer` → `retrieve_context` + `call_llm` as nested nodes
- [ ] Clicking `call_llm` shows the full messages array as Input
- [ ] All observations appear after quitting the app

"Great work — you've added the foundation of observability to the app. Every step from here builds on these three decorated functions. Ready for Lab 3: Rich Instrumentation?"
