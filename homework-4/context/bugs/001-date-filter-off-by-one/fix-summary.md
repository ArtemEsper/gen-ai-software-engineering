# Fix Summary: Bug 001 — Off-by-One in Date Range Filter

## Changes Made

### Change 1 of 1

- **File:** `src/utils.py`
- **Location:** Line 18, inside `filter_by_date_range`
- **Before:**
  ```python
          result = [e for e in result if e.date < end]
  ```
- **After:**
  ```python
          result = [e for e in result if e.date <= end]
  ```
- **Test result after this change:** PASS (22/22 tests green)

## Overall Status

**COMPLETE** — all changes applied, all 22 tests pass.

## Manual Verification

1. Start the API server:
   ```bash
   cd homework-4 && source venv/bin/activate && uvicorn src.main:app --reload
   ```

2. Create an expense dated exactly on a chosen end date (e.g. `2024-03-15`):
   ```bash
   curl -X POST http://localhost:8000/expenses \
     -H "Content-Type: application/json" \
     -d '{"description":"boundary test","amount":50.0,"category":"food","date":"2024-03-15"}'
   ```

3. Query with `end_date` equal to that date — the expense **must appear**:
   ```bash
   curl "http://localhost:8000/expenses?end_date=2024-03-15"
   # Expected: the expense above is included in the response
   ```

4. Query with `end_date` one day earlier — the expense **must be excluded**:
   ```bash
   curl "http://localhost:8000/expenses?end_date=2024-03-14"
   # Expected: empty list (or no entry for the above expense)
   ```

## References

- **File modified:** `src/utils.py`
- **Plan followed:** `context/bugs/001-date-filter-off-by-one/implementation-plan.md`
