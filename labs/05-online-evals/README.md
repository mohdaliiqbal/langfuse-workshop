# Lab 5: Online Evals

## Concept

Traces show you *what* your LLM did. Scores tell you *how well* it did.

Without evaluation, you're flying blind: you can't tell if a model upgrade improved quality, if a prompt change broke something, or which users are getting bad responses. **Scores** attach a quality signal to traces and observations, enabling data-driven decisions.

Langfuse supports three score collection methods:

| Method | When to use |
|--------|-------------|
| **SDK scores** | Programmatic evaluation — run after every request |
| **User feedback** | Capture thumbs up/down from end users |
| **Human annotation** | Manual review queues for spot-checking or labeling |

Scores can be:
- **Numeric** (0.0–1.0): continuous quality metrics
- **Boolean** (true/false): binary pass/fail
- **Categorical** (e.g., "good", "bad", "unsure"): labeled buckets

Once you have scores, you can filter traces by score, chart quality over time, and correlate scores with prompt versions, models, or users.

---

## What You'll Build

1. Add user feedback (thumbs up/down) as scores from the CLI
2. Write a programmatic evaluator that scores every response automatically
3. View score analytics in the Langfuse dashboard

---

## Tasks

### Task 4.1 — Capture user feedback as scores

After each response, ask the user for feedback and record it as a score on the trace.

First, you need the trace ID of the current trace. Inside an `@observe`-decorated function, get it via `get_client()`:

```python
from langfuse import get_client

def get_current_trace_id() -> str | None:
    langfuse = get_client()
    return langfuse.get_current_trace_id()
```

Update `app/main.py` to ask for feedback after each response and record it:

```python
from langfuse import get_client

# After printing the response:
feedback = Prompt.ask("[dim]Was this helpful?[/dim] [bold](y/n/skip)[/bold]", default="skip")

if feedback in ("y", "n"):
    langfuse = get_client()
    trace_id = answer_trace_id  # You'll need to return this from answer()

    langfuse.create_score(
        trace_id=trace_id,
        name="user-feedback",
        value=1 if feedback == "y" else 0,
        data_type="BOOLEAN",
        comment="User thumbs up/down from CLI",
    )
```

> **Tip**: To get the trace ID after calling `answer()`, use `langfuse.get_current_trace_id()` inside `answer()` and return it alongside the response, or call it right after.

---

### Task 4.2 — Write a programmatic evaluator

Programmatic evaluation runs automatically after every request. A common pattern is **LLM-as-a-judge**: use a fast/cheap model to score the quality of a response.

Create a new file `app/evaluator.py`:

```python
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()

EVALUATOR_PROMPT = """You are evaluating the quality of a customer support response.

Question: {question}
Response: {response}

Rate the response on a scale of 0.0 to 1.0 based on:
- Accuracy: Is the information correct?
- Helpfulness: Does it actually answer the question?
- Clarity: Is it easy to understand?

Respond with only a JSON object: {{"score": <float>, "reason": "<one sentence>"}}"""


def evaluate_response(trace_id: str, question: str, response: str) -> None:
    """Run LLM-as-a-judge evaluation and record the score."""
    langfuse = get_client()

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": EVALUATOR_PROMPT.format(question=question, response=response)
        }],
        response_format={"type": "json_object"},
        temperature=0,
    )

    import json
    evaluation = json.loads(result.choices[0].message.content)

    langfuse.create_score(
        trace_id=trace_id,
        name="llm-judge-quality",
        value=evaluation["score"],
        data_type="NUMERIC",
        comment=evaluation["reason"],
    )
```

Call `evaluate_response()` in `app/main.py` after each answer (in a background thread so it doesn't slow down the user experience):

```python
import threading
from app.evaluator import evaluate_response

# After getting the response:
threading.Thread(
    target=evaluate_response,
    args=(trace_id, question, response),
    daemon=True,
).start()
```

---

### Task 4.3 — View score analytics

In Langfuse:
1. Go to **Traces** and filter by `score name = "llm-judge-quality"`. See which traces scored low.
2. Go to **Scores** → **Analytics** to see score distributions over time.
3. Compare scores between different prompt versions (if you updated the prompt in Lab 4).

---

### Task 4.4 — Set up a no-code LLM-as-a-judge evaluator in the UI

Your code-based evaluator in Task 4.2 runs via your own infrastructure. Langfuse also has **built-in evaluators** — you configure them once in the UI and they run automatically on every matching trace, with no code changes needed.

**Prerequisites**: You need to connect an LLM to your Langfuse project first:
1. Go to **Settings** → **LLM Connections** → **Add new LLM connection**
2. Select **OpenAI**, enter your OpenAI API key, click **Save**

**Create the evaluator**:
1. Go to **Evaluation** → **Evaluators** → **+ Set up Evaluator**
2. Pick a managed evaluator — e.g. **Helpfulness** or **Hallucination**
3. Set the target to **Live Observations**, filter by `trace name = support-question`
4. Map variables: `input` → observation input, `output` → observation output
5. Set sampling to `100%` for the workshop, click **Save**

Run the app and ask a few questions. After a short delay, open a trace — alongside your code-based `llm-judge-quality` score, you'll see a new score from the Langfuse-hosted evaluator appear automatically.

> **Code vs UI evaluators**: Your Task 4.2 evaluator gives full control — custom prompts, any scoring logic, runs synchronously. The UI evaluator is zero-maintenance — Langfuse hosts and runs it, it auto-scales, and you can update the rubric without a deployment. In practice, teams use both: UI evaluators for standard quality dimensions, code evaluators for domain-specific checks.

---

## Checkpoint

Ask 5+ questions with mixed quality (simple questions, edge cases, questions the bot can't answer).

- [ ] User feedback (y/n) creates a `user-feedback` score on the trace
- [ ] Each trace automatically gets a `llm-judge-quality` score from your code evaluator
- [ ] Low-scoring traces have a comment explaining why
- [ ] Score analytics show in the Langfuse dashboard
- [ ] A Langfuse-hosted evaluator is running and attaching scores automatically

---

## Why This Matters

With scores, you can:
- **Catch regressions**: If a prompt change drops average quality from 0.85 to 0.70, you see it before users complain
- **Find failure modes**: Filter to traces with score < 0.5 and look for patterns
- **Measure improvements**: Compare quality scores before/after a model upgrade
- **Prioritize fixes**: Sort traces by score and fix the worst experiences first

---

## Solution

See [`solution/assistant.py`](./solution/assistant.py) for the updated assistant, [`solution/evaluator.py`](./solution/evaluator.py) for the LLM-as-a-judge evaluator, and [`solution/main.py`](./solution/main.py) for the updated entry point with feedback collection.

Next: **[Lab 6: Human Annotation](../06-human-annotation/README.md)**
