#!/usr/bin/env bash
# HW4: 4-Agent Pipeline — single-command orchestration
# Usage: ./run-pipeline.sh [bug-id]
#   bug-id  Optional. E.g. "001-date-filter-off-by-one" or just "001".
#           Default: process all bugs in context/bugs/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="artifacts/pipeline-logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
MASTER_LOG="$LOG_DIR/pipeline-$TIMESTAMP.log"

# ── helpers ──────────────────────────────────────────────────────────

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$MASTER_LOG"; }
err() { log "ERROR: $*"; }
sep() { log "──────────────────────────────────────────────────"; }

# Discover the claude binary
find_claude() {
  if [[ -n "${CLAUDE_CODE_EXECPATH:-}" && -x "${CLAUDE_CODE_EXECPATH}" ]]; then
    echo "$CLAUDE_CODE_EXECPATH"
  elif command -v claude &>/dev/null; then
    command -v claude
  else
    return 1
  fi
}

# Parse model: from YAML frontmatter of an .agent.md file
get_model() {
  local agent_file="$1"
  awk '/^---$/{n++; next} n==1 && /^model:/{gsub(/^model:[[:space:]]*/, ""); print; exit}' "$agent_file"
}

# Extract body text after the closing --- of YAML frontmatter
get_body() {
  local agent_file="$1"
  awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' "$agent_file"
}

# Run one agent invocation.
# Args: agent_file  prompt  log_suffix
run_agent() {
  local agent_file="$1"
  local prompt="$2"
  local log_file="$3"

  local model
  model=$(get_model "$agent_file")
  local body
  body=$(get_body "$agent_file")
  local agent_name
  agent_name=$(basename "$agent_file" .agent.md)

  log "  Agent: $agent_name  Model: $model"

  "$CLAUDE" -p \
    --model "$model" \
    --append-system-prompt "$body" \
    --dangerously-skip-permissions \
    --output-format text \
    "$prompt" \
    2>&1 | tee -a "$log_file" "$MASTER_LOG"

  local exit_code=${PIPESTATUS[0]}
  if [[ $exit_code -ne 0 ]]; then
    err "Agent $agent_name exited with code $exit_code"
    return $exit_code
  fi
  log "  Agent $agent_name completed successfully."
}

# ── main ─────────────────────────────────────────────────────────────

log "=============================================="
log "  HW4: 4-Agent Pipeline"
log "=============================================="

CLAUDE=$(find_claude) || {
  err "Claude Code CLI not found."
  err "Set CLAUDE_CODE_EXECPATH or ensure 'claude' is on PATH."
  err ""
  err "To run agents manually in an interactive Claude Code session:"
  err "  1. Open Claude Code in homework-4/"
  err "  2. For each bug dir, paste the agent .md body as context"
  err "  3. Follow the agent's operating instructions"
  exit 1
}
log "Using Claude binary: $CLAUDE"

# Resolve which bug dirs to process
if [[ $# -ge 1 ]]; then
  PATTERN="$1"
  BUG_DIRS=()
  for d in context/bugs/*/; do
    if [[ "$(basename "$d")" == *"$PATTERN"* ]]; then
      BUG_DIRS+=("$d")
    fi
  done
  if [[ ${#BUG_DIRS[@]} -eq 0 ]]; then
    err "No bug directory matching '$PATTERN' found in context/bugs/"
    exit 1
  fi
else
  BUG_DIRS=(context/bugs/*/)
fi

log "Processing ${#BUG_DIRS[@]} bug(s): ${BUG_DIRS[*]}"
sep

FAILED=0

for bug_dir in "${BUG_DIRS[@]}"; do
  bug_name=$(basename "$bug_dir")
  bug_log="$LOG_DIR/${bug_name}-${TIMESTAMP}.log"

  log ""
  log "=== Bug: $bug_name ==="
  sep

  # ── Step 1: Research Verifier ───────────────────────────────────
  log "[1/4] Research Verifier"
  if [[ ! -f "$bug_dir/research/codebase-research.md" ]]; then
    err "Missing $bug_dir/research/codebase-research.md — skipping"
    FAILED=1
    continue
  fi

  PROMPT_RV=$(cat <<EOPROMPT
You are operating on bug: $bug_name

Your task:
1. Read the research file at $bug_dir/research/codebase-research.md
2. Read the skill at skills/research-quality-measurement.md
3. Verify every file:line reference and code snippet against the actual source files in src/
4. Write your output to $bug_dir/research/verified-research.md

Follow the operating instructions in your system prompt exactly.
Working directory: $SCRIPT_DIR
EOPROMPT
  )

  if ! run_agent agents/research-verifier.agent.md "$PROMPT_RV" "$bug_log"; then
    err "Research Verifier failed for $bug_name — stopping this bug"
    FAILED=1
    continue
  fi
  sep

  # ── Step 2: Bug Fixer ───────────────────────────────────────────
  log "[2/4] Bug Fixer"
  if [[ ! -f "$bug_dir/implementation-plan.md" ]]; then
    err "Missing $bug_dir/implementation-plan.md — skipping"
    FAILED=1
    continue
  fi

  PROMPT_BF=$(cat <<EOPROMPT
You are operating on bug: $bug_name

Your task:
1. Read the implementation plan at $bug_dir/implementation-plan.md
2. Apply the code changes exactly as specified
3. After each change, run: cd $SCRIPT_DIR && source venv/bin/activate && python -m pytest tests/ -v
4. Write your output to $bug_dir/fix-summary.md

Follow the operating instructions in your system prompt exactly.
Working directory: $SCRIPT_DIR
EOPROMPT
  )

  if ! run_agent agents/bug-fixer.agent.md "$PROMPT_BF" "$bug_log"; then
    err "Bug Fixer failed for $bug_name — stopping this bug"
    FAILED=1
    continue
  fi
  sep

  # ── Step 3: Security Verifier ───────────────────────────────────
  log "[3/4] Security Verifier"
  if [[ ! -f "$bug_dir/fix-summary.md" ]]; then
    err "Missing $bug_dir/fix-summary.md (Bug Fixer did not produce output) — skipping"
    FAILED=1
    continue
  fi

  PROMPT_SV=$(cat <<EOPROMPT
You are operating on bug: $bug_name

Your task:
1. Read the fix summary at $bug_dir/fix-summary.md
2. Identify all changed source files from the fix summary
3. Read each changed file in full, plus any files they import from src/
4. Scan for security vulnerabilities (injection, hardcoded secrets, insecure comparisons, missing validation, unsafe deps, XSS/CSRF, auth issues, logging issues)
5. Write your output to $bug_dir/security-report.md

Follow the operating instructions in your system prompt exactly.
Working directory: $SCRIPT_DIR
EOPROMPT
  )

  if ! run_agent agents/security-verifier.agent.md "$PROMPT_SV" "$bug_log"; then
    err "Security Verifier failed for $bug_name — stopping this bug"
    FAILED=1
    continue
  fi
  sep

  # ── Step 4: Unit Test Generator ─────────────────────────────────
  log "[4/4] Unit Test Generator"

  PROMPT_UT=$(cat <<EOPROMPT
You are operating on bug: $bug_name

Your task:
1. Read the FIRST skill at skills/unit-tests-FIRST.md
2. Read the fix summary at $bug_dir/fix-summary.md
3. Read the changed source files identified in the fix summary
4. Read existing tests in tests/ to understand conventions
5. Generate new test file: tests/test_bug_${bug_name%%-*}.py
6. Run: cd $SCRIPT_DIR && source venv/bin/activate && python -m pytest tests/ -v
7. Write your output to $bug_dir/test-report.md

Follow the operating instructions in your system prompt exactly.
Working directory: $SCRIPT_DIR
EOPROMPT
  )

  if ! run_agent agents/unit-test-generator.agent.md "$PROMPT_UT" "$bug_log"; then
    err "Unit Test Generator failed for $bug_name — stopping this bug"
    FAILED=1
    continue
  fi

  log ""
  log "=== Bug $bug_name: ALL 4 AGENTS COMPLETE ==="
  sep
done

# ── Summary ──────────────────────────────────────────────────────────

log ""
log "=============================================="
log "  Pipeline Summary"
log "=============================================="
log "Bugs processed: ${#BUG_DIRS[@]}"
log "Master log:     $MASTER_LOG"

if [[ $FAILED -ne 0 ]]; then
  log "Status: PARTIAL — one or more agents failed (see log)"
  exit 1
else
  log "Status: COMPLETE — all agents succeeded"
  exit 0
fi
