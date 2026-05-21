"""
Baseline tests for the Expense Tracker API.

These tests verify core happy-path behaviour. They intentionally do NOT
cover the buggy code paths (date-range boundary, summary average, delete
of non-existent ID) so that the seeded bugs remain undetected until the
agent pipeline finds them.
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


SAMPLE_EXPENSE = {
    "description": "Lunch",
    "amount": 12.50,
    "category": "food",
    "date": "2026-05-01",
}


# ---------- POST /expenses ----------

def test_create_expense(client):
    resp = client.post("/expenses", json=SAMPLE_EXPENSE)
    assert resp.status_code == 201
    body = resp.json()
    assert body["description"] == "Lunch"
    assert body["amount"] == 12.50
    assert body["category"] == "food"
    assert "id" in body
    assert "created_at" in body


def test_create_expense_validation_error(client):
    resp = client.post("/expenses", json={"description": "", "amount": -5, "category": "food", "date": "2026-05-01"})
    assert resp.status_code == 422


def test_create_expense_invalid_category(client):
    resp = client.post("/expenses", json={"description": "X", "amount": 1, "category": "invalid", "date": "2026-05-01"})
    assert resp.status_code == 422


# ---------- GET /expenses ----------

def test_list_expenses_empty(client):
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_expenses_returns_created(client):
    client.post("/expenses", json=SAMPLE_EXPENSE)
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_expenses_filter_by_category(client):
    client.post("/expenses", json=SAMPLE_EXPENSE)
    client.post("/expenses", json={**SAMPLE_EXPENSE, "category": "transport", "description": "Bus"})

    resp = client.get("/expenses", params={"category": "food"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["category"] == "food"


# ---------- GET /expenses/{id} ----------

def test_get_expense_by_id(client):
    created = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    resp = client.get(f"/expenses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_expense_not_found(client):
    resp = client.get("/expenses/nonexistent-id")
    assert resp.status_code == 404


# ---------- GET /summary ----------

def test_summary_empty(client):
    resp = client.get("/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_expenses"] == 0
    assert body["total_amount"] == 0.0


def test_summary_single_category(client):
    """With one category the bug (dividing by category count) gives the same
    result as dividing by expense count, so this test passes even with the bug."""
    client.post("/expenses", json=SAMPLE_EXPENSE)
    client.post("/expenses", json={**SAMPLE_EXPENSE, "description": "Dinner", "amount": 20.0})
    resp = client.get("/summary")
    body = resp.json()
    assert body["total_expenses"] == 2
    assert body["total_amount"] == 32.50


# ---------- DELETE /expenses/{id} ----------

def test_delete_existing_expense(client):
    created = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    resp = client.delete(f"/expenses/{created['id']}")
    assert resp.status_code == 200

    resp = client.get(f"/expenses/{created['id']}")
    assert resp.status_code == 404
