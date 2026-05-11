"""
Run an experiment against the benchmark dataset.

Usage:
    python labs/07-offline-evals/run_experiment.py
    python labs/07-offline-evals/run_experiment.py --name prompt-v2

This script only runs the assistant against each dataset item — scoring is
handled by an LLM-as-a-judge evaluator you configure in the Langfuse UI
(Evaluation → LLM-as-a-Judge, scoped to "Dataset Runs"). The platform
evaluator runs automatically on each experiment item as it's recorded.

Change --name between runs to compare different prompt versions in Langfuse.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path so `app` module can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from app.assistant import answer

langfuse = get_client()

DATASET_NAME = "datastream-support-benchmark"


def run_task(*, item, **kwargs):
    """Run the assistant against one dataset item."""
    question = item.input["question"]
    result = answer(question)
    # answer() returns (response, trace_id, observation_id) from Lab 5 onwards
    if isinstance(result, tuple):
        return result[0]
    return result


def run(experiment_name: str):
    print(f"Running experiment: {experiment_name}")
    print(f"Dataset: {DATASET_NAME}\n")

    dataset = langfuse.get_dataset(DATASET_NAME)

    # No evaluators= here — scoring is done by a Langfuse LLM-as-a-Judge
    # evaluator configured in the UI to run on Dataset Runs.
    result = dataset.run_experiment(
        name=experiment_name,
        task=run_task,
    )

    print(result.format())
    print(f"\nView results: Langfuse → Datasets → {DATASET_NAME} → Runs")
    print("Scores will appear within ~30–60 seconds once the platform evaluator picks them up.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="prompt-v1", help="Experiment name")
    args = parser.parse_args()
    run(args.name)
