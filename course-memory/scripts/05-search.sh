#!/usr/bin/env bash
# ============================================================
# 05-search.sh — Search course memory by keyword
# Usage: bash course-memory/scripts/05-search.sh <query> [--notes-only]
# ============================================================
set -euo pipefail

QUERY="${1:?Usage: $0 <query> [--notes-only]}"
NOTES_ONLY=false; [ "${2:-}" = "--notes-only" ] && NOTES_ONLY=true

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/course-memory/scripts/_vault.sh"

NOTES_DIR="$REPO_ROOT/course-memory/notes"
VAULT_DIR="$REPO_ROOT/course-memory/vault"

C='\033[0;36m'; G='\033[0;32m'; Y='\033[1;33m'; R='\033[0m'

echo -e "${C}=== Searching: \"$QUERY\" ===${R}"; echo ""

# Phase 1: notes/ markdown
echo -e "${G}Phase 1: notes/${R}"
FN=0
for FILE in "$NOTES_DIR"/*.md; do
  [ -f "$FILE" ] || continue
  MATCHES=$(grep -in "$QUERY" "$FILE" 2>/dev/null || true)
  if [ -n "$MATCHES" ]; then
    echo -e "  ${Y}$(basename "$FILE")${R}"
    echo "$MATCHES" | while IFS= read -r line; do echo "    $line"; done
    FN=$((FN+1))
  fi
done
[ "$FN" -eq 0 ] && echo "  (no matches)"; echo ""
$NOTES_ONLY && exit 0

# Phase 2a: local vault blobs
FV=0
if [ -d "$VAULT_DIR" ] && ls "$VAULT_DIR"/*.json &>/dev/null 2>&1; then
  echo -e "${G}Phase 2a: vault/${R}"
  for BLOB in "$VAULT_DIR"/*.json; do
    [ -f "$BLOB" ] || continue
    if grep -qi "$QUERY" "$BLOB" 2>/dev/null; then
      TITLE=$(python3 -c "import json; print(json.load(open('$BLOB')).get('title','?'))" 2>/dev/null || echo "?")
      HASH=$(basename "$BLOB" .json)
      echo -e "  ${Y}[L-$HASH]${R} $TITLE"
      grep -i "$QUERY" "$BLOB" | head -3 | while IFS= read -r l; do echo "    $l"; done
      FV=$((FV+1))
    fi
  done
  [ "$FV" -eq 0 ] && echo "  (no matches)"; echo ""
fi

# Phase 2b: MemPalace cloud IDs
FC=0
CLOUD_IDS=$(grep -oP '`(?!L-)[a-f0-9]{6,16}`' "$INDEX" 2>/dev/null | tr -d '`' | sort -u || true)
if [ -n "$CLOUD_IDS" ]; then
  COUNT=$(echo "$CLOUD_IDS" | wc -l | tr -d ' ')
  echo -e "${G}Phase 2b: MemPalace cloud ($COUNT IDs)${R}"
  TMP="$(mktemp -d /tmp/mp_search_XXXXXX)"; trap 'rm -rf "$TMP"' EXIT
  while IFS= read -r SID; do
    [ -z "$SID" ] && continue
    REC="$TMP/${SID}.json"
    npx mempalace recover "$SID" > "$REC" 2>/dev/null || continue
    if grep -qi "$QUERY" "$REC" 2>/dev/null; then
      TITLE=$(grep "\`$SID\`" "$INDEX" | head -1 | awk -F'|' '{print $3}' | xargs)
      echo -e "  ${Y}[$SID]${R} $TITLE"
      grep -i "$QUERY" "$REC" | head -3 | while IFS= read -r l; do echo "    $l"; done
      FC=$((FC+1))
    fi
  done <<< "$CLOUD_IDS"
  [ "$FC" -eq 0 ] && echo "  (no matches)"
fi

echo ""; echo "Results — notes: $FN | vault: $FV | cloud: $FC"
