#!/bin/bash
set -e

echo "Setting up Langfuse Workshop..."

# Check uv is installed
if ! command -v uv &> /dev/null; then
  echo "Error: uv is not installed."
  echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# Install Python 3.14 and dependencies
echo "Installing dependencies..."
uv sync

# Set up .env if not present
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "Created .env from .env.example."
  echo "Please fill in your API keys in .env before proceeding."
else
  echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Fill in your API keys in .env"
echo "  2. Activate the virtual environment: source .venv/bin/activate"
echo "  3. Run the baseline app: python -m app.main"
echo "  4. Open labs/01-langfuse/README.md to start Lab 1"
