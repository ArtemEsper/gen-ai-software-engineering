# Bug 003: Missing ID Validation on Delete

## Summary
The `DELETE /expenses/{expense_id}` endpoint does not verify that the expense exists before attempting deletion. It returns HTTP 200 for any ID, including non-existent ones.

## Affected File
`src/main.py` — function `delete_expense`

## Expected Behaviour
Deleting a non-existent expense should return HTTP 404 with `{"detail": "Expense not found"}`.

## Actual Behaviour
Deleting a non-existent expense returns HTTP 200 with `{"detail": "Expense deleted"}` — a silent success for a no-op.

## Root Cause
```python
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    storage.delete(expense_id)          # returns False for missing ID but is ignored
    return {"detail": "Expense deleted"}
```
The return value of `storage.delete()` (which is `False` when the ID doesn't exist) is never checked.

## Impact
- Clients cannot distinguish between successful deletion and a no-op
- Violates REST conventions (DELETE of non-existent resource should 404)
- Could mask bugs in client applications that pass wrong IDs

## Reproduction Steps
1. Call `DELETE /expenses/does-not-exist`
2. Response is 200 `{"detail": "Expense deleted"}` instead of 404

## Severity
Low — no data corruption, but violates API contract.
