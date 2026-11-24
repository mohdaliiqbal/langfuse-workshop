"""Restore the milestone files for one workshop chapter.

The TypeScript workshop does this with `git checkout checkpoint/<name>`.
This port keeps those states as snapshots under `checkpoints/` so a single
branch can move between them without force-pushing tags.

    uv run python scripts/use_checkpoint.py 02-tracing
    uv run python scripts/use_checkpoint.py reference
    uv run python scripts/use_checkpoint.py --check
"""

from __future__ import annotations

import argparse
import filecmp
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
CHECKPOINTS = ROOT / "checkpoints"
MILESTONE_FILES = ("server.py", "support_agent.py", "tools.py")
PROMPT_BEGIN = "# checkpoint-sync:begin system-prompt"
PROMPT_END = "# checkpoint-sync:end system-prompt"

# Chapters 00, 01, and 02 share the untraced base app.
# Chapter 03 is traced, with the prompt still local.
# Chapter 04 onward matches the finished reference on main.
ALIASES = {
    "00-setup": "00-setup",
    "01-base-app": "00-setup",
    "02-tracing": "00-setup",
    "03-prompt-management": "03-prompt-management",
    "04-monitoring": "reference",
    "05-dataset": "reference",
    "06-experiments": "reference",
    "07-evaluation": "reference",
    "08-wrap-up": "reference",
    "reference": "reference",
    "main": "reference",
}


def _prompt_block(path: Path) -> str:
    text = path.read_text()
    start = text.index(PROMPT_BEGIN)
    end = text.index(PROMPT_END)
    return text[start:end]


def check() -> list[str]:
    problems: list[str] = []
    reference_prompt = _prompt_block(APP / "support_agent.py")
    for name in ("00-setup", "03-prompt-management", "reference"):
        directory = CHECKPOINTS / name
        for filename in MILESTONE_FILES:
            path = directory / filename
            if not path.is_file():
                problems.append(f"missing {path.relative_to(ROOT)}")
        agent = directory / "support_agent.py"
        if agent.is_file() and _prompt_block(agent) != reference_prompt:
            problems.append(f"{agent.relative_to(ROOT)} system prompt drifted from app/support_agent.py")
    for filename in MILESTONE_FILES:
        live = APP / filename
        snapshot = CHECKPOINTS / "reference" / filename
        if live.is_file() and snapshot.is_file() and not filecmp.cmp(live, snapshot, shallow=False):
            problems.append(f"checkpoints/reference/{filename} is not a copy of app/{filename}")
    base_tools = (CHECKPOINTS / "00-setup" / "tools.py").read_text()
    traced_tools = (CHECKPOINTS / "reference" / "tools.py").read_text()
    if "@observe" in base_tools:
        problems.append("checkpoints/00-setup/tools.py should not trace tools yet")
    if "@observe" not in traced_tools:
        problems.append("checkpoints/reference/tools.py should trace tools")
    base_agent = (CHECKPOINTS / "00-setup" / "support_agent.py").read_text()
    prompt_agent = (CHECKPOINTS / "03-prompt-management" / "support_agent.py").read_text()
    reference_agent = (CHECKPOINTS / "reference" / "support_agent.py").read_text()
    if "langfuse" in base_agent:
        problems.append("checkpoints/00-setup/support_agent.py should not import Langfuse")
    if "get_prompt" in prompt_agent:
        problems.append("checkpoints/03-prompt-management should still use the local prompt")
    if "get_prompt" not in reference_agent:
        problems.append("reference agent should fetch the Langfuse prompt")
    return problems


def restore(name: str) -> None:
    snapshot = ALIASES[name]
    source = CHECKPOINTS / snapshot
    for filename in MILESTONE_FILES:
        target = APP / filename
        target.write_text((source / filename).read_text())
        print(f"wrote app/{filename} from checkpoints/{snapshot}/{filename}")
    print(f"Checkpoint {name} is now in app/. Restore the finished app with: uv run python scripts/use_checkpoint.py reference")


def main() -> None:
    parser = argparse.ArgumentParser(description="Switch milestone files to a workshop chapter.")
    parser.add_argument("checkpoint", nargs="?", choices=sorted(ALIASES))
    parser.add_argument("--check", action="store_true", help="Validate snapshots without writing files.")
    args = parser.parse_args()
    if args.check or not args.checkpoint:
        problems = check()
        if problems:
            print("\n".join(problems), file=sys.stderr)
            raise SystemExit(1)
        print("Checkpoint snapshots match the chapter map.")
        if not args.checkpoint:
            return
    restore(args.checkpoint)


if __name__ == "__main__":
    main()
