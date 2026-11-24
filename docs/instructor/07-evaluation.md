---
title: "Workshop: Instructor Notes for Evaluating a Change"
description: "Facilitator notes for evidence-driven prompt iteration: inspect low-scoring items, change one thing, rerun, and compare regressions."
---

# 07 Evaluate a Change

Learner guide: [07 Evaluate a Change](../learner/07-evaluation.md)

## Instructor notes

- Make learners inspect run 1 before changing anything.
- Publish the error-analysis prompt in the UI, or with `WORKSHOP_PROMPT_VARIANT=error-analysis uv run python scripts/publish_prompt.py`. `.env` wins when that variable is set there. The example file leaves it unset, so the shell prefix works.
- Upstream test runs on this 25-item set moved from `behavior_match` about 0.68–0.72 to 1.00 and `correctness` about 0.68 to 0.84. Tell the room to read items, not only averages.
- One prompt version, one rerun, one comparison.
- A drop in `correctness` with a rise in `behavior_match` is the regression worth stopping on.

## Demo rhythm

1. Open the baseline run and one low-scoring out-of-scope item.
2. Publish the new prompt version and move `production`.
3. `uv run python scripts/run_dataset.py`.
4. Compare the two runs in the dataset Experiments view.
