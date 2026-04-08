# Lab 5: Scoring & Evaluation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 5" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through adding two quality signals to their app: user feedback scores from the CLI, and automated LLM-as-a-judge evaluation running in the background.

---

## Step 1 — Return the trace ID from `answer()`

To attach scores to a trace, you need its ID. Update `answer()` in `app/assistant.py` to return a `(response, trace_id)` tuple:

```python
@observe()
def answer(question, history=None, session_id=None, user_id=None) -> tuple[str, str | None]:
    langfuse = get_client()
    with propagate_attributes(...):
        ...
        response = call_llm(messages, prompt=prompt_obj)
        trace_id = langfuse.get_current_trace_id()
    return response, trace_id
```

**Explain**: `get_current_trace_id()` returns the ID of the trace currently in scope. We capture it before the `propagate_attributes` context closes, then return it alongside the response so `main.py` can use it to attach scores.

---

## Step 2 — Create the LLM-as-a-judge evaluator

Create a new file `app/evaluator.py`:

```python
import json, os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()

JUDGE_PROMPT = """You are evaluating the quality of a customer support response.

Question: {question}
Response: {response}

Rate 0.0–1.0 on accuracy, helpfulness, and clarity.
Respond with JSON only: {{"score": <float>, "reason": "<one sentence>"}}"""

def evaluate_response(trace_id: str, question: str, response: str) -> None:
    langfuse = get_client()
    try:
        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(
                question=question, response=response
            )}],
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

**Explain**: This is LLM-as-a-judge — using a cheap/fast model to automatically score every response. We use `response_format={"type": "json_object"}` to get reliable structured output, and we catch exceptions so an evaluation failure never breaks the user experience.

---

## Step 3 — Add feedback and background evaluation to `main.py`

Update `app/main.py` to:
1. Unpack the `(response, trace_id)` tuple from `answer()`
2. Ask the user for feedback after each response
3. Record the feedback as a score
4. Kick off the LLM judge in a background thread

```python
import threading
from langfuse import get_client
from app.evaluator import evaluate_response

# In the loop, replace the answer() call:
response, trace_id = answer(question, history, session_id=session_id, user_id=user_id)

console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

# User feedback
feedback = Prompt.ask("[dim]Was this helpful?[/dim]", choices=["y", "n", "skip"], default="skip")
if feedback in ("y", "n") and trace_id:
    get_client().create_score(
        trace_id=trace_id,
        name="user-feedback",
        value=1 if feedback == "y" else 0,
        data_type="BOOLEAN",
        comment="User thumbs up/down from CLI",
    )

# Background LLM evaluation
if trace_id:
    threading.Thread(
        target=evaluate_response,
        args=(trace_id, question, response),
        daemon=True,
    ).start()
```

**Run**: Ask 5+ questions with a mix of good and edge-case inputs. Rate some positively and some negatively.

**Verify in Langfuse**:
1. Open a trace — you should see two scores attached: `user-feedback` and `llm-judge-quality`
2. Go to **Tracing** and filter by score name to find low-scoring traces
3. Go to **Scores** → **Analytics** to see score distributions

**Explain**: With scores you can move from "I think quality is good" to "average quality score is 0.82 this week, down from 0.91 last week after the prompt change." This is how teams catch regressions before users do.

---

## Completion check

- [ ] `answer()` returns `(response, trace_id)`
- [ ] `app/evaluator.py` exists and `evaluate_response()` works
- [ ] Each trace has a `user-feedback` score and a `llm-judge-quality` score
- [ ] Low-scoring traces have a comment explaining why

Once confirmed, tell the attendee they're ready for **Lab 6: Datasets & Experiments**.
