from __future__ import annotations

from datetime import datetime
from typing import Optional

from .models import Category, Priority, Status, Ticket


class TicketStore:
    def __init__(self) -> None:
        self._data: dict[str, Ticket] = {}

    def add(self, ticket: Ticket) -> Ticket:
        self._data[ticket.id] = ticket
        return ticket

    def get(self, ticket_id: str) -> Optional[Ticket]:
        return self._data.get(ticket_id)

    def update(self, ticket_id: str, updates: dict) -> Optional[Ticket]:
        ticket = self._data.get(ticket_id)
        if ticket is None:
            return None
        data = ticket.model_dump()
        for key, value in updates.items():
            if value is not None:
                data[key] = value
        data["updated_at"] = datetime.utcnow()
        if updates.get("status") in (Status.RESOLVED, Status.CLOSED) and ticket.resolved_at is None:
            data["resolved_at"] = datetime.utcnow()
        updated = Ticket(**data)
        self._data[ticket_id] = updated
        return updated

    def delete(self, ticket_id: str) -> bool:
        if ticket_id not in self._data:
            return False
        del self._data[ticket_id]
        return True

    def list(
        self,
        category: Optional[Category] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None,
        customer_id: Optional[str] = None,
    ) -> list[Ticket]:
        results = list(self._data.values())
        if category is not None:
            results = [t for t in results if t.category == category]
        if priority is not None:
            results = [t for t in results if t.priority == priority]
        if status is not None:
            results = [t for t in results if t.status == status]
        if customer_id is not None:
            results = [t for t in results if t.customer_id == customer_id]
        return results

    def clear(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)


store = TicketStore()
