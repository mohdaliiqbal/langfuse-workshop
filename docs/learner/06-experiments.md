---
title: "Workshop: Run Langfuse Experiments"
description: "Run the support agent across the Langfuse dataset, score every item with callback evaluators inside run_experiment, and inspect scored experiment runs."
---

# 06 Experiments

## Why experiments

A trace tells you about one turn. An experiment tells you about behavior across the dataset. Every experiment run does three things:

1. Pulls each item from the dataset.
2. Runs the item's input through the agent: the same `run_support_conversation(...)` the web app uses.
3. Scores the actual output with one or more evaluators.

- Docs: [Experiments via SDK](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk)
- Academy: [Experiments](https://langfuse.com/academy/experiments) and [Evaluate](https://langfuse.com/academy/evaluate)

## Goal

1. You can run the full dataset against the agent on demand.
2. Every item gets a `behavior_match` score and a `correctness` score, both from `run_experiment` callbacks.
3. Both scores and the per-item traces are visible in Langfuse.

## Starting point

```bash
uv run python scripts/use_checkpoint.py 06-experiments
```

Your dataset is seeded. `scripts/run_dataset.py` is already in the repo.

## Step 1: Choose the evaluators

Each goal from chapter 05 gets one evaluator, and each reads its own field from `expectedOutput`:

- **`behavior_match`** (decision model + deterministic match): did Specs reply, defer, or ask a follow-up when we expected it to? The OpenAI Decisions API picks one of three labels, and the script compares that label with `expectedBehavior`.
- **`correctness`** (LLM-as-a-judge regression check): is the answer still correct? Paraphrases pass. Missing required detail or a contradicted fact fails.

Impersonation and lengthy replies have no evaluator here. Read those traces, and add a check (for example a word count) if they become worth tracking.

## Step 2: Understand the run script

Open `scripts/run_dataset.py`.

- Loads the hosted dataset with `langfuse.get_dataset(env.dataset_name)`.
- For each item, calls `run_support_conversation(...)`.
- Uses `dataset.run_experiment(...)` to roll the traces into one run.
- Attaches `behavior_match` and `correctness` as callback evaluators.

The Python method is `run_experiment` (snake case). Evaluators return `Evaluation(name=..., value=..., comment=...)`. The keyword for the reference answer is `expected_output`, which is the SDK's name for the dataset field `expectedOutput`.

```python
result = dataset.run_experiment(
    name="Dad IT Support Agent experiment",
    run_name=run_name,
    description="Workshop dataset run for the Dad IT Support Agent",
    metadata={"model": env.openai_model},
    max_concurrency=1,
    task=task,
    evaluators=[behavior_evaluator, correctness_evaluator],
)
print(result.format())
```

- **`task`** is the application. It calls `run_support_conversation`, so the trace shape matches production.
- **`evaluators`** run in this process after `task` returns and attach scores to the item trace.
- **`run_name`** includes a timestamp so two runs do not collide.

Both scores are callbacks. The console summary already includes them when the script exits. This chapter does not use Langfuse Platform evaluators, because configuring one needs existing experiment data to preview variable mappings.

## Step 3: Review the `behavior_match` evaluator

`decide_behavior(...)` posts to the [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions) (`POST /v1/decisions`, model `gpt-6-luna`) with one `choice` question. The API can only answer `reply`, `defer_question`, or `ask_follow_up`. The callback compares that label with `expectedBehavior`: `1` on a match, `0` otherwise. The comment records both labels and the confidence.

The model never sees the expected label. The score itself is an equality check. The Python OpenAI SDK call goes through `httpx` to `POST /v1/decisions`, which is the same request the TypeScript runner sends with `openai.post("/decisions", ...)`.

## Step 4: Review the `correctness` regression check

The second callback asks OpenAI whether the agent answer preserves the material meaning of `idealAnswer`. It maps the judge's true/false result to `0` or `1` plus a short comment. The judge uses `OPENAI_API_KEY` and `OPENAI_MODEL` from `.env`. `behavior_match` uses the same API key with `gpt-6-luna` fixed in the script. You do not need the Langfuse evaluator model from section 4.2 for this chapter.

## Step 5: Run the dataset

```bash
uv run python scripts/run_dataset.py
```

This first run is your **baseline experiment**. It uses the production `dad-it-support-agent` prompt, so expect misses on the out-of-scope and vague items. In 07 you compare it with the prompt from error analysis.

## What to inspect in Langfuse

- The new **Run** under your dataset: one row per item with `behavior_match` and `correctness`, plus a trace link.
- Item-level traces with the same `dad-it-support-chat-turn` root as production.
- The dataset chart view: per-run averages for every score.

## How to verify you are done

- One run row appears under the dataset.
- Every item has a trace and both scores.
- The console summary printed both `behavior_match` and `correctness`.
- The trace shape matches a normal production trace.

## End state

This is the starting point for `07-evaluation`.
