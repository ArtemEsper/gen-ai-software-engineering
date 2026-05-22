# Fix Summary: Bug 002 — Incorrect Average in Summary Calculation

## Changes Made

### Change 1 of 1

- **File:** `src/utils.py`
- **Line:** 38
- **Function:** `calculate_summary`

**Before:**
```python
    average = total / len(by_category)
```

**After:**
```python
    average = total / len(expenses)
```

**Test result after this change:** PASS (11/11 tests green)

---

## Overall Status

**COMPLETE** — all changes applied, all tests pass.

---

## Manual Verification

To confirm the fix works end-to-end:

1. Start the API server:
   ```bash
   cd homework-4 && source venv/bin/activate && uvicorn src.main:app --reload
   ```

2. Create three expenses with two sharing the same category:
   ```bash
   curl -s -X POST http://localhost:8000/expenses \
     -H "Content-Type: application/json" \
     -d '{"amount": 10.0, "category": "food", "description": "breakfast", "date": "2024-01-01"}'

   curl -s -X POST http://localhost:8000/expenses \
     -H "Content-Type: application/json" \
     -d '{"amount": 20.0, "category": "food", "description": "lunch", "date": "2024-01-02"}'

   curl -s -X POST http://localhost:8000/expenses \
     -H "Content-Type: application/json" \
     -d '{"amount": 30.0, "category": "transport", "description": "taxi", "date": "2024-01-03"}'
   ```

3. Fetch the summary and verify `average_amount`:
   ```bash
   curl -s http://localhost:8000/summary | python -m json.tool
   ```

   **Expected output (key fields):**
   ```json
   {
     "total_expenses": 3,
     "total_amount": 60.0,
     "average_amount": 20.0
   }
   ```
   Before the fix, `average_amount` would have been `30.0` (60 / 2 categories).
   After the fix it is `20.0` (60 / 3 expenses).

---

## References

- **File modified:** `src/utils.py` (line 38)
- **Plan followed:** `context/bugs/002-incorrect-average/implementation-plan.md`
