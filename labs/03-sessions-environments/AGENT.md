# Lab 3: Sessions & Environments — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 3" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "Please make sure you have a terminal window open in the workshop directory, and open the lab README in your browser for screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/03-sessions-environments/README.md**
>
> I'll reference specific tasks in the README at each verification step."

---

## Your task

You are teaching Lab 3 as a live instructor. Lab 2 already gave us rich, named, costed traces. Lab 3 attaches two pieces of context that you can't derive from the trace tree alone: **who** the request belongs to (session + user) and **which environment** it came from. Two short steps, then we're done.

---

## Step 1 — Add session and user tracking

**Announce**: Right now each question creates an isolated trace. Sessions group all turns of a single conversation together; user IDs link traces to a specific user. Both are essential when a support team needs to replay a customer interaction or filter to one user who reported a bug.

**Make the change** — in `app/assistant.py`, add the imports and update `answer()` to accept `session_id` + `user_id` and propagate them:

```python
# app/assistant.py — add to imports at the top:
import uuid
from langfuse import observe, propagate_attributes

# Replace answer() with:
@observe(name="support-question")
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> str:
    with propagate_attributes(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
    ):
        context = retrieve_context(question)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        return call_llm(messages)
```

> **Web app**: `app/web.py` already passes `session_id` and `user_id` automatically once those parameters exist in `answer()`'s signature — no changes to `web.py` needed. Each browser tab gets its own session ID; the user ID is hard-coded to `workshop-user-1`.

**Explain**: Without sessions, a 10-turn conversation appears as 10 unrelated traces. With them you can open **Sessions** in Langfuse and replay the entire conversation in order — exactly what a support team needs when a customer calls to complain. User IDs let you filter to one user's full history when investigating a complaint. `propagate_attributes` attaches both to the current trace and all child observations automatically.

**Terminal prompt**: "Save the file — Gradio reloads automatically. Ask 3+ questions in the browser."

**Langfuse check**: "In Langfuse, go to **Sessions** — you should see a session containing all questions from that run. Then go to **Users** — `workshop-user-1` should appear with a trace count."

📸 **See Task 3.1 in the lab README** for screenshots of the Sessions and Users views.

> **If the Sessions view is empty**: Check that `session_id` is declared in `answer()`'s signature — `app/web.py` only passes it if the parameter exists. Wait a few seconds and refresh; traces are sent asynchronously.

**✋ Check in**: "Do you see a session with multiple turns, and `workshop-user-1` in the Users view?"

---

## Step 2 — Separate development from production with the tracing environment

**Announce**: When you deploy this to production, your dev and prod traces would both flow into the same Langfuse project and mix together — that's how dashboards get polluted with test data. One env var fixes it for good.

**Check** — open the attendee's `.env` file and confirm this line is already there (it was copied from `.env.example` during setup):

```bash
LANGFUSE_TRACING_ENVIRONMENT=development
```

If it's missing, add it now. Otherwise, no change needed.

**Explain**: Every trace now carries an `environment` attribute. In production you'd set `LANGFUSE_TRACING_ENVIRONMENT=production` and the two data streams stay completely separate — same project, same prompts, same datasets, but dashboards and evaluators can be scoped per environment. No code change is needed: Langfuse picks the env var up automatically.

**Terminal prompt**: "Restart the app (so the `.env` is loaded fresh) and ask a question."

**Langfuse check**: "Use the **Environment** filter at the top of the Traces table. Select `development` — only your workshop traces should appear."

📸 **See Task 3.2 in the lab README** for a screenshot of the environment filter.

**✋ Check in**: "Does the environment filter work? Are only development traces visible when you select it?"

---

## Completion check

- [ ] Traces are grouped under a Session in the Sessions view
- [ ] `workshop-user-1` appears in the Users view
- [ ] Traces are filterable by `environment = development`

"Nice — your traces now carry session, user, and environment context. Ready for Lab 4: Prompt Management?"
