# Lab 4: Prompts — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 4" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "Please make sure you have a terminal open in the workshop directory, and open the lab README in your browser:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/04-prompt-management/README.md**
>
> This lab mixes UI steps (you do in Langfuse) and code changes (I'll make). I'll tell you which to do at each step."

---

## Your task

You are teaching Lab 4 as a live instructor. This lab combines UI steps and code changes. Make one change at a time, explain why, then wait for the attendee to confirm.

The goal: move the hardcoded `SYSTEM_PROMPT` into Langfuse Prompts, so it can be edited by anyone — without a code change or deployment.

---

## Step 1 — Create the prompt in Langfuse

**Announce**: Before writing any code, the prompt needs to exist in Langfuse. This is a UI-only step.

**Direct the attendee** to do the following in their Langfuse project:

1. Go to **Prompts** → click **New Prompt** (or **Create Prompt**)
2. Name it: `datastream-system-prompt`, Type: **Text**
3. Paste this content:

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

4. Leave **"Use the 'production' label"** checked (default) → click **Create prompt**

**Explain**: `{{product_name}}` is a variable — filled in at runtime by your code. This means a PM can change the product name or add a new guideline without touching the codebase. Labels are how the code knows which version to fetch: `get_prompt(..., label="production")` always returns whichever version currently carries the `production` label.

📸 **See Task 4.1 in the lab README** for screenshots of the prompt creation form.

**✋ Check in**: "Have you created `datastream-system-prompt` in Langfuse? Can you see it in the Prompts list with the `production` label?"

Wait for confirmation before making any code changes.

---

## Step 2 — Fetch, compile, and link the prompt in code

**Announce**: Now we wire the code to fetch the prompt from Langfuse instead of using the hardcoded string.

**Make these four changes** to `app/assistant.py`:

**1. Update the import** (add `get_client`):
```python
from langfuse import observe, get_client, propagate_attributes
```

**2. Add a `get_system_prompt()` helper** above `answer()`:
```python
def get_system_prompt():
    langfuse = get_client()
    return langfuse.get_prompt("datastream-system-prompt", label="production")
```

**3. Update `answer()`** to fetch, compile, and pass the prompt object:
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

**4. Update `call_llm()`** to accept and pass through the prompt object:
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

**Explain**: `prompt.compile(product_name="DataStream")` fills in the `{{product_name}}` variable. Passing `langfuse_prompt=prompt` to the OpenAI call is how the wrapper links the generation to the specific prompt version — enabling you to filter all traces by prompt version. This is how you answer: "did quality change after I updated the prompt last Tuesday?"

**Terminal prompt**: "Run the app and ask a question."

**Langfuse check**: "Open the trace and click the generation inside `call_llm`. You should see a **Prompt** field showing `datastream-system-prompt @ version 1`."

📸 **See Task 4.2 in the lab README** for a screenshot of the linked prompt version on the generation.

**✋ Check in**: "Do you see the linked prompt version on the generation? What version number does it show?"

---

## Step 3 — Test prompt changes in the Playground

**Announce**: Before committing any change to `production`, test it in the Langfuse Playground — no code deployment needed.

**Direct the attendee** to:

1. Go to **Prompts** → `datastream-system-prompt` → click **Playground**
2. Fill in `product_name = DataStream` in the variables panel
3. Add a user message: *"What connectors do you support?"* → click **Run**
4. Edit the prompt text inline and run again to compare

Also show: open any recent generation → click **Open in Playground** — this loads the exact prompt and messages from that response for immediate reproduction.

**Explain**: The Playground is your iteration environment. You prototype a change, test it on real inputs from production, and only promote it when you're confident. Changes here don't affect the running app until you explicitly save and label them — engineers own the deployment pipeline, everyone else owns the prompt content.

📸 **See Task 4.3 in the lab README** for a screenshot of the Playground in use.

**✋ Check in**: "Have you run a test in the Playground? Did the response change when you edited the prompt text?"

---

## Step 4 — Update the prompt without touching code

**Announce**: This is the payoff — edit the prompt in Langfuse and watch the app's behaviour change with zero code changes.

**Direct the attendee** to:

1. Go to **Prompts** → `datastream-system-prompt` → **New version**
2. Add a guideline, for example:
   ```
   - Always end your response with "Is there anything else I can help you with?"
   ```
3. Check **"Set the production label"** (not checked by default) → **Save new prompt version**

**Terminal prompt**: "Run the app — without changing any code — and ask a question."

**Langfuse check**: "Open the latest trace's generation. The **Prompt** field should now show `version 2`. Does the assistant's response end with the new sign-off?"

📸 **See Task 4.4 in the lab README** for screenshots of saving a new version and the generation showing version 2.

**✋ Check in**: "Did the response change without a code change? What version does the generation show?"

**Explain**: The code is unchanged. The only thing that changed was a field in the Langfuse UI — live immediately. Your earlier traces remain linked to version 1 — the full version history is preserved. If the new prompt causes a quality regression you can promote version 1 back to `production` in one click.

---

## Completion check

- [ ] `get_prompt("datastream-system-prompt")` works without error
- [ ] Generations show a linked prompt version in the trace detail
- [ ] Editing the prompt in the UI changes the assistant's behaviour without a code change

"You've decoupled prompts from code. Ready for Lab 5: Online Evals?"
