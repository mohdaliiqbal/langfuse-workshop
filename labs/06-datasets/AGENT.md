# Lab 6: Datasets & Experiments — Agent Instructions

> **For the attendee**: Paste this file's contents into your AI assistant, or say "start lab 6" if your assistant has already loaded `AGENTS.md`.

---

## Your task

Guide the attendee through creating a golden benchmark dataset in Langfuse and running experiments to compare prompt versions. This lab is mostly running existing scripts and comparing results in the UI.

No changes to `app/assistant.py` or `app/main.py` are needed.

---

## Step 1 — Create the dataset

Run the dataset creation script:

```bash
python labs/06-datasets/create_dataset.py
```

**Verify in Langfuse**: Go to **Datasets** in the left sidebar. You should see `datastream-support-benchmark` with 10 items. Click into it to see the questions and their expected answers.

**Explain**: A dataset is a curated set of input/expected-output pairs — your golden benchmark. These 10 questions cover the main topics the assistant should handle. Any regression in quality will show up here before users notice it.

---

## Step 2 — Run the first experiment

Run the experiment against the current prompt (version in Langfuse right now):

```bash
python labs/06-datasets/run_experiment.py --name prompt-v1
```

This will run all 10 questions through the assistant, score each response using LLM-as-a-judge, and print a summary.

**Verify in Langfuse**: Go to **Datasets** → `datastream-support-benchmark` → **Runs**. You should see `prompt-v1` with an average score and per-item results.

**Explain**: Each item in the dataset ran through the actual `answer()` function — these are real traces linked to the dataset run. You can click any item to see the full trace, including what prompt was used and what the model returned.

---

## Step 3 — Change the prompt and run a second experiment

Guide the attendee to update their prompt in Langfuse:

1. Go to **Prompt Management** → `datastream-system-prompt`
2. Edit the prompt — make a meaningful change (e.g. add: "Always cite the specific feature or plan name when relevant.")
3. Save and publish as `production`

Now run the experiment again with a different name:

```bash
python labs/06-datasets/run_experiment.py --name prompt-v2
```

**Verify in Langfuse**: Go to **Datasets** → `datastream-support-benchmark` → **Runs**. Both `prompt-v1` and `prompt-v2` are now listed. Compare their average scores and look for items where the score changed significantly in either direction.

**Explain**: This is the core evaluation workflow: change something (prompt, model, retrieval) → run the benchmark → compare scores. You've replaced "I think the new prompt is better" with a measurable, reproducible result.

---

## Going further (optional)

If the attendee wants to explore more:

- **Add their own dataset items**: Open `labs/06-datasets/create_dataset.py`, add more test cases, and re-run it
- **Try a different model**: Change `APP_MODEL` in `.env` to `gpt-4o` and run `prompt-v3` to compare cost vs quality
- **Score on multiple dimensions**: Add a second score (e.g. `answer-completeness`) in `run_experiment.py` alongside `answer-correctness`

---

## Completion check

- [ ] Dataset `datastream-support-benchmark` has 10 items in Langfuse
- [ ] `prompt-v1` experiment run appears in the Datasets → Runs view with scores
- [ ] `prompt-v2` experiment run appears after the prompt change
- [ ] The attendee can compare both runs side by side in the UI

**Congratulations — they've completed the workshop.** They've instrumented an LLM application from scratch, added rich observability, moved prompts out of code, set up evaluation, and built a systematic testing workflow.
