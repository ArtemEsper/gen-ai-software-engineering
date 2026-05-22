# Codebase Research: Bug 003 — Missing ID Validation on Delete

## Bug Summary
The `DELETE /expenses/{expense_id}` endpoint does not check whether the
expense exists before attempting deletion. It returns HTTP 200 with
`{"detail": "Expense deleted"}` regardless of whether the ID was found,
violating standard REST conventions.

## Affected Code

### Primary location
**File:** `src/main.py:64-68` — function `delete_expense`

```python
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    # BUG: no existence check — always returns 200, even for non-existent IDs
    storage.delete(expense_id)
    return {"detail": "Expense deleted"}
```

The return value of `storage.delete()` is ignored. The function always
returns a 200 response.

### Storage layer
**File:** `src/storage.py:21-25` — method `ExpenseStorage.delete`

```python
    def delete(self, expense_id: str) -> bool:
        if expense_id in self._expenses:
            del self._expenses[expense_id]
            return True
        return False
```

`delete()` already returns `False` when the ID is not found — the
information is available but the endpoint ignores it.

### Comparison — GET endpoint (correct pattern)
**File:** `src/main.py:50-55` — function `get_expense`

```python
@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: str):
    expense = storage.get(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense
```

The GET-by-ID endpoint correctly raises 404 for missing IDs. The DELETE
endpoint should follow the same pattern.

## Root Cause
`delete_expense` on line 67 calls `storage.delete(expense_id)` without
inspecting the boolean return value. It should check the return and raise
`HTTPException(status_code=404)` when the result is `False`.

## Impact
- **User-facing:** Clients cannot distinguish a successful deletion from a
  no-op on a non-existent resource.
- **REST compliance:** DELETE of a non-existent resource should return 404.
- **Downstream:** Client applications that rely on HTTP status codes to
  confirm deletion may silently proceed after a no-op.

## References
| File | Lines | What |
|------|-------|------|
| `src/main.py` | 64-68 | `delete_expense` endpoint (contains bug) |
| `src/main.py` | 67 | `storage.delete()` return value ignored |
| `src/storage.py` | 21-25 | `ExpenseStorage.delete` returns `bool` |
| `src/main.py` | 50-55 | `get_expense` — correct 404 pattern for comparison |
