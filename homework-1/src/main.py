from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, model_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD",
    "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "INR", "RUB", "BRL", "ZAR",
    "DKK", "PLN", "THB", "IDR", "HUF", "CZK", "ILS", "CLP", "PHP", "AED",
    "COP", "SAR", "MYR", "RON",
}

ACCOUNT_PATTERN = re.compile(r"^ACC-[A-Za-z0-9]{5}$")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TransactionCreate(BaseModel):
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType

    @field_validator("fromAccount", "toAccount")
    @classmethod
    def validate_account_format(cls, v: str) -> str:
        if not ACCOUNT_PATTERN.match(v):
            raise ValueError(
                "Account number must follow the format ACC-XXXXX "
                "(5 alphanumeric characters after the dash)"
            )
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be a positive number")
        # Check max 2 decimal places using Decimal exponent — avoids float rounding edge cases
        if Decimal(str(v)).as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return round(v, 2)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        upper = v.upper()
        if upper not in VALID_CURRENCIES:
            raise ValueError(
                f"Invalid currency code '{v}'. Must be a valid ISO 4217 code "
                f"(e.g. USD, EUR, GBP, JPY)"
            )
        return upper


class Transaction(BaseModel):
    id: str
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

transactions: dict[str, Transaction] = {}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Banking Transactions API",
    description="A simple in-memory banking transactions REST API.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Custom validation error handler — returns assignment-style error shape
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": details},
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _format_transaction(t: Transaction) -> dict:
    return {
        "id": t.id,
        "fromAccount": t.fromAccount,
        "toAccount": t.toAccount,
        "amount": t.amount,
        "currency": t.currency,
        "type": t.type.value,
        "timestamp": t.timestamp.isoformat(),
        "status": t.status.value,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/transactions", status_code=201)
def create_transaction(payload: TransactionCreate):
    """Create a new transaction."""
    tx = Transaction(
        id=str(uuid.uuid4()),
        fromAccount=payload.fromAccount,
        toAccount=payload.toAccount,
        amount=payload.amount,
        currency=payload.currency,
        type=payload.type,
        timestamp=datetime.now(timezone.utc),
        status=TransactionStatus.completed,
    )
    transactions[tx.id] = tx
    return _format_transaction(tx)


@app.get("/transactions")
def list_transactions(
    accountId: Optional[str] = Query(default=None),
    type: Optional[TransactionType] = Query(default=None),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
):
    """
    List all transactions with optional filters:
    - accountId: matches fromAccount OR toAccount
    - type: deposit | withdrawal | transfer
    - from: start date (YYYY-MM-DD)
    - to: end date (YYYY-MM-DD)
    """
    result = list(transactions.values())

    if accountId is not None:
        result = [
            t for t in result
            if t.fromAccount == accountId or t.toAccount == accountId
        ]

    if type is not None:
        result = [t for t in result if t.type == type]

    if from_date is not None:
        result = [t for t in result if t.timestamp.date() >= from_date]

    if to_date is not None:
        result = [t for t in result if t.timestamp.date() <= to_date]

    return [_format_transaction(t) for t in result]


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    """Get a specific transaction by ID."""
    tx = transactions.get(transaction_id)
    if tx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction '{transaction_id}' not found",
        )
    return _format_transaction(tx)


@app.get("/accounts/{accountId}/balance")
def get_balance(accountId: str):
    """
    Get the current balance for an account.

    Balance logic:
    - deposit  → toAccount receives amount
    - withdrawal → fromAccount loses amount
    - transfer → fromAccount loses amount, toAccount receives amount
    """
    if not ACCOUNT_PATTERN.match(accountId):
        raise HTTPException(
            status_code=400,
            detail="Account number must follow the format ACC-XXXXX",
        )

    balance = 0.0
    found = False

    for tx in transactions.values():
        if tx.fromAccount == accountId or tx.toAccount == accountId:
            found = True

        if tx.type == TransactionType.deposit and tx.toAccount == accountId:
            balance += tx.amount
        elif tx.type == TransactionType.withdrawal and tx.fromAccount == accountId:
            balance -= tx.amount
        elif tx.type == TransactionType.transfer:
            if tx.toAccount == accountId:
                balance += tx.amount
            if tx.fromAccount == accountId:
                balance -= tx.amount

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Account '{accountId}' not found",
        )

    return {
        "accountId": accountId,
        "balance": round(balance, 2),
        "currency": "USD",  # balance shown in base currency; mixed-currency not handled
    }


@app.get("/accounts/{accountId}/summary")
def get_summary(accountId: str):
    """
    Get a transaction summary for an account.

    Returns total deposits, total withdrawals, transaction count,
    and the most recent transaction date.
    """
    if not ACCOUNT_PATTERN.match(accountId):
        raise HTTPException(
            status_code=400,
            detail="Account number must follow the format ACC-XXXXX",
        )

    account_txs = [
        t for t in transactions.values()
        if t.fromAccount == accountId or t.toAccount == accountId
    ]

    if not account_txs:
        raise HTTPException(
            status_code=404,
            detail=f"Account '{accountId}' not found",
        )

    total_deposits = 0.0
    total_withdrawals = 0.0

    for tx in account_txs:
        if tx.type == TransactionType.deposit and tx.toAccount == accountId:
            total_deposits += tx.amount
        elif tx.type == TransactionType.withdrawal and tx.fromAccount == accountId:
            total_withdrawals += tx.amount
        elif tx.type == TransactionType.transfer:
            if tx.toAccount == accountId:
                total_deposits += tx.amount
            if tx.fromAccount == accountId:
                total_withdrawals += tx.amount

    most_recent = max(account_txs, key=lambda t: t.timestamp)

    return {
        "accountId": accountId,
        "total_deposits": round(total_deposits, 2),
        "total_withdrawals": round(total_withdrawals, 2),
        "transaction_count": len(account_txs),
        "most_recent_transaction": most_recent.timestamp.isoformat(),
    }


# ---------------------------------------------------------------------------
# Entry point (for direct execution)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
