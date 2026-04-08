#!/bin/bash
set -e

echo "Setting up Langfuse Workshop..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required="3.10"
if [ "$(printf '%s\n' "$required" "$python_version" | sort -V | head -n1)" != "$required" ]; then
  echo "Error: Python 3.10+ required (found $python_version)"
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

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
echo "  4. Open labs/01-tracing/README.md to start Lab 1"
