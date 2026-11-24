"""Refresh workshop screenshots, or report why they were not refreshed.

Langfuse Cloud screenshots in docs/images/ are reused from the upstream
TypeScript workshop because they show the Langfuse UI, which does not depend
on the sample app's language. Trace screenshots match this port when the
observation names are unchanged (`dad-it-support-chat-turn`,
`get_support_context`, `search_help_library`).

A full refresh needs a logged-in browser session. This script does not store
passwords. Provide either:

    LANGFUSE_PROJECT_URL=https://cloud.langfuse.com/project/<id>
    LANGFUSE_UI_STORAGE_STATE=/absolute/path/to/playwright-storage.json

or set both LANGFUSE_UI_EMAIL and LANGFUSE_UI_PASSWORD together with
LANGFUSE_PROJECT_URL. Playwright is an optional dependency:

    uv run --with playwright python scripts/refresh_screenshots.py
    uv run --with playwright python -m playwright install chromium

Without those values the script lists every checked-in screenshot, marks it
as reused from upstream, and exits 0.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
OUTPUT = ROOT / "docs" / "images" / "refresh"

# Views a logged-in session can recapture. Paths are relative to the project URL.
CAPTURES = {
    "tracing/02-tracing-step-1.png": "/traces",
    "tracing/02-tracing-step-2.png": "/traces",
    "tracing/02-tracing-step-3.png": "/traces",
    "prompt-management/03-prompt-management-published-prompt.png": "/prompts",
    "prompt-management/03-prompt-management-prompt-badge.png": "/traces",
    "datasets/05-dataset-items.png": "/datasets",
    "evaluate-a-change/side-by-side-runs.png": "/datasets",
    "monitoring/home-dashboard.png": "/dashboards",
}


def _flagged() -> list[Path]:
    return sorted(path for path in IMAGES.rglob("*") if path.is_file() and path.suffix.lower() == ".png")


def _missing_env() -> list[str]:
    required = ["LANGFUSE_PROJECT_URL"]
    has_state = bool(os.environ.get("LANGFUSE_UI_STORAGE_STATE"))
    has_password = bool(os.environ.get("LANGFUSE_UI_EMAIL") and os.environ.get("LANGFUSE_UI_PASSWORD"))
    missing = [name for name in required if not os.environ.get(name)]
    if not has_state and not has_password:
        missing.append("LANGFUSE_UI_STORAGE_STATE or LANGFUSE_UI_EMAIL + LANGFUSE_UI_PASSWORD")
    return missing


def _report_reuse(reason: str) -> int:
    print(reason)
    print("Checked-in screenshots kept as upstream Langfuse UI captures:")
    for path in _flagged():
        print(f"  - {path.relative_to(ROOT)}")
    print("Exit 0. Set the env vars in the module docstring to refresh them.")
    return 0


def _refresh() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return _report_reuse("Playwright is not installed, so screenshots were not recaptured.")

    project_url = os.environ["LANGFUSE_PROJECT_URL"].rstrip("/")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context_kwargs = {}
        storage = os.environ.get("LANGFUSE_UI_STORAGE_STATE")
        if storage:
            context_kwargs["storage_state"] = storage
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        if not storage:
            page.goto("https://cloud.langfuse.com/auth/sign-in", wait_until="networkidle")
            page.fill('input[type="email"]', os.environ["LANGFUSE_UI_EMAIL"])
            page.fill('input[type="password"]', os.environ["LANGFUSE_UI_PASSWORD"])
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
        for relative, route in CAPTURES.items():
            destination = OUTPUT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            page.goto(project_url + route, wait_until="networkidle")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(destination), full_page=True)
            print(f"wrote {destination.relative_to(ROOT)}")
        browser.close()
    print("New captures are in docs/images/refresh/. Compare them before replacing docs/images/.")
    return 0


def main() -> int:
    missing = _missing_env()
    if missing:
        return _report_reuse("Not refreshing screenshots. Missing " + ", ".join(missing) + ".")
    try:
        return _refresh()
    except Exception as exc:
        print(f"Screenshot refresh failed: {exc}", file=sys.stderr)
        print("The checked-in upstream screenshots were left unchanged.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
