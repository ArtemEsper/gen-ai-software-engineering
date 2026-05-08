#!/usr/bin/env bash
# ============================================================
# Banking Transactions API — Test Suite
# Covers: Task 1 (core), Task 2 (validation),
#         Task 3 (filtering), Task 4 Option A (summary)
# Usage:  bash demo/sample-requests.sh [BASE_URL]
# Default BASE_URL: http://127.0.0.1:3000
# ============================================================

BASE="${1:-http://127.0.0.1:3000}"
PASS=0
FAIL=0

# ── helpers ──────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

section() { echo -e "\n${BOLD}${CYAN}━━━ $1 ━━━${RESET}"; }

# assert_status <label> <expected_http_code> <actual_http_code> [response_body]
assert_status() {
  local label="$1" expected="$2" actual="$3" body="$4"
  if [ "$actual" = "$expected" ]; then
    echo -e "  ${GREEN}PASS${RESET} [$actual] $label"
    PASS=$((PASS + 1))
  else
    echo -e "  ${RED}FAIL${RESET} [$actual != $expected] $label"
    [ -n "$body" ] && echo "       body: $body"
    FAIL=$((FAIL + 1))
  fi
}

# assert_contains <label> <substring> <body>
assert_contains() {
  local label="$1" needle="$2" body="$3"
  if echo "$body" | grep -q "$needle"; then
    echo -e "  ${GREEN}PASS${RESET} (contains '$needle') $label"
    PASS=$((PASS + 1))
  else
    echo -e "  ${RED}FAIL${RESET} (missing '$needle') $label"
    echo "       body: $body"
    FAIL=$((FAIL + 1))
  fi
}

# Temp file for response body (avoids head -n -1 which breaks on macOS BSD head)
_TMPFILE=$(mktemp /tmp/api_test_XXXXXX.json)
trap 'rm -f "$_TMPFILE"' EXIT

# do_post <path> <json>  → sets $STATUS and $BODY
do_post() {
  STATUS=$(curl -s -o "$_TMPFILE" -w "%{http_code}" -X POST "$BASE$1" \
    -H "Content-Type: application/json" -d "$2")
  BODY=$(cat "$_TMPFILE")
}

# do_get <path>  → sets $STATUS and $BODY
do_get() {
  STATUS=$(curl -s -o "$_TMPFILE" -w "%{http_code}" "$BASE$1")
  BODY=$(cat "$_TMPFILE")
}

# ── check server is up ────────────────────────────────────────
section "Health check"
do_get "/"
if [ "$STATUS" != "200" ] && [ "$STATUS" != "404" ]; then
  echo -e "${RED}ERROR: API is not reachable at $BASE (got $STATUS)${RESET}"
  echo "Make sure the server is running:  uvicorn src.main:app --reload --host 127.0.0.1 --port 3000"
  exit 1
fi
echo -e "  ${GREEN}OK${RESET}  Server is reachable at $BASE"

# ============================================================
# TASK 1 — Core API
# ============================================================
section "Task 1 — POST /transactions (create)"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002",
  "amount":      500.00,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "create transfer — expect 201" 201 "$STATUS" "$BODY"
TX1_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

do_post "/transactions" '{
  "fromAccount": "ACC-ZZZZ1",
  "toAccount":   "ACC-BB002",
  "amount":      200.00,
  "currency":    "EUR",
  "type":        "deposit"
}'
assert_status "create deposit — expect 201" 201 "$STATUS" "$BODY"
TX2_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

do_post "/transactions" '{
  "fromAccount": "ACC-BB002",
  "toAccount":   "ACC-ZZZZ1",
  "amount":      50.75,
  "currency":    "GBP",
  "type":        "withdrawal"
}'
assert_status "create withdrawal — expect 201" 201 "$STATUS" "$BODY"
TX3_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

section "Task 1 — GET /transactions"
do_get "/transactions"
assert_status "list all — expect 200" 200 "$STATUS" "$BODY"
assert_contains "list all — has transactions array" '"id"' "$BODY"

section "Task 1 — GET /transactions/:id"
do_get "/transactions/$TX1_ID"
assert_status "get by id — expect 200" 200 "$STATUS" "$BODY"
assert_contains "get by id — correct id returned" "$TX1_ID" "$BODY"

do_get "/transactions/nonexistent-id-000"
assert_status "get by unknown id — expect 404" 404 "$STATUS" "$BODY"

section "Task 1 — GET /accounts/:accountId/balance"
do_get "/accounts/ACC-BB002/balance"
assert_status "balance — expect 200" 200 "$STATUS" "$BODY"
assert_contains "balance — has balance field" '"balance"' "$BODY"

do_get "/accounts/ACC-XXXXX/balance"
assert_status "balance — unknown account → 404" 404 "$STATUS" "$BODY"

# ============================================================
# TASK 2 — Validation
# ============================================================
section "Task 2 — Validation: amount"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002",
  "amount":      -10,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "negative amount → 400" 400 "$STATUS" "$BODY"
assert_contains "negative amount — error message present" "amount" "$BODY"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002",
  "amount":      0,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "zero amount → 400" 400 "$STATUS" "$BODY"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002",
  "amount":      10.123,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "3 decimal places → 400" 400 "$STATUS" "$BODY"

section "Task 2 — Validation: account format"

do_post "/transactions" '{
  "fromAccount": "INVALID",
  "toAccount":   "ACC-BB002",
  "amount":      100,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "bad fromAccount format → 400" 400 "$STATUS" "$BODY"
assert_contains "bad fromAccount — details field" "fromAccount" "$BODY"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002!",
  "amount":      100,
  "currency":    "USD",
  "type":        "transfer"
}'
assert_status "bad toAccount format → 400" 400 "$STATUS" "$BODY"

section "Task 2 — Validation: currency"

do_post "/transactions" '{
  "fromAccount": "ACC-AA001",
  "toAccount":   "ACC-BB002",
  "amount":      100,
  "currency":    "XYZ",
  "type":        "transfer"
}'
assert_status "invalid currency → 400" 400 "$STATUS" "$BODY"
assert_contains "invalid currency — error message present" "currency" "$BODY"

section "Task 2 — Validation: error response shape"
do_post "/transactions" '{
  "fromAccount": "BAD",
  "toAccount":   "ACC-BB002",
  "amount":      -5,
  "currency":    "FAKE",
  "type":        "transfer"
}'
assert_status "multiple errors → 400" 400 "$STATUS" "$BODY"
assert_contains "error envelope has 'error' key"   '"error"'   "$BODY"
assert_contains "error envelope has 'details' key" '"details"' "$BODY"

# ============================================================
# TASK 3 — Filtering
# ============================================================
section "Task 3 — Filter by accountId"
do_get "/transactions?accountId=ACC-BB002"
assert_status "filter accountId — expect 200" 200 "$STATUS" "$BODY"
assert_contains "filter accountId — results include ACC-BB002" "ACC-BB002" "$BODY"

section "Task 3 — Filter by type"
do_get "/transactions?type=deposit"
assert_status "filter type=deposit — expect 200" 200 "$STATUS" "$BODY"
assert_contains "filter type=deposit — results contain deposit" "deposit" "$BODY"

do_get "/transactions?type=transfer"
assert_status "filter type=transfer — expect 200" 200 "$STATUS" "$BODY"

section "Task 3 — Filter by date range"
TODAY=$(date +%Y-%m-%d)
do_get "/transactions?from=${TODAY}&to=${TODAY}"
assert_status "filter date range today — expect 200" 200 "$STATUS" "$BODY"
assert_contains "filter date range — results have transactions" '"id"' "$BODY"

do_get "/transactions?from=2000-01-01&to=2000-01-02"
assert_status "filter past date range (empty) — expect 200" 200 "$STATUS" "$BODY"

section "Task 3 — Combined filters"
do_get "/transactions?accountId=ACC-BB002&type=transfer"
assert_status "combined accountId+type — expect 200" 200 "$STATUS" "$BODY"

do_get "/transactions?accountId=ACC-BB002&from=${TODAY}&to=${TODAY}"
assert_status "combined accountId+date — expect 200" 200 "$STATUS" "$BODY"

# ============================================================
# TASK 4 — Summary (Option A)
# ============================================================
section "Task 4 — GET /accounts/:accountId/summary"
do_get "/accounts/ACC-BB002/summary"
assert_status "summary — expect 200" 200 "$STATUS" "$BODY"
assert_contains "summary — total_deposits"         '"total_deposits"'         "$BODY"
assert_contains "summary — total_withdrawals"      '"total_withdrawals"'      "$BODY"
assert_contains "summary — transaction_count"      '"transaction_count"'      "$BODY"
assert_contains "summary — most_recent_transaction" '"most_recent_transaction"' "$BODY"

do_get "/accounts/ACC-NOPE9/summary"
assert_status "summary — unknown account → 404" 404 "$STATUS" "$BODY"

# ============================================================
# Results
# ============================================================
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
TOTAL=$((PASS + FAIL))
echo -e "${BOLD}Results: $TOTAL tests  |  ${GREEN}$PASS passed${RESET}${BOLD}  |  ${RED}$FAIL failed${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
[ "$FAIL" -gt 0 ] && exit 1 || exit 0
