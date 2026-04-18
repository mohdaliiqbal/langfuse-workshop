# Lab 5: Online Evals — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 5" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through adding three quality signals to their app: user feedback scores from the CLI, a no-code Langfuse-hosted evaluator, and a programmatic LLM-as-a-judge evaluator using a prompt managed in Langfuse.

---

## Step 1 — Return the trace ID from `answer()`

To attach scores to a trace, you need its ID. Update `app/assistant.py`:

**Add `get_client` to the existing import:**

```python
from langfuse import observe, get_client, propagate_attributes
```

**Replace the entire `answer()` function** with this version that returns `(response, trace_id)`:

```python
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

**Explain**: `get_current_trace_id()` returns the ID of the observation currently in scope. We capture it before the `propagate_attributes` context closes, then return it alongside the response so `main.py` can use it to attach scores. Without an ID there's no way to connect a score back to the specific request that produced it — every score would be a floating data point with no context.

---

## Step 2 — Add user feedback to `main.py`

Replace the full `main()` function in `app/main.py` with this version that unpacks the tuple, asks for feedback, and records it as a score:

```python
from app.evaluator import evaluate_response
import threading

def main():
    console.print(Panel.fit(
        "[bold cyan]DataStream Support Assistant[/bold cyan]\n"
        "[dim]Type your question or 'quit' to exit[/dim]",
        border_style="cyan"
    ))

    session_id = str(uuid.uuid4())
    user_id = "workshop-user-1"
    history = []
    langfuse = get_client()              # for recording scores

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

        # Ask for feedback and record it as a score on the trace
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

        # Run LLM-as-a-judge in the background so it doesn't slow down the user
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

Also ensure the import line at the top includes `get_client`:

```python
from langfuse import get_client
```

**Run**: Ask a question and give feedback (y/n).

**Verify in Langfuse**: Open the trace — you should see a `user-feedback` score attached to it.

**Explain**: User feedback is the highest-signal evaluation you can capture — it comes from humans who had a real need and can judge whether it was met. Automated judges can score format and coherence; only the user knows if the answer actually solved their problem. Even a small fraction of rated responses reveals patterns: which topics confuse users, which phrasings get thumbs-down, which edge cases the model handles poorly.

---

## Step 3 — Set up a no-code UI evaluator

Tell the attendee to do the following in Langfuse (no code needed):

**First, connect an LLM:**
1. Go to **Settings** → **LLM Connections** → **Add new LLM connection**
2. Select **OpenAI**, enter their OpenAI API key, click **Save**

**Create the evaluator:**
1. Go to **Evaluation** → **LLM-as-a-Judge** → **Create Evaluator**
2. Pick a managed evaluator — e.g. **Helpfulness** or **Hallucination**
3. Set target to **Live Observations**, add filters:
   - `trace name = support-question`
   - `environment = any of [development]` (use **any of**, not "none of")
4. Map variables:
   - `input` → observation input, JsonPath: `$[1]["content"]` (user question)
   - `output` → observation output, JsonPath: `$["content"]` — the double-quotes are required
5. Set sampling to `100%`, click **Execute**

**Run**: Ask a few questions.

**Verify**: After a short delay (evaluators run async), open a trace — you should see a new score from the Langfuse evaluator appearing automatically.

**Explain**: The UI evaluator runs asynchronously — after your app responds to the user, Langfuse picks up the observation and scores it in the background. That means zero latency impact for the user and no infra to manage. The rubric (which managed evaluator you chose, what threshold counts as "helpful") can be changed in the UI without touching code or redeploying anything — useful when a PM wants to tighten the definition of "hallucination" mid-sprint.

---

## Step 4 — Create a programmatic evaluator

The UI evaluator covers standard dimensions. For domain-specific rubrics you write the evaluator in code. Since Lab 4 we manage prompts in Langfuse — apply the same pattern here so the rubric can be tuned without redeploying code.

**First, create the evaluator prompt in Langfuse:**
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
4. Set label `production` and click **Create prompt**

**Then, create `app/evaluator.py`:**

```python
import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()


def evaluate_response(trace_id: str, question: str, response: str) -> None:
    """Run LLM-as-a-judge evaluation and record the score."""
    langfuse = get_client()

    try:
        # Fetch the prompt from Langfuse — same pattern as Lab 4
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

**Run**: Ask 5+ questions. The evaluator runs in the background thread wired up in Step 2.

**Verify in Langfuse**:
1. Open a trace — you should see both `user-feedback` and `llm-judge-quality` scores
2. Filter by score name to find low-scoring traces and read the judge's reasoning
3. Go to **Scores** → **Analytics** to see score distributions

**Explain**: Keeping the evaluator prompt in Langfuse means your scoring rubric isn't locked in a deployment cycle. A PM or domain expert can tighten the definition of "correct" — without a code review or git commit — by editing `quality-evaluator-prompt` and promoting the new version to `production`. The code picks it up on the next call. The `try/except` wrapper ensures an evaluation failure is silent from the user's perspective: a broken judge is annoying, but it should never interrupt a real support conversation.

---

## Completion check

- [ ] `answer()` returns `(response, trace_id)`
- [ ] User feedback (y/n) creates a `user-feedback` score on the trace
- [ ] A Langfuse-hosted evaluator is active and attaching scores automatically
- [ ] `app/evaluator.py` exists and `llm-judge-quality` scores appear on traces
- [ ] `quality-evaluator-prompt` exists in Langfuse with the `production` label

Once confirmed, tell the attendee they're ready for **Lab 6: Human Annotation**.
