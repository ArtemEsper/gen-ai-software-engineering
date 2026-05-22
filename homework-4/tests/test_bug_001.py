"""
FIRST-compliant tests for Bug 001: Off-by-one in date range filter.
Verifies that expenses on the end date are included after the fix.

FIRST Checklist:
  F - Fast: TestClient, no I/O
  I - Independent: reset_storage fixture clears state
  R - Repeatable: deterministic fixed dates
  S - Self-validating: explicit assertions
  T - Timely: tests the specific fix at src/utils.py:18
"""

import pytest
from datetime import date
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


def _create(client, dt: str, desc: str = "item"):
    return client.post("/expenses", json={
        "description": desc,
        "amount": 10.0,
        "category": "food",
        "date": dt,
    })


def test_end_date_inclusive(client):
    """Expense on the end date must be returned."""
    _create(client, "2026-05-15")
    resp = client.get("/expenses", params={"end_date": "2026-05-15"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_after_end_date_excluded(client):
    """Expense after the end date must not be returned."""
    _create(client, "2026-05-16")
    resp = client.get("/expenses", params={"end_date": "2026-05-15"})
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_full_range_boundaries(client):
    """Both start and end boundaries are inclusive."""
    _create(client, "2026-05-01", "start-boundary")
    _create(client, "2026-05-15", "end-boundary")
    _create(client, "2026-05-10", "middle")
    _create(client, "2026-04-30", "before-range")
    _create(client, "2026-05-16", "after-range")

    resp = client.get("/expenses", params={
        "start_date": "2026-05-01",
        "end_date": "2026-05-15",
    })
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 3
    descriptions = {r["description"] for r in results}
    assert descriptions == {"start-boundary", "end-boundary", "middle"}


def test_same_start_and_end_date(client):
    """When start == end, expenses on that exact date are returned."""
    _create(client, "2026-05-10")
    resp = client.get("/expenses", params={
        "start_date": "2026-05-10",
        "end_date": "2026-05-10",
    })
    assert resp.status_code == 200
    assert len(resp.json()) == 1
