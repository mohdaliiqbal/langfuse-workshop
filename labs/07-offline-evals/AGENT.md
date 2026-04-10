# Lab 7: Offline Evals — Datasets & Experiments — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 7" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through creating a golden benchmark dataset, running SDK-based experiments to compare prompt versions, running a no-code UI experiment, and adding production traces to the dataset. No changes to `app/assistant.py` or `app/main.py` are needed.

---

## Step 1 — Create the dataset

Run the dataset creation script:

```bash
python labs/07-offline-evals/create_dataset.py
```

**Verify in Langfuse**: Go to **Datasets** in the left sidebar. You should see `datastream-support-benchmark` with items. Click into it to see the questions and their expected answers.

**Explain**: A dataset is a curated set of input/expected-output pairs — your golden benchmark. These questions cover the main topics the assistant should handle. Any regression in quality will show up here before users notice it.

---

## Step 2 — Run the first experiment

Run the experiment against the current prompt:

```bash
python labs/07-offline-evals/run_experiment.py
```

**Verify in Langfuse**: Go to **Datasets** → `datastream-support-benchmark` → **Runs**. You should see `prompt-v1` with an average score and per-item results.

**Explain**: Each dataset item ran through the actual `answer()` function — these are real traces linked to the dataset run. Click any item to see the full trace, including the prompt version and model response.

---

## Step 3 — Change the prompt and run a second experiment

Guide the attendee to update their prompt in Langfuse:

1. Go to **Prompts** → `datastream-system-prompt` → **New version**
2. Make a meaningful change (e.g. add: "Always cite the specific feature or plan name when relevant.")
3. Check **Set the production label** and save

In `labs/07-offline-evals/run_experiment.py`, change `EXPERIMENT_NAME = "prompt-v2"`, then run:

```bash
python labs/07-offline-evals/run_experiment.py
```

**Verify**: Both `prompt-v1` and `prompt-v2` appear in **Datasets** → **Runs**. Compare average scores and look for items where the score changed significantly.

**Explain**: This replaces "I think the new prompt is better" with a measurable, reproducible result.

---

## Step 4 — Run a no-code experiment from the UI

Tell the attendee to do the following (no code):

1. Go to **Prompts** → **New Prompt**, name it `support-qa-prompt`, type **Chat**
2. Add system message: *"You are a helpful assistant for {{product_name}}."*
3. Add user message placeholder: `{{question}}`
4. Set label `production`, click **Create prompt**

Then:
1. Go to **Datasets** → `datastream-support-benchmark` → **Run experiment**
2. Select `support-qa-prompt`
3. Map: `product_name` → `DataStream` (static), `question` → dataset `question` key
4. Optionally attach a Langfuse-hosted evaluator
5. Click **Run**

**Explain**: No Python needed — Langfuse runs the prompt against every dataset item directly. Useful for quick validation during prompt iteration in the Playground.

---

## Step 5 — Add a production trace to the dataset

1. Go to **Tracing** → **Traces** and find a trace where the response was poor
2. Click **Add to dataset** → select `datastream-support-benchmark`

**Explain**: This closes the loop. Production failures become permanent test cases. The next experiment run will catch this scenario — preventing silent regression.

---

## Completion check

- [ ] Dataset `datastream-support-benchmark` has items in Langfuse
- [ ] `prompt-v1` experiment run appears with scores
- [ ] `prompt-v2` experiment run appears after the prompt change
- [ ] Both runs can be compared side by side
- [ ] A no-code UI experiment has been run
- [ ] At least one production trace has been added to the dataset

**Congratulations — they've completed the workshop!** They've instrumented an LLM app from scratch, added rich observability, managed prompts outside code, set up online and offline evaluation, built a human annotation workflow, and created a systematic testing pipeline.
