#!/usr/bin/env bash
# ============================================================
# 01-init.sh — Initialize MemPalace and course-memory structure
# Run once per machine before any other script.
# Usage: bash course-memory/scripts/01-init.sh [GEMINI_API_KEY]
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MEMORY_DIR="$REPO_ROOT/course-memory"

echo "=== MemPalace init ==="
command -v npx &>/dev/null || { echo "ERROR: npx not found. Install Node.js." >&2; exit 1; }

if [ -n "${1:-}" ]; then
  npx mempalace init --gemini-key "$1"
else
  npx mempalace init
fi

echo ""
echo "=== Ensuring course-memory structure ==="
mkdir -p "$MEMORY_DIR/notes" "$MEMORY_DIR/scripts" "$MEMORY_DIR/vault"

INDEX="$MEMORY_DIR/notes/index.md"
if [ ! -f "$INDEX" ]; then
  cat > "$INDEX" <<'EOF'
# MemPalace Memory Index

| short_id | scope | title | saved_at |
|---|---|---|---|
EOF
  echo "  Created: notes/index.md"
fi

for NOTE in pitfalls decisions prompt-log; do
  FILE="$MEMORY_DIR/notes/${NOTE}.md"
  [ -f "$FILE" ] || { touch "$FILE"; echo "  Created: notes/${NOTE}.md"; }
done

echo ""
echo "Done. Vault: ~/.mempalace/  |  Local fallback: course-memory/vault/"
echo "Next: bash course-memory/scripts/02-mine-homework.sh 1"
