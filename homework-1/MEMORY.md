# Homework 1 — Session Memory

Quick-reference context for resuming work on this homework.
Full course memory (scripts, vault, notes) lives in `course-memory/`.

---

## What was built

- **Stack**: Python 3.9+, FastAPI, Pydantic v2, Uvicorn
- **Storage**: in-memory `dict[str, Transaction]` — no database
- **Port**: 3000 (local dev)
- **Single file**: all API logic in `src/main.py`

### Endpoints

| Method | Path | Task |
|--------|------|------|
| `POST` | `/transactions` | Task 1 |
| `GET` | `/transactions` | Task 1 + Task 3 (filtering) |
| `GET` | `/transactions/{id}` | Task 1 |
| `GET` | `/accounts/{accountId}/balance` | Task 1 |
| `GET` | `/accounts/{accountId}/summary` | Task 4 Option A |

### Validation rules (Task 2)

| Field | Rule |
|-------|------|
| `amount` | positive, max 2 decimal places |
| `fromAccount` / `toAccount` | regex `^ACC-[A-Za-z0-9]{5}$` |
| `currency` | ISO 4217 whitelist (34 codes) |
| `type` | `deposit` \| `withdrawal` \| `transfer` |

Error shape: `{"error": "Validation failed", "details": [{"field": "...", "message": "..."}]}`

### Filtering (Task 3) — all params optional, combinable

```
GET /transactions?accountId=ACC-12345&type=transfer&from=2024-01-01&to=2024-01-31
```

### Summary endpoint (Task 4 Option A)

```json
{
  "accountId": "ACC-12345",
  "total_deposits": 750.00,
  "total_withdrawals": 200.00,
  "transaction_count": 4,
  "most_recent_transaction": "2026-04-23T20:41:30Z"
}
```

---

## How it was generated

`src/dspy_generate_homework.py` — a DSPy `plan → build → review → repair` pipeline:
1. **Plan**: `dspy.Predict` reads `TASKS.md`, outputs a JSON file list
2. **Build**: `dspy.Predict` generates each file with full requirements in context
3. **Review**: `dspy.Predict` audits each file, returns `{pass, issues, fixes}` JSON
4. **Repair**: `dspy.Predict` rewrites files that fail review

Model: `anthropic/claude-sonnet-4-6`

---

## Key bugs fixed during this session

### 1. Decimal validation false negative
`Decimal.quantize(ROUND_DOWN)` did not catch `10.123`.
**Fix**: `Decimal(str(v)).as_tuple().exponent < -2`

### 2. macOS `head -n -1` in test script
`head -n -1` is Linux-only. Caused `$BODY` to always be empty in `demo/sample-requests.sh`.
**Fix**: `curl -o <tmpfile> -w "%{http_code}"`

### 3. DSPy wrong model ID
`anthropic/claude-sonnet-4-5-20250929` does not exist.
**Fix**: `anthropic/claude-sonnet-4-6`

### 4. DSPy wrong ROOT path
`Path(__file__).parent` pointed to `src/`, not `homework-1/`.
**Fix**: `Path(__file__).parent.parent`

---

## Test suite

```bash
bash demo/sample-requests.sh
# 39 tests | 39 passed | 0 failed
```

Covers: all 5 endpoints, all validation rules, all 4 filter combos, 404 cases.

---

## Run the app

```bash
cd homework-1
source venv/bin/activate          # activate venv
uvicorn src.main:app --reload --host 127.0.0.1 --port 3000
# Docs: http://localhost:3000/docs
```

---

## Course memory vault blobs (hw1)

| short_id | content |
|---|---|
| `L-68d9c73a` | src/main.py |
| `L-cdef989f` | src/dspy_generate_homework.py |
| `L-3db0afa8` | requirements.txt |
| `L-0ce8ff37` | README.md |
| `L-1a4eefdc` | HOWTORUN.md |
| `L-c636b04d` | TASKS.md |
| `L-3dab017d` | demo/sample-requests.sh |
| `L-5773d910` | demo/sample-requests.http |
| `L-3129691f` | demo/sample-data.json |
| `L-3b265660` | demo/run.sh |
| `L-f8314607` | conversation chunk 1/3 |
| `L-e8052ce6` | conversation chunk 2/3 |
| `L-622394b2` | conversation chunk 3/3 |

Recover: `cat course-memory/vault/<hash>.json`
