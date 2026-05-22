# Security Report: Bug 001 — Off-by-One in Date Range Filter

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1     |
| HIGH     | 2     |
| MEDIUM   | 1     |
| LOW      | 1     |
| INFO     | 1     |

**Overall risk level: HIGH** — a hardcoded plaintext secret in source code poses an immediate credential-exposure risk. All API endpoints are completely unauthenticated because the `verify_api_key` function is never wired in as a dependency. Log injection via unsanitised user input further increases the attack surface.

---

## Findings

### SEC-001 — Hardcoded API Secret

- **Severity:** CRITICAL
- **File:** `src/main.py:16`
- **OWASP Category:** A07:2021 — Identification and Authentication Failures
- **Description:** The API secret is stored as a plaintext string literal directly in source code. Anyone with read access to the repository obtains the credential. The secret cannot be rotated without modifying and redeploying the application code.
- **Evidence:**
  ```python
  API_SECRET = "supersecret123"
  ```
- **Remediation:** Load the secret from an environment variable (e.g., `os.environ["API_SECRET"]`) or a secrets manager. Remove the hardcoded value from source control, add the variable name to `.env.example`, and rotate the compromised credential.

---

### SEC-002 — Authentication Bypass on All Endpoints

- **Severity:** HIGH
- **File:** `src/main.py:20-22`
- **OWASP Category:** A07:2021 — Identification and Authentication Failures
- **Description:** The `verify_api_key` function is defined but **never injected as a FastAPI dependency** on any route. No endpoint declares `Depends(verify_api_key)`, so all CRUD operations (create, read, list, delete, summary) are completely unauthenticated. Additionally, even if the function were wired in, it only validates when the `X-Api-Key` header is present — omitting the header bypasses the check entirely.
- **Evidence:**
  ```python
  def verify_api_key(x_api_key: Optional[str] = Header(None)):
      if x_api_key is not None and x_api_key != API_SECRET:
          raise HTTPException(status_code=401, detail="Invalid API key")
  ```
  No route or app-level dependency references `verify_api_key`.
- **Remediation:**
  1. Add `verify_api_key` as a global dependency: `app = FastAPI(..., dependencies=[Depends(verify_api_key)])` or apply per-route.
  2. Change the guard to **require** the header — raise `HTTPException(401)` when `x_api_key is None`.

---

### SEC-003 — Log Injection via Unsanitised User Input

- **Severity:** HIGH
- **File:** `src/main.py:29`
- **OWASP Category:** A09:2021 — Security Logging and Monitoring Failures
- **Description:** The `description` field from user-supplied expense data is interpolated directly into a log message via an f-string. An attacker can craft a description containing newline characters (`\n`), carriage returns (`\r`), or ANSI escape sequences to forge log entries, hide malicious activity, or exploit downstream log-processing tools.
- **Evidence:**
  ```python
  logger.info(f"Created expense: {expense.description}")
  ```
- **Remediation:** Sanitise the description before logging by stripping or escaping control characters (e.g., `description.replace('\n', '\\n').replace('\r', '\\r')`). Alternatively, use structured (JSON) logging where the description is a discrete field rather than part of the message string.

---

### SEC-004 — Timing-Unsafe Secret Comparison

- **Severity:** MEDIUM
- **File:** `src/main.py:21`
- **OWASP Category:** A02:2021 — Cryptographic Failures
- **Description:** The API key comparison uses Python's `!=` operator, which short-circuits on the first differing byte. This is vulnerable to timing side-channel attacks that can progressively recover the secret one character at a time.
- **Evidence:**
  ```python
  if x_api_key is not None and x_api_key != API_SECRET:
  ```
- **Remediation:** Use `hmac.compare_digest(x_api_key, API_SECRET)` from the standard library for constant-time comparison.

---

### SEC-005 — Unpinned Dependency Upper Bounds

- **Severity:** LOW
- **File:** `requirements.txt:1-6`
- **OWASP Category:** A06:2021 — Vulnerable and Outdated Components
- **Description:** All dependencies use open-ended `>=` version specifiers with no upper bound. A future `pip install` could pull in a compromised or backwards-incompatible release without warning.
- **Evidence:**
  ```
  fastapi>=0.100.0
  uvicorn>=0.23.0
  pydantic>=2.0.0
  ```
- **Remediation:** Pin exact versions in a lock file (e.g., `pip freeze > requirements.lock`) or use bounded ranges (e.g., `fastapi>=0.100.0,<1.0.0`). Use `pip-audit` or Dependabot to monitor for known CVEs.

---

### SEC-006 — Stale Bug Comments in Fixed Code

- **Severity:** INFO
- **File:** `src/utils.py:17` and `src/utils.py:37`
- **OWASP Category:** N/A
- **Description:** Two comments describe bugs that have already been fixed. On line 17, the comment reads `# BUG: uses < instead of <=` but the code on line 18 already uses `<=`. On line 37, the comment reads `# BUG: divides by number of categories instead of number of expenses` but the code on line 38 already divides by `len(expenses)`. These stale comments could mislead future reviewers into re-introducing the bugs or doubting the correctness of the current code.
- **Evidence:**
  ```python
  # src/utils.py, line 17-18
      # BUG: uses < instead of <=, excluding expenses on the end date
      result = [e for e in result if e.date <= end]

  # src/utils.py, line 37-38
      # BUG: divides by number of categories instead of number of expenses
      average = total / len(expenses)
  ```
- **Remediation:** Remove or update both comments to reflect the corrected logic.

---

## Scope

The following files were reviewed in full:

| File | Reason |
|------|--------|
| `src/utils.py` | Directly modified by the fix |
| `src/main.py` | Imports `filter_by_date_range` and `calculate_summary` from `src/utils`; application entry point |
| `src/models.py` | Imported by `src/utils` and `src/main` |
| `src/storage.py` | Imported by `src/main`; data layer |
| `requirements.txt` | Dependency manifest |

## Methodology

Static manual review of all files modified by the bug fix and their direct imports within the `src/` package. Each file was read in full and inspected against OWASP Top 10 (2021) categories covering injection, authentication failures, cryptographic failures, insecure design, vulnerable components, and logging/monitoring failures. Dependency versions in `requirements.txt` were checked for known-vulnerable ranges. No dynamic analysis or automated scanning tools were used.
