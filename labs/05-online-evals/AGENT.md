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

You are teaching Lab 5 as a live instructor. Online evals are how you **catch interesting signals from production traffic** — moments worth a human's attention — and then **track those signals over time** so you can see whether quality is moving in the right direction.

We'll add three signals in this lab:

1. **User feedback** (👍 / 👎) — the highest-signal input you can get, straight from the people the system is supposed to help.
2. **A no-code UI evaluator** that flags **out-of-scope** requests — questions your assistant isn't designed to answer.
3. **A programmatic LLM-as-a-judge** that runs the same out-of-scope check in code — useful when you want a custom rubric, deterministic prompts, or to call your own services.

Together these give you a way to see, for every production trace: *did the user like it, was it on-topic, did the judge agree with the user?* Disagreement between the user thumb and the automated judge is itself a powerful signal — the traces a human reviewer should look at first.

---

## Step 1 — Return the trace ID from `answer()` (so scores can be attached)

**Announce**: To attach a score to a specific observation, we need its trace ID and observation ID. We'll update `answer()` to return both alongside the response.

**Make the change** — update `app/assistant.py`:

First, ensure `get_client` is in the import:
```python
# app/assistant.py — update import:
from langfuse import observe, get_client, propagate_attributes
```

Then replace the entire `answer()` function:
```python
# app/assistant.py — replace answer():
@observe(name="support-question")
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> tuple[str, str | None, str | None]:
    langfuse = get_client()

    with propagate_attributes(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
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
        observation_id = langfuse.get_current_observation_id()

    return response, trace_id, observation_id
```

**Explain**: `get_current_trace_id()` and `get_current_observation_id()` both read from the active OpenTelemetry context — they must be called before the `propagate_attributes` block closes. Passing `observation_id` to `create_score` pins the score to the exact `support-question` span in the trace, so it appears directly on that observation in the Langfuse UI rather than just at the trace level.

---

## Step 2 — Verify user feedback buttons work

**Announce**: No code changes here — `app/web.py` already has 👍/👎 buttons wired up. Now that `answer()` returns `trace_id` and `observation_id`, they're live.

**Explain**: User feedback is the highest-signal evaluation you can capture — it comes from humans who had a real need and can judge whether it was met. Automated judges score format and coherence; only the user knows if the answer actually solved their problem. The buttons call `get_client().create_score()` with `name="user-feedback"`, value `1` (👍) or `0` (👎), and `observation_id` so the score appears directly on the observation.

**Browser prompt**: "Ask a question in the browser and click 👍 or 👎 on the response."

**Langfuse check**: "Open the observation in Langfuse — you should see a `user-feedback` score attached to it in the Scores tab."

📸 **See Task 5.1 in the lab README** for a screenshot of the score on the trace and the score filter.

**✋ Check in**: "Can you see the `user-feedback` score on the observation? What value does it show?"

---

## Step 3 — Set up a no-code UI evaluator for out-of-scope detection

**Announce**: Our assistant is built for DataStream support. Users asking about competitors, unrelated tech, or personal advice are *out of scope* — a clear production signal worth catching. Langfuse can flag these automatically with a custom LLM-as-a-judge evaluator configured entirely in the UI.

**Direct the attendee** through these UI steps:

**First, connect an LLM (if not done already):**
1. Go to **Settings** → **LLM Connections** → **Add new LLM connection**
2. Select **OpenAI**, enter their OpenAI API key → **Save**

**Create a custom out-of-scope evaluator:**
1. Go to **Evaluation** → **LLM-as-a-Judge** → **Create Evaluator**
2. Choose **Custom** (create from scratch). Name it `out-of-scope-check`.
3. Paste this rubric as the evaluator prompt:
   ```
   You are checking whether a user question is in-scope for a customer
   support assistant for DataStream — a real-time data pipeline platform.

   In-scope: questions about DataStream features, pricing, connectors,
   troubleshooting, security, billing, account setup.

   Out-of-scope examples:
   - Questions about competitors' products
   - Generic coding help unrelated to DataStream
   - Personal / off-topic chat
   - Requests for opinions on unrelated topics

   Question: {{input}}
   Response: {{output}}

   Reply with JSON only: {"in_scope": <true/false>, "reasoning": "<one sentence>"}.
   Score 1 if in_scope is true, 0 if false.
   ```
4. Set **Run on** to **Observations**, add filters:
   - `trace name = support-question`
   - `environment = any of [development]` — use **any of**, not "none of"
5. Map variables:
   - `input` → observation input, JsonPath: `$[1]["content"]` (the user question)
   - `output` → observation output, JsonPath: `$["content"]` — **the double-quotes around `content` are required**
6. Set sampling to `100%` → **Execute**

📸 **See Task 5.2 in the lab README** for screenshots of each configuration step.

**Explain**: This is the *first* production signal you usually want — knowing whether your assistant is even being asked the right questions. If 20% of your traffic is out-of-scope, that's a routing problem, not an LLM-quality problem, and no prompt tweak will fix it. Running this in Langfuse's hosted evaluator means zero infra, zero latency impact, and the rubric is editable in the UI without a deploy.

**Browser prompt**: "Go back to http://localhost:7860 and ask a mix of questions — some real DataStream questions, and some clearly off-topic (e.g. *'What's the best pasta recipe?'* or *'How do I set up Snowflake without DataStream?'*)."

**Langfuse check**: "After 30–60 seconds, open one of the off-topic observations and click the **Scores** tab — you should see `out-of-scope-check` with value `0` and the judge's reasoning in the comment."

**✋ Check in**: "Do you see the `out-of-scope-check` score appearing on observations? Did the off-topic ones score `0`?"

---

## Step 4 — Programmatic out-of-scope evaluator (LLM-as-a-judge in code)

**Announce**: The UI evaluator covers most cases. For full control — custom prompts, custom scoring, calling your own services — you write the evaluator in code. We'll wire the same out-of-scope check programmatically, with the prompt managed in Langfuse so a non-engineer can still tune it.

**Direct the attendee** to create the evaluator prompt in Langfuse:
1. Go to **Prompts** → **New Prompt**
2. Name: `out-of-scope-evaluator-prompt`, Type: **Text**
3. Paste:
   ```
   You are checking whether a user question is in-scope for a customer
   support assistant for DataStream — a real-time data pipeline platform.

   In-scope: questions about DataStream features, pricing, connectors,
   troubleshooting, security, billing, account setup.

   Out-of-scope examples:
   - Questions about competitors' products
   - Generic coding help unrelated to DataStream
   - Personal / off-topic chat
   - Requests for opinions on unrelated topics

   Question: {{question}}
   Response: {{response}}

   Respond with only a JSON object:
   {"in_scope": <true/false>, "reason": "<one sentence>"}
   ```
4. Set label `production` → **Create prompt**

📸 **See Task 5.3 in the lab README** for the full evaluator setup walkthrough.

**✋ Check in**: "Have you created `out-of-scope-evaluator-prompt` with the `production` label?"

Wait for confirmation, then make the code change.

**Make the change** — create `app/evaluator.py`:

```python
# app/evaluator.py (create this new file):
import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()


def evaluate_response(trace_id: str, observation_id: str | None, question: str, response: str) -> None:
    """Score whether the question was in-scope and record the result on the trace."""
    langfuse = get_client()

    try:
        prompt_obj = langfuse.get_prompt("out-of-scope-evaluator-prompt", label="production")
        prompt_text = prompt_obj.compile(question=question, response=response)

        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0,
        )

        evaluation = json.loads(result.choices[0].message.content)
        in_scope = bool(evaluation.get("in_scope", True))

        langfuse.create_score(
            trace_id=trace_id,
            observation_id=observation_id,
            name="in-scope",
            value=1 if in_scope else 0,
            data_type="BOOLEAN",
            comment=evaluation.get("reason", ""),
        )
    except Exception as e:
        print(f"Evaluation failed: {e}")
```

Then wire it into `app/web.py` — add inside `_submit()`, after `trace_ids = state["trace_ids"] + [trace_id]`:

```python
# app/web.py — add inside _submit(), after trace_ids = ...:
if trace_id:
    import threading
    from app.evaluator import evaluate_response
    threading.Thread(target=evaluate_response, args=(trace_id, observation_id, message, response), daemon=True).start()
```

**Explain**: The code evaluator runs in a background thread so the user gets their response immediately — no added latency. Keeping the prompt in Langfuse means a domain expert can tighten the rubric without a code review. The `try/except` guarantees a broken judge never crashes the web server. The score is BOOLEAN (`1` = in-scope, `0` = out-of-scope), matching the user-feedback shape so the two are directly comparable.

**Browser prompt**: "Ask 5+ questions in the browser with a mix of on-topic and off-topic inputs."

**Langfuse check**: "Open an observation — you should see three scores on it: `user-feedback`, the UI evaluator's `out-of-scope-check`, and the code evaluator's `in-scope`."

**✋ Check in**: "Do all three scores appear on observations? Click any score to read its comment — does the reasoning match what you'd expect?"

---

## Step 5 — Find disagreement and track quality over time

**Announce**: Three independent signals on every trace is the foundation. Now the interesting question: **where do they disagree?** A user who clicked 👍 but the judge flagged out-of-scope is a trace worth a human's attention.

**Direct the attendee** in Langfuse:

1. Go to **Observations** → open filters → add two filters:
   - Numeric Scores: `user-feedback` = `1`
   - Numeric Scores: `in-scope` = `0`
2. The remaining rows are traces where the user was happy but the judge flagged the question as off-topic — interesting disagreements to review.

📸 **See Task 5.4 in the lab README** for screenshots of the disagreement filter and the Scores → Analytics view.

**Explain**: That's the first half of online evals — *catching interesting signals from production.* The second half is *tracking quality over time*: go to **Scores → Analytics** to see how the `out-of-scope-check` and `user-feedback` distributions move week over week. If your team has a clear definition of "good" — e.g. "≥90% of traffic is in-scope, ≥80% thumbs-up" — these charts are where you watch it move. Without that opinion of what quality means, the charts are just numbers; with it, they're a dashboard.

**✋ Check in**: "Do you see any traces in the disagreement view? Can you find the Scores → Analytics chart for `in-scope` over time?"

---

## Completion check

- [ ] `answer()` returns `(response, trace_id, observation_id)`
- [ ] Clicking 👍/👎 in the browser creates a `user-feedback` score on the observation
- [ ] A UI evaluator (`out-of-scope-check`) is active and attaching scores automatically
- [ ] `app/evaluator.py` exists and `in-scope` scores appear on observations
- [ ] `out-of-scope-evaluator-prompt` exists in Langfuse with the `production` label
- [ ] You can find traces where user-feedback and the judge disagree

"You now have three independent quality signals flowing into every trace, with a clear path from *catching* problems to *tracking* whether they're getting better. Ready for Lab 6: Human Annotation?"
