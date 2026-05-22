# Test Report: Bug 001 — Off-by-One in Date Range Filter

## Test Summary
- **Tests generated:** 4
- **Tests passed:** 4
- **Tests failed:** 0
- **FIRST compliance:** PASS (all 5 principles satisfied)

## Generated Tests

### 1. `test_end_date_inclusive`
- **What it tests:** `src/utils.py:18` — expense on end date is included after `<` → `<=` fix
- **Pass/fail:** PASS
- **FIRST:** F=Y I=Y R=Y S=Y T=Y

### 2. `test_after_end_date_excluded`
- **What it tests:** `src/utils.py:18` — expense after end date is still excluded
- **Pass/fail:** PASS
- **FIRST:** F=Y I=Y R=Y S=Y T=Y

### 3. `test_full_range_boundaries`
- **What it tests:** `src/utils.py:15,18` — both start and end boundaries are inclusive
- **Pass/fail:** PASS
- **FIRST:** F=Y I=Y R=Y S=Y T=Y

### 4. `test_same_start_and_end_date`
- **What it tests:** `src/utils.py:15,18` — single-day range returns that day's expenses
- **Pass/fail:** PASS
- **FIRST:** F=Y I=Y R=Y S=Y T=Y

## Coverage Impact
- Lines newly covered by these tests: `src/utils.py:16-18` (end-date filter path)
- Coverage delta: `src/utils.py` from 70% → higher (end-date branch now exercised)

## FIRST Compliance Matrix

| Test Name | F | I | R | S | T |
|-----------|---|---|---|---|---|
| test_end_date_inclusive | Y | Y | Y | Y | Y |
| test_after_end_date_excluded | Y | Y | Y | Y | Y |
| test_full_range_boundaries | Y | Y | Y | Y | Y |
| test_same_start_and_end_date | Y | Y | Y | Y | Y |
