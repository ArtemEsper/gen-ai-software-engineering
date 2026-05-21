# Requirements Breakdown — Homework 4: 4-Agent Pipeline

## Source
`homework-4/TASKS.md` — instructor-provided specification.

> Note: The "Expected Project Structure" section in TASKS.md shows `homework-5/` which is a typo; this is homework-4.

---

## Required Agents

- [x] **Bug Research Verifier** (`agents/research-verifier.agent.md`)
  - Reads `research/codebase-research.md`
  - Verifies file:line references and code snippets match source
  - Creates `research/verified-research.md` using the research quality skill
  - Documents discrepancies
  - Sections required: Verification Summary, Verified Claims, Discrepancies Found, Research Quality Assessment, References

- [x] **Bug Fixer** (`agents/bug-fixer.agent.md`)
  - Reads `implementation-plan.md`
  - Applies code changes as specified
  - Runs tests after each change
  - Creates `fix-summary.md` with: Changes Made (file, location, before/after, test result), Overall Status, Manual Verification, References

- [x] **Security Vulnerabilities Verifier** (`agents/security-verifier.agent.md`)
  - Reads `fix-summary.md` and changed files
  - Scans for: injection, hardcoded secrets, insecure comparisons, missing validation, unsafe deps, XSS/CSRF
  - Rates findings: CRITICAL/HIGH/MEDIUM/LOW/INFO
  - Creates `security-report.md` (report only, no code edits)

- [x] **Unit Test Generator** (`agents/unit-test-generator.agent.md`)
  - Reads `fix-summary.md` and changed files
  - Generates tests for new/changed code only
  - Follows project test framework and FIRST principles (via skill)
  - Runs tests
  - Creates `test-report.md`

---

## Required Skills

- [x] **Research Quality Measurement** (`skills/research-quality-measurement.md`)
  - Defines levels/labels for research quality
  - Used by Research Verifier when writing verified-research.md

- [x] **FIRST Unit Test Principles** (`skills/unit-tests-FIRST.md`)
  - Defines FIRST: Fast, Independent, Repeatable, Self-validating, Timely
  - Used by Unit Test Generator

---

## Required Outputs (per bug context)

Each bug context folder (`context/bugs/XXX/`) must contain:

| Output File | Producer | Description |
|-------------|----------|-------------|
| `bug-context.md` | Manual (pre-created) | Documents the seeded bug |
| `research/codebase-research.md` | Manual or Bug Researcher | Research on the bug |
| `research/verified-research.md` | Research Verifier agent | Verified research with quality assessment |
| `implementation-plan.md` | Manual or Bug Planner | Plan for fixing the bug |
| `fix-summary.md` | Bug Fixer agent | Summary of applied changes |
| `security-report.md` | Security Verifier agent | Security review of changes |
| `test-report.md` | Unit Test Generator agent | Test results for changed code |

---

## Required Screenshots

In `docs/screenshots/`:
- [ ] Pipeline run (showing single-command execution)
- [ ] Bug fixes applied (before/after or test output)
- [ ] Security scan results
- [ ] Unit test results

---

## Required Documentation

- [ ] `README.md` — overview, how to run pipeline and app, author/student info, model choices per agent
- [ ] `HOWTORUN.md` — step-by-step guide

---

## Single-Command Pipeline

- [ ] Entire pipeline must run via one command (e.g., `./run-pipeline.sh` or `npm run pipeline`)
- [ ] Must start all agents in correct order
- [ ] Must load related skills automatically
- [ ] No manual per-agent invocation between steps

---

## Agent Model Selection

- [ ] Each agent must have explicit model selection in `.agent.md` frontmatter
- [ ] Model must be appropriate to task complexity
- [ ] Model choices documented and justified in README

Recommended model allocation:
| Agent | Recommended Model | Rationale |
|-------|------------------|-----------|
| Research Verifier | opus (stronger reasoning) | Needs careful verification of references |
| Bug Fixer | sonnet (balanced) | Code changes following a plan |
| Security Verifier | opus (stronger reasoning) | Security analysis requires deep reasoning |
| Unit Test Generator | sonnet (faster) | Routine test scaffolding |

---

## Sample Mini Application

- [ ] Small, self-contained app in `src/`
- [ ] At least 2 intentional bugs
- [ ] At least 1 intentional security issue
- [ ] Runnable locally in a few commands
- [ ] Test command works
- [ ] Bugs documented in `context/bugs/XXX/bug-context.md`
- [ ] Before/after state demonstrable

---

## Artifacts to Commit

- [ ] `agents/` — 4 agent files
- [ ] `skills/` — 2 skill files
- [ ] `context/` — bug context folders with all pipeline outputs
- [ ] `src/` — mini application source
- [ ] `tests/` — test files (including agent-generated ones)
- [ ] `docs/screenshots/` — evidence screenshots
- [ ] `README.md` — complete documentation
- [ ] `HOWTORUN.md` — run instructions
- [ ] `run-pipeline.sh` — single-command pipeline script

---

## Pipeline Flow (6 steps, 4 agents)

```
Step 1: [Pre-created]        Bug context + codebase research
Step 2: [Agent 1]            Research Verifier -> verified-research.md
Step 3: [Pre-created]        Implementation plan (based on verified research)
Step 4: [Agent 2]            Bug Fixer -> fix-summary.md + code changes
Step 5: [Agent 3]            Security Verifier -> security-report.md
Step 6: [Agent 4]            Unit Test Generator -> test-report.md + test files
```

Steps 5 and 6 can run in parallel (both read fix-summary.md + changed files).

---

## Grading Weights (from root README)

| Criteria | Weight |
|----------|--------|
| Functionality | 30% |
| AI Usage Documentation | 25% |
| Code Quality | 20% |
| Documentation | 15% |
| Demo & Screenshots | 10% |
