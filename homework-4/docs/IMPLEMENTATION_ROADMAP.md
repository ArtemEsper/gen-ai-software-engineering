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

## Phase 6: Pipeline Script

**Goal**: Single-command pipeline orchestration.

**Tasks**:
1. Implement `run-pipeline.sh`:
   - Accept optional bug directory argument (default: all bugs)
   - For each bug: run agents 1-4 in order
   - Capture output and errors
   - Print summary at end
2. Test pipeline on one bug first
3. Test full pipeline run across all bugs
4. Add error handling (stop on agent failure with clear message)

**Exit criteria**: `./run-pipeline.sh` chains all 4 agents for all bugs; all output files generated.

---

## Phase 7: Screenshots

**Goal**: Capture all required evidence.

**Tasks**:
1. Screenshot `pipeline-run.png` — terminal showing `./run-pipeline.sh` execution
2. Screenshot `bug-fixes.png` — diff or test output showing bugs resolved
3. Screenshot `security-scan.png` — security-report.md content or terminal output
4. Screenshot `unit-tests.png` — pytest output with passing generated tests

**Exit criteria**: 4 screenshots in `docs/screenshots/`.

---

## Phase 8: Documentation & Validation

**Goal**: README, HOWTORUN, and full validation pass.

**Tasks**:
1. Create `README.md`:
   - Student header (name, date, AI tools)
   - Project overview
   - Architecture/pipeline diagram (Mermaid)
   - Model choices per agent with justification
   - How to run pipeline and app
   - Feature list
2. Create `HOWTORUN.md`:
   - Prerequisites (Python 3.9+, Claude Code)
   - Setup steps (clone, venv, install deps)
   - How to run the mini app
   - How to run the pipeline
   - How to run tests
   - How to view results
3. Run full submission checklist from HW_EXECUTION_SPEC.md
4. Verify all acceptance criteria pass
5. Create PR with detailed description and embedded screenshots

**Exit criteria**: All checklist items green; PR ready for review.

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
