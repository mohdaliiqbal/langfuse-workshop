# Lab 5: Datasets & Experiments

## Concept

Individual trace scores tell you how well a single response performed. But to make confident decisions about your system — "is prompt v2 better than v1?" — you need to run the same set of questions through both versions and compare.

**Datasets** are curated collections of input/expected-output pairs used as a benchmark. **Experiments** run your application against a dataset and record the results as traces, which you can then score and compare.

This is the foundation of **systematic evaluation**:

```
Dataset                     Experiment A (prompt v1)    Experiment B (prompt v2)
──────────────────          ────────────────────────    ────────────────────────
Q: "How do I get started?"  → response + score: 0.8     → response + score: 0.9
Q: "What does Pro cost?"    → response + score: 0.9     → response + score: 0.85
Q: "Why is my auth failing?"→ response + score: 0.6     → response + score: 0.8
                            avg: 0.77                   avg: 0.85 ✓ (use v2)
```

This replaces "I think the new prompt is better" with "the new prompt scores 10% higher on our benchmark."

---

## What You'll Build

1. Create a golden dataset of support questions with expected answers
2. Run an experiment against the dataset
3. Compare results between two prompt versions

---

## Tasks

### Task 5.1 — Create a dataset

Create a file `labs/05-datasets/create_dataset.py` to populate a dataset in Langfuse:

```python
from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

langfuse = get_client()

DATASET_NAME = "datastream-support-benchmark"

# Create the dataset
langfuse.create_dataset(
    name=DATASET_NAME,
    description="Golden set of DataStream support questions for benchmarking",
)

# Add test cases
test_cases = [
    {
        "input": {"question": "How do I install DataStream?"},
        "expected_output": "pip install datastream-cli",
    },
    {
        "input": {"question": "What is the price of the Pro plan?"},
        "expected_output": "$49/month",
    },
    {
        "input": {"question": "What connectors does DataStream support?"},
        "expected_output": "Kafka, PostgreSQL, MySQL, BigQuery, Snowflake",
    },
    {
        "input": {"question": "I'm getting an AUTH_FAILED error, what should I do?"},
        "expected_output": "Verify your API keys and permissions in Settings > Credentials",
    },
    {
        "input": {"question": "How do I set up monitoring alerts?"},
        "expected_output": "Settings > Alerts",
    },
    {
        "input": {"question": "Is DataStream GDPR compliant?"},
        "expected_output": "Yes, DataStream is SOC 2 Type II certified and GDPR compliant",
    },
    {
        "input": {"question": "What is the API rate limit on the Free plan?"},
        "expected_output": "100 requests/minute",
    },
    {
        "input": {"question": "How do I create a pipeline?"},
        "expected_output": "datastream init my-pipeline",
    },
]

for case in test_cases:
    langfuse.create_dataset_item(
        dataset_name=DATASET_NAME,
        input=case["input"],
        expected_output=case["expected_output"],
    )

print(f"Created dataset '{DATASET_NAME}' with {len(test_cases)} items.")
print("View it in Langfuse: Datasets → datastream-support-benchmark")
```

Run it:

```bash
python labs/05-datasets/create_dataset.py
```

Verify the dataset appears in Langfuse → **Datasets**.

---

### Task 5.2 — Run an experiment

Create `labs/05-datasets/run_experiment.py`:

```python
import json
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langfuse import get_client, observe
from app.assistant import answer  # Uses current prompt

langfuse = get_client()
oai = OpenAI()

DATASET_NAME = "datastream-support-benchmark"
EXPERIMENT_NAME = "prompt-v1"  # Change this for each run


def score_response(question: str, expected: str, actual: str) -> float:
    """Use LLM to judge if the actual response contains the expected information."""
    result = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""Does the actual response correctly answer the question and contain the key information from the expected answer?

Question: {question}
Expected key info: {expected}
Actual response: {actual}

Respond with JSON: {{"contains_answer": true/false, "score": 0.0-1.0, "reason": "..."}}"""
        }],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(result.choices[0].message.content)


def run():
    dataset = langfuse.get_dataset(DATASET_NAME)

    results = []
    for item in dataset.items:
        question = item.input["question"]
        expected = item.expected_output

        # Run the assistant (creates a trace automatically)
        with item.observe(run_name=EXPERIMENT_NAME) as trace_id:
            actual = answer(question)

            # Score the response
            evaluation = score_response(question, expected, actual)

            # Record the score on the trace
            langfuse.create_score(
                trace_id=trace_id,
                name="answer-correctness",
                value=evaluation["score"],
                data_type="NUMERIC",
                comment=evaluation["reason"],
            )

            results.append({
                "question": question,
                "score": evaluation["score"],
                "contains_answer": evaluation["contains_answer"],
            })

        print(f"  [{evaluation['score']:.2f}] {question[:60]}")

    avg_score = sum(r["score"] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r["contains_answer"]) / len(results)

    print(f"\nExperiment: {EXPERIMENT_NAME}")
    print(f"Average score: {avg_score:.2f}")
    print(f"Pass rate:     {pass_rate:.0%}")
    print(f"\nView in Langfuse: Datasets → {DATASET_NAME} → Runs")

    langfuse.flush()


if __name__ == "__main__":
    run()
```

Run the experiment:

```bash
python labs/05-datasets/run_experiment.py
```

---

### Task 5.3 — Compare two prompt versions

Now update your system prompt in Langfuse (create a new version with different instructions), then run the experiment again with a different `EXPERIMENT_NAME`:

1. In Langfuse, edit `datastream-system-prompt` — add or change something meaningful (e.g., require the assistant to always mention relevant pricing, or always suggest contacting support for complex issues).
2. Publish the new version as `production`.
3. In `run_experiment.py`, change `EXPERIMENT_NAME = "prompt-v2"`.
4. Run the experiment again.

In Langfuse → **Datasets** → `datastream-support-benchmark` → **Runs**, you can now compare both experiment runs side by side.

---

## Checkpoint

- [ ] Dataset appears in Langfuse with 8 items
- [ ] First experiment run creates traces linked to the dataset
- [ ] Each trace has an `answer-correctness` score
- [ ] After changing the prompt, the second run shows different scores
- [ ] The dataset runs view shows both experiments for comparison

---

## Why This Matters

Without datasets, you can only evaluate changes subjectively ("the responses seem better"). With datasets:

- You have a **regression test suite** — new changes can't silently break existing behaviour
- You can **A/B test prompts, models, or retrieval strategies** with confidence
- You build up a **benchmark** over time that reflects your real use cases
- You can **automate evaluation** as part of CI/CD before deploying prompt changes

Production traces are also a great source of dataset items: when you see a trace that went wrong, add it to the dataset so it becomes a test case.

---

## Solution

See [`create_dataset.py`](./create_dataset.py) and [`run_experiment.py`](./run_experiment.py).
