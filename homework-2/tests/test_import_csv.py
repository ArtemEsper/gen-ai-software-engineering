"""CSV import tests — 6 tests."""
import pytest

from src.parsers import parse_csv


VALID_CSV = """\
customer_id,customer_email,customer_name,subject,description,category,priority,status
CUST-1,a@b.com,Alice,Test subject,This description is long enough to be valid.,account_access,medium,new
CUST-2,b@c.com,Bob,Another subject,Another description that is long enough to pass.,billing_question,high,in_progress
"""

MISSING_COLUMN_CSV = """\
customer_id,customer_name,subject,description
CUST-1,Alice,Test subject,Long enough description here.
"""

BAD_EMAIL_CSV = """\
customer_id,customer_email,customer_name,subject,description
CUST-1,not-an-email,Alice,Test subject,This description is long enough to be valid.
"""

SHORT_DESC_CSV = """\
customer_id,customer_email,customer_name,subject,description
CUST-1,a@b.com,Alice,Test subject,Short
"""


class TestParseCSV:
    def test_valid_csv_parses_all_rows(self):
        result = parse_csv(VALID_CSV)
        assert result.successful == 2
        assert result.failed == 0
        assert result.total == 2

    def test_valid_csv_ticket_fields(self):
        result = parse_csv(VALID_CSV)
        ticket = result.tickets[0]
        assert ticket.customer_id == "CUST-1"
        assert ticket.customer_email == "a@b.com"
        assert ticket.category.value == "account_access"

    def test_missing_required_column_returns_error(self):
        result = parse_csv(MISSING_COLUMN_CSV)
        assert result.failed > 0
        assert len(result.errors) > 0

    def test_invalid_email_row_fails(self):
        result = parse_csv(BAD_EMAIL_CSV)
        assert result.failed >= 1

    def test_short_description_row_fails(self):
        result = parse_csv(SHORT_DESC_CSV)
        assert result.failed >= 1

    def test_mixed_valid_invalid_rows(self):
        mixed = VALID_CSV.rstrip() + "\nCUST-3,not-an-email,Charlie,Sub,This is a long enough description.\n"
        result = parse_csv(mixed)
        assert result.successful == 2
        assert result.failed == 1
        assert result.total == 3
