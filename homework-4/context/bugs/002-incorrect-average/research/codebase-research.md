# Codebase Research: Bug 002 — Incorrect Average in Summary Calculation

## Bug Summary
The `calculate_summary()` function computes the average expense by dividing
the total amount by the number of **distinct categories** instead of the
number of **expenses**. This produces a wrong average whenever the expense
count differs from the category count.

## Affected Code

### Primary location
**File:** `src/utils.py:22-45` — function `calculate_summary`

```python
def calculate_summary(expenses: List[Expense]) -> ExpenseSummary:
    if not expenses:
        return ExpenseSummary(
            total_expenses=0,
            total_amount=0.0,
            average_amount=0.0,
            by_category={},
        )

    total = sum(e.amount for e in expenses)

    by_category = defaultdict(float)
    for e in expenses:
        by_category[e.category.value] += e.amount

    # BUG: divides by number of categories instead of number of expenses
    average = total / len(by_category)

    return ExpenseSummary(
        total_expenses=len(expenses),
        total_amount=round(total, 2),
        average_amount=round(average, 2),
        by_category=dict(by_category),
    )
```

The bug is on **`src/utils.py:38`** — `total / len(by_category)`.

The correct divisor is `len(expenses)`, which is already computed and used on
line 41 (`total_expenses=len(expenses)`), confirming the intent.

### Call site
**File:** `src/main.py:58-61` — inside `get_summary`

```python
@app.get("/summary", response_model=ExpenseSummary)
def get_summary():
    expenses = storage.list_all()
    return calculate_summary(expenses)
```

### Return model
**File:** `src/models.py:34-38` — `ExpenseSummary`

```python
class ExpenseSummary(BaseModel):
    total_expenses: int
    total_amount: float
    average_amount: float
    by_category: dict
```

## Root Cause
Line 38 divides `total` by `len(by_category)` (the number of distinct
category keys in the defaultdict) instead of `len(expenses)` (the number of
expense records). For example, 3 expenses across 2 categories yields
`total / 2` instead of `total / 3`.

## Impact
- **User-facing:** The `/summary` endpoint returns a wrong `average_amount`.
- **Masked in trivial cases:** When all expenses share one category,
  `len(by_category) == 1`, which only equals `len(expenses)` when there is
  exactly one expense. The baseline test (`test_summary_single_category`)
  uses two expenses in one category, so `average = total / 1` which
  differs from `total / 2` — but that test doesn't assert `average_amount`
  directly against the correct value, so the bug slips past.

## References
| File | Lines | What |
|------|-------|------|
| `src/utils.py` | 22-45 | `calculate_summary` function (contains bug) |
| `src/utils.py` | 38 | Buggy divisor `len(by_category)` |
| `src/utils.py` | 41 | Correct `len(expenses)` used for `total_expenses` |
| `src/main.py` | 58-61 | Call site in `get_summary` |
| `src/models.py` | 34-38 | `ExpenseSummary` model |
