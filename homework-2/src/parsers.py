from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import Optional

from pydantic import ValidationError

from .models import (
    BulkImportError,
    BulkImportResult,
    Category,
    DeviceType,
    Priority,
    Source,
    Status,
    Ticket,
    TicketMetadata,
)

_REQUIRED_CSV_COLUMNS = {
    "customer_id",
    "customer_email",
    "customer_name",
    "subject",
    "description",
}


def _dict_to_ticket(record: dict, row: int) -> tuple[Optional[Ticket], Optional[BulkImportError]]:
    """Convert a raw dict to a Ticket, returning (ticket, None) or (None, error)."""
    try:
        metadata_raw = record.get("metadata", {})
        if isinstance(metadata_raw, str):
            try:
                metadata_raw = json.loads(metadata_raw)
            except (json.JSONDecodeError, ValueError):
                metadata_raw = {}
        metadata = TicketMetadata(
            source=metadata_raw.get("source", Source.API) if metadata_raw else Source.API,
            browser=metadata_raw.get("browser") if metadata_raw else None,
            device_type=metadata_raw.get("device_type") if metadata_raw else None,
        )

        tags_raw = record.get("tags", [])
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        else:
            tags = list(tags_raw)

        ticket = Ticket(
            customer_id=str(record["customer_id"]).strip(),
            customer_email=str(record["customer_email"]).strip(),
            customer_name=str(record["customer_name"]).strip(),
            subject=str(record["subject"]).strip(),
            description=str(record["description"]).strip(),
            category=record.get("category") or None,
            priority=record.get("priority") or None,
            status=record.get("status") or Status.NEW,
            assigned_to=record.get("assigned_to") or None,
            tags=tags,
            metadata=metadata,
        )
        return ticket, None
    except (KeyError, TypeError) as exc:
        return None, BulkImportError(row=row, error=f"Missing required field: {exc}")
    except ValidationError as exc:
        errors = exc.errors()
        field_name = str(errors[0]["loc"][0]) if errors else None
        msg = errors[0]["msg"] if errors else str(exc)
        return None, BulkImportError(row=row, field=field_name, error=msg)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def parse_csv(content: str) -> BulkImportResult:
    result = BulkImportResult()
    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames:
        present = {f.strip().lower() for f in reader.fieldnames if f}
        missing = _REQUIRED_CSV_COLUMNS - present
        if missing:
            result.failed += 1
            result.total += 1
            result.errors.append(
                BulkImportError(row=0, error=f"CSV missing required columns: {sorted(missing)}")
            )
            return result

    for row_num, raw_row in enumerate(reader, start=2):
        result.total += 1
        row = {k.strip().lower(): (v.strip() if v else v) for k, v in raw_row.items()}
        ticket, error = _dict_to_ticket(row, row_num)
        if ticket:
            result.tickets.append(ticket)
            result.successful += 1
        else:
            result.errors.append(error)
            result.failed += 1

    return result


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def parse_json(content: str) -> BulkImportResult:
    result = BulkImportResult()

    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        result.total = 1
        result.failed = 1
        result.errors.append(BulkImportError(row=0, error=f"Invalid JSON: {exc}"))
        return result

    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        if "tickets" in raw:
            records = raw["tickets"]
        elif "data" in raw:
            records = raw["data"]
        else:
            result.total = 1
            result.failed = 1
            result.errors.append(
                BulkImportError(row=0, error="JSON root object must have 'tickets' or 'data' key")
            )
            return result
    else:
        result.total = 1
        result.failed = 1
        result.errors.append(
            BulkImportError(row=0, error="JSON must be a list or object with 'tickets' key")
        )
        return result

    for idx, record in enumerate(records):
        result.total += 1
        if not isinstance(record, dict):
            result.errors.append(BulkImportError(row=idx, error="Record must be an object"))
            result.failed += 1
            continue
        ticket, error = _dict_to_ticket(record, idx)
        if ticket:
            result.tickets.append(ticket)
            result.successful += 1
        else:
            result.errors.append(error)
            result.failed += 1

    return result


# ---------------------------------------------------------------------------
# XML
# ---------------------------------------------------------------------------

def parse_xml(content: str) -> BulkImportResult:
    result = BulkImportResult()

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        result.total = 1
        result.failed = 1
        result.errors.append(BulkImportError(row=0, error=f"XML parse error: {exc}"))
        return result

    if root.tag == "ticket":
        elements = [root]
    else:
        elements = root.findall("ticket")
        if not elements:
            elements = root.findall("./ticket")

    for idx, elem in enumerate(elements):
        result.total += 1
        try:
            record = _elem_to_dict(elem)
            ticket, error = _dict_to_ticket(record, idx)
            if ticket:
                result.tickets.append(ticket)
                result.successful += 1
            else:
                result.errors.append(error)
                result.failed += 1
        except Exception as exc:
            result.errors.append(BulkImportError(row=idx, error=str(exc)))
            result.failed += 1

    return result


def _elem_to_dict(elem: ET.Element) -> dict:
    def get_text(tag: str) -> Optional[str]:
        child = elem.find(tag)
        val = (child.text if child is not None else None) or elem.get(tag)
        return val.strip() if val and val.strip() else None

    metadata_elem = elem.find("metadata")
    metadata: dict = {}
    if metadata_elem is not None:
        for child in metadata_elem:
            metadata[child.tag] = child.text.strip() if child.text else None

    tags_elem = elem.find("tags")
    tags = []
    if tags_elem is not None:
        tags = [t.text.strip() for t in tags_elem.findall("tag") if t.text]

    return {
        "customer_id": get_text("customer_id"),
        "customer_email": get_text("customer_email"),
        "customer_name": get_text("customer_name"),
        "subject": get_text("subject"),
        "description": get_text("description"),
        "category": get_text("category"),
        "priority": get_text("priority"),
        "status": get_text("status"),
        "assigned_to": get_text("assigned_to"),
        "tags": tags,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def parse_by_extension(filename: str, content: str) -> BulkImportResult:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "csv":
        return parse_csv(content)
    elif ext == "json":
        return parse_json(content)
    elif ext == "xml":
        return parse_xml(content)
    else:
        # Sniff by content
        stripped = content.lstrip()
        if stripped.startswith("<"):
            return parse_xml(content)
        elif stripped.startswith(("[", "{")):
            return parse_json(content)
        else:
            return parse_csv(content)
