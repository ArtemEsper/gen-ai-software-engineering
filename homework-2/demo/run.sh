#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

cd "$ROOT"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Starting server at http://localhost:8000 ..."
echo "API docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
