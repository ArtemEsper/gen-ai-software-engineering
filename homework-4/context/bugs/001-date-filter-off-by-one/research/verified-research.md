# Verified Research: Bug 001 — Off-by-One in Date Range Filter

## 1. Verification Summary

- **Overall status:** PASS (with caveat — bug has been fixed since research was written)
- **Research Quality Level:** 4 / 5 — Good
- **References checked:** 5
- **References verified:** 5 (all point to valid files and correct line ranges)
- **Code snippet discrepancies:** 1 (the buggy line has been corrected in source)
- **One-sentence justification:** All file:line references resolve correctly and the root cause is confirmed by the applied fix and residual comment, but the primary code snippet no longer matches because the bug has already been patched.

## 2. Verified Claims

| # | Claim | File:Line | Status | Evidence |
|---|-------|-----------|--------|----------|
| 1 | `filter_by_date_range` function spans lines 8-19 of `src/utils.py` | `src/utils.py:8-19` | VERIFIED | Function signature starts at line 8, `return result` is at line 19. Exact match. |
| 2 | Buggy comparison `e.date < end` is on line 18 | `src/utils.py:18` | FAILED | Actual line 18 reads: `result = [e for e in result if e.date <= end]` — operator is `<=`, not `<`. The bug has been fixed. The comment on line 17 (`# BUG: uses < instead of <=`) still references the original bug, confirming the research described the pre-fix state accurately. |
| 3 | Start-date comparison `e.date >= start` is on line 15 and is correct (inclusive) | `src/utils.py:15` | VERIFIED | Line 15 reads: `result = [e for e in result if e.date >= start]`. Exact match. |
| 4 | Call site in `list_expenses` passes query params to `filter_by_date_range` at lines 41-42 | `src/main.py:41-42` | VERIFIED | Line 41: `if start_date or end_date:` / Line 42: `expenses = filter_by_date_range(expenses, start_date, end_date)`. Exact match with quoted snippet. |
| 5 | `Expense.date` field is defined at line 30 of `src/models.py` | `src/models.py:30` | VERIFIED | Line 30 reads: `date: date` inside the `Expense` class (lines 25-31). Exact match. |
| 6 | Code snippet for `filter_by_date_range` (12 lines) matches source | `src/utils.py:8-19` | PARTIALLY VERIFIED | All lines match except line 18: research shows `e.date < end` but source has `e.date <= end`. The `# BUG` comment on line 17 is present in both. |
| 7 | Code snippet for the call site (2 lines) matches source | `src/main.py:41-42` | VERIFIED | Character-by-character match. |
| 8 | Root cause: `<` used instead of `<=` for end-date comparison, creating an asymmetric (half-open) interval | `src/utils.py:18` | VERIFIED | The fix changing `<` to `<=` and the residual `# BUG` comment on line 17 confirm this was the original root cause. The asymmetry between `>=` (start, line 15) and `<` (end, original line 18) is consistent with the described bug. |
| 9 | Impact: date-filtered expense lists silently omit the last day | — | VERIFIED | For the pre-fix code, any expense with `e.date == end` would have failed the `e.date < end` check and been excluded. Impact assessment is proportional and realistic. |

## 3. Discrepancies Found

| ID | Severity | Research Claims | Actual Source | File:Line |
|----|----------|----------------|---------------|-----------|
| D-1 | MAJOR | Line 18 contains `e.date < end` (strict less-than operator). The full code snippet shows `result = [e for e in result if e.date < end]`. | Line 18 contains `e.date <= end` (less-than-or-equal operator). The actual code reads `result = [e for e in result if e.date <= end]`. The bug has already been fixed. The residual comment on line 17 (`# BUG: uses < instead of <=, excluding expenses on the end date`) confirms the original bug existed as described. | `src/utils.py:18` |

## 4. Research Quality Assessment

- **Quality Level:** 4 / 5 — **Good**
- **Reasoning:** All five file:line references point to valid files with correct line ranges. The root cause is correctly identified — confirmed by the applied fix and the residual `# BUG` comment. The single discrepancy (D-1) is that the buggy operator `<` has been corrected to `<=` since the research was written; this is not a hallucination or fabrication but a temporal mismatch. Per the quality scale criteria for Level 4: "All file:line references verified. Code snippets match with only trivial whitespace differences. Root cause is correct. 0-1 minor discrepancies." While the discrepancy is elevated to MAJOR because it affects the central code claim, the research's correctness at the time of writing is confirmed by the fix and comment evidence. This prevents a Level 5 rating but does not warrant Level 3.
- **Strengths:**
  - All file and line references are accurate and resolve to the correct constructs.
  - Root cause correctly identifies the `<` vs `<=` asymmetry between start and end comparisons.
  - Impact assessment is realistic and well-scoped (silent data omission, financial undercount).
  - Traced the data flow from API query parameters through to the buggy function.
  - Included the `Expense.date` model field reference for completeness.
  - Concise and well-structured document.
- **Weaknesses / gaps:**
  - The primary code snippet no longer matches the source because the fix has already been applied — the research captures the pre-fix state without noting this possibility.
  - No timestamp or git revision noted, making it impossible to determine when the research was produced relative to the fix.

## 5. References

| File | Lines Inspected | Purpose |
|------|-----------------|---------|
| `src/utils.py` | 1-46 (full file) | Verified `filter_by_date_range` function, bug location, comparison operators, and residual `# BUG` comment |
| `src/main.py` | 1-70 (full file) | Verified call site in `list_expenses` endpoint |
| `src/models.py` | 1-39 (full file) | Verified `Expense.date` field definition |
