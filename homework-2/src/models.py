from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Category(str, Enum):
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL_ISSUE = "technical_issue"
    BILLING_QUESTION = "billing_question"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Source(str, Enum):
    WEB_FORM = "web_form"
    EMAIL = "email"
    API = "api"
    CHAT = "chat"
    PHONE = "phone"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class TicketMetadata(BaseModel):
    source: Source = Source.API
    browser: Optional[str] = None
    device_type: Optional[DeviceType] = None


class TicketCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    customer_email: EmailStr
    customer_name: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    status: Status = Status.NEW
    assigned_to: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)


class TicketUpdate(BaseModel):
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = Field(None, min_length=1)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    assigned_to: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[TicketMetadata] = None


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    status: Status = Status.NEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)
    classification_confidence: Optional[float] = None
    classification_reasoning: Optional[list[str]] = None


class BulkImportError(BaseModel):
    row: int
    field: Optional[str] = None
    error: str


class BulkImportResult(BaseModel):
    total: int = 0
    successful: int = 0
    failed: int = 0
    errors: list[BulkImportError] = Field(default_factory=list)
    tickets: list[Ticket] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    ticket_id: str
    category: Category
    priority: Priority
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: list[str]
    keywords_found: list[str]
