---
title: "Workshop: Instructor Notes for Experiments"
description: "Facilitator notes for running Langfuse experiments with callback evaluators inside run_experiment."
---

# 06 Experiments

Learner guide: [06 Experiments](../learner/06-experiments.md)

## Instructor notes

- The experiment calls the same `run_support_conversation` as the web app.
- Production monitors in 4.2 have no reference answer. This chapter compares against `expectedOutput`.
- `behavior_match` is a Decisions API label (`gpt-6-luna`) plus an equality check. `correctness` is the regression judge and uses `OPENAI_MODEL`.
- Both are callbacks on `dataset.run_experiment`. Do not set up a platform evaluator before the first run.
- Keep `max_concurrency` at 1.
- The console summary from `uv run python scripts/run_dataset.py` should already list both scores.
- Expect the baseline to miss out-of-scope and vague items. That run is what chapter 07 compares against.

## Watch for

- A missing score usually means the script hit an OpenAI or Langfuse error. Read the terminal before debugging the UI.
- `expected_output` in the Python evaluator signature is the same field as `expectedOutput` on the dataset item.
