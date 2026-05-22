# Security Report: Bug 002 — Incorrect Average in Summary Calculation

## Executive Summary

**Overall Risk Level: HIGH**

A security review of the files changed in bug 002 and their direct imports identified **7 findings**: 0 Critical, 2 High, 2 Medium, 2 Low, 1 Informational.

The changed file (`src/utils.py`) itself is clean. However, the broader call graph — specifically `src/main.py`, which imports and uses the changed function — contains a hardcoded API secret and completely bypassable authentication that together represent the most significant risk.

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH     | 2 |
| MEDIUM   | 2 |
| LOW      | 2 |
| INFO     | 1 |

---

## Findings

### SEC-001 — Hardcoded API Secret

- **Severity:** HIGH
- **File:** `src/main.py:15`
- **OWASP Category:** A07:2021 — Identification and Authentication Failures

**Description:**
The API secret is hardcoded as a string literal directly in source code. Anyone with read access to the repository (or the compiled bytecode) can extract this credential.

**Evidence:**
```python
API_SECRET = "supersecret123"
```

**Recommended Remediation:**
Load the secret from an environment variable or a secrets manager. For example:
```python
import os
API_SECRET = os.environ["API_SECRET"]
```
Rotate the exposed credential immediately, as it must be considered compromised once committed to version control.

---

### SEC-002 — Bypassable Authentication

- **Severity:** HIGH
- **File:** `src/main.py:20-22`
- **OWASP Category:** A07:2021 — Identification and Authentication Failures

**Description:**
The `verify_api_key` function is defined but **never registered as a FastAPI dependency** on any route. All endpoints (`POST /expenses`, `GET /expenses`, `GET /expenses/{id}`, `GET /summary`, `DELETE /expenses/{id}`) are completely unauthenticated. Additionally, even if the function were used, its logic allows requests with no `X-Api-Key` header through — it only rejects requests where a key is provided but incorrect.

**Evidence:**
```python
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is not None and x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
```
No route uses `Depends(verify_api_key)`.

**Recommended Remediation:**
1. Register `verify_api_key` as a global dependency or per-route dependency:
   ```python
   app = FastAPI(dependencies=[Depends(verify_api_key)])
   ```
2. Make the API key required (not optional) for protected routes — remove the `is not None` guard so missing keys are also rejected.

---

### SEC-003 — Log Injection via User Input

- **Severity:** MEDIUM
- **File:** `src/main.py:29`
- **OWASP Category:** A09:2021 — Security Logging and Monitoring Failures

**Description:**
The `description` field from user input is interpolated directly into a log message without sanitization. An attacker can inject newline characters (`\n`) to forge log entries, potentially hiding malicious activity or creating misleading audit trails.

**Evidence:**
```python
logger.info(f"Created expense: {expense.description}")
```

**Recommended Remediation:**
Sanitize user input before logging by stripping or escaping control characters:
```python
safe_desc = expense.description.replace("\n", "\\n").replace("\r", "\\r")
logger.info(f"Created expense: {safe_desc}")
```
Alternatively, use structured logging (JSON format) which inherently handles this.

---

### SEC-004 — Timing-Unsafe Secret Comparison

- **Severity:** MEDIUM
- **File:** `src/main.py:21`
- **OWASP Category:** A02:2021 — Cryptographic Failures

**Description:**
The API key comparison uses Python's standard `!=` operator, which short-circuits on the first differing byte. This makes it theoretically vulnerable to timing side-channel attacks that could reveal the secret one character at a time.

**Evidence:**
```python
if x_api_key is not None and x_api_key != API_SECRET:
```

**Recommended Remediation:**
Use `hmac.compare_digest()` for constant-time comparison:
```python
import hmac
if x_api_key is not None and not hmac.compare_digest(x_api_key, API_SECRET):
```

---

### SEC-005 — Unpinned Dependency Versions

- **Severity:** LOW
- **File:** `requirements.txt:1-6`
- **OWASP Category:** A06:2021 — Vulnerable and Outdated Components

**Description:**
All dependencies use minimum-version constraints (`>=`) without upper bounds or pinned versions. This means `pip install` may resolve to any newer version, including ones with known vulnerabilities, or conversely may stay on old versions that have since been patched. There is no lock file to ensure reproducible builds.

**Evidence:**
```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
httpx>=0.24.0
```

**Recommended Remediation:**
Pin exact versions or use a lock file (e.g., `pip freeze > requirements.lock` or use `pip-tools`/`poetry`/`uv` for deterministic resolution). Regularly audit dependencies with `pip-audit` or `safety check`.

---

### SEC-006 — Missing Existence Check on Delete Endpoint

- **Severity:** LOW
- **File:** `src/main.py:64-68`
- **OWASP Category:** A04:2021 — Insecure Design

**Description:**
The `DELETE /expenses/{expense_id}` endpoint always returns HTTP 200 with `"Expense deleted"` regardless of whether the expense existed. This violates the principle of least surprise and could mask enumeration issues — an attacker cannot distinguish between existing and non-existing resources, but the inconsistency with the GET endpoint (which returns 404) may signal sloppy validation elsewhere.

**Evidence:**
```python
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    storage.delete(expense_id)
    return {"detail": "Expense deleted"}
```

**Recommended Remediation:**
Check the return value of `storage.delete()` and return 404 if the expense was not found:
```python
if not storage.delete(expense_id):
    raise HTTPException(status_code=404, detail="Expense not found")
```

---

### SEC-007 — Unvalidated Category Query Parameter

- **Severity:** INFO
- **File:** `src/main.py:37`
- **OWASP Category:** A03:2021 — Injection

**Description:**
The `category` query parameter on `GET /expenses` is accepted as an unvalidated string. While it is only used for in-memory filtering (no injection risk in this context), it does not validate against the `Category` enum. Invalid categories silently return empty results instead of a 400 error, which could confuse API consumers.

**Evidence:**
```python
category: Optional[str] = None,
...
expenses = [e for e in expenses if e.category.value == category]
```

**Recommended Remediation:**
Type the parameter as `Optional[Category]` so FastAPI validates it automatically:
```python
from src.models import Category
category: Optional[Category] = None,
```

---

## Scope

The following files were reviewed in full:

| File | Role |
|------|------|
| `src/utils.py` | **Changed file** — contains the bug fix |
| `src/models.py` | Direct import of `utils.py` |
| `src/main.py` | Imports and calls functions from `utils.py` |
| `src/storage.py` | Direct import of `main.py` |
| `requirements.txt` | Dependency manifest |

## Methodology

This report was produced via static analysis of all files changed in the bug-002 fix (`src/utils.py`) and their direct imports within the `src/` package. Each file was read in full and inspected against the OWASP Top 10 (2021) categories, with attention to injection, authentication, secrets management, logging, input validation, and dependency hygiene. No dynamic analysis or automated scanning tools were used.
