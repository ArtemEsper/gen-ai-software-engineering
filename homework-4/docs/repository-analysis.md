# Repository Analysis for Homework 4

## Existing Conventions

### Directory Layout
Each homework lives in `homework-N/` with a consistent structure:
- `README.md` — student header (name, date, AI tools) + project overview
- `HOWTORUN.md` — step-by-step guide to run the application
- `TASKS.md` — instructor-provided assignment (read-only)
- `src/` — source code
- `tests/` — test suite (HW2 used `tests/` at homework root)
- `docs/screenshots/` — screenshots of AI interactions, running app, test results
- `demo/` — run scripts, sample requests (HW1/HW2)

### Branching & Submission
- Branch: `homework-N-submission` (current: `homework-4-submission`)
- PR: base = `main`, compare = branch
- PR body must include: summary, AI tools used, challenges, embedded screenshots
- Reviewer: Alexey-Popov

### Language & Stack
| HW | Language | Framework | Test Framework | Package Manager |
|----|----------|-----------|----------------|-----------------|
| 1  | Python   | FastAPI   | pytest         | pip / venv      |
| 2  | Python   | FastAPI   | pytest + coverage | pip / venv   |
| 3  | N/A (spec only) | N/A | N/A          | N/A             |

Python 3.9.6 and Node.js v23.0.0 are available locally.

### README Header Convention
```markdown
> **Student Name**: Artem Chumachenko
> **Date Submitted**: [Date]
> **AI Tools Used**: Claude Code
```

### Testing Conventions
- pytest as test runner
- pytest-cov for coverage measurement
- `htmlcov/` for HTML coverage reports
- Coverage target: >85% (HW2)

### .gitignore Coverage
Already handles: `venv/`, `__pycache__/`, `.env`, `.coverage`, `htmlcov/`, `node_modules/`, IDE files, OS files.

---

## Reusable Structures

### From HW1
- FastAPI app boilerplate with in-memory storage
- Pydantic model validation pattern
- DSPy pipeline for AI-driven code generation (but overkill for HW4)

### From HW2
- pytest fixture patterns
- Coverage configuration
- Multi-file source layout (`src/__init__.py`, `src/models.py`, etc.)
- Demo scripts (`run.sh`, `sample-requests.sh`)

### From HW3
- Specification template structure (layered: high-level > mid-level > tasks)
- Multi-agent workflow pattern (3 agents with separation of concerns)
- `.cursorrules` / agent rules pattern

---

## Lessons from Previous HWs

1. **Python + FastAPI is the proven stack** — used in HW1 and HW2 successfully, familiar to the student, tooling all in place.

2. **venv must be gitignored** — HW2 committed a full venv once; `.gitignore` now handles it but worth being careful about.

3. **Screenshots are mandatory** — every HW expects `docs/screenshots/` with evidence of running app, AI interactions, and test results.

4. **Single-command execution matters** — HW4 explicitly requires the entire pipeline to run via one command. HW2 had `run.sh` as a pattern to follow.

5. **Author header in README is required** — root README and TASKS.md both emphasize `README.md` must include student/author info.

6. **Multi-agent separation works well** — HW3's 3-agent workflow (Product/Compliance/QA) was validated as effective. HW4 extends this to 4 code-operating agents.

7. **Pre-commit hooks or CI are not used** — no `.github/workflows/` or pre-commit configuration exists. All validation is manual.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude Code agent `.agent.md` files don't chain properly in a single pipeline run | Medium | High | Test pipeline orchestration early; use a shell script wrapper |
| Seeded bugs are too obvious or too subtle for agents to find/fix | Medium | Medium | Design bugs at varying difficulty; document expected detection in bug-context.md |
| Security vulnerability is flagged by the security verifier but can't be auto-fixed | Low | Medium | Security verifier is report-only (no code edits) per spec |
| Python 3.9 lacks some newer typing features | Low | Low | Stick to 3.9-compatible syntax |
| Pipeline takes too long due to multiple LLM calls | Medium | Low | Use faster/cheaper models for routine tasks (as required by TASKS.md) |
| Screenshots hard to capture for automated pipeline | Low | Medium | Run pipeline manually once for screenshot capture; use terminal recording |

---

## Recommended Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.9+ | Consistent with HW1/HW2; available locally |
| Framework | FastAPI | Proven in previous HWs; async support; auto-docs |
| Test Framework | pytest + pytest-cov | Established pattern from HW2 |
| Package Manager | pip + venv | Consistent with repo conventions |
| Pipeline Runner | Shell script (`run-pipeline.sh`) | Simplest single-command solution; chains Claude Code agent invocations |
| Agent Format | `.agent.md` (Claude Code) | Required by TASKS.md specification |
| Mini App Type | REST API (Expense Tracker) | Small, financial domain, easy to seed bugs |
