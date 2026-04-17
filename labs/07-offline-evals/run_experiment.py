"""
Run an experiment against the benchmark dataset.

Usage:
    python labs/07-offline-evals/run_experiment.py
    python labs/07-offline-evals/run_experiment.py --name prompt-v2

Change --name between runs to compare different versions in Langfuse.
"""

import json
import os
import sys
import argparse
from pathlib import Path

# Add project root to path so `app` module can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langfuse import get_client, Evaluation
from app.assistant import answer

langfuse = get_client()
oai = OpenAI()

DATASET_NAME = "datastream-support-benchmark"

def judge(question: str, expected: str, actual: str) -> dict:
    """Score a response using an LLM judge. Prompt is managed in Langfuse."""
    prompt_obj = langfuse.get_prompt("experiment-judge-prompt", label="production")
    prompt_text = prompt_obj.compile(question=question, expected=expected, actual=actual)

    result = oai.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt_text}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(result.choices[0].message.content)


def run_task(*, item, **kwargs):
    """Run the assistant against one dataset item."""
    question = item.input["question"]
    result = answer(question)
    # answer() returns (response, trace_id) from Lab 5 onwards
    if isinstance(result, tuple):
        return result[0]
    return result


def evaluate_item(*, input, output, expected_output, **kwargs):
    """Score the assistant's response against the expected answer using LLM-as-a-judge."""
    evaluation = judge(input["question"], expected_output, output)
    return Evaluation(
        name="answer-correctness",
        value=float(evaluation["score"]),
        comment=evaluation.get("reason", ""),
    )


def run(experiment_name: str):
    print(f"Running experiment: {experiment_name}")
    print(f"Dataset: {DATASET_NAME}\n")

    dataset = langfuse.get_dataset(DATASET_NAME)

    result = dataset.run_experiment(
        name=experiment_name,
        task=run_task,
        evaluators=[evaluate_item],
    )

    print(result.format())
    print(f"\nView results: Langfuse → Datasets → {DATASET_NAME} → Runs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="prompt-v1", help="Experiment name")
    args = parser.parse_args()
    run(args.name)
