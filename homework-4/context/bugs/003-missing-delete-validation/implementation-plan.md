# Implementation Plan: Bug 003 — Missing ID Validation on Delete

## Objective
Make the DELETE endpoint return 404 when the expense ID does not exist.

## Changes

### Change 1 of 1
**File:** `src/main.py`
**Lines:** 64-68
**Function:** `delete_expense`

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

Note: `HTTPException` is already imported at `src/main.py:5`.

## Test Command
```bash
cd homework-4 && source venv/bin/activate && python -m pytest tests/ -v
```

## Acceptance Criteria
1. `DELETE /expenses/{valid_id}` returns 200 and removes the expense.
2. `DELETE /expenses/{non_existent_id}` returns 404 with
   `{"detail": "Expense not found"}`.
3. After a successful delete, `GET /expenses/{same_id}` returns 404.
4. All existing tests continue to pass.
