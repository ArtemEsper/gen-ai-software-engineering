# How to Run

## Prerequisites

| Requirement | Version | Check command |
|-------------|---------|---------------|
| Python | 3.9+ | `python3 --version` |
| pip | Any | `pip --version` |
| Claude Code | Latest | `claude --version` or check `$CLAUDE_CODE_EXECPATH` |

Claude Code is only needed for `run-pipeline.sh`. The mini app and tests run without it.

---

## Setup

```bash
# 1. Navigate to homework directory
cd homework-4

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## Run the Mini App

```bash
# Start the Expense Tracker API (default: http://127.0.0.1:8000)
source venv/bin/activate
python -m uvicorn src.main:app --reload

# Test with curl
curl -X POST http://localhost:8000/expenses \
  -H 'Content-Type: application/json' \
  -d '{"description":"Lunch","amount":12.50,"category":"food","date":"2026-05-01"}'

curl http://localhost:8000/expenses
curl http://localhost:8000/summary
```

API docs are available at `http://localhost:8000/docs` (Swagger UI).

---

## Run the Full Pipeline

```bash
# Run all 4 agents across all 3 bugs
./run-pipeline.sh

# Run for a single bug (partial match supported)
./run-pipeline.sh 001
./run-pipeline.sh 002-incorrect-average
./run-pipeline.sh 003
```

The pipeline requires Claude Code. If unavailable, the script prints manual instructions.

### Pipeline output

Each bug directory gets four output files:

```
context/bugs/<bug-name>/
  research/verified-research.md   # Agent 1: Research Verifier
  fix-summary.md                  # Agent 2: Bug Fixer
  security-report.md              # Agent 3: Security Verifier
  test-report.md                  # Agent 4: Unit Test Generator
```

Logs are written to `artifacts/pipeline-logs/`.

---

## Run Tests

```bash
source venv/bin/activate

# Run all tests (22 tests)
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run a specific test file
python -m pytest tests/test_bug_001.py -v
```

Expected output: 22 passed, 98% coverage.

---

## View Generated Outputs

### Agent outputs (per bug)

```bash
# Verified research
cat context/bugs/001-date-filter-off-by-one/research/verified-research.md

# Fix summary
cat context/bugs/002-incorrect-average/fix-summary.md

# Security report
cat context/bugs/003-missing-delete-validation/security-report.md

# Test report
cat context/bugs/001-date-filter-off-by-one/test-report.md
```

### Screenshot-ready artifacts

```bash
cat artifacts/pipeline-execution-output.txt   # pipeline run
cat artifacts/pytest-results-output.txt       # test results
cat artifacts/security-findings-summary.txt   # security summary
```

### Agent definitions

```bash
cat agents/research-verifier.agent.md
cat agents/bug-fixer.agent.md
cat agents/security-verifier.agent.md
cat agents/unit-test-generator.agent.md
```

### Skills

```bash
cat skills/research-quality-measurement.md
cat skills/unit-tests-FIRST.md
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `command not found: claude` | Set `CLAUDE_CODE_EXECPATH` or install Claude Code CLI |
| `ModuleNotFoundError: src` | Ensure you're running from `homework-4/` directory with venv activated |
| Pipeline fails mid-run | Check `artifacts/pipeline-logs/` for the per-bug log. Re-run with `./run-pipeline.sh <bug>` for just that bug |
| `pip install` fails | Ensure Python 3.9+ and pip are installed. Try `pip install --upgrade pip` first |
| Tests fail after pipeline | Run `python -m pytest tests/ -v --tb=long` for detailed failure output |
| Port 8000 in use | Use `python -m uvicorn src.main:app --port 8099` |

---

## Project Structure

```
homework-4/
  README.md
  HOWTORUN.md
  requirements.txt
  pyproject.toml
  run-pipeline.sh
  agents/                          # 4 agent definitions
  skills/                          # 2 skill definitions
  src/                             # Expense Tracker API
  tests/                           # 22 tests (11 baseline + 11 generated)
  context/bugs/                    # 3 bug contexts with all outputs
  artifacts/                       # Pipeline logs + screenshot-ready files
  docs/                            # Planning docs + screenshots
```
