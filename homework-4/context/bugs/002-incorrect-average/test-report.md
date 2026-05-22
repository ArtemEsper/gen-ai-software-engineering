# Test Report: Bug 002 — Incorrect Average in Summary Calculation

## 1. Test Summary

| Metric | Value |
|--------|-------|
| Tests generated | 4 |
| Tests passed | 4 |
| Tests failed | 0 |
| Total suite (including pre-existing) | 15 passed / 0 failed |
| Execution time | 0.38 s |
| FIRST compliance | **PASS** — all five principles satisfied |

---

## 2. Generated Tests

### `test_average_divides_by_expense_count_not_category_count`

- **What it tests:** `src/utils.py:38` — the core fix: `average = total / len(expenses)` when two expenses share a category, so `len(by_category) != len(expenses)`. Mirrors the exact 3-expense manual verification scenario from `fix-summary.md` (food ×2, transport ×1; total 60.0, expected average 20.0 not 30.0).
- **FIRST checklist:**

  | # | Check | Result |
  |---|-------|--------|
  | 1 | Executes in under 1 second | ✅ |
  | 2 | Uses no external services or network | ✅ |
  | 3 | Uses `reset_storage` autouse fixture | ✅ |
  | 4 | No shared mutable state from other tests | ✅ |
  | 5 | Fixed dates (2024-01-01/02/03) and fixed amounts | ✅ |
  | 6 | No wall-clock time dependency | ✅ |
  | 7 | Three `assert` statements | ✅ |
  | 8 | Messages show expected value, actual value, and what the bug would produce | ✅ |
  | 9 | Directly targets the changed line `src/utils.py:38` | ✅ |
  | 10 | Tests the canonical failing scenario for the bug | ✅ |

- **Status:** PASS

---

### `test_average_all_same_category`

- **What it tests:** `src/utils.py:38` — extreme edge case where all four expenses share one category. Before fix: `100.0 / 1 = 100.0`; after fix: `100.0 / 4 = 25.0`.
- **FIRST checklist:**

  | # | Check | Result |
  |---|-------|--------|
  | 1 | Executes in under 1 second | ✅ |
  | 2 | Uses no external services or network | ✅ |
  | 3 | Uses `reset_storage` autouse fixture | ✅ |
  | 4 | No shared mutable state from other tests | ✅ |
  | 5 | Fixed amounts (10, 20, 30, 40) and fixed date | ✅ |
  | 6 | No wall-clock time dependency | ✅ |
  | 7 | One `assert` statement | ✅ |
  | 8 | Message shows expected, actual, and what the bug would produce | ✅ |
  | 9 | Targets the changed line `src/utils.py:38` | ✅ |
  | 10 | Tests the boundary case most severely affected by the bug | ✅ |

- **Status:** PASS

---

### `test_average_single_expense`

- **What it tests:** `src/utils.py:38` — boundary case with one expense. `len(expenses) == len(by_category) == 1`, so both the buggy and fixed code agree. Guards against regression in the single-item path.
- **FIRST checklist:**

  | # | Check | Result |
  |---|-------|--------|
  | 1 | Executes in under 1 second | ✅ |
  | 2 | Uses no external services or network | ✅ |
  | 3 | Uses `reset_storage` autouse fixture | ✅ |
  | 4 | No shared mutable state from other tests | ✅ |
  | 5 | Fixed amount (4.50) and fixed date (2024-03-15) | ✅ |
  | 6 | No wall-clock time dependency | ✅ |
  | 7 | Two `assert` statements | ✅ |
  | 8 | Messages show expected vs actual values | ✅ |
  | 9 | Targets `src/utils.py:38` via the summary endpoint | ✅ |
  | 10 | Covers the minimum boundary (n=1) | ✅ |

- **Status:** PASS

---

### `test_average_one_expense_per_category`

- **What it tests:** `src/utils.py:38` — happy path where every expense has a unique category (`len(expenses) == len(by_category)`). The bug was invisible here; confirms the fix does not break this case.
- **FIRST checklist:**

  | # | Check | Result |
  |---|-------|--------|
  | 1 | Executes in under 1 second | ✅ |
  | 2 | Uses no external services or network | ✅ |
  | 3 | Uses `reset_storage` autouse fixture | ✅ |
  | 4 | No shared mutable state from other tests | ✅ |
  | 5 | Fixed amounts (10.0, 20.0) and fixed dates | ✅ |
  | 6 | No wall-clock time dependency | ✅ |
  | 7 | Two `assert` statements | ✅ |
  | 8 | Messages show expected vs actual values | ✅ |
  | 9 | Targets `src/utils.py:38` via the summary endpoint | ✅ |
  | 10 | Tests the happy path (no category collisions) | ✅ |

- **Status:** PASS

---

## 3. Coverage Impact

The new tests call `calculate_summary` via the `GET /summary` endpoint in scenarios not previously exercised by `test_basic.py`:

| Scenario | Covered by existing tests? | Covered by new tests? |
|---|---|---|
| Average with duplicate categories (core bug) | No | Yes |
| Average with all expenses in one category | No | Yes |
| Average with a single expense | No | Yes |
| Average with one expense per category | No | Yes |

**Lines directly exercised by new tests in `src/utils.py`:**
- Line 31: `total = sum(e.amount for e in expenses)`
- Lines 33–35: `by_category` accumulation loop
- **Line 38:** `average = total / len(expenses)` ← the fixed line
- Lines 40–44: `ExpenseSummary` construction

**Coverage delta:** The four new tests add meaningful coverage of `calculate_summary` under the multi-category-collision scenarios that the bug affected. The existing `test_summary_single_category` and `test_summary_empty` tests already covered the empty-list and single-category paths.

---

## 4. FIRST Compliance Matrix

| Test Name | F | I | R | S | T |
|-----------|---|---|---|---|---|
| `test_average_divides_by_expense_count_not_category_count` | Y | Y | Y | Y | Y |
| `test_average_all_same_category` | Y | Y | Y | Y | Y |
| `test_average_single_expense` | Y | Y | Y | Y | Y |
| `test_average_one_expense_per_category` | Y | Y | Y | Y | Y |
