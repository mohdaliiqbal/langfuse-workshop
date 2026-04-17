# Lab 6: Human Annotation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 6" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through Langfuse's human annotation workflows — Score Configs, ad-hoc trace annotation, and Annotation Queues. This lab is entirely UI-based: no code changes needed.

---

## Step 1 — Create Score Configs

Tell the attendee to do the following in the Langfuse UI:

1. Go to **Settings** → **Scores** → **+ Add score config**
2. Create these two configs:

   **Config 1:**
   - Name: `response-quality`
   - Type: **Numeric** (range 1–5)
   - Description: *Overall quality — accuracy, helpfulness, clarity*

   **Config 2:**
   - Name: `answer-grounded`
   - Type: **Boolean**
   - Description: *Is the answer grounded in the documentation context?*

Ask the attendee to confirm both configs are created.

**Explain**: Score Configs are reusable rubric dimensions. Every annotation in the project — ad-hoc, queued, or experiment review — uses the same configs for consistency.

---

## Step 2 — Annotate a trace

1. Go to **Tracing** → **Traces** and open any recent trace
2. Click **Annotate** in the trace detail panel
3. Fill in `response-quality` (1–5) and `answer-grounded` (true/false)
4. Add an optional comment, then click **Save**

**Explain**: This is how a domain expert or PM can contribute quality signals without touching code. Encourage them to rate a trace they think has a bad response — low scores become useful signal for dataset curation in Lab 7.

---

## Step 3 — Create an Annotation Queue and work through it

**Create the queue:**
1. Go to **Human Annotation** → **Annotation Queues** → **New Queue**
2. Name: `workshop-review`, select both Score Configs (`response-quality` and `answer-grounded`), click **Create**

**Add traces to the queue:**
1. Go to **Tracing** → **Traces**
2. Select 5–10 traces using the checkboxes
3. Click **Actions** → **Add to queue** → select `workshop-review`

**Work through the queue:**
1. Go to **Human Annotation** → **Annotation Queues** → `workshop-review`
2. Click **Process queue**
3. For each trace, review the input and output, fill in your scores, and optionally provide a corrected output
4. Click **Mark Completed** to move to the next item

**Explain**: Queues are designed for batch review — a QA reviewer or subject matter expert works through them without needing to navigate the full trace list. Progress is tracked so multiple reviewers can divide the work. Any trace with a clearly wrong or unhelpful response is a candidate for Lab 7's dataset.

---

## Completion check

- [ ] `response-quality` and `answer-grounded` Score Configs exist
- [ ] At least one trace has manual annotation scores
- [ ] `workshop-review` annotation queue exists with 5+ traces
- [ ] At least one queue item is marked completed

Once confirmed, tell the attendee they're ready for **Lab 7: Offline Evals — Datasets & Experiments**.
