from __future__ import annotations

import logging
from datetime import datetime

from .models import Category, ClassificationResult, Priority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword tables (from TASKS.md spec)
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    Category.ACCOUNT_ACCESS: [
        "login", "password", "sign in", "signin", "2fa", "two-factor",
        "two factor", "authentication", "access denied", "locked out",
        "account locked", "forgot password", "reset password", "can't log",
        "cannot log", "unable to login",
    ],
    Category.TECHNICAL_ISSUE: [
        "bug", "error", "crash", "exception", "not working", "broken",
        "fails", "failure", "glitch", "freeze", "hang", "timeout",
        "502", "503", "500", "internal server", "connection refused",
        "page not loading", "slow", "performance issue",
    ],
    Category.BILLING_QUESTION: [
        "payment", "invoice", "refund", "charge", "billing", "subscription",
        "plan", "price", "cost", "fee", "receipt", "overcharged",
        "duplicate charge", "credit card", "debit", "cancellation",
    ],
    Category.FEATURE_REQUEST: [
        "feature", "enhancement", "suggestion", "idea", "improvement",
        "would like", "wish", "could you add", "please add", "request",
        "new functionality", "can you support", "integration",
    ],
    Category.BUG_REPORT: [
        "reproduce", "steps to reproduce", "expected behavior", "actual behavior",
        "regression", "introduced in", "defect", "incorrect behavior",
        "wrong result", "inconsistent", "always fails", "every time",
    ],
}

PRIORITY_KEYWORDS: dict[Priority, list[str]] = {
    Priority.URGENT: [
        "can't access", "cannot access", "critical", "production down",
        "security", "data breach", "urgent", "emergency", "immediately",
        "outage", "down for all", "all users affected", "revenue impact",
    ],
    Priority.HIGH: [
        "important", "blocking", "asap", "as soon as possible",
        "high priority", "severely impacting", "major issue",
    ],
    Priority.LOW: [
        "minor", "cosmetic", "suggestion", "nice to have", "not urgent",
        "low priority", "when you get a chance", "no rush",
    ],
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify(subject: str, description: str) -> tuple[Category, Priority, float, list[str], list[str]]:
    """
    Classify a ticket by subject + description.

    Returns: (category, priority, confidence, reasoning, keywords_found)
    """
    text = (subject + " " + description).lower()

    # --- Category scoring ---
    category_scores: dict[Category, int] = {c: 0 for c in Category}
    category_hits: dict[Category, list[str]] = {c: [] for c in Category}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                category_scores[category] += 1
                category_hits[category].append(kw)

    best_category = max(category_scores, key=lambda c: category_scores[c])
    if category_scores[best_category] == 0:
        best_category = Category.OTHER

    # --- Priority scoring ---
    priority_scores: dict[Priority, int] = {p: 0 for p in Priority}
    priority_hits: dict[Priority, list[str]] = {p: [] for p in Priority}

    for priority, keywords in PRIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                priority_scores[priority] += 1
                priority_hits[priority].append(kw)

    # Priority order: URGENT > HIGH > MEDIUM > LOW
    best_priority = Priority.MEDIUM
    for p in (Priority.URGENT, Priority.HIGH, Priority.LOW):
        if priority_scores[p] > 0:
            best_priority = p
            break

    # --- Confidence ---
    max_possible_cat = max(len(v) for v in CATEGORY_KEYWORDS.values())
    max_possible_pri = max(len(v) for v in PRIORITY_KEYWORDS.values())
    cat_score = category_scores[best_category] if best_category != Category.OTHER else 0
    pri_score = priority_scores[best_priority] if best_priority != Priority.MEDIUM else 0

    cat_conf = min(cat_score / max_possible_cat, 1.0)
    pri_conf = min(pri_score / max_possible_pri, 1.0) if pri_score > 0 else 0.5
    confidence = round((cat_conf * 0.6 + pri_conf * 0.4), 3)

    # --- Reasoning & keywords ---
    all_keywords: list[str] = category_hits[best_category] + priority_hits[best_priority]
    reasoning: list[str] = []
    if category_hits[best_category]:
        reasoning.append(
            f"Category '{best_category.value}' matched keywords: {category_hits[best_category]}"
        )
    else:
        reasoning.append("No category keywords matched; defaulting to 'other'")
    if priority_hits[best_priority]:
        reasoning.append(
            f"Priority '{best_priority.value}' matched keywords: {priority_hits[best_priority]}"
        )
    else:
        reasoning.append(f"No priority keywords matched; defaulting to '{best_priority.value}'")

    return best_category, best_priority, confidence, reasoning, all_keywords


def classify_ticket(ticket_id: str, subject: str, description: str) -> ClassificationResult:
    """Run classification and return a ClassificationResult, logging the decision."""
    category, priority, confidence, reasoning, keywords_found = classify(subject, description)

    result = ClassificationResult(
        ticket_id=ticket_id,
        category=category,
        priority=priority,
        confidence=confidence,
        reasoning=reasoning,
        keywords_found=keywords_found,
    )

    logger.info(
        "[CLASSIFY] ticket_id=%s category=%s priority=%s confidence=%.3f keywords=%s",
        ticket_id, category.value, priority.value, confidence, keywords_found,
    )

    return result
