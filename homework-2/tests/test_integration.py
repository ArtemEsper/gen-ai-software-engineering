"""Integration tests — 5 tests."""
import asyncio
import io
import pathlib

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.conftest import sample_payload

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestTicketLifecycle:
    def test_full_ticket_lifecycle(self, client: TestClient):
        # Create
        created = client.post("/tickets", json=sample_payload()).json()
        ticket_id = created["id"]
        assert created["status"] == "new"

        # Get
        fetched = client.get(f"/tickets/{ticket_id}").json()
        assert fetched["id"] == ticket_id

        # Update
        updated = client.put(f"/tickets/{ticket_id}", json={"status": "in_progress"}).json()
        assert updated["status"] == "in_progress"

        # Auto-classify
        cls_resp = client.post(f"/tickets/{ticket_id}/auto-classify")
        assert cls_resp.status_code == 200
        cls = cls_resp.json()
        assert "category" in cls
        assert "confidence" in cls

        # Verify ticket updated with classification
        final = client.get(f"/tickets/{ticket_id}").json()
        assert final["category"] is not None

        # Delete
        del_resp = client.delete(f"/tickets/{ticket_id}")
        assert del_resp.status_code == 204
        assert client.get(f"/tickets/{ticket_id}").status_code == 404


class TestBulkImportWithClassification:
    def test_bulk_import_csv_with_auto_classify(self, client: TestClient):
        csv_file = (FIXTURES / "sample_tickets.csv").read_bytes()
        resp = client.post(
            "/tickets/import?auto_classify=true",
            files={"file": ("sample_tickets.csv", io.BytesIO(csv_file), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["successful"] == 50
        assert data["failed"] == 0

        # Verify tickets are classified
        tickets = client.get("/tickets").json()
        assert len(tickets) == 50
        classified = [t for t in tickets if t["priority"] is not None]
        assert len(classified) == 50

    def test_bulk_import_invalid_csv_returns_summary(self, client: TestClient):
        csv_file = (FIXTURES / "invalid_tickets.csv").read_bytes()
        resp = client.post(
            "/tickets/import",
            files={"file": ("invalid_tickets.csv", io.BytesIO(csv_file), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["failed"] > 0
        assert len(data["errors"]) > 0


class TestFiltering:
    def test_filter_by_category_and_priority(self, client: TestClient):
        client.post("/tickets", json=sample_payload(category="billing_question", priority="high"))
        client.post("/tickets", json=sample_payload(category="technical_issue", priority="low"))
        client.post("/tickets", json=sample_payload(category="billing_question", priority="low"))

        resp = client.get("/tickets?category=billing_question&priority=high")
        tickets = resp.json()
        assert len(tickets) == 1
        assert tickets[0]["category"] == "billing_question"
        assert tickets[0]["priority"] == "high"


class TestConcurrency:
    def test_20_concurrent_requests(self):
        async def run():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
                tasks = [
                    ac.post("/tickets", json=sample_payload(customer_id=f"CUST-CONC-{i}"))
                    for i in range(20)
                ]
                responses = await asyncio.gather(*tasks)
            return responses

        responses = asyncio.run(run())
        assert all(r.status_code == 201 for r in responses)
        # All 20 tickets created with unique IDs
        ids = {r.json()["id"] for r in responses}
        assert len(ids) == 20
