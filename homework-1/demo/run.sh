#!/usr/bin/env bash

# demo/run.sh — Start the Banking Transactions API

set -e

# Navigate to the project root (one level up from demo/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check that Python 3 is available
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is not installed or not on PATH." >&2
  exit 1
fi

# Create a virtual environment if one does not already exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Start the API server
echo ""
echo "Starting Banking Transactions API on http://localhost:8000"
echo "Interactive docs available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
echo ""

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
