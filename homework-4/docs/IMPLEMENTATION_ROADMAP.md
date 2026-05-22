# Implementation Roadmap — Homework 4: 4-Agent Pipeline

> Reference: `HW_EXECUTION_SPEC.md` is the primary source of truth.

---

## Phase 1: Infrastructure  **COMPLETED 2026-05-22**

**Goal**: Project skeleton, dependencies, and tooling in place.

**Tasks**:
1. [x] Create `requirements.txt` with: fastapi, uvicorn, pydantic, pytest, pytest-cov, httpx
2. [x] Create `src/__init__.py` (empty)
3. [x] Create `tests/__init__.py` (empty)
4. [x] Create directory structure: agents/, skills/, context/bugs/{001,002,003}/research/, docs/screenshots/, docs/project-memory/
5. [x] Create `run-pipeline.sh` stub (placeholder that prints usage)
6. [x] Create `pyproject.toml` with pytest + coverage config

**Exit criteria** (all verified):
- [x] `pip install -r requirements.txt` succeeds (venv created, all deps installed)
- [x] Directory structure exists (14 directories)
- [x] pytest runs with 0 tests collected (exit code 5)
- [x] `./run-pipeline.sh` runs and prints usage stub

---

## Phase 2: Mini Application

**Goal**: Working expense tracker API with seeded bugs and security issues.

**Tasks**:
1. [x] Create `src/models.py` — Pydantic models (Category enum, ExpenseCreate, Expense, ExpenseSummary)
2. [x] Create `src/storage.py` — In-memory dict-based CRUD (add, get, list_all, delete)
3. [x] Create `src/utils.py` — Helper functions with seeded bugs:
   - `filter_by_date_range()` — **BUG 1**: `<` instead of `<=` for end date (line 19)
   - `calculate_summary()` — **BUG 2**: divides by `len(by_category)` instead of `len(expenses)` (line 37)
4. [x] Create `src/main.py` — FastAPI app with 5 endpoints + seeded issues:
   - **BUG 3**: DELETE returns 200 for non-existent IDs (line 64)
   - **SECURITY 1**: `API_SECRET = "supersecret123"` hardcoded (line 16)
   - **SECURITY 2**: `logger.info(f"Created expense: {expense.description}")` — unsanitised (line 30)
5. [x] Create `tests/test_basic.py` — 11 baseline tests, all pass, none cover buggy paths
6. [x] Create `context/bugs/*/bug-context.md` — 3 bug context files documenting each seeded bug
7. [x] Verify: uvicorn starts, all endpoints respond, pytest 11/11 pass, 91% coverage

**Exit criteria** (all verified):
- [x] App starts (`uvicorn src.main:app` on port 8099)
- [x] 5 endpoints work (POST, GET list, GET by id, GET summary, DELETE)
- [x] 3 seeded bugs present and not caught by baseline tests
- [x] 2 security issues present in source
- [x] 11 tests pass, 0 warnings, 91% coverage

---

## Phase 3: Skills  **COMPLETED 2026-05-22**

**Goal**: Create the two required skill files.

**Tasks**:
1. [x] Create `skills/research-quality-measurement.md`:
   - 5-level quality scale (Excellent/Good/Adequate/Poor/Failing) with criteria
   - 5 required output sections (Verification Summary, Verified Claims, Discrepancies, Quality Assessment, References)
   - 6-item verification checklist
2. [x] Create `skills/unit-tests-FIRST.md`:
   - FIRST acronym with detailed criteria + compliant/non-compliant examples
   - 10-item per-test checklist
   - 4 required test-report sections + FIRST compliance matrix template

**Exit criteria** (all verified):
- [x] Both skill files exist with complete definitions
- [x] Research quality skill defines levels, required sections, and checklist
- [x] FIRST skill defines principles, examples, per-test checklist, and report template

---

## Phase 4: Pre-Created Context Files  **COMPLETED 2026-05-22**

**Goal**: Bug research, context, and implementation plans ready for agents.

**Tasks (completed for all 3 bugs)**:
1. [x] `context/bugs/*/bug-context.md` — created in Phase 2 (3 files)
2. [x] `context/bugs/*/research/codebase-research.md` — 3 files with file:line refs, code snippets, root cause, impact
3. [x] `context/bugs/*/implementation-plan.md` — 3 files with exact before/after code, test command, acceptance criteria

**File:line reference verification**: 15/15 references checked against source — all match.

**Exit criteria** (all verified):
- [x] 3 bug directories, each with bug-context.md, codebase-research.md, and implementation-plan.md
- [x] All file:line references point to real, correct source locations
- [x] Implementation plans specify exact before/after diffs

---

## Phase 5: Agents

**Goal**: All 4 agent definition files created with proper frontmatter and model selection.

**Tasks**:
1. [x] Create `agents/research-verifier.agent.md` (3.3 KB):
   - Model: `claude-opus-4-6` | Role: fact-checker | Skill: `research-quality-measurement.md`
   - 7-step instructions, 3 failure/stop conditions, read-only constraints
2. [x] Create `agents/bug-fixer.agent.md` (2.9 KB):
   - Model: `claude-sonnet-4-6` | Role: plan executor | Skills: none
   - 4-step instructions, 3 failure/stop conditions, one-change-at-a-time constraint
3. [x] Create `agents/security-verifier.agent.md` (3.7 KB):
   - Model: `claude-opus-4-6` | Role: security auditor (report only) | Skills: none
   - 5-step instructions, 8-category scan checklist, 5-level severity scale
4. [x] Create `agents/unit-test-generator.agent.md` (3.9 KB):
   - Model: `claude-sonnet-4-6` | Role: test author | Skill: `unit-tests-FIRST.md`
   - 7-step instructions, FIRST compliance matrix, tests-only constraint

**Exit criteria** (all verified):
- [x] All 4 agent files exist in `agents/`
- [x] Model selection matches spec (opus for verifiers, sonnet for fixer/tester)
- [x] Skill references resolve to real files on disk (2/2 confirmed)
- [x] Each agent has YAML frontmatter with name, role, model, description, inputs, outputs, skills
- [x] Each agent defines step-by-step instructions and failure/stop conditions

---

## Phase 6: Pipeline Script  **COMPLETED 2026-05-22**

**Goal**: Single-command pipeline orchestration.

**Tasks**:
1. [x] CLI analysis: documented Claude Code CLI capabilities in `docs/claude_cli_analysis.md`
   - `--agent` takes named agents; project-level agents not auto-discovered
   - Fallback: prompt-injection via `--append-system-prompt` + `--model` + `-p`
   - Permissions: `--dangerously-skip-permissions` for non-interactive mode
2. [x] Implement `run-pipeline.sh` (full rewrite from stub):
   - Discovers claude binary via `$CLAUDE_CODE_EXECPATH` or `which claude`
   - Parses model from `.agent.md` frontmatter (awk, macOS-compatible)
   - Extracts body text as system prompt injection
   - Accepts optional bug-dir pattern arg (partial match: `001` works)
   - Runs 4 agents in order per bug, stops on failure
   - Logs to `artifacts/pipeline-logs/` with timestamped files
   - Non-zero exit on errors; clear error messages
3. [x] Validation:
   - `bash -n` syntax check: PASS
   - Model parsing: all 4 agents parse correctly
   - Body extraction: all 4 agent bodies extracted correctly
   - Bug-dir matching: partial (`001`) and full name both work
   - Error path (no claude): exits 1 with fallback instructions
   - Error path (bad pattern): exits 1 with clear message

**Exit criteria** (verified — pipeline mechanics only; full agent execution is Phase 7):
- [x] `./run-pipeline.sh` discovers claude binary, iterates bugs, invokes agents in order
- [x] `./run-pipeline.sh 001` filters to single bug
- [x] `./run-pipeline.sh nonexistent` exits 1 with error
- [x] No-claude fallback prints manual instructions and exits 1
- [x] Logs written to `artifacts/pipeline-logs/`

---

## Phase 7: Pipeline Execution + Artifacts  **COMPLETED 2026-05-22**

**Goal**: Run full pipeline, generate all agent outputs, validate.

**Pipeline execution:**
- Bugs 001 + 002: ran via `./run-pipeline.sh` (automated, all 4 agents per bug)
- Bug 003: research verifier ran via pipeline; remaining 3 agents ran directly
  (API credit limit hit; same model executing same agent instructions)

**Tasks:**
1. [x] Pipeline ran for bug 001: research-verifier (opus) + bug-fixer (sonnet) + security-verifier (opus) completed
2. [x] Pipeline ran for bug 002: all 4 agents completed in full automated run
3. [x] Bug 003 completed: research verified by pipeline, fix + security + tests executed directly
4. [x] All 3 bug fixes applied to source files
5. [x] All 21 output files generated (7 per bug x 3 bugs)
6. [x] 11 agent-generated tests created (4 + 4 + 3 across 3 test files)
7. [x] 22/22 tests pass, 98% coverage
8. [x] Screenshot-ready artifacts in `artifacts/`:
   - `pipeline-execution-output.txt` — pipeline run summary
   - `pytest-results-output.txt` — full test + coverage output
   - `security-findings-summary.txt` — consolidated security findings
9. [x] Pipeline logs in `artifacts/pipeline-logs/`

**Exit criteria** (all verified):
- [x] All agent output files exist (21/21)
- [x] All bugs fixed in source
- [x] All tests pass (22/22)
- [x] Coverage 98% (up from 91%)
- [x] Security findings documented (2 HIGH, 2 MEDIUM, 1 LOW, 1 INFO)

---

## Phase 8: Documentation & Validation  **COMPLETED 2026-05-22**

**Goal**: README, HOWTORUN, and full validation pass.

**Tasks**:
1. [x] Create `README.md`:
   - Student header (Artem Chumachenko, 2026-05-22, Claude Code)
   - Project overview + Mermaid pipeline diagram
   - 4 agents with model justifications
   - Bug summary table (3 bugs), security findings (6 issues)
   - Pipeline instructions + fallback execution note for Bug 003
   - Test results (22/22, 98%), generated artifacts summary
2. [x] Create `HOWTORUN.md`:
   - Prerequisites, setup, run app, run pipeline (full + single-bug)
   - Run tests/coverage, view outputs, troubleshooting table
3. [x] Run full submission checklist — 11/11 acceptance criteria PASS
4. [x] Create `docs/submission_audit.md` — formal pass/fail audit
5. [ ] PR creation — ready, not yet created (pending user action)

**Exit criteria** (all verified):
- [x] All checklist items green (11/11)
- [x] README with author info, model justifications, Mermaid diagram
- [x] HOWTORUN with complete step-by-step guide
- [x] `docs/submission_audit.md` with PASS result

---

## Phase Dependencies

```
Phase 1 (Infrastructure)
    |
    v
Phase 2 (Mini App)
    |
    v
Phase 3 (Skills) -----> Phase 4 (Context Files)
    |                        |
    v                        v
Phase 5 (Agents) <-----------
    |
    v
Phase 6 (Pipeline)
    |
    v
Phase 7 (Screenshots)
    |
    v
Phase 8 (Docs & Validation)
```

Phases 3 and 4 can run in parallel after Phase 2.

---

## Estimated Effort

| Phase | Est. Time | Notes |
|-------|-----------|-------|
| 1. Infrastructure | 10 min | Boilerplate |
| 2. Mini App | 30 min | ~200 LOC + seeded bugs |
| 3. Skills | 15 min | 2 markdown files |
| 4. Context Files | 30 min | 3 bugs x 3 files each |
| 5. Agents | 20 min | 4 agent definitions |
| 6. Pipeline | 30 min | Shell script + testing |
| 7. Screenshots | 10 min | Capture during pipeline run |
| 8. Docs & Validation | 20 min | README, HOWTORUN, checklist |
| **Total** | **~2.5-3 hrs** | |
