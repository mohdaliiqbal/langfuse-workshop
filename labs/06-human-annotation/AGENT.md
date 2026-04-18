# Lab 6: Human Annotation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 6" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through Langfuse's human annotation workflows — Score Configs, ad-hoc trace annotation, and Annotation Queues. This lab is entirely UI-based: no code changes needed.

---

## Step 1 — Create Score Configs

Tell the attendee to do the following in the Langfuse UI:

1. Go to **Settings** → **Score Configs** → **Add New Score Config**
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

**Explain**: This is how a domain expert or PM can contribute quality signals without touching code. Scores are immediately queryable — in **Tracing**, filter by `score: response-quality < 3` to surface all low-scoring observations. That's more reliable than trying to remember a specific bad trace from earlier.

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

**Explain**: Queues solve the coordination problem in team annotation. Without them, two reviewers working through the same trace list will overlap, skip items, or lose their place. A queue assigns each item atomically — no duplicated effort, trackable progress, and multiple people can work simultaneously without stepping on each other. Once the queue is complete, filter **Tracing** by `score: response-quality < 3` to find candidates for Lab 7's dataset — no need to remember which specific traces scored badly.

---

## Completion check

- [ ] `response-quality` and `answer-grounded` Score Configs exist
- [ ] At least one trace has manual annotation scores
- [ ] `workshop-review` annotation queue exists with 5+ traces
- [ ] At least one queue item is marked completed

Once confirmed, tell the attendee they're ready for **Lab 7: Offline Evals — Datasets & Experiments**.
