# Architecture & Tooling Decisions

Key decisions made during this course and the reasoning behind them.
Add entries with: `bash course-memory/scripts/07-record-note.sh decision "<text>"`

---

## 2026-04-23 — FastAPI over Flask (Homework 1)

Chose **FastAPI** for the banking API because:
- Automatic Pydantic request validation — no manual `request.json` parsing
- Auto-generated `/docs` Swagger UI and `/redoc` — useful for homework screenshots
- `RequestValidationError` handler makes the assignment's `{"error","details"}` shape trivial
- `uvicorn` ASGI server is faster and more modern than Flask's dev server

---

## 2026-04-23 — In-memory storage as module-level dict

Used `transactions: dict[str, Transaction] = {}` at module level.
- Zero setup, restarts cleanly for tests
- Data lost on restart — acceptable per assignment spec ("no database required")
- Keeps the entire application in one file (`src/main.py`)

---

## 2026-04-23 — DSPy plan → build → review → repair pipeline

Used a 4-step DSPy pipeline to generate the API (`src/dspy_generate_homework.py`):
1. **Plan** — `dspy.Predict` chooses file list and extra feature (Option A: summary)
2. **Build** — `dspy.Predict` generates each file with full TASKS.md requirements in context
3. **Review** — `dspy.Predict` audits each file against requirements, returns pass/issues JSON
4. **Repair** — `dspy.Predict` rewrites files that failed review

Used `dspy.ChainOfThought` for the main `src/main.py` (complex logic benefits from
reasoning steps); `dspy.Predict` for mechanical files like `requirements.txt`, `run.sh`.

---

## 2026-04-23 — Manual MemPalace scripts over automatic hooks

Chose explicit shell scripts over Claude Code hooks because:
- Hooks fire on every tool call and would mine unrelated project directories
- Student machines have multiple projects; accidental broad mining is a real risk
- Scripts are auditable, debuggable, and only run when explicitly invoked
- Backfill script handles all prior history; future milestones just need `02-mine-homework.sh`

---

## 2026-04-23 — Local vault fallback for MemPalace

Since MemPalace cloud requires a paid API key, added automatic local fallback:
- `_vault.sh` tries cloud save first; on 403 stores to `vault/<sha256[:8]>.json`
- Local IDs prefixed `L-` to distinguish from cloud IDs in `notes/index.md`
- `vault/` is git-ignored (content too large); `notes/index.md` stays in git as the index
- `05-search.sh` greps vault JSON directly — no need to recover by ID for search

---

## 2026-04-23 — Branch naming: `homework-1-submission`

Using `homework-1-submission` per course README instruction.
- PR target: own fork `ArtemEsper/gen-ai-software-engineering`, base branch `main`
- **Not** into upstream `Alexey-Popov/gen-ai-software-engineering`
- Add `Alexey-Popov` only as reviewer, not as PR base

---

## 2026-04-23 — Task 4 Option A: Account Summary

Chose **Option A (Transaction Summary)** over B/C/D because:
- Reuses existing balance calculation logic, minimal new code
- No external dependencies (Option D rate-limiting needs Redis or similar)
- No file I/O or format conversion (Option C CSV)
- Most useful for account overview in a banking context

---
