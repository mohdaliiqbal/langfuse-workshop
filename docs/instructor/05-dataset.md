---
title: "Workshop: Instructor Notes for Build Eval Datasets"
description: "Facilitator notes for deciding what an eval dataset should evaluate and seeding it into Langfuse."
---

# 05 Build eval datasets

Learner guide: [05 Build eval datasets](../learner/05-dataset.md)

## Instructor notes

- Start with the goal: correct answers, and the right reply / defer / follow-up behavior.
- 9 of the 25 items come from the 4.1 traces (`"source": "error-analysis"`). The other 16 are `"starter"`.
- `idealAnswer` feeds `correctness`. `expectedBehavior` feeds `behavior_match`.
- Seed with `uv run python scripts/seed_dataset.py`. Item ids are stable, so running it again updates those rows.

## Demo rhythm

1. Open `data/seed-dataset.json` and show `input.messages`, `expectedOutput`, and `metadata`, including one multi-turn item.
2. Run the seed script.
3. Open the dataset in Langfuse and read one error-analysis item next to the kind of trace it came from.
