"""API endpoint tests — 11 tests."""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import sample_payload


class TestCreateTicket:
    def test_create_ticket_returns_201(self, client: TestClient):
        resp = client.post("/tickets", json=sample_payload())
        assert resp.status_code == 201

    def test_create_ticket_returns_full_model(self, client: TestClient):
        resp = client.post("/tickets", json=sample_payload())
        data = resp.json()
        assert "id" in data
        assert data["customer_email"] == "test@example.com"
        assert data["status"] == "new"

    def test_create_ticket_invalid_email_returns_422(self, client: TestClient):
        resp = client.post("/tickets", json=sample_payload(customer_email="not-an-email"))
        assert resp.status_code == 422

    def test_create_ticket_auto_classify(self, client: TestClient):
        payload = sample_payload(subject="Production is down critical outage")
        resp = client.post("/tickets?auto_classify=true", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["priority"] == "urgent"
        assert data["classification_confidence"] is not None


class TestGetTickets:
    def test_list_tickets_empty(self, client: TestClient):
        resp = client.get("/tickets")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_tickets_filter_by_status(self, client: TestClient):
        client.post("/tickets", json=sample_payload(status="new"))
        client.post("/tickets", json=sample_payload(status="resolved"))
        resp = client.get("/tickets?status=new")
        assert all(t["status"] == "new" for t in resp.json())

    def test_get_ticket_by_id(self, client: TestClient):
        created = client.post("/tickets", json=sample_payload()).json()
        resp = client.get(f"/tickets/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_ticket_not_found(self, client: TestClient):
        resp = client.get("/tickets/nonexistent-id")
        assert resp.status_code == 404


class TestUpdateTicket:
    def test_update_ticket_status(self, client: TestClient):
        created = client.post("/tickets", json=sample_payload()).json()
        resp = client.put(f"/tickets/{created['id']}", json={"status": "resolved"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"

    def test_update_ticket_not_found(self, client: TestClient):
        resp = client.put("/tickets/nonexistent-id", json={"status": "resolved"})
        assert resp.status_code == 404


class TestDeleteTicket:
    def test_delete_ticket_returns_204(self, client: TestClient):
        created = client.post("/tickets", json=sample_payload()).json()
        resp = client.delete(f"/tickets/{created['id']}")
        assert resp.status_code == 204

    def test_delete_ticket_not_found(self, client: TestClient):
        resp = client.delete("/tickets/nonexistent-id")
        assert resp.status_code == 404
