#!/usr/bin/env bash
# ============================================================
# _vault.sh — Shared save/recover/list helpers for course memory
#
# Source this file from other scripts:
#   source "$(dirname "$0")/_vault.sh"
#
# REPO_ROOT must be set by the caller before sourcing.
#
# Storage strategy:
#   1. Try npx mempalace save (requires cloud API key)
#   2. On 403/auth failure → local vault: course-memory/vault/<sha256[:8]>.json
#      Local IDs prefixed "L-" to distinguish from cloud IDs.
#
# Env overrides:
#   MEMPALACE_LOCAL_ONLY=1   skip cloud, always use local vault
#   MEMPALACE_CLOUD_ONLY=1   fail if cloud save fails
# ============================================================

: "${REPO_ROOT:?REPO_ROOT must be set before sourcing _vault.sh}"

VAULT_DIR="$REPO_ROOT/course-memory/vault"
INDEX="$REPO_ROOT/course-memory/notes/index.md"

# ── vault_save ────────────────────────────────────────────────
# Save a JSON blob. Prints the short_id. Appends row to index.md.
# Usage: SHORT_ID=$(vault_save /tmp/blob.json "scope: label")
vault_save() {
  local json_file="$1"
  local label="${2:-}"
  local short_id=""

  if [ -z "$label" ]; then
    label=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('title','unknown'))" 2>/dev/null || echo "unknown")
  fi

  local scope
  scope=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('metadata',{}).get('scope','unknown'))" 2>/dev/null || echo "unknown")

  local now
  now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # ── Try MemPalace cloud ──────────────────────────────────────
  if [ "${MEMPALACE_LOCAL_ONLY:-0}" != "1" ]; then
    local mp_out
    mp_out=$(npx mempalace save "$json_file" 2>&1)
    if echo "$mp_out" | grep -qiE "403|401|unauthorized|failed to store|invalid.*api"; then
      : # fall through to local
    else
      short_id=$(echo "$mp_out" | grep -oE '\b[a-f0-9]{6,16}\b' | head -1 || true)
    fi
  fi

  # ── Local vault fallback ─────────────────────────────────────
  if [ -z "$short_id" ]; then
    [ "${MEMPALACE_CLOUD_ONLY:-0}" = "1" ] && { echo "ERROR: cloud save failed" >&2; return 1; }
    mkdir -p "$VAULT_DIR"
    local hash
    hash=$(python3 -c "
import hashlib, json
with open('$json_file') as f: data = f.read()
print(hashlib.sha256(data.encode()).hexdigest()[:8])
")
    cp "$json_file" "$VAULT_DIR/${hash}.json"
    short_id="L-${hash}"
  fi

  echo "| \`$short_id\` | \`$scope\` | $label | $now |" >> "$INDEX"
  echo "$short_id"
}

# ── vault_recover ─────────────────────────────────────────────
# Recover a blob by short_id. Prints JSON to stdout.
vault_recover() {
  local short_id="$1"
  if [[ "$short_id" == L-* ]]; then
    local vault_file="$VAULT_DIR/${short_id#L-}.json"
    [ -f "$vault_file" ] || { echo "ERROR: not found: $vault_file" >&2; return 1; }
    cat "$vault_file"
  else
    npx mempalace recover "$short_id" 2>&1
  fi
}

# ── vault_list ────────────────────────────────────────────────
# List index rows, optionally filtered by scope tag.
vault_list() {
  local scope_filter="${1:-}"
  [ -f "$INDEX" ] || { echo "(index not found)"; return; }
  if [ -n "$scope_filter" ]; then
    grep "\`$scope_filter\`" "$INDEX" || echo "(no entries for: $scope_filter)"
  else
    grep -v '^#\|^|\s*short_id\|^$\|^---' "$INDEX" || echo "(index is empty)"
  fi
}
