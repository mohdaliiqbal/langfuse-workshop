# Lab 3: Prompt Management

## Concept

The system prompt in `assistant.py` is hardcoded. Every time you want to tweak the tone, add a guideline, or fix a behaviour, you need to edit code, commit, and redeploy.

**Prompt management** decouples prompts from code. Prompts live in Langfuse where they can be:
- **Edited** by anyone (PMs, content writers, engineers) without touching code
- **Versioned** — every change creates a new version; you can roll back instantly
- **Labeled** — deploy different versions to `production` vs `staging`
- **Linked to traces** — see which prompt version produced each response

This is the difference between a prompt that lives in your codebase and one that lives in your product.

### How it works

```
Langfuse UI         →   Your Code
─────────────           ──────────────────────────────────────────
Create prompt       →   langfuse.get_prompt("system-prompt")
Add variables       →   prompt.compile(product_name="DataStream")
Label as production →   langfuse.get_prompt("system-prompt", label="production")
Edit & save v2      →   (code picks up new version automatically)
```

---

## What You'll Build

1. Create the system prompt in Langfuse UI
2. Fetch and use it in code instead of the hardcoded string
3. Add a template variable to make the prompt reusable
4. Update the prompt in the UI and see the change reflected without touching code

---

## Tasks

### Task 3.1 — Create the prompt in Langfuse

1. In your Langfuse project, go to **Prompt Management**.
2. Click **New Prompt**.
3. Name it: `datastream-system-prompt`
4. Set the type to **Text**.
5. Paste in this content:

```
You are a helpful customer support assistant for {{product_name}}, a real-time data pipeline platform.

Your role is to help users with questions about {{product_name}}'s features, pricing, troubleshooting, and best practices.

Guidelines:
- Be concise and direct. Answer the question asked.
- Use the provided documentation context when available.
- If the answer is not in the context, say so honestly rather than guessing.
- For technical issues, provide actionable steps.
- Maintain a friendly, professional tone.
```

6. In the **Labels** field, type `production` and press Enter to add it.
7. Click **Create prompt** — this creates version 1 with the `production` label attached.

> Notice the `{{product_name}}` placeholder — that's a **variable** you'll compile at runtime.

> **About labels**: Labels are how you signal which version is "live". The code calls `get_prompt(..., label="production")` which fetches whichever version currently has that label. Without a label, the fetch would fail. You can have multiple labels (`staging`, `production`, etc.) on different versions at the same time.

---

### Task 3.2 — Fetch the prompt in code

In `app/assistant.py`, replace the hardcoded `SYSTEM_PROMPT` string with a call to Langfuse:

```python
from langfuse import get_client

def get_system_prompt() -> str:
    langfuse = get_client()
    prompt = langfuse.get_prompt("datastream-system-prompt", label="production")
    return prompt.compile(product_name="DataStream")
```

Then in `answer()`, call `get_system_prompt()` instead of using `SYSTEM_PROMPT`:

```python
@observe()
def answer(question: str, ...) -> str:
    system_prompt = get_system_prompt()
    ...
    messages = [{"role": "system", "content": system_prompt}]
```

> **Performance note**: Langfuse caches prompts client-side, so `get_prompt()` is as fast as reading from memory after the first call. No network latency per request.

Run the app and ask a question:

```bash
python -m app.main
```

The assistant should respond exactly as before — the behaviour hasn't changed, only where the prompt comes from. In Langfuse, open the latest trace and click the `call_llm` generation. The Input should still show the compiled system prompt. Nothing looks different yet — that's the point. The next task is what makes this useful.

---

### Task 3.3 — Link the prompt to the trace

Langfuse can link a specific prompt version to the generation that used it. This lets you filter traces by prompt version in the UI.

When creating the generation, pass the prompt object:

```python
from langfuse import observe, get_client

@observe()  # plain span — langfuse.openai creates the generation inside it
def call_llm(messages: list[dict], prompt=None) -> str:
    langfuse = get_client()

    response = client.chat.completions.create(...)

    langfuse.update_current_observation(prompt=prompt)  # links to prompt version

    return response.choices[0].message.content
```

Update the call chain to pass the prompt object through:

```python
def get_system_prompt():
    langfuse = get_client()
    return langfuse.get_prompt("datastream-system-prompt", label="production")

@observe()
def answer(question: str, ...) -> str:
    prompt_obj = get_system_prompt()
    system_prompt = prompt_obj.compile(product_name="DataStream")
    ...
    return call_llm(messages, prompt=prompt_obj)
```

Run the app and ask a question:

```bash
python -m app.main
```

Open the trace in Langfuse and click the generation inside `call_llm`. You should now see a **Prompt** field showing `datastream-system-prompt @ version 1`. This is the link — every generation now records exactly which prompt version produced it.

This becomes powerful at scale: if quality drops, you can filter all traces by prompt version to pinpoint when it started.

---

### Task 3.4 — Update the prompt without touching code

1. Go back to Langfuse → **Prompt Management** → `datastream-system-prompt`.
2. Click **Edit** and add a new guideline, e.g.:
   ```
   - Always end your response with "Is there anything else I can help you with?"
   ```
3. Save — this creates version 2. Langfuse will ask you to confirm the labels for the new version; make sure `production` is applied.

Now run the app again — without changing any code, the assistant's behaviour has changed.

In Langfuse, look at your traces — you'll see some linked to version 1 and new ones linked to version 2.

---

## Checkpoint

- [ ] `get_prompt("datastream-system-prompt")` returns successfully
- [ ] The compiled system prompt contains "DataStream" (not `{{product_name}}`)
- [ ] Traces show a linked prompt version in the generation detail
- [ ] Updating the prompt in the UI changes assistant behaviour without a code change

---

## Why This Matters

Without prompt management, a PM wanting to adjust the chatbot's tone needs to file a ticket, wait for engineering, get a code review, and trigger a deployment. With prompt management, they open Langfuse, edit the prompt, and it's live in seconds.

The version history also gives you a safety net: if a prompt change causes quality to drop, you roll back in one click.

---

## Solution

See [`solution/assistant.py`](./solution/assistant.py) for the instrumented assistant and [`solution/main.py`](./solution/main.py) for the updated entry point.
