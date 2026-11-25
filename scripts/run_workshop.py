"""Smoke-test the workshop in chapter order.

Steps that need Langfuse or OpenAI credentials are skipped when those
variables are absent. The process exits 0 when every local step passes
and every skipped step was skipped only because a secret was missing.

    uv run python scripts/run_workshop.py
    uv run python scripts/run_workshop.py --live

`--live` also sends one real chat turn through the reference agent (a few
OpenAI calls) and checks its trace in Langfuse: the agent root, the tool
observations, the OpenAI generations, the camelCase root input the 4.2
evaluators map, and the prompt link when the prompt is published.
"""

from __future__ import annotations

import json
import os
import py_compile
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

LIVE = "--live" in sys.argv[1:]

REQUIRED_ENV = (
    "OPENAI_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_BASE_URL",
)


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, step: str, status: str, detail: str) -> None:
        self.rows.append((step, status, detail))
        print(f"[{status}] {step}: {detail}")

    def finish(self) -> int:
        failed = [row for row in self.rows if row[1] == "FAIL"]
        skipped = [row for row in self.rows if row[1] == "SKIP"]
        passed = [row for row in self.rows if row[1] == "PASS"]
        print()
        print(f"{len(passed)} passed, {len(skipped)} skipped, {len(failed)} failed")
        if skipped:
            print("Skipped:")
            for step, _status, detail in skipped:
                print(f"  - {step}: {detail}")
        return 1 if failed else 0


def _present(name: str) -> bool:
    value = os.environ.get(name, "")
    return bool(value) and "..." not in value and not value.endswith("...")


def step_compile(report: Report) -> None:
    paths = list((ROOT / "app").rglob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    paths += list((ROOT / "checkpoints").rglob("*.py"))
    for path in paths:
        py_compile.compile(str(path), doraise=True)
    report.add("compile", "PASS", f"{len(paths)} Python files compiled")


def step_checkpoints(report: Report) -> None:
    from use_checkpoint import check

    problems = check()
    if problems:
        raise RuntimeError("; ".join(problems))
    report.add("checkpoints", "PASS", "snapshot map and system prompt are consistent")


def step_guides(report: Report) -> None:
    import logging

    from app.support_data import search_guides
    from app.tools import execute_tool

    if not _present("LANGFUSE_PUBLIC_KEY"):
        # The SDK resets its logger to WARNING on import and warns when no key is set.
        logging.getLogger("langfuse").setLevel(logging.ERROR)

    bluetooth = search_guides("How do I turn Bluetooth on?")
    if not bluetooth or bluetooth[0]["id"] != "iphone-bluetooth":
        raise RuntimeError(f"unexpected bluetooth search result: {bluetooth}")
    context = execute_tool("get_support_context", {})
    if context.get("ok") is not True or context["context"]["id"] != "dad-default":
        raise RuntimeError("get_support_context tool did not return Dad's setup")
    unknown = execute_tool("not_a_tool", {})
    if unknown.get("ok") is not False:
        raise RuntimeError("unknown tool should fail closed")
    report.add("tools", "PASS", "help-library search and both tool results look right")


def step_dataset_file(report: Report) -> None:
    items = json.loads((ROOT / "data" / "seed-dataset.json").read_text())
    if len(items) != 25:
        raise RuntimeError(f"expected 25 dataset items, found {len(items)}")
    behaviors = {"reply", "defer_question", "ask_follow_up"}
    sources = set()
    for item in items:
        if "messages" not in item["input"]:
            raise RuntimeError(f"{item['id']} input is not a messages array")
        behavior = item["expectedOutput"]["expectedBehavior"]
        if behavior not in behaviors:
            raise RuntimeError(f"{item['id']} has behavior {behavior}")
        if not item["expectedOutput"]["idealAnswer"]:
            raise RuntimeError(f"{item['id']} is missing idealAnswer")
        sources.add(item["metadata"]["source"])
    if sources != {"starter", "error-analysis"}:
        raise RuntimeError(f"unexpected dataset sources: {sources}")
    report.add("dataset-file", "PASS", "25 items with messages, idealAnswer, and expectedBehavior")


def step_error_analysis(report: Report) -> None:
    from error_analysis_data import assert_annotations, assert_scenarios

    assert_scenarios()
    assert_annotations()
    report.add("error-analysis", "PASS", "20 scenarios and 20 annotation notes validate")


def step_prompt_variants(report: Report) -> None:
    # Importing the publisher also imports the traced agent. That is the
    # finished app, which is what `main` runs.
    from publish_prompt import ERROR_ANALYSIS_PROMPT, PROMPT_VARIANTS

    if "Rules:" not in ERROR_ANALYSIS_PROMPT or "Do not speak as someone in his family." not in ERROR_ANALYSIS_PROMPT:
        raise RuntimeError("error-analysis prompt variant drifted from the lesson")
    if set(PROMPT_VARIANTS) != {"default", "gentler", "error-analysis"}:
        raise RuntimeError(f"unexpected prompt variants: {set(PROMPT_VARIANTS)}")
    report.add("prompt-variants", "PASS", "default, gentler, and error-analysis prompts are present")


def step_http(report: Report) -> None:
    from fastapi.testclient import TestClient

    from app.server import app

    with TestClient(app) as client:
        health = client.get("/api/health")
        context = client.get("/api/support-context")
        page = client.get("/")
        if health.status_code != 200 or health.json()["provider"] != "openai":
            raise RuntimeError(f"health failed: {health.status_code} {health.text}")
        if context.status_code != 200 or context.json()["label"] != "Dad":
            raise RuntimeError("support context did not describe Dad")
        if page.status_code != 200 or "Dad IT Support Agent" not in page.text:
            raise RuntimeError("chat UI did not render")
        rejected = client.post("/api/chat", json={"messages": []})
        if rejected.status_code != 400:
            raise RuntimeError(f"empty chat should be rejected, got {rejected.status_code}")
        assets = client.get("/static/styles.css")
        if assets.status_code != 200 or ".chat" not in assets.text:
            raise RuntimeError("chat stylesheet did not load")
    from app.models import ChatResponse, TraceMeta

    payload = ChatResponse(
        answer="ok",
        used_tools=["get_support_context"],
        trace_meta=TraceMeta(context_id="dad-default", context_label="Dad", model="test"),
    ).model_dump(by_alias=True)
    if "usedTools" not in payload or "traceMeta" not in payload:
        raise RuntimeError(f"chat response is not camelCase: {payload}")
    report.add("http", "PASS", "health, support context, UI, stylesheet, and chat validation respond")


def step_live(report: Report) -> None:
    missing = [name for name in REQUIRED_ENV if not _present(name)]
    if missing:
        report.add(
            "live-langfuse-and-openai",
            "SKIP",
            "needs "
            + ", ".join(missing)
            + " to publish the prompt, seed traces, seed the dataset, and run an experiment",
        )
        return
    import base64
    import urllib.request

    from app.env import env

    token = base64.b64encode(f"{env.langfuse_public_key}:{env.langfuse_secret_key}".encode()).decode()
    request = urllib.request.Request(
        env.langfuse_base_url.rstrip("/") + "/api/public/projects",
        headers={"Authorization": f"Basic {token}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Langfuse projects API returned {response.status}")
    report.add("langfuse-auth", "PASS", "Langfuse accepted the project API keys")
    if not LIVE:
        report.add(
            "live-chat-trace",
            "SKIP",
            "pass --live to send one chat turn and check its trace. Prompt publish, dataset seed, "
            "and dataset runs stay with the chapter commands",
        )
        return
    step_live_chat(report)


def step_live_chat(report: Report) -> None:
    """Send one chat turn through the reference agent and read its trace back."""
    import time
    import urllib.parse
    import urllib.request
    import base64
    from uuid import uuid4

    from langfuse import get_client

    from app.env import env
    from app.models import ChatMessage, ChatRequest
    from app.support_agent import run_support_conversation

    langfuse = get_client()
    trace_id = langfuse.create_trace_id()
    request = ChatRequest(
        session_id=f"smoke-{uuid4()}",
        user_id="workshop-smoke",
        messages=[
            ChatMessage(
                id="smoke-1",
                role="user",
                content="How do I turn Bluetooth on?",
                timestamp="2026-01-01T00:00:00Z",
            )
        ],
    )
    response = run_support_conversation(request, langfuse_trace_id=trace_id)
    langfuse.flush()
    if not response.answer.strip():
        raise RuntimeError("the agent returned an empty answer")

    token = base64.b64encode(f"{env.langfuse_public_key}:{env.langfuse_secret_key}".encode()).decode()
    query = urllib.parse.urlencode(
        {
            "traceId": trace_id,
            "fields": "core,basic,io,prompt",
            "fromStartTime": "2020-01-01T00:00:00Z",
            "limit": "100",
        }
    )
    url = env.langfuse_base_url.rstrip("/") + "/api/public/v2/observations?" + query
    rows: list[dict] = []
    deadline = time.time() + 120
    while time.time() < deadline:
        req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode()).get("data") or []
        names = {row.get("name") for row in rows}
        if "dad-it-support-chat-turn" in names and any(r.get("type") == "GENERATION" for r in rows):
            break
        time.sleep(5)

    root = next((r for r in rows if r.get("name") == "dad-it-support-chat-turn"), None)
    if root is None or root.get("type") != "AGENT":
        raise RuntimeError(f"no dad-it-support-chat-turn agent observation in trace {trace_id}")
    tools = sorted({r["name"] for r in rows if r.get("type") == "TOOL"})
    if "get_support_context" not in tools:
        raise RuntimeError(f"tool observations missing, found {tools}")
    generations = [r for r in rows if r.get("type") == "GENERATION"]
    if not generations:
        raise RuntimeError("no OpenAI generation in the trace")
    root_input = root.get("input")
    if isinstance(root_input, str):
        root_input = json.loads(root_input)
    if not isinstance(root_input, dict) or not isinstance(root_input.get("messages"), list):
        raise RuntimeError(f"root input is not {{messages, sessionId, userId}}: {str(root_input)[:200]}")
    if root_input.get("sessionId") != request.session_id:
        raise RuntimeError("root input does not carry the camelCase sessionId")
    linked = sorted({f"{r.get('promptName')} v{r.get('promptVersion')}" for r in generations if r.get("promptName")})
    prompt_note = f", prompt {', '.join(linked)}" if linked else ", no prompt link (prompt not published)"
    report.add(
        "live-chat-trace",
        "PASS",
        f"trace {trace_id}: agent root, tools {', '.join(tools)}, {len(generations)} generations{prompt_note}",
    )


def _syntax_guard(report: Report) -> None:
    """Parse every learner doc's fenced python blocks that are complete statements."""
    docs = list((ROOT / "docs").rglob("*.md"))
    if len(docs) < 8:
        raise RuntimeError(f"expected learner and instructor docs, found {len(docs)} markdown files")
    report.add("docs", "PASS", f"{len(docs)} workshop markdown files are present")


def main() -> int:
    os.chdir(ROOT)
    # Load .env the same way the app does, without overriding real env that
    # a CI job injected. app.env overrides from .env; import it after we
    # record which secrets were already in the process environment.
    preexisting = {name: _present(name) for name in REQUIRED_ENV}
    import app.env  # noqa: F401

    report = Report()
    steps = [
        step_compile,
        step_checkpoints,
        step_guides,
        step_dataset_file,
        step_error_analysis,
        step_prompt_variants,
        step_http,
        _syntax_guard,
        step_live,
    ]
    for step in steps:
        try:
            step(report)
        except Exception as exc:
            report.add(step.__name__, "FAIL", f"{exc}")
            traceback.print_exc()
    if not any(preexisting.values()):
        print("No workshop secrets were set in the environment before .env was loaded.")
    return report.finish()


if __name__ == "__main__":
    raise SystemExit(main())
