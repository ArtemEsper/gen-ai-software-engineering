"""XML import tests — 5 tests."""
import pytest

from src.parsers import parse_xml


VALID_XML = """<?xml version="1.0"?>
<tickets>
  <ticket>
    <customer_id>C1</customer_id>
    <customer_email>a@b.com</customer_email>
    <customer_name>Alice</customer_name>
    <subject>Test subject</subject>
    <description>This description is long enough to be valid.</description>
    <category>account_access</category>
    <priority>medium</priority>
    <status>new</status>
  </ticket>
  <ticket>
    <customer_id>C2</customer_id>
    <customer_email>b@c.com</customer_email>
    <customer_name>Bob</customer_name>
    <subject>Another subject</subject>
    <description>Another description long enough to be valid here.</description>
  </ticket>
</tickets>"""

MALFORMED_XML = "<tickets><ticket><customer_id>C1</broken>"

SINGLE_TICKET_XML = """<ticket>
  <customer_id>C1</customer_id>
  <customer_email>a@b.com</customer_email>
  <customer_name>Alice</customer_name>
  <subject>Single ticket subject</subject>
  <description>This description is long enough to be valid.</description>
</ticket>"""

BAD_EMAIL_XML = """<tickets>
  <ticket>
    <customer_id>C1</customer_id>
    <customer_email>not-an-email</customer_email>
    <customer_name>Alice</customer_name>
    <subject>Test subject</subject>
    <description>This description is long enough to be valid.</description>
  </ticket>
</tickets>"""


class TestParseXML:
    def test_valid_xml_parses_all_tickets(self):
        result = parse_xml(VALID_XML)
        assert result.successful == 2
        assert result.failed == 0

    def test_valid_xml_ticket_fields(self):
        result = parse_xml(VALID_XML)
        assert result.tickets[0].customer_id == "C1"
        assert result.tickets[0].category.value == "account_access"

    def test_malformed_xml_returns_error(self):
        result = parse_xml(MALFORMED_XML)
        assert result.failed >= 1
        assert any("XML parse error" in e.error for e in result.errors)

    def test_single_ticket_root_element(self):
        result = parse_xml(SINGLE_TICKET_XML)
        assert result.successful == 1

    def test_invalid_email_ticket_fails(self):
        result = parse_xml(BAD_EMAIL_XML)
        assert result.failed >= 1
