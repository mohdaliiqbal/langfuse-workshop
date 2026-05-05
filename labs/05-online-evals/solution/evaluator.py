"""
Lab 5 Solution: LLM-as-a-judge evaluator.
The judge prompt is managed in Langfuse (not hardcoded here).
Called in a background thread after each response.
"""

import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()


def evaluate_response(trace_id: str, observation_id: str | None, question: str, response: str) -> None:
    """
    Run LLM-as-a-judge evaluation and record the score in Langfuse.
    Fetches the evaluator prompt from Langfuse — iterate on the rubric
    without redeploying code.
    """
    langfuse = get_client()

    try:
        # Fetch the prompt from Langfuse (same pattern as Lab 4)
        prompt_obj = langfuse.get_prompt("quality-evaluator-prompt", label="production")
        prompt_text = prompt_obj.compile(question=question, response=response)

        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0,
        )

        evaluation = json.loads(result.choices[0].message.content)

        langfuse.create_score(
            trace_id=trace_id,
            observation_id=observation_id,
            name="llm-judge-quality",
            value=float(evaluation["score"]),
            data_type="NUMERIC",
            comment=evaluation.get("reason", ""),
        )
    except Exception as e:
        print(f"[dim]Evaluation failed: {e}[/dim]")
