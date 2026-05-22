# Fix Summary: Bug 003 — Missing ID Validation on Delete

## Changes Made

### Change 1 of 1
- **File:** `src/main.py`
- **Lines:** 64-68
- **Function:** `delete_expense`

**Before:**
```python
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    # BUG: no existence check — always returns 200, even for non-existent IDs
    storage.delete(expense_id)
    return {"detail": "Expense deleted"}
```

**After:**
```python
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    deleted = storage.delete(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}
```

- **Test result after change:** PASS — 15 tests green (11 baseline + 4 bug-002 tests)

## Overall Status
**COMPLETE** — all changes applied, all tests pass.

## Manual Verification
1. Start app: `source venv/bin/activate && python -m uvicorn src.main:app`
2. Create an expense: `curl -X POST http://localhost:8000/expenses -H 'Content-Type: application/json' -d '{"description":"Test","amount":10,"category":"food","date":"2026-05-01"}'`
3. Note the returned `id`
4. Delete it: `curl -X DELETE http://localhost:8000/expenses/<id>` — should return 200
5. Delete again: `curl -X DELETE http://localhost:8000/expenses/<id>` — should return 404
6. Delete non-existent: `curl -X DELETE http://localhost:8000/expenses/fake-id` — should return 404

## References
- Implementation plan: `context/bugs/003-missing-delete-validation/implementation-plan.md`
- Modified file: `src/main.py`
- `HTTPException` was already imported at `src/main.py:5`
