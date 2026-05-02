# Lab 5: Online Evals — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 5" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "Please make sure you have a terminal open in the workshop directory, and open the lab README for screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/05-online-evals/README.md**
>
> This lab has both UI steps and code changes — I'll tell you which is which at each step."

---

## Your task

You are teaching Lab 5 as a live instructor. Add three quality signals one at a time: user feedback scores, a no-code Langfuse-hosted evaluator, and a programmatic LLM-as-a-judge. Wait for the attendee to verify each one before continuing.

---

## Step 1 — Return the trace ID from `answer()`

**Announce**: To attach a score to a trace, you need its ID. We'll update `answer()` to return it alongside the response.

**Make the change** — update `app/assistant.py`:

First, ensure `get_client` is in the import:
```python
# app/assistant.py — update import:
from langfuse import observe, get_client, propagate_attributes
```

Then replace the entire `answer()` function:
```python
# app/assistant.py — replace answer():
@observe()
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> tuple[str, str | None]:
    langfuse = get_client()

    with propagate_attributes(
        trace_name="support-question",
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
        tags=["workshop"],
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

        response = call_llm(messages, prompt=prompt_obj)
        trace_id = langfuse.get_current_trace_id()

    return response, trace_id
```

**Explain**: `get_current_trace_id()` returns the ID of the observation currently in scope. We capture it before the `propagate_attributes` context closes. Without an ID there's no way to connect a score back to the specific request that produced it. The return type changes from `str` to `tuple[str, str | None]` — callers now unpack `response, trace_id = answer(...)`.

---

## Step 2 — Add user feedback to `main.py`

**Announce**: Now we wire up the feedback prompt and score recording in the chat loop.

**Make the change** — update `app/main.py`. Ensure `get_client` is imported, add `evaluate_response` and `threading` imports, and replace the `main()` function:

```python
# app/main.py — add these imports at the top:
from app.evaluator import evaluate_response
import threading

# app/main.py — replace main():
def main():
    console.print(Panel.fit(
        "[bold cyan]DataStream Support Assistant[/bold cyan]\n"
        "[dim]Type your question or 'quit' to exit[/dim]",
        border_style="cyan"
    ))

    session_id = str(uuid.uuid4())
    user_id = "workshop-user-1"
    history = []
    langfuse = get_client()

    while True:
        question = Prompt.ask("\n[bold green]You[/bold green]")

        if question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        if not question.strip():
            continue

        with console.status("[dim]Thinking...[/dim]"):
            response, trace_id = answer(question, history, session_id=session_id, user_id=user_id)

        console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        feedback = Prompt.ask(
            "[dim]Was this helpful?[/dim]",
            choices=["y", "n", "skip"],
            default="skip",
        )

        if feedback in ("y", "n") and trace_id:
            langfuse.create_score(
                trace_id=trace_id,
                name="user-feedback",
                value=1 if feedback == "y" else 0,
                data_type="BOOLEAN",
                comment="User thumbs up/down from CLI",
            )

        if trace_id:
            threading.Thread(
                target=evaluate_response,
                args=(trace_id, question, response),
                daemon=True,
            ).start()

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})

    langfuse.flush()
```

Note: `app/evaluator.py` doesn't exist yet — the import will fail until Step 4. If the attendee wants to test Step 2 in isolation first, temporarily comment out that import line.

**Explain**: User feedback is the highest-signal evaluation you can capture — it comes from humans who had a real need and can judge whether it was met. Automated judges score format and coherence; only the user knows if the answer actually solved their problem.

**Terminal prompt**: "Run the app, ask a question, and give it a `y` or `n` rating."

**Langfuse check**: "Open the observation in Langfuse — you should see a `user-feedback` score attached to it in the Scores tab."

📸 **See Task 5.1 in the lab README** for a screenshot of the score on the trace and the score filter.

**✋ Check in**: "Can you see the `user-feedback` score on the observation? What value does it show?"

---

## Step 3 — Set up a no-code UI evaluator

**Announce**: Langfuse can evaluate every observation automatically — no code. We'll configure a managed evaluator that runs in the background after each response.

**Direct the attendee** through these UI steps:

**First, connect an LLM:**
1. Go to **Settings** → **LLM Connections** → **Add new LLM connection**
2. Select **OpenAI**, enter their OpenAI API key → **Save**

**Create the evaluator:**
1. Go to **Evaluation** → **LLM-as-a-Judge** → **Create Evaluator**
2. Pick a managed evaluator — e.g. **Helpfulness**
3. Set target to **Live Observations**, add filters:
   - `trace name = support-question`
   - `environment = any of [development]` — use **any of**, not "none of"
4. Map variables:
   - `input` → observation input, JsonPath: `$[1]["content"]` (the user question)
   - `output` → observation output, JsonPath: `$["content"]` — **the double-quotes around `content` are required**
5. Set sampling to `100%` → **Execute**

📸 **See Task 5.2 in the lab README** for screenshots of each configuration step (LLM connections, evaluator creation, variable mapping).

**Explain**: The UI evaluator runs asynchronously — after your app responds, Langfuse picks up the observation and scores it in the background. Zero latency impact for the user, zero infra to manage. The rubric can be changed in the UI without touching code — useful when a PM wants to tighten the definition of "helpful" mid-sprint.

**Terminal prompt**: "Run the app and ask a few questions."

**Langfuse check**: "After a short delay (30–60 seconds), open an observation. You should see a score from the Langfuse-hosted evaluator."

**✋ Check in**: "Do you see the evaluator score appearing on observations? What name does it use?"

---

## Step 4 — Create a programmatic evaluator

**Announce**: The UI evaluator covers standard dimensions. For custom scoring logic you write the evaluator in code. First create the prompt in Langfuse — consistent with Lab 4.

**Direct the attendee** to create the evaluator prompt in Langfuse UI:
1. Go to **Prompts** → **New Prompt**
2. Name: `quality-evaluator-prompt`, Type: **Text**
3. Paste:
   ```
   You are evaluating the quality of a customer support response.

   Question: {{question}}
   Response: {{response}}

   Rate the response on a scale of 0.0 to 1.0 based on:
   - Accuracy: Is the information correct?
   - Helpfulness: Does it actually answer the question?
   - Clarity: Is it easy to understand?

   Respond with only a JSON object: {"score": <float>, "reason": "<one sentence>"}
   ```
4. Set label `production` → **Create prompt**

📸 **See Task 5.3 in the lab README** for the full evaluator setup walkthrough.

**✋ Check in**: "Have you created `quality-evaluator-prompt` with the `production` label?"

Wait for confirmation, then make the code change.

**Make the change** — create `app/evaluator.py`:

```python
# app/evaluator.py (create this new file):
import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()


def evaluate_response(trace_id: str, question: str, response: str) -> None:
    """Run LLM-as-a-judge evaluation and record the score."""
    langfuse = get_client()

    try:
        prompt_obj = langfuse.get_prompt("quality-evaluator-prompt", label="production")
        prompt_text = prompt_obj.compile(question=question, response=response)

        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0,
        )

        evaluation = json.loads(result.choices[0].message.content)

        langfuse.create_score(
            trace_id=trace_id,
            name="llm-judge-quality",
            value=float(evaluation["score"]),
            data_type="NUMERIC",
            comment=evaluation.get("reason", ""),
        )
    except Exception as e:
        print(f"Evaluation failed: {e}")
```

**Explain**: Keeping the evaluator prompt in Langfuse means the scoring rubric isn't locked in a deployment cycle — a domain expert can tighten the definition of "correct" without a code review or git commit. The `try/except` ensures a broken judge never interrupts a real support conversation.

**Terminal prompt**: "Run the app and ask 5+ questions with a mix of good and edge-case inputs."

**Langfuse check**: "Open an observation — you should see three scores: `user-feedback`, the Langfuse-hosted evaluator score, and `llm-judge-quality`. Click the `llm-judge-quality` score to read the judge's reasoning in the comment."

**✋ Check in**: "Do all three scores appear on observations? Can you find a low `llm-judge-quality` score — what reason did the judge give?"

---

## Completion check

- [ ] `answer()` returns `(response, trace_id)`
- [ ] User feedback (y/n) creates a `user-feedback` score on the observation
- [ ] A Langfuse-hosted evaluator is active and attaching scores automatically
- [ ] `app/evaluator.py` exists and `llm-judge-quality` scores appear on observations
- [ ] `quality-evaluator-prompt` exists in Langfuse with the `production` label

"You now have three independent quality signals flowing into every trace. Ready for Lab 6: Human Annotation?"
