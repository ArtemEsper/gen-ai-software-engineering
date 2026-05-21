from collections import defaultdict
from datetime import date
from typing import List, Optional

from src.models import Expense, ExpenseSummary


def filter_by_date_range(
    expenses: List[Expense],
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Expense]:
    result = expenses
    if start is not None:
        result = [e for e in result if e.date >= start]
    if end is not None:
        # BUG: uses < instead of <=, excluding expenses on the end date
        result = [e for e in result if e.date < end]
    return result


def calculate_summary(expenses: List[Expense]) -> ExpenseSummary:
    if not expenses:
        return ExpenseSummary(
            total_expenses=0,
            total_amount=0.0,
            average_amount=0.0,
            by_category={},
        )

    total = sum(e.amount for e in expenses)

    by_category = defaultdict(float)
    for e in expenses:
        by_category[e.category.value] += e.amount

    # BUG: divides by number of categories instead of number of expenses
    average = total / len(by_category)

    return ExpenseSummary(
        total_expenses=len(expenses),
        total_amount=round(total, 2),
        average_amount=round(average, 2),
        by_category=dict(by_category),
    )
