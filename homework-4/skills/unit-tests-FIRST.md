# Skill: FIRST Unit Test Principles

## Purpose

Defines the FIRST framework for writing high-quality unit tests. The Unit
Test Generator agent must apply this skill when generating tests and writing
`test-report.md`.

---

## FIRST Principles

### F — Fast
Tests execute in milliseconds. No network calls, no file I/O, no database
connections, no sleeps or timeouts. Use in-memory test clients and fixtures.

**Compliant:**
```python
def test_create_expense(client):
    resp = client.post("/expenses", json=SAMPLE)
    assert resp.status_code == 201
```

**Non-compliant:**
```python
def test_create_expense():
    import requests
    resp = requests.post("http://localhost:8000/expenses", json=SAMPLE)  # real HTTP
    assert resp.status_code == 201
```

### I — Independent
Each test stands alone. No test relies on state left by a previous test. No
shared mutable state between tests. Use fresh fixtures for each test.

**Compliant:**
```python
@pytest.fixture(autouse=True)
def reset():
    storage._expenses.clear()
    yield
    storage._expenses.clear()
```

**Non-compliant:**
```python
created_id = None

def test_create():
    global created_id
    created_id = create_expense()  # later tests depend on this

def test_get():
    get_expense(created_id)  # fails if test_create didn't run first
```

### R — Repeatable
Same result every run, regardless of environment, time, or execution order.
No randomness, no dependency on wall-clock time, no OS-specific behaviour.

**Compliant:**
```python
def test_date_filter():
    expense = create_expense(date=date(2026, 5, 15))  # deterministic date
    results = filter_by_date_range([expense], end=date(2026, 5, 15))
```

**Non-compliant:**
```python
def test_date_filter():
    expense = create_expense(date=date.today())  # depends on when test runs
```

### S — Self-Validating
Pass or fail without manual inspection. Clear assertions that produce
meaningful failure messages. No "check the log output" or "verify visually".

**Compliant:**
```python
def test_average():
    summary = calculate_summary(expenses)
    assert summary.average_amount == 20.0, f"Expected 20.0, got {summary.average_amount}"
```

**Non-compliant:**
```python
def test_average():
    summary = calculate_summary(expenses)
    print(f"Average: {summary.average_amount}")  # requires human to check
```

### T — Timely
Tests are written alongside the code change, not as an afterthought. Each
fix or feature gets its corresponding test in the same commit.

---

## Per-Test Checklist

The Unit Test Generator must verify each generated test against this checklist:

| # | Check | FIRST Principle |
|---|-------|-----------------|
| 1 | Executes in under 1 second | Fast |
| 2 | Uses no external services or network | Fast |
| 3 | Has its own setup/teardown or uses a fresh fixture | Independent |
| 4 | Does not reference global mutable state from other tests | Independent |
| 5 | Uses deterministic inputs (fixed dates, known IDs) | Repeatable |
| 6 | Produces same result on any OS / timezone | Repeatable |
| 7 | Contains at least one `assert` statement | Self-validating |
| 8 | Assert messages are descriptive on failure | Self-validating |
| 9 | Covers the specific code change from fix-summary.md | Timely |
| 10 | Tests both the happy path and the boundary/edge case | Timely |

---

## Test Report Sections

Every `test-report.md` produced using this skill must contain:

### 1. Test Summary
- Total tests generated
- Tests passed / failed
- FIRST compliance: pass / fail per principle

### 2. Generated Tests
For each test:
- Test name
- What it tests (file:line of the changed code)
- FIRST checklist result (all 10 checks)
- Pass/fail status

### 3. Coverage Impact
- Lines covered by new tests
- Coverage delta (before vs. after)

### 4. FIRST Compliance Matrix
| Test Name | F | I | R | S | T |
|-----------|---|---|---|---|---|
| test_xxx  | Y | Y | Y | Y | Y |
