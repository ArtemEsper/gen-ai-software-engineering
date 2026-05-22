# Codebase Research: Bug 001 — Off-by-One in Date Range Filter

## Bug Summary
The date range filter in `filter_by_date_range()` uses strict less-than (`<`)
instead of less-than-or-equal (`<=`) when comparing against the end date. This
excludes expenses that fall exactly on the boundary day.

## Affected Code

### Primary location
**File:** `src/utils.py:8-19` — function `filter_by_date_range`

```python
def filter_by_date_range(
    expenses: List[Expense],
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Expense]:
    result = expenses
    if start is not None:
        result = [e for e in result if e.date >= start]
    if end is not None:
        # BUG: uses < instead of <=, excluding expenses on the end date
        result = [e for e in result if e.date < end]
    return result
```

The bug is on **`src/utils.py:18`** — the comparison `e.date < end`.

### Call site
**File:** `src/main.py:41-42` — inside `list_expenses`

```python
    if start_date or end_date:
        expenses = filter_by_date_range(expenses, start_date, end_date)
```

The query parameters `start_date` and `end_date` from the GET `/expenses`
endpoint are passed directly to the buggy function.

### Related — start-date comparison (correct)
**File:** `src/utils.py:15` — `e.date >= start` — this uses `>=`, which
correctly **includes** expenses on the start date. The asymmetry between
`>=` (start) and `<` (end) confirms this is a bug, not an intentional
half-open interval.

## Root Cause
Line 18 uses `<` where it should use `<=`. A user querying
`?start_date=2026-05-01&end_date=2026-05-15` expects to receive expenses
from May 1 through May 15 inclusive, but expenses dated May 15 are excluded.

## Impact
- **User-facing:** Date-filtered expense lists silently omit the last day.
- **Financial:** Summaries or exports built on filtered results will
  undercount.

## References
| File | Lines | What |
|------|-------|------|
| `src/utils.py` | 8-19 | `filter_by_date_range` function (contains bug) |
| `src/utils.py` | 18 | Buggy comparison `e.date < end` |
| `src/utils.py` | 15 | Correct comparison `e.date >= start` (for contrast) |
| `src/main.py` | 41-42 | Call site in `list_expenses` |
| `src/models.py` | 30 | `Expense.date` field definition |
