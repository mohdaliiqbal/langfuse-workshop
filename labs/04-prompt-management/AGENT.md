# Lab 4: Prompt Management — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 4" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through moving the hardcoded `SYSTEM_PROMPT` in `app/assistant.py` into Langfuse Prompt Management. This lab involves both UI steps and code changes.

---

## Step 1 — Create the prompt in Langfuse UI

Tell the attendee to do the following in their Langfuse project (you cannot do this for them):

1. Go to **Prompt Management** in the left sidebar
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

5. Click **Save** (creates version 1)
6. Click **Publish** and label it `production`

Ask the attendee to confirm when done before continuing.

**Explain**: `{{product_name}}` is a variable that gets filled in at runtime. Storing prompts in Langfuse means anyone — a PM, a content writer — can update the assistant's behaviour without touching code or triggering a deployment.

---

## Step 2 — Fetch the prompt in code

**Change**: In `app/assistant.py`, add a `get_system_prompt()` function and remove the hardcoded `SYSTEM_PROMPT` constant:

```python
from langfuse import observe, get_client, propagate_attributes

def get_system_prompt():
    langfuse = get_client()
    return langfuse.get_prompt("datastream-system-prompt", label="production")
```

Update `answer()` to fetch the prompt instead of using the hardcoded string:

```python
@observe()
def answer(question, history=None, session_id=None, user_id=None):
    with propagate_attributes(...):
        prompt_obj = get_system_prompt()
        system_prompt = prompt_obj.compile(product_name="DataStream")

        context = retrieve_context(question)
        messages = [{"role": "system", "content": system_prompt}]
        ...
        return call_llm(messages, prompt=prompt_obj)
```

Update `call_llm()` to accept and link the prompt object:

```python
@observe()
def call_llm(messages: list[dict], prompt=None) -> str:
    langfuse = get_client()
    response = client.chat.completions.create(...)
    langfuse.update_current_observation(prompt=prompt)
    return response.choices[0].message.content
```

**Run**: Ask a question.

**Verify in Langfuse**: Open the trace, click the generation inside `call_llm`. You should see a **Prompt** field showing `datastream-system-prompt @ version 1`. This links this generation to the exact prompt version that produced it.

**Explain**: `prompt.compile(product_name="DataStream")` fills in the `{{product_name}}` variable. The prompt object is passed through to `call_llm` so Langfuse can link the generation to the specific version — enabling you to filter traces by prompt version and measure quality per version.

---

## Step 3 — Update the prompt without touching code

Guide the attendee to:

1. Go to **Prompt Management** → `datastream-system-prompt`
2. Click **Edit** and add a new guideline, for example:
   ```
   - Always end your response with "Is there anything else I can help you with?"
   ```
3. Save as a new version and publish it to `production`

**Run**: Ask a question again without changing any code.

**Verify**: The assistant's response now ends with the new sign-off. In Langfuse, the new trace's generation shows `version 2` of the prompt.

**Explain**: The code didn't change — only the prompt in Langfuse did. This is the separation of concerns: engineers own the code, product teams own the prompt content.

---

## Completion check

- [ ] `get_prompt("datastream-system-prompt")` works without error
- [ ] Generations show a linked prompt version in the trace detail
- [ ] Editing the prompt in the UI changes the assistant's behaviour with no code change

Once confirmed, tell the attendee they're ready for **Lab 5: Evaluation**.
