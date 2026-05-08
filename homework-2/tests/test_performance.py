"""Performance benchmark tests — 5 tests."""
import io
import pathlib
import time

import pytest
from fastapi.testclient import TestClient

from src.classifier import classify_ticket
from src.parsers import parse_csv, parse_json, parse_xml

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestImportPerformance:
    def test_csv_import_50_tickets_under_2s(self):
        content = (FIXTURES / "sample_tickets.csv").read_text()
        start = time.perf_counter()
        result = parse_csv(content)
        elapsed = time.perf_counter() - start
        assert result.successful == 50
        assert elapsed < 2.0, f"CSV import took {elapsed:.3f}s, expected < 2s"

    def test_json_import_20_tickets_under_1s(self):
        content = (FIXTURES / "sample_tickets.json").read_text()
        start = time.perf_counter()
        result = parse_json(content)
        elapsed = time.perf_counter() - start
        assert result.successful == 20
        assert elapsed < 1.0, f"JSON import took {elapsed:.3f}s, expected < 1s"

    def test_xml_import_30_tickets_under_1s(self):
        content = (FIXTURES / "sample_tickets.xml").read_text()
        start = time.perf_counter()
        result = parse_xml(content)
        elapsed = time.perf_counter() - start
        assert result.successful == 30
        assert elapsed < 1.0, f"XML import took {elapsed:.3f}s, expected < 1s"


class TestClassificationPerformance:
    def test_classify_50_tickets_under_1s(self):
        tickets = [
            ("Production is down critical", "All users are affected. Emergency situation requiring immediate fix."),
            ("Billing question about invoice", "I need a refund for the duplicate charge on my account."),
            ("App crash on startup", "The application fails every time I try to open the settings page."),
            ("Feature request: dark mode", "It would be great to have a dark mode option in the UI."),
            ("Cannot login to account", "My password reset is not working and I am locked out."),
        ]
        subjects_descs = tickets * 10  # 50 tickets

        start = time.perf_counter()
        for i, (subject, description) in enumerate(subjects_descs):
            classify_ticket(f"perf-ticket-{i}", subject, description)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"50 classifications took {elapsed:.3f}s, expected < 1s"

    def test_bulk_import_via_api_50_tickets_under_3s(self, client: TestClient):
        csv_bytes = (FIXTURES / "sample_tickets.csv").read_bytes()
        start = time.perf_counter()
        resp = client.post(
            "/tickets/import",
            files={"file": ("sample_tickets.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        elapsed = time.perf_counter() - start
        assert resp.status_code == 200
        assert resp.json()["successful"] == 50
        assert elapsed < 3.0, f"API bulk import took {elapsed:.3f}s, expected < 3s"
