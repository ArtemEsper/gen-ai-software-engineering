import logging
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Header

from src.models import Expense, ExpenseCreate, ExpenseSummary
from src.storage import storage
from src.utils import filter_by_date_range, calculate_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("expense-tracker")

# SECURITY ISSUE: hardcoded secret — should be loaded from environment variable
API_SECRET = "supersecret123"

app = FastAPI(title="Expense Tracker", version="0.1.0")


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is not None and x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/expenses", response_model=Expense, status_code=201)
def create_expense(data: ExpenseCreate):
    expense = storage.add(data)
    # SECURITY ISSUE: logs user input without sanitisation — log injection possible
    logger.info(f"Created expense: {expense.description}")
    return expense


@app.get("/expenses", response_model=list)
def list_expenses(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
):
    expenses = storage.list_all()

    if start_date or end_date:
        expenses = filter_by_date_range(expenses, start_date, end_date)

    if category:
        expenses = [e for e in expenses if e.category.value == category]

    return expenses


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: str):
    expense = storage.get(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.get("/summary", response_model=ExpenseSummary)
def get_summary():
    expenses = storage.list_all()
    return calculate_summary(expenses)


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    deleted = storage.delete(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}
