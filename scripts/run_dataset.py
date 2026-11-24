"""Run the hosted dataset against the live agent.

For each item:
  1. Call the same run_support_conversation the web app uses.
  2. Roll the per-item traces into one experiment run.
  3. Attach callback evaluators:
     - behavior_match (decision model + deterministic match)
     - correctness (LLM-as-a-judge regression check)

    uv run python scripts/run_dataset.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from uuid import uuid4

import httpx

import _bootstrap  # noqa: F401
from app.env import env
from app.models import ChatMessage, ChatRequest
from app.support_agent import run_support_conversation

BEHAVIORS = ("defer_question", "reply", "ask_follow_up")
DECISION_MODEL = "gpt-6-luna"

CORRECTNESS_PROMPT = """You are an expert semantic-equivalence evaluator for AI systems.
You will receive an actual assistant output and an expected output.
Your job is to decide whether the actual output preserves the expected output's material meaning.

## Scope
- Compare only semantic content.
- Treat the expected output as the source of truth for required conclusions, facts, constraints, and relationships.
- Ignore output shape, serialization, key order, nesting, formatting, whitespace, length, and presentation style unless a difference changes material meaning.

## Golden Rule
Score true only when the actual output conveys every material meaning, fact, constraint, and conclusion in the expected output without a material contradiction. Score false for any material semantic mismatch.

## Semantic Comparison
- Accept paraphrases, synonyms, equivalent calculations, reordered statements, and accurately reformatted structured data.
- Accept additional detail only when it is non-conflicting and does not alter or obscure the expected meaning.
- Treat equivalent information expressed in text, objects, arrays, or another representation as matching when the meaning is preserved.
- Score false for a wrong conclusion, contradicted fact, missing required detail, altered constraint, unsupported claim, misleading addition, or changed relationship between facts.

## What Is Material For This Support Agent
- Material: the kind of reply (steps, a decline, or a clarifying question), any limitation the expected output states, and the screens and actions needed to finish the task.
- Not material: confirmations of what the user will see, optional alternatives (for example Face ID or passcode), the exact wording of a decline or whether it names the topic, the example options a clarifying question lists, and a minor step the user can skip and still finish the task.
- A different valid route to the same result is a match.

## Decision Rules
1. Identify the expected output's material claims, facts, constraints, conclusions, and relationships.
2. Compare the actual output against each semantic requirement.
3. Ignore purely structural or formatting differences that do not change meaning.
4. Return true only if all material semantic requirements are preserved.
5. Return false if either value is missing, the expected meaning is unclear, or any material semantic mismatch remains.

## Examples
- Expected: "The capital of France is Paris." Actual: "Paris is the capital of France." → true
- Expected: {"answer": "Paris"} Actual: "The answer is Paris." → true
- Expected: ["refund", "invoice"] Actual: "The required items are refund and invoice." → true
- Expected: {"answer": "Paris", "country": "France"} Actual: "The answer is Paris." → false
- Expected: "Return YES or NO." Actual: "The correct answer is maybe." → false
True only when the actual output preserves every material semantic requirement in the expected output; false otherwise.

Actual assistant output: {{assistant_output}}
Expected output: {{expected_output}}"""


def _expect(expected_output: object) -> dict:
    if not isinstance(expected_output, dict):
        raise ValueError("Dataset item is missing expectedOutput.")
    return expected_output


def decide_behavior(messages: list[dict], answer: str) -> dict:
    """Ask the OpenAI Decisions API for one of reply / defer_question / ask_follow_up."""
    response = httpx.post(
        "https://api.openai.com/v1/decisions",
        headers={"Authorization": f"Bearer {env.openai_api_key}"},
        json={
            "model": DECISION_MODEL,
            "input": [*messages, {"role": "assistant", "content": answer}],
            "questions": [
                {
                    "type": "choice",
                    "name": "behavior",
                    "instructions": "How did the assistant handle the user's latest request?",
                    "choices": [
                        {
                            "value": "defer_question",
                            "description": "Declines the request itself because it is out of scope, even if it then offers other help.",
                        },
                        {
                            "value": "reply",
                            "description": "Gives help with the request the user actually asked. It may mention a limitation along the way.",
                        },
                        {
                            "value": "ask_follow_up",
                            "description": "Asks the user a clarifying question instead of answering yet.",
                        },
                    ],
                }
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    answers = response.json().get("answers") or []
    result = answers[0] if answers else None
    if not result or result.get("type") != "choice":
        return {"behavior": "refusal"}
    return {"behavior": result.get("choice"), "confidence": result.get("confidence")}


def _parse_correctness(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return False


def score_correctness(answer: str, ideal_answer: str) -> dict:
    from langfuse.openai import OpenAI

    prompt = CORRECTNESS_PROMPT.replace("{{assistant_output}}", answer).replace(
        "{{expected_output}}", ideal_answer
    )
    client = OpenAI(api_key=env.openai_api_key)
    response = client.chat.completions.create(
        model=env.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": 'Follow the evaluation instructions in the user message. Return JSON only: {"score": true or false, "reasoning": "short explanation"}.',
            },
            {"role": "user", "content": prompt},
        ],
    )
    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}
    passed = _parse_correctness(parsed.get("score"))
    reasoning = parsed.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        reasoning = (
            "Preserves the expected material meaning."
            if passed
            else "Does not preserve the expected material meaning."
        )
    return {"score": 1 if passed else 0, "reasoning": reasoning.strip()}


def _runtime_request(item_input: dict) -> ChatRequest:
    now = datetime.now(timezone.utc).isoformat()
    messages = [
        ChatMessage(
            id=f"dataset-message-{index + 1}",
            role=message["role"],
            content=message["content"],
            timestamp=now,
        )
        for index, message in enumerate(item_input["messages"])
    ]
    return ChatRequest(
        session_id=f"dataset-{uuid4()}",
        user_id="dataset-runner",
        messages=messages,
    )


def behavior_evaluator(*, input, output, expected_output, **_kwargs):
    from langfuse import Evaluation

    expected = _expect(expected_output)
    decision = decide_behavior(input["messages"], output)
    behavior = decision["behavior"]
    confidence = decision.get("confidence")
    confidence_text = "" if confidence is None else f" (confidence {float(confidence):.2f})"
    return Evaluation(
        name="behavior_match",
        value=1 if behavior == expected["expectedBehavior"] else 0,
        comment=f"Expected {expected['expectedBehavior']}, got {behavior}{confidence_text}.",
    )


def correctness_evaluator(*, output, expected_output, **_kwargs):
    from langfuse import Evaluation

    expected = _expect(expected_output)
    judged = score_correctness(output, expected["idealAnswer"])
    return Evaluation(name="correctness", value=judged["score"], comment=judged["reasoning"])


def task(*, item, **_kwargs):
    response = run_support_conversation(_runtime_request(item.input))
    return response.answer


def main() -> None:
    if not env.langfuse_configured:
        raise SystemExit("Langfuse credentials are required to run dataset experiments.")
    if not env.openai_api_key:
        raise SystemExit(
            "OPENAI_API_KEY is required to run the agent, the behavior decision, and the correctness judge."
        )

    from langfuse import get_client

    langfuse = get_client()
    dataset = langfuse.get_dataset(env.dataset_name)
    run_name = f"dad-it-support-{datetime.now(timezone.utc).isoformat()}"
    result = dataset.run_experiment(
        name="Dad IT Support Agent experiment",
        run_name=run_name,
        description="Workshop dataset run for the Dad IT Support Agent",
        metadata={"model": env.openai_model},
        max_concurrency=1,
        task=task,
        evaluators=[behavior_evaluator, correctness_evaluator],
    )
    print(result.format())
    langfuse.flush()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
