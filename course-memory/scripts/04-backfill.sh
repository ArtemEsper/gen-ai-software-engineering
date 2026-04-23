#!/usr/bin/env bash
# ============================================================
# 04-backfill.sh — Backfill Claude Code transcript history
# Usage: bash course-memory/scripts/04-backfill.sh <hw_number>
# Transcript dir: ~/.claude/projects/-Users-macbook-Documents-GitHub-gen-ai-software-engineering/
# ============================================================
set -euo pipefail

HW_NUM="${1:?Usage: $0 <hw_number>}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/course-memory/scripts/_vault.sh"

SCOPE="hw${HW_NUM}_convos"
HELPER="$REPO_ROOT/course-memory/scripts/_transcript.py"
TRANSCRIPT_DIR="$HOME/.claude/projects/-Users-macbook-Documents-GitHub-gen-ai-software-engineering"

[ -d "$TRANSCRIPT_DIR" ] || {
  echo "ERROR: transcript dir not found: $TRANSCRIPT_DIR" >&2
  echo "Check with: ls ~/.claude/projects/" >&2; exit 1; }

JSONL_FILES=()
while IFS= read -r -d '' f; do JSONL_FILES+=("$f"); done \
  < <(find "$TRANSCRIPT_DIR" -maxdepth 1 -name "*.jsonl" -print0)

[ ${#JSONL_FILES[@]} -gt 0 ] || { echo "No .jsonl files found." >&2; exit 1; }

echo "=== Backfilling transcripts → $SCOPE (${#JSONL_FILES[@]} file(s)) ==="
TMPDIR_CUSTOM="$(mktemp -d /tmp/mp_backfill_XXXXXX)"
trap 'rm -rf "$TMPDIR_CUSTOM"' EXIT

TOTAL=0
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

for JSONL in "${JSONL_FILES[@]}"; do
  BASE=$(basename "$JSONL" .jsonl)
  echo "Processing: $BASE.jsonl"
  BLOBS="$TMPDIR_CUSTOM/${BASE}_blobs.json"
  python3 "$HELPER" "$JSONL" "$SCOPE" 5000 > "$BLOBS"
  COUNT=$(python3 -c "import json; print(len(json.load(open('$BLOBS'))))")
  [ "$COUNT" -eq 0 ] && { echo "  No messages — skipping."; continue; }
  echo "  Extracted $COUNT chunk(s)"

  for IDX in $(seq 0 $((COUNT-1))); do
    BLOB="$TMPDIR_CUSTOM/${BASE}_chunk_${IDX}.json"
    python3 -c "import json; blobs=json.load(open('$BLOBS')); print(json.dumps(blobs[$IDX],indent=2))" > "$BLOB"
    TITLE=$(python3 -c "import json; print(json.load(open('$BLOB'))['title'])")
    echo -n "  Chunk $((IDX+1))/$COUNT: $TITLE ... "
    SID=$(vault_save "$BLOB" "$TITLE")
    echo "$SID"; TOTAL=$((TOTAL+1))
  done
done

echo ""; echo "Done: $TOTAL chunk(s) saved."
