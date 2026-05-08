# Intelligent Customer Support System

> **Student Name**: Artem Chumachenko
> **Date Submitted**: 2026-05-08
> **AI Tools Used**: [Claude Code Sonnet 4.6, Opus 4.6, Haiku 4.5, CC GUI]

---

> Refined with Claude Opus 4.6

## Project Overview

A REST API for customer support ticket management with:
- Multi-format bulk import (CSV, JSON, XML)
- Automatic ticket categorization and priority assignment via keyword rules
- Comprehensive test suite (>85% coverage)
- In-memory storage, Python/FastAPI stack

## Architecture

```mermaid
graph TD
    Client -->|HTTP| API[FastAPI App<br/>src/main.py]
    API --> Store[TicketStore<br/>src/storage.py]
    API --> Parser[Parsers<br/>src/parsers.py]
    API --> Classifier[Classifier<br/>src/classifier.py]
    Parser -->|CSV/JSON/XML| Store
    Classifier -->|category + priority| Store
    Store -->|dict[id, Ticket]| Memory[(In-Memory)]
```

## Features

| Task | Feature |
|------|---------|
| Task 1 | REST CRUD API + bulk import from CSV/JSON/XML |
| Task 2 | Keyword-based auto-classification (category + priority) |
| Task 3 | 58 tests across 8 files, 92% coverage (target >85%) |
| Task 4 | README, API_REFERENCE, ARCHITECTURE, TESTING_GUIDE, HOWTORUN (see note below) |
| Task 5 | Integration + concurrency + performance tests |

### Note on Task 3: Test counts vs TASKS.md

TASKS.md specifies `test_ticket_api` (11 tests) and `test_ticket_model` (9 tests). The actual implementation exceeds those numbers: `test_ticket_api.py` contains **12 tests** and `test_ticket_model.py` contains **10 tests**, bringing the total to **58 tests** (vs 56 implied by the spec). The additional tests cover `auto_classify` on creation and `TicketMetadata` source validation.

### Note on Task 4: Documentation count

TASKS.md states "Generate **5** documentation files" but names only 4 explicitly: README.md, API_REFERENCE.md, ARCHITECTURE.md, and TESTING_GUIDE.md. To fulfil the requirement of 5, a **HOWTORUN.md** file was added covering installation, server startup, environment setup, and demo scripts.

## Project Structure

```
homework-2/
├── src/
│   ├── main.py          # FastAPI app, all endpoints
│   ├── models.py        # Pydantic models and enums
│   ├── storage.py       # In-memory TicketStore
│   ├── parsers.py       # CSV/JSON/XML import
│   └── classifier.py    # Keyword rule engine
├── tests/
│   ├── conftest.py
│   ├── test_ticket_api.py
│   ├── test_ticket_model.py
│   ├── test_import_csv.py
│   ├── test_import_json.py
│   ├── test_import_xml.py
│   ├── test_categorization.py
│   ├── test_integration.py
│   ├── test_performance.py
│   └── fixtures/        # Sample data files
├── demo/
│   ├── run.sh
│   ├── sample-requests.sh
│   └── sample-requests.http
├── docs/screenshots/
├── requirements.txt
├── README.md             # Task 4 — doc 1/5
├── API_REFERENCE.md      # Task 4 — doc 2/5
├── ARCHITECTURE.md       # Task 4 — doc 3/5
├── TESTING_GUIDE.md      # Task 4 — doc 4/5
├── HOWTORUN.md           # Task 4 — doc 5/5
└── TASKS.md
```

## Quick Start

```bash
cd homework-2
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Running Tests

```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

Coverage report at `htmlcov/index.html`.
