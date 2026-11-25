#!/bin/bash
set -e

echo "Setting up the Langfuse Workshop..."

if ! command -v uv &> /dev/null; then
  echo "Error: uv is not installed."
  echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "Installing dependencies..."
uv sync

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "Created .env from .env.example."
  echo "Fill in your API keys in .env before the later chapters."
else
  echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Fill in OPENAI_API_KEY and LANGFUSE_* in .env"
echo "  2. Start the app: uv run python -m app.server"
echo "  3. Open http://127.0.0.1:3333"
echo "  4. Follow docs/learner/00-setup.md"
