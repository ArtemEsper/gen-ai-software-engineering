#!/usr/bin/env bash
# ============================================================
# 07-record-note.sh — Append a distilled note to notes/ markdown
# Usage: bash course-memory/scripts/07-record-note.sh <type> "<text>"
# Types: pitfall | decision | prompt
# ============================================================
set -euo pipefail

TYPE="${1:?Usage: $0 <pitfall|decision|prompt> \"<text>\"}"
TEXT="${2:?No text provided}"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NOTES_DIR="$REPO_ROOT/course-memory/notes"

case "$TYPE" in
  pitfall)  FILE="$NOTES_DIR/pitfalls.md"   ;;
  decision) FILE="$NOTES_DIR/decisions.md"  ;;
  prompt)   FILE="$NOTES_DIR/prompt-log.md" ;;
  *) echo "ERROR: type must be pitfall | decision | prompt" >&2; exit 1 ;;
esac

NOW=$(date -u +"%Y-%m-%d %H:%M UTC")
DATE=$(date -u +"%Y-%m-%d")

cat >> "$FILE" <<EOF

## $DATE — $TYPE

$TEXT

_Recorded: ${NOW}_
EOF

echo "Appended to: $(basename "$FILE")"
tail -6 "$FILE"
