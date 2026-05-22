# HW4 Execution Spec: 4-Agent Pipeline

> This document is the **primary source of truth** for the Homework 4 implementation.

---

## Objective

Build a 4-agent Claude Code pipeline (Bug Research Verifier, Bug Fixer, Security Verifier, Unit Test Generator) that operates on a small Python application with seeded bugs and a security vulnerability. The pipeline must execute via a single command and produce verifiable artifacts.

---

## Deliverables

| # | Deliverable | Path | Status |
|---|-------------|------|--------|
| 1 | Research Verifier agent | `agents/research-verifier.agent.md` | TODO |
| 2 | Bug Fixer agent | `agents/bug-fixer.agent.md` | TODO |
| 3 | Security Verifier agent | `agents/security-verifier.agent.md` | TODO |
| 4 | Unit Test Generator agent | `agents/unit-test-generator.agent.md` | TODO |
| 5 | Research Quality skill | `skills/research-quality-measurement.md` | TODO |
| 6 | FIRST Unit Test skill | `skills/unit-tests-FIRST.md` | TODO |
| 7 | Mini application (with bugs) | `src/` | TODO |
| 8 | Bug context files | `context/bugs/*/bug-context.md` | TODO |
| 9 | Research files | `context/bugs/*/research/` | TODO |
| 10 | Implementation plans | `context/bugs/*/implementation-plan.md` | TODO |
| 11 | Pipeline outputs | `context/bugs/*/fix-summary.md`, etc. | TODO |
| 12 | Pipeline runner | `run-pipeline.sh` | TODO |
| 13 | Tests | `tests/` | TODO |
| 14 | Screenshots | `docs/screenshots/` | TODO |
| 15 | README | `README.md` | TODO |
| 16 | HOWTORUN | `HOWTORUN.md` | TODO |

---

## Mini Application: Expense Tracker API

### Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Testing**: pytest + pytest-cov
- **Dependencies**: fastapi, uvicorn, pydantic, pytest, pytest-cov, httpx

### Description
A minimal REST API for tracking personal expenses with in-memory storage. Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/expenses` | Create a new expense |
| `GET` | `/expenses` | List expenses (with optional filters) |
| `GET` | `/expenses/{id}` | Get expense by ID |
| `GET` | `/summary` | Get spending summary |
| `DELETE` | `/expenses/{id}` | Delete an expense |

### Expense Model
```python
{
    "id": "uuid",
    "description": "string",
    "amount": "float",
    "category": "food | transport | utilities | entertainment | health | other",
    "date": "YYYY-MM-DD",
    "created_at": "ISO 8601 datetime"
}
```

### Source Files
```
src/
  __init__.py
  main.py          # FastAPI app, routes
  models.py         # Pydantic models
  storage.py        # In-memory storage layer
  utils.py          # Helper functions (date parsing, summary calc)
```

---

## Seeded Bugs (minimum 2 required, we'll do 3)

### Bug 1: Off-by-one in Date Range Filter
- **File**: `src/utils.py`
- **Nature**: Date range filter uses `<` instead of `<=` for the end date, excluding expenses on the last day
- **Impact**: Users filtering by date range miss the final day's expenses
- **Detection**: Straightforward for Research Verifier — comparison operator is visible in source

### Bug 2: Incorrect Summary Calculation
- **File**: `src/utils.py`
- **Nature**: The `calculate_summary` function divides total by number of categories instead of number of expenses when computing average
- **Impact**: Average expense amount is wrong
- **Detection**: Logic error in arithmetic — agent must understand intent vs. implementation

### Bug 3: Missing ID Validation on Delete
- **File**: `src/main.py`
- **Nature**: The DELETE endpoint doesn't check if the expense exists before attempting deletion, returns 200 even for non-existent IDs
- **Impact**: Silent failure; no 404 for missing resources
- **Detection**: Missing guard clause

---

## Security Vulnerability (minimum 1 required)

### Security Issue 1: Hardcoded Secret Key
- **File**: `src/main.py`
- **Nature**: An API key or secret is hardcoded as a string constant (e.g., `API_SECRET = "supersecret123"` used for a simple auth header check)
- **Severity**: HIGH
- **OWASP**: A07:2021 — Identification and Authentication Failures
- **Remediation**: Load from environment variable

### Security Issue 2: Log Injection via Description Field
- **File**: `src/main.py`
- **Nature**: Expense description is logged directly without sanitization, allowing log injection via newline characters
- **Severity**: MEDIUM
- **OWASP**: A09:2021 — Security Logging and Monitoring Failures
- **Remediation**: Sanitize log input (strip newlines/control chars)

---

## Agents

### Agent 1: Research Verifier
- **File**: `agents/research-verifier.agent.md`
- **Model**: `claude-opus-4-6` (strong reasoning needed for reference verification)
- **Input**: `context/bugs/XXX/research/codebase-research.md`
- **Output**: `context/bugs/XXX/research/verified-research.md`
- **Skills loaded**: `skills/research-quality-measurement.md`
- **Behavior**:
  1. Read codebase-research.md
  2. For each file:line reference, verify it exists and matches
  3. For each code snippet, verify it matches source
  4. Apply research quality measurement skill to rate quality
  5. Write verified-research.md with sections: Verification Summary, Verified Claims, Discrepancies Found, Research Quality Assessment, References

### Agent 2: Bug Fixer
- **File**: `agents/bug-fixer.agent.md`
- **Model**: `claude-sonnet-4-6` (balanced speed/quality for plan execution)
- **Input**: `context/bugs/XXX/implementation-plan.md`
- **Output**: `context/bugs/XXX/fix-summary.md` + modified source files
- **Behavior**:
  1. Read implementation-plan.md
  2. Apply code changes per file as specified
  3. Run `pytest` after each change
  4. Write fix-summary.md with sections: Changes Made (file, location, before/after, test result), Overall Status, Manual Verification, References

### Agent 3: Security Verifier
- **File**: `agents/security-verifier.agent.md`
- **Model**: `claude-opus-4-6` (deep reasoning for security analysis)
- **Input**: `context/bugs/XXX/fix-summary.md` + changed source files
- **Output**: `context/bugs/XXX/security-report.md`
- **Behavior**:
  1. Read fix-summary.md to identify changed files
  2. Read each changed file
  3. Scan for: injection, hardcoded secrets, insecure comparisons, missing validation, unsafe deps, XSS/CSRF
  4. Rate each finding: CRITICAL/HIGH/MEDIUM/LOW/INFO with file:line and remediation
  5. Write security-report.md (report only, no code edits)

### Agent 4: Unit Test Generator
- **File**: `agents/unit-test-generator.agent.md`
- **Model**: `claude-sonnet-4-6` (faster for test scaffolding)
- **Input**: `context/bugs/XXX/fix-summary.md` + changed source files
- **Output**: `context/bugs/XXX/test-report.md` + new test files in `tests/`
- **Skills loaded**: `skills/unit-tests-FIRST.md`
- **Behavior**:
  1. Read fix-summary.md to identify changed code
  2. Read changed files
  3. Generate tests following FIRST principles
  4. Tests only cover new/changed code
  5. Run tests with pytest
  6. Write test-report.md with results

---

## Skills

### Research Quality Measurement (`skills/research-quality-measurement.md`)

Defines quality levels:
| Level | Label | Criteria |
|-------|-------|----------|
| 5 | Excellent | All references verified, no discrepancies, comprehensive coverage |
| 4 | Good | All references verified, minor discrepancies, good coverage |
| 3 | Adequate | Most references verified, some discrepancies, acceptable coverage |
| 2 | Poor | Several unverified references, significant discrepancies |
| 1 | Failing | Most references invalid, major discrepancies, incomplete coverage |

Sections the skill mandates in output: Verification Summary, Verified Claims, Discrepancies Found, Research Quality Assessment (level + reasoning), References.

### FIRST Unit Test Principles (`skills/unit-tests-FIRST.md`)

Defines FIRST framework:
- **F**ast: Tests execute in milliseconds, no external dependencies
- **I**ndependent: Each test stands alone, no shared mutable state
- **R**epeatable: Same result every run, no randomness or time dependency
- **S**elf-validating: Pass/fail without manual inspection, clear assertions
- **T**imely: Written alongside the code change, not as afterthought

Checklist the skill provides for each generated test.

---

## Pipeline Orchestration

### `run-pipeline.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# For each bug context directory:
for bug_dir in context/bugs/*/; do
  bug_name=$(basename "$bug_dir")
  echo "=== Processing bug: $bug_name ==="

  # Step 1: Research Verifier
  claude --agent agents/research-verifier.agent.md \
    --input "$bug_dir/research/codebase-research.md"

  # Step 2: Bug Fixer
  claude --agent agents/bug-fixer.agent.md \
    --input "$bug_dir/implementation-plan.md"

  # Step 3: Security Verifier (reads fix-summary from bug_dir)
  claude --agent agents/security-verifier.agent.md \
    --input "$bug_dir/fix-summary.md"

  # Step 4: Unit Test Generator (reads fix-summary from bug_dir)
  claude --agent agents/unit-test-generator.agent.md \
    --input "$bug_dir/fix-summary.md"
done

echo "=== Pipeline complete ==="
```

> Note: Exact CLI syntax for Claude Code agent invocation will be validated during implementation.
> The script structure above is illustrative; actual invocation may use `claude -p` with agent context
> or a Python orchestrator that runs `subprocess.run()` calls.

### Pipeline Order
```
codebase-research.md (pre-created)
        |
        v
[Agent 1] Research Verifier --> verified-research.md
        |
        v
implementation-plan.md (pre-created, informed by verified research)
        |
        v
[Agent 2] Bug Fixer --> fix-summary.md + code changes
        |
       / \
      /   \
     v     v
[Agent 3]  [Agent 4]
Security   Unit Test
Verifier   Generator
    |          |
    v          v
security-  test-report.md
report.md  + test files
```

---

## Context File Structure (per bug)

```
context/bugs/001-date-filter-off-by-one/
  bug-context.md
  research/
    codebase-research.md
    verified-research.md          <-- Agent 1 output
  implementation-plan.md
  fix-summary.md                  <-- Agent 2 output
  security-report.md              <-- Agent 3 output
  test-report.md                  <-- Agent 4 output

context/bugs/002-incorrect-average/
  (same structure)

context/bugs/003-missing-delete-validation/
  (same structure)
```

---

## Screenshots Required

| Screenshot | Shows | Filename |
|------------|-------|----------|
| Pipeline execution | Terminal showing `./run-pipeline.sh` running all 4 agents | `pipeline-run.png` |
| Bug fix before/after | Diff or test output showing bugs fixed | `bug-fixes.png` |
| Security scan | Contents of security-report.md or terminal output | `security-scan.png` |
| Unit test results | pytest output with passing tests | `unit-tests.png` |

---

## Acceptance Criteria

1. **Pipeline runs end-to-end** with a single command (`./run-pipeline.sh`)
2. **All 4 agents** produce their expected output files
3. **Mini app** runs locally with `uvicorn src.main:app`
4. **At least 2 bugs** are found and fixed by the pipeline
5. **At least 1 security issue** is identified in the security report
6. **Unit tests** are generated and pass
7. **Each agent** has an explicit model selection in frontmatter with justification
8. **Skills** are created and referenced by the appropriate agents
9. **Screenshots** capture pipeline run, fixes, security scan, and test results
10. **README** includes author info, project overview, model choices, and run instructions
11. **HOWTORUN** provides step-by-step setup and execution guide

---

## Milestones

| # | Milestone | Key Output |
|---|-----------|------------|
| M1 | Infrastructure | `requirements.txt`, venv, project skeleton, `run-pipeline.sh` stub |
| M2 | Mini App | Working expense tracker API in `src/` with seeded bugs |
| M3 | Skills | `skills/research-quality-measurement.md`, `skills/unit-tests-FIRST.md` |
| M4 | Pre-created Context | `bug-context.md`, `codebase-research.md`, `implementation-plan.md` for each bug |
| M5 | Agents | All 4 `.agent.md` files with model selection |
| M6 | Pipeline | Working `run-pipeline.sh` that chains all agents |
| M7 | Pipeline Run & Artifacts | All output files generated by pipeline |
| M8 | Screenshots | All 4 required screenshots captured |
| M9 | Documentation | README.md, HOWTORUN.md finalized |
| M10 | Validation | Full checklist pass, ready for PR |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude Code agent CLI syntax differs from assumed | Medium | High | Validate early in M5; adapt `run-pipeline.sh` |
| Agents produce inconsistent output format | Medium | Medium | Define output format in agent frontmatter; use skill templates |
| Seeded bugs too easy/hard for agents | Low | Medium | Test pipeline on each bug individually before full run |
| Pipeline timing out on large context | Low | Medium | Keep mini app small (~200 LOC); limit context per agent |
| Model API rate limits during pipeline | Low | Low | Add retry logic in pipeline script |

---

## Submission Checklist

- [ ] Branch: `homework-4-submission`
- [ ] All 4 agents in `agents/`
- [ ] Both skills in `skills/`
- [ ] Mini app in `src/` with seeded bugs (before state visible in git history)
- [ ] Bug context folders in `context/bugs/`
- [ ] All pipeline output files generated
- [ ] `run-pipeline.sh` works end-to-end
- [ ] Tests pass after pipeline run
- [ ] Screenshots in `docs/screenshots/`
- [ ] `README.md` with author info + model justifications
- [ ] `HOWTORUN.md` complete
- [ ] PR created with detailed description + embedded screenshots
