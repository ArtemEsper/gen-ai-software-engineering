from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse

from .classifier import classify_ticket
from .models import (
    BulkImportResult,
    Category,
    ClassificationResult,
    Priority,
    Status,
    Ticket,
    TicketCreate,
    TicketUpdate,
)
from .parsers import parse_by_extension
from .storage import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="Intelligent Customer Support System",
    description="Customer support ticket management with multi-format import and auto-classification.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(
    payload: TicketCreate,
    auto_classify: bool = Query(False, description="Run auto-classification on creation"),
) -> Ticket:
    ticket = Ticket(**payload.model_dump())

    if auto_classify:
        result = classify_ticket(ticket.id, ticket.subject, ticket.description)
        ticket.category = result.category
        ticket.priority = result.priority
        ticket.classification_confidence = result.confidence
        ticket.classification_reasoning = result.reasoning

    store.add(ticket)
    return ticket


@app.post("/tickets/import", response_model=BulkImportResult)
async def import_tickets(
    file: UploadFile = File(...),
    auto_classify: bool = Query(False, description="Auto-classify each imported ticket"),
) -> BulkImportResult:
    content = (await file.read()).decode("utf-8")
    filename = file.filename or "upload"
    result = parse_by_extension(filename, content)

    for ticket in result.tickets:
        if auto_classify:
            cls = classify_ticket(ticket.id, ticket.subject, ticket.description)
            ticket.category = cls.category
            ticket.priority = cls.priority
            ticket.classification_confidence = cls.confidence
            ticket.classification_reasoning = cls.reasoning
        store.add(ticket)

    return result


@app.get("/tickets", response_model=list[Ticket])
def list_tickets(
    category: Optional[Category] = Query(None),
    priority: Optional[Priority] = Query(None),
    status: Optional[Status] = Query(None),
    customer_id: Optional[str] = Query(None),
) -> list[Ticket]:
    return store.list(
        category=category,
        priority=priority,
        status=status,
        customer_id=customer_id,
    )


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str) -> Ticket:
    ticket = store.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")
    return ticket


@app.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: str, payload: TicketUpdate) -> Ticket:
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    ticket = store.update(ticket_id, updates)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")
    return ticket


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: str) -> None:
    if not store.delete(ticket_id):
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")


# ---------------------------------------------------------------------------
# Auto-classify
# ---------------------------------------------------------------------------

@app.post("/tickets/{ticket_id}/auto-classify", response_model=ClassificationResult)
def auto_classify_ticket(ticket_id: str) -> ClassificationResult:
    ticket = store.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")

    result = classify_ticket(ticket_id, ticket.subject, ticket.description)

    store.update(ticket_id, {
        "category": result.category,
        "priority": result.priority,
        "classification_confidence": result.confidence,
        "classification_reasoning": result.reasoning,
    })

    return result


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "tickets": len(store)}
