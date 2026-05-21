# Implementation Plan: Bug 002 — Incorrect Average in Summary Calculation

## Objective
Fix the average expense calculation to divide by the number of expenses
instead of the number of categories.

## Changes

### Change 1 of 1
**File:** `src/utils.py`
**Line:** 38
**Function:** `calculate_summary`

**Before:**
```python
    average = total / len(by_category)
```

**After:**
```python
    average = total / len(expenses)
```

## Test Command
```bash
cd homework-4 && source venv/bin/activate && python -m pytest tests/ -v
```

## Acceptance Criteria
1. `GET /summary` returns `average_amount == total_amount / total_expenses`.
2. With 3 expenses ($10 food, $20 food, $30 transport), average is $20.00
   (not $30.00).
3. With a single expense, average equals that expense's amount.
4. Empty expense list still returns `average_amount == 0.0`.
5. All existing tests continue to pass.
