from typing import Dict, List, Optional

from src.models import Expense, ExpenseCreate


class ExpenseStorage:
    def __init__(self):
        self._expenses: Dict[str, Expense] = {}

    def add(self, data: ExpenseCreate) -> Expense:
        expense = Expense(**data.model_dump())
        self._expenses[expense.id] = expense
        return expense

    def get(self, expense_id: str) -> Optional[Expense]:
        return self._expenses.get(expense_id)

    def list_all(self) -> List[Expense]:
        return list(self._expenses.values())

    def delete(self, expense_id: str) -> bool:
        if expense_id in self._expenses:
            del self._expenses[expense_id]
            return True
        return False


storage = ExpenseStorage()
