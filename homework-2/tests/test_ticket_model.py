"""Pydantic model validation tests — 9 tests."""
import pytest
from pydantic import ValidationError

from src.models import Category, Priority, Status, Ticket, TicketCreate, TicketMetadata, TicketUpdate


class TestTicketCreate:
    def test_valid_ticket_create(self):
        t = TicketCreate(
            customer_id="CUST-001",
            customer_email="a@b.com",
            customer_name="Alice",
            subject="A valid subject",
            description="This description is long enough to pass validation.",
        )
        assert t.status == Status.NEW
        assert t.tags == []

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            TicketCreate(
                customer_id="C1",
                customer_email="bad",
                customer_name="Alice",
                subject="Sub",
                description="Long enough description here.",
            )

    def test_description_too_short_raises(self):
        with pytest.raises(ValidationError):
            TicketCreate(
                customer_id="C1",
                customer_email="a@b.com",
                customer_name="Alice",
                subject="Sub",
                description="Short",
            )

    def test_subject_too_long_raises(self):
        with pytest.raises(ValidationError):
            TicketCreate(
                customer_id="C1",
                customer_email="a@b.com",
                customer_name="Alice",
                subject="x" * 201,
                description="Long enough description here.",
            )

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            TicketCreate(
                customer_id="C1",
                customer_email="a@b.com",
                customer_name="Alice",
                subject="Sub",
                description="Long enough description here.",
                category="not_valid",
            )

    def test_invalid_priority_raises(self):
        with pytest.raises(ValidationError):
            TicketCreate(
                customer_id="C1",
                customer_email="a@b.com",
                customer_name="Alice",
                subject="Sub",
                description="Long enough description here.",
                priority="super_urgent",
            )


class TestTicketUpdate:
    def test_all_fields_optional(self):
        u = TicketUpdate()
        assert u.status is None
        assert u.category is None

    def test_valid_status_update(self):
        u = TicketUpdate(status=Status.RESOLVED)
        assert u.status == Status.RESOLVED


class TestTicketMetadata:
    def test_defaults(self):
        m = TicketMetadata()
        assert m.source.value == "api"
        assert m.browser is None

    def test_valid_source(self):
        m = TicketMetadata(source="email")
        assert m.source.value == "email"
