"""Seed the 200 traces for section 4.2 Detect topics and issues.

The TypeScript workshop clones an OpenTelemetry export, shifts its
timestamps, and replays it. This port builds the same 200 scenarios
(`scripts/topics_data.py`, identical wording and order) and sends them to
Langfuse's OpenTelemetry endpoint with explicit start times. Each trace has
the workshop shape: one `dad-it-support-chat-turn` agent root, the two tool
observations, and a generation whose output is the seeded answer.

Topics only reads recent traces, so the timestamps matter: traces are 36
minutes apart, about five days in all, and the newest one is about 10 minutes
old. That keeps the batch inside the 7-day window and past the 5-minute wait
before a new trace is summarized. The Langfuse SDK's observation helpers
always start "now", which is why this script uses an OpenTelemetry tracer
directly with the same `langfuse.*` attributes the SDK writes. No scores are
written.

Not idempotent: every run creates 200 new traces.

    uv run python scripts/seed_topics_traces.py
    uv run python scripts/seed_topics_traces.py --dry-run
    uv run python scripts/seed_topics_traces.py --check
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from collections import Counter
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

import _bootstrap  # noqa: F401
from topics_data import (
    LAPTOP_COUNT,
    ORDINARY_COUNT,
    SCENARIOS,
    SEED_TAG,
    STUCK_COUNT,
    assert_scenarios,
    frustrated_count,
    timestamps,
)

ROOT_NAME = "dad-it-support-chat-turn"
USER_ID = "seed-user-dad"


def _ns(moment: datetime) -> int:
    return int(moment.timestamp() * 1_000_000_000)


def _messages(turns: list[dict], end: datetime) -> list[dict]:
    """Same shape as the app's request messages, 20 seconds apart, ending at `end`."""
    return [
        {
            "role": turn["role"],
            "content": turn["content"],
            "id": f"turn-{index}",
            "timestamp": (end - timedelta(seconds=20 * (len(turns) - index))).isoformat().replace("+00:00", "Z"),
        }
        for index, turn in enumerate(turns)
    ]


def _support_context_payload() -> dict:
    from app.support_data import get_support_context

    context = get_support_context()
    return {
        "ok": True,
        "context": {
            key: context[key]
            for key in ("id", "label", "devices", "deviceSummary", "responseStyle", "scopeHighlights", "notableApps")
        },
    }


def _search_output(guide: dict | None) -> dict:
    if not guide:
        return {"ok": True, "results": []}
    return {
        "ok": True,
        "results": [
            {
                "id": "topics-guide",
                "title": guide["title"],
                "summary": guide["summary"],
                "steps": guide["steps"],
                "caution": None,
            }
        ],
    }


def _trace_attributes(index: int) -> dict:
    """Trace-level attributes, set on every span the way `propagate_attributes` does."""
    attributes = {
        "user.id": USER_ID,
        "session.id": f"seed-session-tp-{index + 1:03d}",
        "langfuse.trace.name": ROOT_NAME,
        "langfuse.trace.tags": ["dad-it-support", "langfuse-workshop", SEED_TAG],
        "langfuse.trace.metadata.seedSource": "topics",
    }
    environment = os.environ.get("LANGFUSE_TRACING_ENVIRONMENT")
    if environment:
        attributes["langfuse.environment"] = environment
    return attributes


def _child(tracer, root, shared: dict, start: datetime, name: str, kind: str, offsets: tuple[float, float], attributes: dict) -> None:
    """One child observation under `root`, `offsets` seconds after the trace start."""
    from opentelemetry import trace

    child = tracer.start_span(
        name,
        context=trace.set_span_in_context(root),
        start_time=_ns(start + timedelta(seconds=offsets[0])),
        attributes={**shared, "langfuse.observation.type": kind, **attributes},
    )
    child.end(end_time=_ns(start + timedelta(seconds=offsets[1])))


def write_traces(tracer, now: datetime, model: str, context_payload: dict) -> None:
    """Emit one trace per scenario on `tracer`, oldest first."""
    for index, (scenario, start) in enumerate(zip(SCENARIOS, timestamps(now))):
        shared = _trace_attributes(index)
        messages = _messages(scenario["turns"], start)
        guide = scenario["guide"]
        request = {"messages": messages, "sessionId": shared["session.id"], "userId": USER_ID}
        answer = {
            "answer": scenario["final_answer"],
            "usedTools": ["get_support_context", "search_help_library"] if guide else ["get_support_context"],
        }

        root = tracer.start_span(
            ROOT_NAME,
            start_time=_ns(start),
            attributes={
                **shared,
                "langfuse.observation.type": "agent",
                "langfuse.observation.input": json.dumps(request),
                "langfuse.observation.output": json.dumps(answer),
            },
        )
        _child(tracer, root, shared, start, "get_support_context", "tool", (0.15, 0.25), {
            "langfuse.observation.input": json.dumps({}),
            "langfuse.observation.output": json.dumps(context_payload),
        })
        _child(tracer, root, shared, start, "search_help_library", "tool", (0.3, 0.45), {
            "langfuse.observation.input": json.dumps({"question": scenario["search_question"]}),
            "langfuse.observation.output": json.dumps(_search_output(guide)),
        })
        _child(tracer, root, shared, start, "chat.completion", "generation", (0.5, 3.5), {
            "langfuse.observation.model.name": model,
            "langfuse.observation.input": json.dumps({"messages": messages}),
            "langfuse.observation.output": json.dumps({"content": scenario["final_answer"]}),
        })
        root.end(end_time=_ns(start + timedelta(seconds=3.7)))


class _CountingExporter:
    """Wrap an exporter and remember whether every batch was accepted."""

    def __init__(self, inner) -> None:
        self.inner = inner
        self.exported = 0
        self.failed = 0

    def export(self, spans: Sequence) -> object:
        from opentelemetry.sdk.trace.export import SpanExportResult

        result = self.inner.export(spans)
        if result == SpanExportResult.SUCCESS:
            self.exported += len(spans)
        else:
            self.failed += len(spans)
        return result

    def shutdown(self) -> None:
        self.inner.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return self.inner.force_flush(timeout_millis)


def build_offline(now: datetime | None = None) -> list:
    """Build every span in memory, without network, and check the trace shape."""
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    now = now or datetime.now(timezone.utc)
    memory = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory))
    write_traces(provider.get_tracer("langfuse-workshop.seed-topics"), now, "gpt-test", {"ok": True})
    spans = memory.get_finished_spans()
    roots = [item for item in spans if item.parent is None]
    if len(spans) != 4 * len(SCENARIOS) or len(roots) != len(SCENARIOS):
        raise AssertionError(f"Expected {len(SCENARIOS)} traces of 4 observations, got {len(spans)} spans.")
    if len({item.context.trace_id for item in roots}) != len(SCENARIOS):
        raise AssertionError("Each scenario must be its own trace.")
    for item in roots:
        if item.name != ROOT_NAME or item.attributes["langfuse.observation.type"] != "agent":
            raise AssertionError("Every trace root must be the dad-it-support-chat-turn agent.")
        if not json.loads(item.attributes["langfuse.observation.input"])["messages"]:
            raise AssertionError("The root input must carry the messages array.")
        if SEED_TAG not in item.attributes["langfuse.trace.tags"]:
            raise AssertionError(f"Every trace must be tagged {SEED_TAG}.")
    starts = [item.start_time for item in roots]
    newest = datetime.fromtimestamp(max(starts) / 1e9, timezone.utc)
    oldest = datetime.fromtimestamp(min(starts) / 1e9, timezone.utc)
    if not (timedelta(minutes=5) < now - newest and now - oldest < timedelta(days=7)):
        raise AssertionError("Topics traces must be older than 5 minutes and inside the last 7 days.")
    return spans


def seed() -> int:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from langfuse import __version__ as langfuse_version

    from app.env import env

    if not env.langfuse_configured:
        raise SystemExit("Langfuse credentials are required to seed topics traces.")

    token = base64.b64encode(f"{env.langfuse_public_key}:{env.langfuse_secret_key}".encode()).decode()
    exporter = _CountingExporter(
        OTLPSpanExporter(
            endpoint=env.langfuse_base_url.rstrip("/") + "/api/public/otel/v1/traces",
            # The same headers the Langfuse SDK's own exporter sends.
            headers={
                "Authorization": f"Basic {token}",
                "x-langfuse-sdk-name": "python",
                "x-langfuse-sdk-version": langfuse_version,
                "x-langfuse-public-key": env.langfuse_public_key,
            },
        )
    )
    # A private provider, so nothing else in the process exports through it.
    provider = TracerProvider(resource=Resource.create({"service.name": "langfuse-workshop-seed"}))
    provider.add_span_processor(BatchSpanProcessor(exporter, max_export_batch_size=200))
    now = datetime.now(timezone.utc)
    write_traces(provider.get_tracer("langfuse-workshop.seed-topics"), now, env.openai_model, _support_context_payload())
    provider.force_flush()
    provider.shutdown()
    if exporter.failed:
        print(f"Langfuse rejected {exporter.failed} of {exporter.failed + exporter.exported} spans.", file=sys.stderr)
        return 1
    first, last = timestamps(now)[0], timestamps(now)[-1]
    print(
        f"Seeded {len(SCENARIOS)} traces tagged {SEED_TAG} ({exporter.exported} observations), "
        f"from {first:%Y-%m-%d %H:%M} to {last:%Y-%m-%d %H:%M} UTC. Running this again adds another {len(SCENARIOS)}."
    )
    return 0


def _summary() -> str:
    return (
        f"Topics seed OK: {ORDINARY_COUNT} ordinary, {LAPTOP_COUNT} laptop, "
        f"{STUCK_COUNT} stuck follow-ups, {frustrated_count()} frustrated."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed section 4.2 topics traces.")
    parser.add_argument("--check", action="store_true", help="Validate the 200 scenarios and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Build every trace in memory without calling Langfuse.")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    assert_scenarios(now)
    if args.check:
        print(_summary())
        return 0
    if args.dry_run:
        spans = build_offline(now)
        kinds = Counter(scenario["kind"] for scenario in SCENARIOS)
        print(_summary())
        print(f"Dry run: built {len(spans)} observations for {len(SCENARIOS)} traces ({dict(kinds)}). Nothing was sent.")
        for index, scenario in enumerate(SCENARIOS[:5], start=1):
            ask = next(turn["content"] for turn in reversed(scenario["turns"]) if turn["role"] == "user")
            print(f"- {index:03d} {scenario['kind']}: {ask[:90]}")
        print(f"- ... {len(SCENARIOS) - 5} more")
        return 0
    return seed()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
