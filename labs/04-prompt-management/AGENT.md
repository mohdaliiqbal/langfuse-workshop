# Lab 4: Prompts — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 4" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through moving the hardcoded `SYSTEM_PROMPT` in `app/assistant.py` into Langfuse Prompts. This lab involves both UI steps and code changes.

---

## Step 1 — Create the prompt in Langfuse UI

Tell the attendee to do the following in their Langfuse project (you cannot do this for them):

1. Go to **Prompts** in the left sidebar (the menu item is called "Prompts")
2. Click **New Prompt**
3. Set:
   - **Name**: `datastream-system-prompt`
   - **Type**: Text
4. Paste this content:

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

5. The **"Use the 'production' label"** checkbox is checked by default — leave it as is
6. Click **Create prompt** — this creates version 1 with the `production` label attached

Ask the attendee to confirm when done before continuing.

**Explain**: Labels are how the code knows which version to fetch. `get_prompt(..., label="production")` fetches whatever version currently has the `production` label. Without setting this label, the fetch will fail. The `{{product_name}}` placeholder is a variable filled in at runtime — so PMs can edit the prompt content without knowing about product names in code.

---

## Step 2 — Fetch, compile, and link the prompt in code

Make four changes to `app/assistant.py`:

**Change 1** — Add `get_client` to the existing langfuse import (already there from Lab 3):

```python
from langfuse import observe, get_client, propagate_attributes
```

**Change 2** — Add a `get_system_prompt()` function above `answer()`:

```python
def get_system_prompt():
    langfuse = get_client()
    return langfuse.get_prompt("datastream-system-prompt", label="production")
```

**Change 3** — Update `answer()` to fetch and compile the prompt, and pass the prompt object to `call_llm`:

```python
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
        tags=["workshop", "lab-4"],
        metadata={"app_version": "1.0.0"},
    ):
        prompt_obj = get_system_prompt()
        system_prompt = prompt_obj.compile(product_name="DataStream")

        context = retrieve_context(question)

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        return call_llm(messages, prompt=prompt_obj)
```

**Change 4** — Update `call_llm()` to accept the prompt and pass it as `langfuse_prompt=` to the API call:

```python
@observe()
def call_llm(messages: list[dict], prompt=None) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
        langfuse_prompt=prompt,  # links this generation to the prompt version
    )
    return response.choices[0].message.content
```

**Run**: Ask a question.

**Verify in Langfuse**: Open the trace, click the generation inside `call_llm`. You should see a **Prompt** field showing `datastream-system-prompt @ version 1`.

**Explain**: `prompt.compile(product_name="DataStream")` fills in the `{{product_name}}` variable. Passing `langfuse_prompt=prompt` to `client.chat.completions.create()` is how the `langfuse.openai` wrapper links the generation to the specific prompt version — enabling you to filter traces by version and measure quality per version.

---

## Step 3 — Update the prompt without touching code

Guide the attendee to:

1. Go to **Prompts** → `datastream-system-prompt`
2. Click **New version** and add a new guideline, for example:
   ```
   - Always end your response with "Is there anything else I can help you with?"
   ```
3. The `production` label carries over automatically. Click **Save** to create version 2.

**Run**: Ask a question again without changing any code.

**Verify**: The assistant's response now ends with the new sign-off. In Langfuse, the new trace's generation shows `version 2` of the prompt.

**Explain**: The code didn't change — only the prompt in Langfuse did. This is the separation of concerns: engineers own the code, product teams own the prompt content.

---

## Completion check

- [ ] `get_prompt("datastream-system-prompt")` works without error
- [ ] Generations show a linked prompt version in the trace detail
- [ ] Editing the prompt in the UI changes the assistant's behaviour with no code change

Once confirmed, tell the attendee they're ready for **Lab 5: Evaluation**.
