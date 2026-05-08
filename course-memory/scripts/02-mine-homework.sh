#!/usr/bin/env bash
# ============================================================
# 02-mine-homework.sh — Mine a homework directory into memory
# Usage: bash course-memory/scripts/02-mine-homework.sh <hw_number>
# Run from repo root after each coding milestone.
# ============================================================
set -euo pipefail

HW_NUM="${1:?Usage: $0 <hw_number>}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/course-memory/scripts/_vault.sh"

HW_DIR="$REPO_ROOT/homework-$HW_NUM"
SCOPE="hw${HW_NUM}_repo"
TMPDIR_CUSTOM="$(mktemp -d /tmp/mp_mine_XXXXXX)"
trap 'rm -rf "$TMPDIR_CUSTOM"' EXIT

[ -d "$HW_DIR" ] || { echo "ERROR: not found: $HW_DIR" >&2; exit 1; }
echo "=== Mining homework-$HW_NUM → $SCOPE ==="

FILES=(
  "src/main.py"
  "src/dspy_generate_homework.py"
  "requirements.txt"
  "README.md"
  "HOWTORUN.md"
  "TASKS.md"
  "MEMORY.md"
  "demo/sample-requests.sh"
  "demo/sample-requests.http"
  "demo/sample-data.json"
  "demo/run.sh"
)

SAVED=0; SKIPPED=0
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mine_file() {
  local rel="$1" abs="$HW_DIR/$1"
  if [ ! -f "$abs" ]; then echo "  SKIP: $rel"; SKIPPED=$((SKIPPED+1)); return; fi
  local title="${SCOPE}: ${rel}"
  local jf="$TMPDIR_CUSTOM/$(echo "$rel" | tr '/' '_').json"
  python3 - <<PYEOF > "$jf"
import json
payload = {
    "title": "$title",
    "content": open("$abs", encoding="utf-8", errors="replace").read()[:8000],
    "tags": ["$SCOPE", "repo", "mined"],
    "metadata": {"scope": "$SCOPE", "source": "homework-$HW_NUM/$rel", "mined_at": "$NOW"},
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
PYEOF
  echo -n "  Saving: $rel ... "
  local sid; sid=$(vault_save "$jf" "$title")
  echo "$sid"; SAVED=$((SAVED+1))
}

for f in "${FILES[@]}"; do mine_file "$f"; done
echo ""; echo "Done: $SAVED saved, $SKIPPED skipped."
