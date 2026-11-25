.PHONY: setup dev smoke screenshots checkpoint-check

setup:
	./setup.sh

dev:
	uv run python -m app.server

smoke:
	uv run python scripts/run_workshop.py

screenshots:
	uv run python scripts/refresh_screenshots.py

checkpoint-check:
	uv run python scripts/use_checkpoint.py --check
