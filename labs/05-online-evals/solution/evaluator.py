"""
Lab 5 Solution: programmatic out-of-scope evaluator.
The judge prompt is managed in Langfuse so the rubric can be tuned without code changes.
Called in a background thread after each response.
"""

import json
import os
from openai import OpenAI
from langfuse import get_client

client = OpenAI()


def evaluate_response(trace_id: str, observation_id: str | None, question: str, response: str) -> None:
    """Score whether the question was in-scope and record the result on the trace."""
    langfuse = get_client()

    try:
        prompt_obj = langfuse.get_prompt("out-of-scope-evaluator-prompt", label="production")
        prompt_text = prompt_obj.compile(question=question, response=response)

        result = client.chat.completions.create(
            model=os.getenv("APP_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0,
        )

        evaluation = json.loads(result.choices[0].message.content)
        in_scope = bool(evaluation.get("in_scope", True))

        langfuse.create_score(
            trace_id=trace_id,
            observation_id=observation_id,
            name="in-scope",
            value=1 if in_scope else 0,
            data_type="BOOLEAN",
            comment=evaluation.get("reason", ""),
        )
    except Exception as e:
        print(f"[dim]Evaluation failed: {e}[/dim]")
