"""JSON import tests — 5 tests."""
import json

import pytest

from src.parsers import parse_json


VALID_TICKETS = [
    {"customer_id": "C1", "customer_email": "a@b.com", "customer_name": "Alice",
     "subject": "Test subject", "description": "This description is long enough to be valid."},
    {"customer_id": "C2", "customer_email": "b@c.com", "customer_name": "Bob",
     "subject": "Another subject", "description": "Another description that is long enough."},
]


class TestParseJSON:
    def test_parse_list_format(self):
        result = parse_json(json.dumps(VALID_TICKETS))
        assert result.successful == 2
        assert result.failed == 0

    def test_parse_object_with_tickets_key(self):
        result = parse_json(json.dumps({"tickets": VALID_TICKETS}))
        assert result.successful == 2

    def test_parse_object_with_data_key(self):
        result = parse_json(json.dumps({"data": VALID_TICKETS}))
        assert result.successful == 2

    def test_invalid_json_returns_error(self):
        result = parse_json("not valid json {{{")
        assert result.failed >= 1
        assert len(result.errors) >= 1

    def test_invalid_email_record_fails(self):
        tickets = [{"customer_id": "C1", "customer_email": "not-an-email",
                    "customer_name": "Alice", "subject": "Sub",
                    "description": "This description is long enough to be valid."}]
        result = parse_json(json.dumps(tickets))
        assert result.failed >= 1
