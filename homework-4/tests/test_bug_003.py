"""
FIRST-compliant tests for Bug 003: Missing delete validation.
Verifies that deleting a non-existent expense returns 404 after the fix.

FIRST Checklist:
  F - Fast: TestClient, no I/O
  I - Independent: reset_storage fixture clears state
  R - Repeatable: deterministic inputs
  S - Self-validating: explicit assertions
  T - Timely: tests the specific fix at src/main.py:64-68
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


SAMPLE = {
    "description": "Test expense",
    "amount": 25.0,
    "category": "transport",
    "date": "2026-05-10",
}


def test_delete_nonexistent_returns_404(client):
    """DELETE of a non-existent ID must return 404."""
    resp = client.delete("/expenses/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Expense not found"


def test_delete_existing_returns_200(client):
    """DELETE of an existing expense returns 200 and removes it."""
    created = client.post("/expenses", json=SAMPLE).json()
    resp = client.delete(f"/expenses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Expense deleted"

    get_resp = client.get(f"/expenses/{created['id']}")
    assert get_resp.status_code == 404


def test_double_delete_returns_404(client):
    """Deleting the same expense twice: first succeeds, second returns 404."""
    created = client.post("/expenses", json=SAMPLE).json()
    eid = created["id"]

    first = client.delete(f"/expenses/{eid}")
    assert first.status_code == 200

    second = client.delete(f"/expenses/{eid}")
    assert second.status_code == 404
    assert second.json()["detail"] == "Expense not found"
