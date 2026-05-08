import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.storage import store


@pytest.fixture(autouse=True)
def clear_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)


def sample_payload(**overrides) -> dict:
    base = {
        "customer_id": "CUST-TEST",
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "subject": "Test subject for ticket",
        "description": "This is a test description that is long enough to pass validation.",
        "category": "technical_issue",
        "priority": "medium",
        "status": "new",
        "tags": [],
        "metadata": {"source": "api"},
    }
    base.update(overrides)
    return base
