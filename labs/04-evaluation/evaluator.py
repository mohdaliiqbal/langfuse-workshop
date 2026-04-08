"""
Lab 4 Solution: LLM-as-a-judge evaluator
"""

import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()

EVALUATOR_PROMPT = """You are evaluating the quality of a customer support response for a data pipeline product.

Question asked by user:
{question}

Response given by the assistant:
{response}

Rate the response on a scale of 0.0 to 1.0 based on:
- Accuracy: Is the information factually correct?
- Helpfulness: Does it actually answer what was asked?
- Clarity: Is it easy to understand and act on?

Respond with only a JSON object in this format:
{{"score": <float between 0.0 and 1.0>, "reason": "<one concise sentence explaining the score>"}}"""


def evaluate_response(trace_id: str, question: str, response: str) -> None:
    """
    Run LLM-as-a-judge evaluation on a trace and record the score in Langfuse.
    Designed to be called in a background thread.
    """
    langfuse = get_client()

    try:
        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{
                "role": "user",
                "content": EVALUATOR_PROMPT.format(question=question, response=response)
            }],
            response_format={"type": "json_object"},
            temperature=0,
        )

        evaluation = json.loads(result.choices[0].message.content)

        langfuse.create_score(
            trace_id=trace_id,
            name="llm-judge-quality",
            value=float(evaluation["score"]),
            data_type="NUMERIC",
            comment=evaluation.get("reason", ""),
        )
    except Exception as e:
        # Don't let evaluation errors affect the main application
        print(f"[dim]Evaluation failed: {e}[/dim]")
