# Lab 2: Basic Tracing

## Concept

When an LLM application fails or behaves unexpectedly, where do you look? Without observability, you're debugging blind — no visibility into what prompt was sent, what the model returned, how long it took, or where in the pipeline things went wrong.

**Langfuse traces** give you a structured record of every request through your system:
- The full input and output at each step
- Timing for every operation
- Nested structure showing how calls relate to each other
- Cost and token usage

A **trace** represents one end-to-end request (e.g., a user asking a question). Within it, **observations** represent individual steps — an LLM call, a retrieval step, a tool execution.

```
Trace: "answer user question"
├── Span: "retrieve context"       ← retrieval step
└── Generation: "llm call"         ← LLM call (tracks model, tokens, cost)
```

The simplest way to create traces in Langfuse is the `@observe` decorator — wrap a function and Langfuse automatically captures its name, inputs, outputs, and timing.

---

## What You'll Build

Instrument `app/assistant.py` so that every question answered creates a trace in Langfuse with:
- A root span for the full `answer()` call
- A child span for the retrieval step
- A generation for the LLM call

### The app you're instrumenting

Open `app/assistant.py` and read through it before starting. Here's what each part does:

- **`SYSTEM_PROMPT`** — the instructions given to the model on every request, defining its persona and behaviour
- **`retrieve(question)` / `format_context(docs)`** — imported from `app/knowledge_base.py`. Open that file and have a quick look: it contains a list of DataStream documentation entries (each with a title, content, and tags), and a `retrieve()` function that scores each entry by counting how many words from the query appear in it, returning the top matches. `format_context()` then joins those matches into a single text block that gets inserted into the prompt. Find `retrieve()` at the top of `app/knowledge_base.py` — it's the function that starts with `def retrieve(query: str, top_k: int = 3)`
- **`answer(question, history)`** — the main function you'll be modifying; it retrieves context, builds the message list (system prompt + conversation history + user question + context), calls OpenAI, and returns the response string

The flow is: **user question → retrieve docs → build messages → call LLM → return answer**. That's exactly the structure your trace will reflect.

---

## Tasks

### Task 2.1 — Add the `@observe` decorator to `answer()`

Open `app/assistant.py`. Import and apply `@observe` to the `answer` function.

```python
from langfuse import observe

@observe()
def answer(question: str, history: list[dict] | None = None) -> str:
    ...
```

Run the app, ask a question, then check your Langfuse dashboard. You should see a trace appear.

```bash
python -m app.main
```

In Langfuse, go to **Tracing** — you'll land on the **observations table**, where every individual operation your app performs appears as its own row. This is Langfuse's primary view: each decorated function call is an observation you can query directly.

> **Set up a saved view (do this once now):** The observations table shows everything — LLM calls, retrieval steps, root spans, all mixed together. To keep the workshop tidy, filter the table to just your root `answer()` calls:
> 1. Open the filter sidebar and add: `name = "answer"`
> 2. Click **Save view** and name it `Workshop – answer calls`
>
> From here on, use this saved view to jump straight to your data with one click.

![Langfuse observations table](assets/langfuse-trace-ui.png)

Click on any row to open the detail view. You'll see:
- **Input** — the exact arguments passed to `answer()` (the question and history)
- **Output** — the string returned by `answer()`
- **Metadata** — timing, tags, and any other attributes attached to the observation

![Langfuse observation detail](assets/langfuse-trace-dialog.png)

> **What happened?** `@observe` automatically captured the function name, its arguments as input, and its return value as output. It also recorded the start and end time.

---

### Task 2.2 — Add a span for retrieval

The trace shows the full `answer()` call, but we want to see the retrieval step separately. Wrap the retrieval logic in its own `@observe`-decorated function.

```python
@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)
```

Then call `retrieve_context(question)` from inside `answer()` instead of calling `retrieve` and `format_context` directly.

Ask another question and check the trace. You should now see a **nested** span for retrieval inside the root trace.

![Langfuse trace with retrieve_context span](assets/langfuse-trace-retrieve.png)

Compared to the previous step, notice what's new: the left panel now shows a tree with two nodes — `answer` at the top and `retrieve_context` indented beneath it. Clicking `retrieve_context` shows its own Input (the question) and Output (the formatted docs text that was passed to the LLM). You can now see exactly what the retrieval step returned and how long it took, separately from the overall `answer` call.

> **Key concept**: When one `@observe`-decorated function calls another, Langfuse automatically creates a parent-child relationship between the spans.

---

### Task 2.3 — Track the LLM call as a generation

LLM calls are special — Langfuse has a dedicated type for them called a **generation** that tracks model name, token usage, and cost. Wrap the OpenAI call in an `@observe(as_type="generation")` decorated function.

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

Call `call_llm(messages)` from inside `answer()`.

Ask another question and open the trace. You'll now see all three nodes in the left panel: `answer` → `retrieve_context` and `call_llm` side by side beneath it.

![Langfuse trace with call_llm generation](assets/langfuse-trace-call-llm.png)

Click on `call_llm`. This is where things get interesting — the Input shows the **full messages array** that was sent to the model: the system prompt, the retrieved documentation context, and the user's question all assembled together. The Output shows exactly what the model returned. This is the most valuable view for debugging — if the model gave a bad answer, you can see precisely what it was working with.

> **Note**: The `@observe` decorator captures return values automatically. For generations, Langfuse also infers token counts when the full response object is returned. We'll improve this in Lab 3.

---

### Task 2.4 — Flush on exit

In a long-running server, Langfuse sends data in the background. In a short-lived script, you need to flush manually to ensure all events are sent before the process exits.

Add to `app/main.py`:

```python
from langfuse import get_client

# At the end of main(), after the loop:
get_client().flush()
```

---

## Checkpoint

Run the app and ask 2-3 questions. In your Langfuse dashboard:

- [ ] Each question creates a new trace
- [ ] Each trace has a nested retrieval span and an LLM generation
- [ ] The inputs and outputs are visible on each span
- [ ] The generation shows a model name

---

## Explore the UI

In your Langfuse project, go to **Traces**. Click into a trace and explore:
- The timeline view shows span durations
- Click a generation to see the full prompt and completion
- The "Input / Output" tab shows what was sent and received

---

## Solution

See [`solution/assistant.py`](./solution/assistant.py) for the instrumented assistant and [`solution/main.py`](./solution/main.py) for the updated entry point.
