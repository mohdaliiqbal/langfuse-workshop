"""Render the two agent diagrams from their HTML sources at 2x.

    uv run --with playwright python docs/images/source/render.py

Needs a Chromium: `uv run --with playwright python -m playwright install chromium`.
The values in the HTML come from a real Python run (see docs/images/README.md).
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
src = Path(__file__).resolve().parent
jobs = [("process_illustration.html", 850, 267, str(src.parent / "tracing" / "process_illustration.png")),
        ("specs_illustration.html", 840, 366, str(src.parent / "specs_illustration.png"))]
with sync_playwright() as p:
    args = ["--no-sandbox", "--allow-file-access-from-files"]
    try:
        b = p.chromium.launch(args=args)
    except Exception:  # no bundled Chromium: fall back to an installed Chrome
        b = p.chromium.launch(channel="chrome", args=args)
    for name, w, h, out in jobs:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.goto((src / name).as_uri(), wait_until="networkidle"); pg.wait_for_timeout(500)
        pg.screenshot(path=out); pg.close()
    b.close()
