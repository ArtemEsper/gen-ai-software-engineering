# Implementation Plan: Bug 001 — Off-by-One in Date Range Filter

## Objective
Fix the date range filter so that expenses on the end date are included.

## Changes

### Change 1 of 1
**File:** `src/utils.py`
**Line:** 18
**Function:** `filter_by_date_range`

**Before:**
```python
        result = [e for e in result if e.date < end]
```

**After:**
```python
        result = [e for e in result if e.date <= end]
```

## Test Command
```bash
cd homework-4 && source venv/bin/activate && python -m pytest tests/ -v
```

## Acceptance Criteria
1. An expense dated exactly on `end_date` is returned by
   `GET /expenses?end_date=<that date>`.
2. An expense dated **after** `end_date` is still excluded.
3. All existing tests continue to pass.
4. The start-date boundary (`>=`) remains unchanged.
