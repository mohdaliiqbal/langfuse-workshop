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

**Verify in Langfuse**: Go to **Datasets** in the left sidebar. You should see `datastream-support-benchmark` with 9 items. Click into it to see the questions and their expected answers.

**Explain**: A dataset is a curated set of input/expected-output pairs — your golden benchmark. These questions cover the main topics the assistant should handle. Any regression in quality will show up here before users notice it.

---

## Step 2 — Run the first experiment

Run the experiment against the current prompt:

```bash
python labs/07-offline-evals/run_experiment.py --name prompt-v1
```

**Verify in Langfuse**: Go to **Datasets** → `datastream-support-benchmark` → **Runs**. You should see `prompt-v1` with an average score and per-item results.

**Explain**: `dataset.run_experiment()` loops over every dataset item, runs your `run_task` function (which calls the real `answer()` function), then calls your `evaluate_item` function and returns an `Evaluation` object with the score. Each item becomes a real trace linked to the dataset run — click any item to see the full trace including the prompt version used.

---

## Step 3 — Change the prompt and run a second experiment

Guide the attendee to update their prompt in Langfuse:

1. Go to **Prompts** → `datastream-system-prompt` → **New version**
2. Make a meaningful change (e.g. add: "Always cite the specific feature or plan name when relevant.")
3. Check **Set the production label** and save

Then run the experiment again with a different name — no file edits needed:

```bash
python labs/07-offline-evals/run_experiment.py --name prompt-v2
```

**Verify**: Both `prompt-v1` and `prompt-v2` appear in **Datasets** → **Runs**. Compare average scores and look for items where the score changed significantly.

**Explain**: This replaces "I think the new prompt is better" with a measurable, reproducible result. The `--name` flag is how you label each run — use descriptive names like `prompt-v2`, `gpt-4o`, or `retrieval-v3` to make comparisons meaningful.

---

## Step 4 — Run a no-code experiment from the UI

Tell the attendee to do the following (no code):

**Create a simple prompt:**
1. Go to **Prompts** → **New Prompt**, name it `support-qa-prompt`, type **Chat**
2. Add a system message: *"You are a helpful assistant for DataStream product."*
3. Add a user message: `{{question}}`
4. Set label `production`, click **Create prompt**

**Run the experiment:**
1. Go to **Datasets** → `datastream-support-benchmark` → **Run experiment**
2. Select **Configure** under _via User Interface_
3. Select the `support-qa-prompt` prompt
4. Select the `datastream-support-benchmark` dataset
5. Optionally attach a Langfuse-hosted evaluator (e.g. Helpfulness) and set input/output mapping
6. Click **Run Experiment**

**Explain**: No Python needed — Langfuse runs the prompt against every dataset item directly. Useful for quick validation during prompt iteration in the Playground before writing the code evaluator.

---

## Step 5 — Add a production trace to the dataset

1. Go to **Tracing** → **Traces** and find a trace where the response was poor
2. Click **Add to dataset** → select `datastream-support-benchmark`

**Explain**: This closes the loop. Production failures become permanent test cases. The next experiment run will catch this scenario — preventing silent regression.

---

## Completion check

- [ ] Dataset `datastream-support-benchmark` has items in Langfuse
- [ ] `prompt-v1` experiment run appears with `answer-correctness` scores
- [ ] `prompt-v2` experiment run appears after the prompt change
- [ ] Both runs can be compared side by side in the Runs tab
- [ ] A no-code UI experiment has been run
- [ ] At least one production trace has been added to the dataset

**Congratulations — they've completed the workshop!** They've instrumented an LLM app from scratch, added rich observability, managed prompts outside code, set up online and offline evaluation, built a human annotation workflow, and created a systematic testing pipeline.
