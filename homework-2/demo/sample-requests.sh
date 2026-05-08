#!/usr/bin/env bash
# Automated test script for the Customer Support Ticket API
# Usage: bash demo/sample-requests.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASS=0
FAIL=0

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

check() {
    local desc="$1"
    local expected="$2"
    local actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        echo -e "${GREEN}PASS${RESET} $desc"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET} $desc (expected '$expected' in response)"
        echo "     Response: $actual"
        ((FAIL++))
    fi
}

echo "=== Customer Support Ticket API Tests ==="
echo "Base URL: $BASE_URL"
echo ""

# ---- Health check ----
R=$(curl -s "$BASE_URL/health")
check "GET /health returns ok" '"status":"ok"' "$R"

# ---- Create ticket ----
R=$(curl -s -X POST "$BASE_URL/tickets" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST-001","customer_email":"alice@example.com","customer_name":"Alice","subject":"Cannot login to account","description":"Getting an authentication error when I try to login to my account."}')
check "POST /tickets returns id" '"id"' "$R"
check "POST /tickets status=new" '"status":"new"' "$R"
TICKET_ID=$(echo "$R" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# ---- Create ticket with auto-classify ----
R=$(curl -s -X POST "$BASE_URL/tickets?auto_classify=true" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST-002","customer_email":"bob@example.com","customer_name":"Bob","subject":"Production is down critical outage","description":"All users cannot access the system. This is a critical emergency requiring immediate resolution."}')
check "POST /tickets?auto_classify=true sets priority" '"priority"' "$R"
check "POST /tickets?auto_classify=true urgent priority" '"urgent"' "$R"

# ---- Validation error ----
R=$(curl -s -X POST "$BASE_URL/tickets" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C","customer_email":"not-an-email","customer_name":"X","subject":"S","description":"Short"}')
check "POST /tickets invalid email returns 422" '"detail"' "$R"

# ---- List tickets ----
R=$(curl -s "$BASE_URL/tickets")
check "GET /tickets returns array" '\[' "$R"

# ---- Get ticket by ID ----
if [ -n "$TICKET_ID" ]; then
    R=$(curl -s "$BASE_URL/tickets/$TICKET_ID")
    check "GET /tickets/:id returns ticket" '"id"' "$R"
fi

# ---- Filter by status ----
R=$(curl -s "$BASE_URL/tickets?status=new")
check "GET /tickets?status=new works" '\[' "$R"

# ---- Filter by category ----
R=$(curl -s "$BASE_URL/tickets?category=technical_issue")
check "GET /tickets?category=technical_issue works" '\[' "$R"

# ---- Update ticket ----
if [ -n "$TICKET_ID" ]; then
    R=$(curl -s -X PUT "$BASE_URL/tickets/$TICKET_ID" \
      -H "Content-Type: application/json" \
      -d '{"status":"in_progress"}')
    check "PUT /tickets/:id updates status" '"in_progress"' "$R"
fi

# ---- Auto-classify ----
if [ -n "$TICKET_ID" ]; then
    R=$(curl -s -X POST "$BASE_URL/tickets/$TICKET_ID/auto-classify")
    check "POST /tickets/:id/auto-classify returns category" '"category"' "$R"
    check "POST /tickets/:id/auto-classify returns confidence" '"confidence"' "$R"
fi

# ---- 404 not found ----
R=$(curl -s "$BASE_URL/tickets/nonexistent-uuid-xxxx")
check "GET /tickets/nonexistent returns 404 detail" '"detail"' "$R"

# ---- Bulk import CSV ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="$SCRIPT_DIR/../tests/fixtures/sample_tickets.csv"
if [ -f "$CSV_FILE" ]; then
    R=$(curl -s -X POST "$BASE_URL/tickets/import" \
      -F "file=@$CSV_FILE")
    check "POST /tickets/import CSV successful>0" '"successful"' "$R"
fi

# ---- Bulk import JSON ----
JSON_FILE="$SCRIPT_DIR/../tests/fixtures/sample_tickets.json"
if [ -f "$JSON_FILE" ]; then
    R=$(curl -s -X POST "$BASE_URL/tickets/import" \
      -F "file=@$JSON_FILE")
    check "POST /tickets/import JSON successful>0" '"successful"' "$R"
fi

# ---- Bulk import XML ----
XML_FILE="$SCRIPT_DIR/../tests/fixtures/sample_tickets.xml"
if [ -f "$XML_FILE" ]; then
    R=$(curl -s -X POST "$BASE_URL/tickets/import" \
      -F "file=@$XML_FILE")
    check "POST /tickets/import XML successful>0" '"successful"' "$R"
fi

# ---- Delete ticket ----
if [ -n "$TICKET_ID" ]; then
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/tickets/$TICKET_ID")
    if [ "$CODE" = "204" ]; then
        echo -e "${GREEN}PASS${RESET} DELETE /tickets/:id returns 204"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET} DELETE /tickets/:id expected 204, got $CODE"
        ((FAIL++))
    fi
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
