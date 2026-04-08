"""
Lab 5 Solution: Run an experiment against the benchmark dataset.

Usage:
    python labs/05-datasets/run_experiment.py
    python labs/05-datasets/run_experiment.py --name prompt-v2

Change --name between runs to compare different versions.
"""

import json
import os
import argparse
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langfuse import get_client
from app.assistant import answer

langfuse = get_client()
oai = OpenAI()

DATASET_NAME = "datastream-support-benchmark"

JUDGE_PROMPT = """You are evaluating a customer support response for correctness.

Question: {question}
Expected key information: {expected}
Actual response: {actual}

Does the actual response correctly answer the question and contain the essential information from the expected answer?
Partial credit is fine if the response is mostly correct.

Respond with JSON only:
{{"contains_answer": <true/false>, "score": <0.0 to 1.0>, "reason": "<one sentence>"}}"""


def judge(question: str, expected: str, actual: str) -> dict:
    result = oai.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=question,
                expected=expected,
                actual=actual,
            )
        }],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(result.choices[0].message.content)


def run(experiment_name: str):
    print(f"Running experiment: {experiment_name}")
    print(f"Dataset: {DATASET_NAME}\n")

    dataset = langfuse.get_dataset(DATASET_NAME)
    results = []

    for item in dataset.items:
        question = item.input["question"]
        expected = item.expected_output

        with item.observe(run_name=experiment_name) as trace_id:
            actual = answer(question)
            evaluation = judge(question, expected, actual)

            langfuse.create_score(
                trace_id=trace_id,
                name="answer-correctness",
                value=float(evaluation["score"]),
                data_type="NUMERIC",
                comment=evaluation.get("reason", ""),
            )

        results.append({
            "question": question,
            "score": evaluation["score"],
            "correct": evaluation["contains_answer"],
            "reason": evaluation.get("reason", ""),
        })

        status = "PASS" if evaluation["contains_answer"] else "FAIL"
        print(f"  [{status}] [{evaluation['score']:.2f}] {question[:55]}")

    avg_score = sum(r["score"] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r["correct"]) / len(results)

    print(f"\n{'─' * 50}")
    print(f"Experiment:    {experiment_name}")
    print(f"Average score: {avg_score:.2f}")
    print(f"Pass rate:     {pass_rate:.0%} ({sum(1 for r in results if r['correct'])}/{len(results)})")
    print(f"\nView results: Langfuse → Datasets → {DATASET_NAME} → Runs")

    langfuse.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="prompt-v1", help="Experiment name")
    args = parser.parse_args()
    run(args.name)
