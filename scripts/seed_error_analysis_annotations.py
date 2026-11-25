"""Write open-coding notes and pass/fail marks for the error-analysis seed.

Finds root observations tagged `error-analysis-seed`, adds any that are missing
from the `error analysis` queue, writes the two annotation scores, and marks
those items completed. Notes describe the reply and do not name the clusters.

Idempotent: each score uses a stable id, so a second run updates the same scores.

    uv run python scripts/seed_error_analysis_annotations.py
    uv run python scripts/seed_error_analysis_annotations.py --dry-run
    uv run python scripts/seed_error_analysis_annotations.py --check
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import _bootstrap  # noqa: F401
from error_analysis_data import (
    SCENARIOS,
    annotation_for,
    annotation_key,
    assert_annotations,
    last_user_content,
)

SEED_TAG = "error-analysis-seed"
DEFAULT_QUEUE_NAME = "error analysis"
OPEN_CODING_NAME = "open coding"
PASS_FAIL_NAME = "pass or fail"


def _score_id(observation_id: str, name: str) -> str:
    digest = hashlib.sha256(f"error-analysis:{observation_id}:{name}".encode()).hexdigest()
    return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"


class LangfuseApi:
    def __init__(self) -> None:
        from app.env import env

        if not env.langfuse_configured:
            raise SystemExit("Langfuse credentials are required to seed annotations.")
        self.base_url = env.langfuse_base_url.rstrip("/")
        token = base64.b64encode(
            f"{env.langfuse_public_key}:{env.langfuse_secret_key}".encode()
        ).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    def request(self, method: str, path: str, body: object | None = None, query: dict | None = None):
        url = self.base_url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read().decode()
                status = response.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:800]
            raise SystemExit(f"{method} {path} failed ({exc.code}): {detail}") from exc
        if status == 207:
            raise SystemExit(f"{method} {path} partially rejected scores: {raw[:800]}")
        return json.loads(raw) if raw else None

    def list_pages(self, path: str, query: dict | None = None) -> list:
        rows: list = []
        page = 1
        while True:
            body = self.request("GET", path, query={**(query or {}), "page": str(page), "limit": "100"})
            rows.extend(body.get("data") or [])
            total = (body.get("meta") or {}).get("totalPages") or 1
            if page >= total:
                return rows
            page += 1


def _parse_json(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _messages_from_input(value) -> list:
    parsed = _parse_json(value)
    if not isinstance(parsed, dict):
        return []
    messages = parsed.get("messages")
    return messages if isinstance(messages, list) else []


def _answer_from_output(value) -> str:
    parsed = _parse_json(value)
    if isinstance(parsed, dict) and isinstance(parsed.get("answer"), str):
        return parsed["answer"].strip()
    return ""


def _list_roots(api: LangfuseApi) -> list[dict]:
    rows: list[dict] = []
    cursor = None
    filter_value = json.dumps(
        [
            {"type": "arrayOptions", "column": "traceTags", "operator": "any of", "value": [SEED_TAG]},
            {"type": "string", "column": "name", "operator": "=", "value": "dad-it-support-chat-turn"},
            {"type": "boolean", "column": "isRootObservation", "operator": "=", "value": True},
        ]
    )
    while True:
        query = {
            "fields": "core,basic,io",
            "fromStartTime": "2020-01-01T00:00:00.000Z",
            "limit": "100",
            "filter": filter_value,
        }
        if cursor:
            query["cursor"] = cursor
        body = api.request("GET", "/api/public/v2/observations", query=query)
        rows.extend(body.get("data") or [])
        cursor = (body.get("meta") or {}).get("cursor")
        if not cursor:
            return rows


def _queue_configs(configs: list[dict]) -> tuple[dict, dict]:
    open_coding = next(
        (config for config in configs if config.get("dataType") == "TEXT" and config.get("name") == OPEN_CODING_NAME),
        None,
    )
    pass_fail = None
    for config in configs:
        labels = [category.get("label", "").lower() for category in (config.get("categories") or [])]
        if (
            config.get("dataType") == "CATEGORICAL"
            and config.get("name") == PASS_FAIL_NAME
            and "pass" in labels
            and "fail" in labels
        ):
            pass_fail = config
    if not open_coding or not pass_fail:
        raise SystemExit(
            f'Queue needs a text config "{OPEN_CODING_NAME}" and a categorical config '
            f'"{PASS_FAIL_NAME}" with pass and fail.'
        )
    return open_coding, pass_fail


def annotate(queue_name: str, dry_run: bool) -> None:
    api = LangfuseApi()
    templates = {annotation_for(scenario)["key"]: annotation_for(scenario) for scenario in SCENARIOS}
    queues = api.list_pages("/api/public/annotation-queues")
    queue = next((entry for entry in queues if entry.get("name") == queue_name), None)
    if queue is None:
        found = ", ".join(entry.get("name", "") for entry in queues) or "none"
        raise SystemExit(f'No annotation queue named "{queue_name}". Found: {found}.')
    configs = [api.request("GET", f"/api/public/score-configs/{config_id}") for config_id in queue["scoreConfigIds"]]
    open_coding, pass_fail = _queue_configs(configs)
    observations = _list_roots(api)
    if not observations:
        raise SystemExit(f"No root observations tagged {SEED_TAG}. Seed traces first.")

    planned = []
    for observation in observations:
        ask = last_user_content(_messages_from_input(observation.get("input")))
        answer = _answer_from_output(observation.get("output"))
        annotation = templates.get(annotation_key(ask, answer))
        if annotation is None:
            raise SystemExit(
                f"Observation {observation.get('id')} does not match a scenario. Last question: {ask[:80]}"
            )
        planned.append((observation, annotation))

    counts = {"pass": 0, "fail": 0}
    for _observation, annotation in planned:
        counts[annotation["pass_fail"]] += 1
    verb = "Would annotate" if dry_run else "Annotating"
    print(f'{verb} {len(planned)} observations on "{queue["name"]}": {counts["pass"]} pass, {counts["fail"]} fail.')
    if dry_run:
        for _observation, annotation in planned:
            print(f"- {annotation['pass_fail']}: {annotation['note']}")
        return

    items = api.list_pages(f"/api/public/annotation-queues/{queue['id']}/items")
    by_object = {
        item["objectId"]: item
        for item in items
        if item.get("objectType") == "OBSERVATION"
    }
    now = datetime.now(timezone.utc).isoformat()
    for observation, annotation in planned:
        item = by_object.get(observation["id"])
        if item is None:
            item = api.request(
                "POST",
                f"/api/public/annotation-queues/{queue['id']}/items",
                {"objectId": observation["id"], "objectType": "OBSERVATION", "status": "PENDING"},
            )
            by_object[observation["id"]] = item
        shared = {
            "traceId": observation["traceId"],
            "observationId": observation["id"],
            "queueId": queue["id"],
            "source": "ANNOTATION",
            "timestamp": now,
            "environment": observation.get("environment"),
        }
        for config, value, data_type in (
            (open_coding, annotation["note"], "TEXT"),
            (pass_fail, annotation["pass_fail"], "CATEGORICAL"),
        ):
            api.request(
                "POST",
                "/api/public/scores",
                {
                    **shared,
                    "id": _score_id(observation["id"], config["name"]),
                    "name": config["name"],
                    "configId": config["id"],
                    "dataType": data_type,
                    "value": value,
                },
            )
    completed = 0
    for observation, _annotation in planned:
        item = by_object[observation["id"]]
        if item.get("status") != "COMPLETED":
            api.request(
                "PATCH",
                f"/api/public/annotation-queues/{queue['id']}/items/{item['id']}",
                {"status": "COMPLETED"},
            )
            completed += 1
    print(f"Wrote {len(planned) * 2} scores and completed {completed} queue items.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed error-analysis annotation scores.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--queue", default=DEFAULT_QUEUE_NAME)
    args = parser.parse_args()
    assert_annotations()
    if args.check:
        print(f"Error-analysis annotations OK: {len(SCENARIOS)} notes, 7 pass and 13 fail.")
        return
    annotate(args.queue, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
