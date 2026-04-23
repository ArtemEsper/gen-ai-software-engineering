#!/usr/bin/env bash
# ============================================================
# 06-wakeup.sh — Generate wake-up context before a new session
# Usage: bash course-memory/scripts/06-wakeup.sh <hw_number> [max_blobs]
# Paste the output at the start of your Claude Code session.
# ============================================================
set -euo pipefail

HW_NUM="${1:?Usage: $0 <hw_number> [max_blobs]}"
MAX_BLOBS="${2:-8}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/course-memory/scripts/_vault.sh"

NOTES_DIR="$REPO_ROOT/course-memory/notes"
VAULT_DIR="$REPO_ROOT/course-memory/vault"

echo "============================================================"
echo " WAKE-UP CONTEXT — Homework $HW_NUM"
echo " Generated: $(date -u +"%Y-%m-%d %H:%M UTC")"
echo "============================================================"; echo ""

# Human notes
for NOTE in decisions pitfalls prompt-log; do
  FILE="$NOTES_DIR/${NOTE}.md"
  LABEL="${NOTE//-/ }"; LABEL="${LABEL^}"
  echo "## $LABEL"
  echo ""
  [ -s "$FILE" ] && cat "$FILE" || echo "  (empty)"
  echo ""
done

# Memory blobs from vault
echo "## Recent Memory Blobs (hw${HW_NUM}_repo + hw${HW_NUM}_convos)"
echo ""
BLOB_COUNT=0

recover_scope() {
  local scope="$1"
  local ids
  ids=$(grep "\`${scope}\`" "$INDEX" 2>/dev/null \
    | awk -F'|' '{print $2}' | tr -d '` ' | tail -"$MAX_BLOBS" || true)
  [ -z "$ids" ] && return

  while IFS= read -r SID; do
    [ -z "$SID" ] && continue
    [ "$BLOB_COUNT" -ge "$MAX_BLOBS" ] && break
    local content=""
    if [[ "$SID" == L-* ]]; then
      local vf="$VAULT_DIR/${SID#L-}.json"
      [ -f "$vf" ] || continue
      content=$(python3 -c "
import json
d = json.load(open('$vf'))
print(f\"### [$SID] {d.get('title','?')}\n\n{d.get('content','')[:2000]}\")
" 2>/dev/null || true)
    else
      local tmp; tmp=$(mktemp /tmp/wakeup_XXXXXX.json)
      if npx mempalace recover "$SID" > "$tmp" 2>/dev/null; then
        TITLE=$(grep "\`$SID\`" "$INDEX" | head -1 | awk -F'|' '{print $3}' | xargs)
        content="### [$SID] $TITLE"$'\n\n'"$(head -60 "$tmp")"
      fi
      rm -f "$tmp"
    fi
    if [ -n "$content" ]; then
      echo "$content"; echo ""; echo "---"; echo ""
      BLOB_COUNT=$((BLOB_COUNT+1))
    fi
  done <<< "$ids"
}

recover_scope "hw${HW_NUM}_repo"
recover_scope "hw${HW_NUM}_convos"
[ "$BLOB_COUNT" -eq 0 ] && echo "  (no blobs — run scripts 02 and 04 first)"

echo ""
echo "============================================================"
echo " END — paste above into your new Claude session"
echo "============================================================"
