"""
Unit tests for Bug 002 — Incorrect Average in Summary Calculation.

Fix location: src/utils.py:38, function `calculate_summary`
Before fix:   average = total / len(by_category)   # wrong: divides by category count
After fix:    average = total / len(expenses)       # correct: divides by expense count

# FIRST Checklist applied to every test in this file
# ┌────┬──────────────────────────────────────────────────────┬───────────┐
# │  # │ Check                                                │ Principle │
# ├────┼──────────────────────────────────────────────────────┼───────────┤
# │  1 │ Executes in under 1 second (TestClient, no I/O)     │ Fast      │
# │  2 │ Uses no external services or network                │ Fast      │
# │  3 │ reset_storage fixture (autouse) clears state        │ Indep.    │
# │  4 │ No shared mutable state between tests               │ Indep.    │
# │  5 │ Fixed dates and fixed amounts                       │ Repeatable│
# │  6 │ No wall-clock time, no OS-specific behaviour        │ Repeatable│
# │  7 │ Every test has ≥1 assert statement                  │ Self-val. │
# │  8 │ Assert messages identify expected vs actual         │ Self-val. │
# │  9 │ Covers the exact line changed in fix-summary.md     │ Timely    │
# │ 10 │ Happy path and edge/boundary cases both present     │ Timely    │
# └────┴──────────────────────────────────────────────────────┴───────────┘
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.storage import storage


@pytest.fixture(autouse=True)
def reset_storage():
    storage._expenses.clear()
    yield
    storage._expenses.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Core fix: two expenses share a category — len(by_category) != len(expenses)
# Before fix: 60.0 / 2 categories = 30.0  (wrong)
# After fix:  60.0 / 3 expenses   = 20.0  (correct)
# Mirrors the exact manual verification scenario in fix-summary.md.
# ---------------------------------------------------------------------------

def test_average_divides_by_expense_count_not_category_count(client):
    client.post("/expenses", json={"description": "breakfast", "amount": 10.0,
                                   "category": "food", "date": "2024-01-01"})
    client.post("/expenses", json={"description": "lunch", "amount": 20.0,
                                   "category": "food", "date": "2024-01-02"})
    client.post("/expenses", json={"description": "taxi", "amount": 30.0,
                                   "category": "transport", "date": "2024-01-03"})

    resp = client.get("/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["average_amount"] == 20.0, (
        f"Expected 20.0 (60.0 / 3 expenses), got {body['average_amount']}. "
        "Bug produces 30.0 (60.0 / 2 categories)."
    )
    assert body["total_expenses"] == 3, (
        f"Expected total_expenses 3, got {body['total_expenses']}."
    )
    assert body["total_amount"] == 60.0, (
        f"Expected total_amount 60.0, got {body['total_amount']}."
    )


# ---------------------------------------------------------------------------
# Extreme edge case: all expenses in one category
# Before fix: 100.0 / 1 category = 100.0  (wrong)
# After fix:  100.0 / 4 expenses  =  25.0  (correct)
# ---------------------------------------------------------------------------

def test_average_all_same_category(client):
    for amount in [10.0, 20.0, 30.0, 40.0]:
        client.post("/expenses", json={"description": "item", "amount": amount,
                                       "category": "food", "date": "2024-06-01"})

    resp = client.get("/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["average_amount"] == 25.0, (
        f"Expected 25.0 (100.0 / 4 expenses), got {body['average_amount']}. "
        "Bug produces 100.0 (100.0 / 1 category)."
    )


# ---------------------------------------------------------------------------
# Boundary case: single expense
# len(expenses) == 1 and len(by_category) == 1, so both buggy and fixed code
# agree — this guards against regression in the single-item path.
# ---------------------------------------------------------------------------

def test_average_single_expense(client):
    client.post("/expenses", json={"description": "coffee", "amount": 4.50,
                                   "category": "food", "date": "2024-03-15"})

    resp = client.get("/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["average_amount"] == 4.50, (
        f"Expected 4.50 (single expense), got {body['average_amount']}."
    )
    assert body["total_expenses"] == 1, (
        f"Expected total_expenses 1, got {body['total_expenses']}."
    )


# ---------------------------------------------------------------------------
# Happy path: one expense per category (len(expenses) == len(by_category))
# The bug was invisible here; this confirms the fix does not break this case.
# ---------------------------------------------------------------------------

def test_average_one_expense_per_category(client):
    client.post("/expenses", json={"description": "groceries", "amount": 10.0,
                                   "category": "food", "date": "2024-07-01"})
    client.post("/expenses", json={"description": "bus", "amount": 20.0,
                                   "category": "transport", "date": "2024-07-02"})

    resp = client.get("/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["average_amount"] == 15.0, (
        f"Expected 15.0 (30.0 / 2 expenses), got {body['average_amount']}."
    )
    assert body["total_expenses"] == 2, (
        f"Expected total_expenses 2, got {body['total_expenses']}."
    )
