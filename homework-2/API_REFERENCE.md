
# API Reference 

> Refined with GPT 4.1

Base URL: `http://localhost:8000`

---

## Endpoints

### POST /tickets
Create a new support ticket.

**Query params:** `auto_classify=true` — run classification on creation (optional, default: false).

**Request Body:**
```json
{
  "customer_id": "CUST-001",                // required, string
  "customer_email": "user@example.com",      // required, valid email
  "customer_name": "Alice Smith",            // required, string
  "subject": "Cannot login to my account",   // required, 1-200 chars
  "description": "I keep getting an authentication error when trying to login.", // required, 10-2000 chars
  "category": "account_access",              // optional, enum (see below)
  "priority": "high",                        // optional, enum (see below)
  "status": "new",                           // optional, enum (default: new)
  "assigned_to": null,                        // optional, string or null
  "tags": ["auth"],                          // optional, array of strings
  "metadata": {                               // optional, object (see below)
    "source": "web_form",                    // optional, enum (default: api)
    "browser": null,                          // optional, string or null
    "device_type": "desktop"                 // optional, enum or null
  }
}
```

**Response 201:**
Returns the created ticket. If `auto_classify=true`, `category`, `priority`, `classification_confidence`, and `classification_reasoning` may be set.
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST-001",
  "customer_email": "user@example.com",
  "customer_name": "Alice Smith",
  "subject": "Cannot login to my account",
  "description": "I keep getting an authentication error when trying to login.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "created_at": "2025-01-01T10:00:00",
  "updated_at": "2025-01-01T10:00:00",
  "resolved_at": null,
  "assigned_to": null,
  "tags": ["auth"],
  "metadata": {"source": "web_form", "browser": null, "device_type": "desktop"},
  "classification_confidence": 0.85,
  "classification_reasoning": ["Category matched keywords: ['login']"]
}
```

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST-001","customer_email":"user@example.com","customer_name":"Alice","subject":"Cannot login","description":"Getting an auth error when I try to login to my account."}'
```

---

### POST /tickets/import
Bulk import tickets from a CSV, JSON, or XML file.

**Query params:** `auto_classify=true` (optional)

**Request:**
Multipart form with a file field:
```bash
curl -X POST http://localhost:8000/tickets/import \
  -F "file=@demo/sample_tickets.csv"
```

**Response 200:**
```json
{
  "total": 50,
  "successful": 48,
  "failed": 2,
  "errors": [
    {"row": 3, "field": "customer_email", "error": "value is not a valid email address"},
    {"row": 7, "field": null, "error": "Missing required field: 'customer_id'"}
  ],
  "tickets": [ /* array of successfully imported Ticket objects */ ]
}
```

---

### GET /tickets
List all tickets with optional filters.

**Query params:**
- `category` (enum, optional)
- `priority` (enum, optional)
- `status` (enum, optional)
- `customer_id` (string, optional)

```bash
curl "http://localhost:8000/tickets?category=billing_question&priority=high"
```

---

### GET /tickets/{ticket_id}
Get a specific ticket by its ID.

```bash
curl http://localhost:8000/tickets/550e8400-e29b-41d4-a716-446655440000
```

**Response 404:**
```json
{"detail": "Ticket '550e8400-e29b-41d4-a716-446655440000' not found"}
```

---

### PUT /tickets/{ticket_id}
Partial update of a ticket (all fields optional).

**Request Body:**
Any subset of the fields from the Ticket model (see below). Only provided fields will be updated.

```bash
curl -X PUT http://localhost:8000/tickets/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved", "assigned_to": "agent@support.com"}'
```

**Response 404:**
```json
{"detail": "Ticket '550e8400-e29b-41d4-a716-446655440000' not found"}
```

---

### DELETE /tickets/{ticket_id}
Delete a ticket by its ID.

```bash
curl -X DELETE http://localhost:8000/tickets/550e8400-e29b-41d4-a716-446655440000
```

**Response:** 204 No Content (success), or 404 if not found.

---

### POST /tickets/{ticket_id}/auto-classify
Run auto-classification on an existing ticket. Updates the ticket's category, priority, and classification fields.

```bash
curl -X POST http://localhost:8000/tickets/550e8400-e29b-41d4-a716-446655440000/auto-classify
```

**Response 200:**
Returns a `ClassificationResult` object:
```json
{
  "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "account_access",
  "priority": "urgent",
  "confidence": 0.72,
  "reasoning": [
    "Category 'account_access' matched keywords: ['login', 'password']",
    "Priority 'urgent' matched keywords: ["can't access"]"
  ],
  "keywords_found": ["login", "password", "can't access"]
}
```

**Response 404:**
```json
{"detail": "Ticket '550e8400-e29b-41d4-a716-446655440000' not found"}
```

---

### GET /health
Health check endpoint. Returns service status and ticket count.

```bash
curl http://localhost:8000/health
```

**Response 200:**
```json
{
  "status": "ok",
  "tickets": 123
}
```

---

## Data Models

### Ticket

| Field                   | Type           | Notes                                                                 |
|------------------------ |--------------- |-----------------------------------------------------------------------|
| id                      | UUID string    | Auto-generated                                                        |
| customer_id             | string         | Required                                                              |
| customer_email          | email string   | Required, validated                                                   |
| customer_name           | string         | Required                                                              |
| subject                 | string         | 1–200 chars, required                                                 |
| description             | string         | 10–2000 chars, required                                               |
| category                | enum           | Optional. One of: `account_access`, `technical_issue`, `billing_question`, `feature_request`, `bug_report`, `other` |
| priority                | enum           | Optional. One of: `urgent`, `high`, `medium`, `low`                   |
| status                  | enum           | One of: `new`, `in_progress`, `waiting_customer`, `resolved`, `closed` (default: `new`) |
| created_at              | ISO datetime   | Auto-set                                                              |
| updated_at              | ISO datetime   | Auto-updated on PUT                                                   |
| resolved_at             | ISO datetime or null | Set when status → resolved/closed                                 |
| assigned_to             | string or null | Optional                                                              |
| tags                    | string array   | Optional                                                              |
| metadata.source         | enum           | Optional. One of: `web_form`, `email`, `api`, `chat`, `phone` (default: `api`) |
| metadata.browser        | string or null | Optional                                                              |
| metadata.device_type    | enum or null   | Optional. One of: `desktop`, `mobile`, `tablet`                       |
| classification_confidence | float or null | Set if auto-classified                                                |
| classification_reasoning  | array of strings or null | Set if auto-classified                                         |

### BulkImportResult
| Field   | Type              | Notes |
|---------|-------------------|-------|
| total   | int               | Total number of rows processed |
| successful | int            | Number of tickets successfully imported |
| failed  | int               | Number of failed imports |
| errors  | array of objects  | List of errors (see BulkImportError) |
| tickets | array of Ticket   | Successfully imported tickets |

### BulkImportError
| Field | Type   | Notes |
|-------|--------|-------|
| row   | int    | Row number in the import file |
| field | string or null | Field with error, if applicable |
| error | string | Error message |

### ClassificationResult
| Field          | Type             | Notes |
|----------------|------------------|-------|
| ticket_id      | UUID string      | Ticket ID |
| category       | enum             | Predicted category |
| priority       | enum             | Predicted priority |
| confidence     | float (0.0–1.0)  | Confidence score |
| reasoning      | array of strings | Reasoning details |
| keywords_found | array of strings | Matched keywords |

### Error Response (422)
Validation error (e.g., invalid email):
```json
{
  "detail": [
    {"loc": ["body", "customer_email"], "msg": "value is not a valid email address", "type": "value_error.email"}
  ]
}
```
