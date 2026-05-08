"""Auto-classification tests — 10 tests."""
import pytest

from src.classifier import classify, classify_ticket
from src.models import Category, Priority


class TestClassify:
    def test_urgent_priority_production_down(self):
        _, priority, _, _, _ = classify("Production is down", "All users cannot access the system.")
        assert priority == Priority.URGENT

    def test_urgent_priority_critical_keyword(self):
        _, priority, _, _, _ = classify("Critical issue", "This is a critical security vulnerability.")
        assert priority == Priority.URGENT

    def test_high_priority_blocking_keyword(self):
        _, priority, _, _, _ = classify("Blocking issue", "This bug is blocking our deployment.")
        assert priority == Priority.HIGH

    def test_low_priority_cosmetic(self):
        _, priority, _, _, _ = classify("Minor cosmetic fix", "This is a minor cosmetic suggestion for the UI.")
        assert priority == Priority.LOW

    def test_account_access_category(self):
        category, _, _, _, _ = classify("Can't login", "I forgot my password and the reset is not working.")
        assert category == Category.ACCOUNT_ACCESS

    def test_billing_category(self):
        category, _, _, _, _ = classify("Invoice question", "I have a billing question about my last payment and refund.")
        assert category == Category.BILLING_QUESTION

    def test_feature_request_category(self):
        category, _, _, _, _ = classify("Feature suggestion", "It would be great to add this enhancement to the product.")
        assert category == Category.FEATURE_REQUEST

    def test_no_keywords_defaults_to_other_and_medium(self):
        category, priority, _, _, _ = classify("Hello", "Just wanted to say hi and ask about partnership.")
        assert category == Category.OTHER
        assert priority == Priority.MEDIUM

    def test_confidence_between_0_and_1(self):
        _, _, confidence, _, _ = classify("App crash error", "The app crashes on startup with an error code.")
        assert 0.0 <= confidence <= 1.0

    def test_classify_ticket_returns_result_model(self):
        result = classify_ticket("ticket-123", "Cannot login critical", "Security issue with 2FA not working.")
        assert result.ticket_id == "ticket-123"
        assert result.category is not None
        assert result.priority is not None
        assert isinstance(result.keywords_found, list)
        assert isinstance(result.reasoning, list)
