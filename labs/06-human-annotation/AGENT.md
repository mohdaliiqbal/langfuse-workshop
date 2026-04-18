# Lab 6: Human Annotation — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 6" if your assistant has already loaded `AGENTS.md`.

---

## Before we start

Tell the attendee:

> "This lab is entirely UI-based — no code changes. Please open the lab README in your browser to follow along with screenshots:
> **https://github.com/mohdaliiqbal/langfuse-workshop/blob/main/labs/06-human-annotation/README.md**
>
> I'll guide you through each step in the Langfuse UI and reference the task numbers for screenshots."

---

## Your task

You are teaching Lab 6 as a live instructor. Guide the attendee through each UI step, explain the concept, and ask them to confirm before moving on. No code changes needed.

---

## Step 1 — Create Score Configs

**Announce**: Before annotating anything, we define the dimensions to score on — like setting up a rubric before grading. We'll create two Score Configs.

**Direct the attendee** to do the following in Langfuse:

1. Go to **Settings** → **Score Configs** → **Add New Score Config**
2. Create two configs:

   **Config 1 — Response Quality**
   - Name: `response-quality`
   - Type: **Numeric** (range 1–5)
   - Description: *Overall quality of the response — accuracy, helpfulness, and clarity*

   **Config 2 — Answer Grounded**
   - Name: `answer-grounded`
   - Type: **Boolean**
   - Description: *Is the answer grounded in the provided documentation context?*

📸 **See Task 6.1 in the lab README** for a screenshot of the completed Score Configs list.

**Explain**: Score Configs are reusable rubric dimensions — every annotation workflow in the project (ad-hoc, queued, experiment review) uses the same configs. Defining them once means your annotation data is consistent across all methods and can be charted together in analytics.

**✋ Check in**: "Have you created both Score Configs? Can you see them listed in Settings → Score Configs?"

---

## Step 2 — Annotate a trace

**Announce**: Now that the rubric exists, we'll use it to rate a real observation from your app.

**Direct the attendee** to:

1. Go to **Tracing** and open any recent observation
2. Click **Annotate** in the observation detail panel
3. Fill in `response-quality` (1–5) and `answer-grounded` (true/false)
4. Optionally add a comment → click **Save**

📸 **See Task 6.2 in the lab README** for screenshots of the Annotate button and the annotation panel.

**Explain**: This is how a domain expert or PM contributes quality signals without touching code. Scores are immediately queryable — filter Tracing by `score: response-quality < 3` to surface all low-quality observations directly, no need to keep mental notes about specific traces.

**✋ Check in**: "Have you annotated an observation? Can you see the scores attached to it in the Scores tab?"

---

## Step 3 — Create an Annotation Queue and work through it

**Announce**: Ad-hoc annotation works for spot checks. Annotation Queues let you review a batch systematically — multiple teammates can work the same queue simultaneously without duplicating effort.

**Create the queue:**
1. Go to **Human Annotation** → **Annotation Queues** → **New Queue**
2. Name: `workshop-review`
3. Select both Score Configs: `response-quality` and `answer-grounded`
4. Click **Create**

📸 **See Task 6.3 in the lab README** for screenshots of creating the queue and adding traces to it.

**Add observations to the queue:**
1. Go to **Tracing**
2. Select 5–10 observations using the checkboxes
3. Click **Actions** → **Add to queue** → select `workshop-review`

**Work through the queue:**
1. Go to **Human Annotation** → **Annotation Queues** → `workshop-review`
2. Click **Process queue**
3. For each observation: review the input and output, fill in your scores, optionally provide a corrected output
4. Click **Mark Completed** to advance to the next item

**Explain**: Queues solve the team coordination problem. Without them, two reviewers working the same trace list will overlap and skip items. A queue assigns each item atomically — trackable progress, no duplicated effort. After working through the queue, filter Tracing by `score: response-quality < 3` to find low-quality observations to add to a dataset in Lab 7.

**✋ Check in**: "Have you processed at least one queue item and marked it completed? What score did you give it?"

---

## Completion check

- [ ] `response-quality` and `answer-grounded` Score Configs exist in Settings
- [ ] At least one observation has manual annotation scores
- [ ] `workshop-review` annotation queue exists with 5+ observations
- [ ] At least one queue item is marked completed

"You've added the human calibration layer to your eval system. Ready for Lab 7: Offline Evals — Datasets & Experiments?"
