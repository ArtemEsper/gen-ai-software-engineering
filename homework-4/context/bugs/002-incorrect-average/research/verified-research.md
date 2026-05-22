# Verified Research: Bug 002 — Incorrect Average in Summary Calculation

## 1. Verification Summary

- **Overall status:** PASS
- **Research Quality Level:** 5 — Excellent
- **References checked:** 7 | **Verified:** 7 | **Failed:** 0
- **Justification:** All file:line references point to existing files and correct line numbers. All code snippets match source verbatim. Root cause is correctly identified and consistent with actual code behaviour. Impact assessment is complete and realistic.

---

## 2. Verified Claims

| # | Claim | File:Line | Status | Evidence |
|---|-------|-----------|--------|----------|
| 1 | `calculate_summary` function located at `src/utils.py:22-45` | `src/utils.py:22-45` | VERIFIED | Function definition begins at line 22 (`def calculate_summary(...)`) and ends at line 45 (closing parenthesis of the return statement). |
| 2 | Code snippet of `calculate_summary` matches source | `src/utils.py:22-45` | VERIFIED | Snippet matches actual source character-for-character, including the `# BUG:` comment on line 37. |
| 3 | Buggy line is `src/utils.py:38` — `average = total / len(by_category)` | `src/utils.py:38` | VERIFIED | Line 38 reads exactly: `    average = total / len(by_category)` |
| 4 | Correct divisor `len(expenses)` already used on line 41 for `total_expenses` | `src/utils.py:41` | VERIFIED | Line 41 reads: `        total_expenses=len(expenses),` |
| 5 | Call site is `get_summary` at `src/main.py:58-61` | `src/main.py:58-61` | VERIFIED | Lines 58-61 contain the `@app.get("/summary")` decorator and `get_summary()` function that calls `calculate_summary(expenses)`. Snippet matches verbatim. |
| 6 | `ExpenseSummary` model at `src/models.py:34-38` | `src/models.py:34-38` | VERIFIED | Lines 34-38 define `class ExpenseSummary(BaseModel)` with fields `total_expenses`, `total_amount`, `average_amount`, `by_category`. Snippet matches verbatim. |
| 7 | Root cause: divides total by `len(by_category)` (distinct categories) instead of `len(expenses)` (expense count) | `src/utils.py:38` | VERIFIED | Line 38 uses `len(by_category)` as divisor. `by_category` is a `defaultdict(float)` keyed by `e.category.value` (line 33-35), so its length is the number of distinct categories, not the number of expenses. |

---

## 3. Discrepancies Found

No discrepancies found.

---

## 4. Research Quality Assessment

- **Quality Level:** 5 — Excellent
- **Reasoning:** Meets all Level 5 criteria: all file:line references verified and accurate; all three code snippets match source verbatim; root cause is correctly identified with a clear explanation of why `len(by_category)` differs from `len(expenses)`; impact assessment is complete, covering both the user-facing symptom (wrong `/summary` response) and the conditions under which the bug is masked.
- **Strengths:**
  - Every line number reference is precise and correct.
  - Code snippets are exact copies of the source, not paraphrased.
  - Root cause explanation includes a concrete example (3 expenses across 2 categories).
  - Impact section identifies the masking condition (single category) and explains why existing tests may not catch the bug.
  - References table provides a clear summary of all relevant locations.
- **Weaknesses / gaps:**
  - The mention of `test_summary_single_category` in the impact section is not backed by a file:line reference to the test file, though this is a minor observation since the test file is outside the stated scope of the research.

---

## 5. References

| File | Lines Inspected |
|------|-----------------|
| `src/utils.py` | 1-46 (full file) |
| `src/main.py` | 1-69 (full file) |
| `src/models.py` | 1-39 (full file) |
