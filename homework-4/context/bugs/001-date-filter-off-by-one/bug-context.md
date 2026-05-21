# Bug 001: Off-by-One in Date Range Filter

## Summary
The date range filter in `filter_by_date_range()` excludes expenses that fall on the end date of the range.

## Affected File
`src/utils.py` — function `filter_by_date_range`

## Expected Behaviour
When a user filters expenses with `end_date=2026-05-15`, expenses dated 2026-05-15 should be **included** in the results.

## Actual Behaviour
Expenses dated exactly on `end_date` are **excluded** because the comparison uses strict less-than (`<`) instead of less-than-or-equal (`<=`).

## Root Cause
```python
result = [e for e in result if e.date < end]   # should be <=
```

## Impact
- Users miss the final day's expenses when filtering by date range
- Financial summaries based on date ranges will undercount

## Reproduction Steps
1. Create an expense with `date=2026-05-15`
2. Call `GET /expenses?start_date=2026-05-01&end_date=2026-05-15`
3. The expense is not returned

## Severity
Medium — data is silently excluded from query results.
