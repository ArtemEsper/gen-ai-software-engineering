#!/usr/bin/env bash
# ============================================================
# 03-mine-course.sh — Mine course-level files into memory
# Usage: bash course-memory/scripts/03-mine-course.sh
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/course-memory/scripts/_vault.sh"

SCOPE="course"
TMPDIR_CUSTOM="$(mktemp -d /tmp/mp_course_XXXXXX)"
trap 'rm -rf "$TMPDIR_CUSTOM"' EXIT
echo "=== Mining course-level files → $SCOPE ==="

FILES=("README.md" ".gitignore" "course-memory/README.md")
SAVED=0
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mine_file() {
  local rel="$1" abs="$REPO_ROOT/$1"
  if [ ! -f "$abs" ]; then echo "  SKIP: $rel"; return; fi
  local title="${SCOPE}: ${rel}"
  local jf="$TMPDIR_CUSTOM/$(echo "$rel" | tr '/' '_').json"
  python3 - <<PYEOF > "$jf"
import json
payload = {
    "title": "$title",
    "content": open("$abs", encoding="utf-8", errors="replace").read()[:8000],
    "tags": ["$SCOPE", "course-setup", "mined"],
    "metadata": {"scope": "$SCOPE", "source": "$rel", "mined_at": "$NOW"},
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
PYEOF
  echo -n "  Saving: $rel ... "
  local sid; sid=$(vault_save "$jf" "$title")
  echo "$sid"; SAVED=$((SAVED+1))
}

for f in "${FILES[@]}"; do mine_file "$f"; done
echo ""; echo "Done: $SAVED saved."
