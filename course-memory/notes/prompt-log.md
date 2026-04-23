# Effective Prompt Patterns

Prompt strategies that worked well during this course.
Add entries with: `bash course-memory/scripts/07-record-note.sh prompt "<text>"`

---

## 2026-04-23 — Structured requirements block for code generation

Providing requirements in a structured format with explicit section headers produces
far better code than prose descriptions. The model can parse requirements sections
independently and check each one against the output.

**Template that worked well:**
```
Build a [tech stack] for [domain].

─── ENDPOINTS ──────────────────────────────────────
POST /foo    Create a foo
GET  /foo    List all foos (supports filters)

─── MODEL ───────────────────────────────────────────
{ "id": "auto-UUID", "field": "string", ... }

─── VALIDATION ──────────────────────────────────────
- amount: positive, max 2 decimal places
- account: format ACC-XXXXX
- currency: ISO 4217 whitelist

─── TECHNICAL ───────────────────────────────────────
- In-memory storage only, no database
- Port 3000, return JSON
```

---

## 2026-04-23 — Ask for raw code, not markdown-wrapped code

Suffix any code-generation prompt with:
> "Return ONLY raw Python/bash/JSON — no markdown fences, no explanation."

Without this, Claude wraps output in triple-backticks which breaks scripts that
write the output directly to files.

---

## 2026-04-23 — Root-cause framing for bug fixes

When a test fails, ask:
> "Here is the exact error output. What is the root cause, and what is the minimal fix?"

vs. the vague:
> "This test fails — fix it."

The first framing produces a targeted 1–3 line patch.
The second often produces a full rewrite with unrelated style changes.

---

## 2026-04-23 — ChainOfThought for complex files, Predict for simple ones

`dspy.ChainOfThought` on the main application file (FastAPI app, complex logic):
- The reasoning step catches missing edge cases before outputting code
- Noticeably better validation coverage than plain `Predict`

`dspy.Predict` for mechanical files:
- `requirements.txt`, `run.sh`, `sample-data.json`, `.gitignore`
- ChainOfThought overhead not worth it for deterministic, formulaic content

---

## 2026-04-23 — Iterative refinement beats single large prompt

Generating the full application in one shot produced a working but slightly incomplete
result. The review→repair loop in the DSPy pipeline (even just one pass) caught:
- Missing `GET /accounts/{id}/summary` endpoint
- Missing date-range filtering
- Incomplete error response shape

Pattern: generate → test → identify gap precisely → targeted fix is more reliable
than trying to frontload every requirement into one giant prompt.

---
