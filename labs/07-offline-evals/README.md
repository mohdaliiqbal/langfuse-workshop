# Lab 7: Offline Evals — Datasets & Experiments

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

### Task 7.1 — Create a dataset

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

### Task 7.2 — Run an experiment

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

### Task 7.3 — Compare two prompt versions

Now update your system prompt in Langfuse (create a new version with different instructions), then run the experiment again with a different `EXPERIMENT_NAME`:

1. In Langfuse, go to **Prompts** → `datastream-system-prompt` → **New version** — add or change something meaningful (e.g., require the assistant to always mention relevant pricing, or always suggest contacting support for complex issues). Check **Set the production label** and save.
2. In `run_experiment.py`, change `EXPERIMENT_NAME = "prompt-v2"`.
3. Run the experiment again.

In Langfuse → **Datasets** → `datastream-support-benchmark` → **Runs**, you can now compare both experiment runs side by side.

---

### Task 7.4 — Run a no-code experiment from the UI

You don't always need to write code to run an experiment. Langfuse can run a prompt directly against your dataset from the UI.

**Prerequisites**: Your dataset must have items with keys that match your prompt's variables. The `datastream-support-benchmark` dataset has a `question` key, but `datastream-system-prompt` uses `product_name`. For this task, create a simpler prompt:

1. Go to **Prompts** → **New Prompt**, name it `support-qa-prompt`, type **Chat**
2. Add a system message: *"You are a helpful assistant for {{product_name}}."*
3. Add a user message placeholder: `{{question}}`
4. Set label `production` and click **Create prompt**

**Run the experiment:**
1. Go to **Datasets** → `datastream-support-benchmark` → **Run experiment**
2. Select the `support-qa-prompt` prompt
3. Map variables: `product_name` → `DataStream` (static), `question` → dataset item `question` key
4. Optionally attach a Langfuse-hosted evaluator (e.g. Helpfulness)
5. Click **Run** — Langfuse executes the prompt against every dataset item

View the results in the **Runs** tab — each item shows the generated output and any scores. No Python required.

> This is useful for quick prompt testing: iterate on the prompt in the Playground, then immediately validate it against the full dataset to catch regressions.

---

### Task 7.5 — Add a production trace to the dataset

Datasets should grow over time with real failures. When you see a bad production trace, add it to the dataset so it becomes a permanent test case.

1. Go to **Tracing** → **Traces** and open a trace where the assistant gave a wrong or unhelpful answer.
2. Click **Add to dataset** in the trace detail panel.
3. Select `datastream-support-benchmark` and click **Add**.

The trace's input is now a dataset item. The next time you run an experiment, it will be tested — ensuring this failure can't silently regress.

> This closes the loop: production failures → dataset items → experiment test cases → caught before deployment.

---

## Checkpoint

- [ ] Dataset appears in Langfuse with 8 items
- [ ] First experiment run creates traces linked to the dataset
- [ ] Each trace has an `answer-correctness` score
- [ ] After changing the prompt, the second run shows different scores
- [ ] The dataset runs view shows both experiments for comparison
- [ ] A no-code UI experiment has been run against the dataset
- [ ] At least one production trace has been added to the dataset from the UI

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

**Congratulations — you've completed the workshop!** 🎉
