"""Seed the 20 traces for section 4.1 Error analysis.

The TypeScript workshop clones an OpenTelemetry export and replays it.
This port writes the same scenarios through the Python SDK so each trace
has the workshop shape: one `dad-it-support-chat-turn` agent root, tool
observations, and a generation whose output is the seeded answer.

Not idempotent: every run creates 20 new traces.

    uv run python scripts/seed_error_analysis.py
    uv run python scripts/seed_error_analysis.py --dry-run
    uv run python scripts/seed_error_analysis.py --check
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone

import _bootstrap  # noqa: F401
from error_analysis_data import SCENARIOS, assert_scenarios

SEED_TAG = "error-analysis-seed"


def _messages(turns: list[dict], end: datetime) -> list[dict]:
    messages = []
    for index, turn in enumerate(turns):
        timestamp = end - timedelta(seconds=20 * (len(turns) - index))
        messages.append(
            {
                "role": turn["role"],
                "content": turn["content"],
                "id": f"turn-{index}",
                "timestamp": timestamp.isoformat(),
            }
        )
    return messages


def _print_plan() -> None:
    counts: dict[str, int] = {}
    for scenario in SCENARIOS:
        counts[scenario["mode"]] = counts.get(scenario["mode"], 0) + 1
    print(
        "Error-analysis seed: "
        + ", ".join(f"{count} {mode}" for mode, count in counts.items())
        + f" ({len(SCENARIOS)} traces, tag {SEED_TAG})."
    )


def seed() -> None:
    from langfuse import get_client, propagate_attributes

    from app.env import env
    from app.support_data import get_support_context

    if not env.langfuse_configured:
        raise SystemExit("Langfuse credentials are required to seed error-analysis traces.")

    langfuse = get_client()
    context = get_support_context()
    context_payload = {
        "ok": True,
        "context": {
            "id": context["id"],
            "label": context["label"],
            "devices": context["devices"],
            "deviceSummary": context["deviceSummary"],
            "responseStyle": context["responseStyle"],
            "scopeHighlights": context["scopeHighlights"],
            "notableApps": context["notableApps"],
        },
    }
    end = datetime.now(timezone.utc)
    for index, scenario in enumerate(SCENARIOS):
        session_id = f"seed-session-ea-{index + 1:03d}"
        user_id = "seed-user-dad"
        messages = _messages(scenario["turns"], end + timedelta(seconds=45 * index))
        guide = scenario["guide"]
        search_output = (
            {
                "ok": True,
                "results": [
                    {
                        "id": "error-analysis-guide",
                        "title": guide["title"],
                        "summary": guide["summary"],
                        "steps": guide["steps"],
                        "caution": None,
                    }
                ],
            }
            if guide
            else {"ok": True, "results": []}
        )
        request = {"messages": messages, "sessionId": session_id, "userId": user_id}
        answer_payload = {
            "answer": scenario["final_answer"],
            "usedTools": ["get_support_context", "search_help_library"] if guide else ["get_support_context"],
        }
        with propagate_attributes(
            user_id=user_id,
            session_id=session_id,
            trace_name="dad-it-support-chat-turn",
            tags=["dad-it-support", "langfuse-workshop", SEED_TAG],
            metadata={"seedSource": "error-analysis", "failureMode": scenario["mode"]},
        ):
            with langfuse.start_as_current_observation(
                name="dad-it-support-chat-turn",
                as_type="agent",
                input=request,
            ) as agent:
                with langfuse.start_as_current_observation(
                    name="get_support_context",
                    as_type="tool",
                    input={},
                ) as tool:
                    tool.update(output=context_payload)
                with langfuse.start_as_current_observation(
                    name="search_help_library",
                    as_type="tool",
                    input={"question": scenario["search_question"]},
                ) as tool:
                    tool.update(output=search_output)
                with langfuse.start_as_current_observation(
                    name="chat.completion",
                    as_type="generation",
                    model=env.openai_model,
                    input={"messages": messages},
                ) as generation:
                    generation.update(output={"content": scenario["final_answer"]})
                agent.update(output=answer_payload)
        print(f"seeded {index + 1:02d}/20 {scenario['mode']}: {messages[-1]['content'][:72]}")
    langfuse.flush()
    print(f"Seeded {len(SCENARIOS)} traces tagged {SEED_TAG}. Running this again adds another 20.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed section 4.1 error-analysis traces.")
    parser.add_argument("--check", action="store_true", help="Validate the 20 scenarios and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without calling Langfuse.")
    args = parser.parse_args()
    assert_scenarios()
    if args.check:
        print(
            "Error-analysis seed OK: 7 ordinary traces, 5 out of scope, "
            "2 subtle impersonation, 2 obvious identity, 4 lengthy."
        )
        return
    _print_plan()
    if args.dry_run:
        for index, scenario in enumerate(SCENARIOS, start=1):
            ask = next(turn["content"] for turn in reversed(scenario["turns"]) if turn["role"] == "user")
            print(f"- {index:02d} {scenario['mode']}: {ask}")
        return
    seed()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
