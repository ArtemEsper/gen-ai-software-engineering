# Bug 002: Incorrect Average in Summary Calculation

## Summary
The `calculate_summary()` function computes the average expense amount by dividing total spend by the number of distinct categories instead of the number of expenses.

## Affected File
`src/utils.py` — function `calculate_summary`

## Expected Behaviour
`average_amount` should equal `total_amount / total_expenses` (i.e., arithmetic mean per expense).

## Actual Behaviour
`average_amount` equals `total_amount / len(by_category)` — the divisor is the count of distinct categories, not the count of expenses.

## Root Cause
```python
average = total / len(by_category)   # should be total / len(expenses)
```

## Impact
- Average is wrong whenever expenses span a different number of categories than the number of expenses (which is almost always)
- With a single category the bug is masked (category count == 1 only matches expense count by coincidence in trivial cases)

## Reproduction Steps
1. Create 3 expenses: 2 in "food" ($10, $20) and 1 in "transport" ($30)
2. Call `GET /summary`
3. Expected average: $60 / 3 = $20.00
4. Actual average: $60 / 2 = $30.00 (2 distinct categories)

## Severity
Medium — financial summary data is incorrect.
