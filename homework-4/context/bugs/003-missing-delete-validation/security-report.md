# Security Report: Bug 003 — Missing Delete Validation

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 2 |
| LOW | 1 |
| INFO | 1 |
| **Total** | **6** |

**Overall risk level:** HIGH — hardcoded secret and bypassable auth remain in `src/main.py`.

The bug fix itself (adding a 404 guard to the DELETE endpoint) is clean and introduces no new vulnerabilities.

## Findings

### SEC-001: Hardcoded API Secret
- **Severity:** HIGH
- **File:** `src/main.py:15`
- **OWASP:** A07:2021 — Identification and Authentication Failures
- **Description:** `API_SECRET = "supersecret123"` is a hardcoded credential. Anyone who reads the source code obtains the secret.
- **Evidence:**
  ```python
  API_SECRET = "supersecret123"
  ```
- **Remediation:** Load from environment variable: `API_SECRET = os.environ["API_SECRET"]`

### SEC-002: Authentication Function Never Used
- **Severity:** HIGH
- **File:** `src/main.py:20-22`
- **OWASP:** A07:2021 — Identification and Authentication Failures
- **Description:** `verify_api_key` is defined but never wired as a FastAPI dependency on any endpoint. All endpoints are completely unauthenticated.
- **Evidence:**
  ```python
  def verify_api_key(x_api_key: Optional[str] = Header(None)):
      if x_api_key is not None and x_api_key != API_SECRET:
          raise HTTPException(status_code=401, detail="Invalid API key")
  ```
  No endpoint uses `Depends(verify_api_key)`.
- **Remediation:** Add `Depends(verify_api_key)` to protected endpoints.

### SEC-003: Log Injection via User Input
- **Severity:** MEDIUM
- **File:** `src/main.py:29`
- **OWASP:** A09:2021 — Security Logging and Monitoring Failures
- **Description:** Expense description is interpolated directly into a log message. A description containing `\n` followed by a fake log line could spoof log entries.
- **Evidence:**
  ```python
  logger.info(f"Created expense: {expense.description}")
  ```
- **Remediation:** Sanitize before logging: `desc = expense.description.replace('\n', ' ').replace('\r', ' ')`

### SEC-004: Timing-Unsafe Secret Comparison
- **Severity:** MEDIUM
- **File:** `src/main.py:21`
- **OWASP:** A02:2021 — Cryptographic Failures
- **Description:** The API key is compared using `!=`, which is vulnerable to timing attacks.
- **Evidence:**
  ```python
  if x_api_key is not None and x_api_key != API_SECRET:
  ```
- **Remediation:** Use `hmac.compare_digest(x_api_key, API_SECRET)`.

### SEC-005: Unpinned Dependency Versions
- **Severity:** LOW
- **File:** `requirements.txt`
- **OWASP:** A06:2021 — Vulnerable and Outdated Components
- **Description:** All dependencies use `>=` minimum version constraints without upper bounds. A future `pip install` could pull a compromised or breaking version.
- **Remediation:** Pin exact versions or use upper bounds (e.g., `fastapi>=0.100.0,<1.0`).

### SEC-006: Stale Bug Comments in Source
- **Severity:** INFO
- **File:** `src/utils.py:17,37`
- **Description:** Comments still read "BUG: ..." even though the code has been fixed. These could mislead reviewers.
- **Remediation:** Update or remove the stale comments.

## Scope
Files reviewed:
- `src/main.py` (changed file — DELETE endpoint fix)
- `src/storage.py` (imported by main.py)
- `src/utils.py` (imported by main.py)
- `src/models.py` (imported by storage.py and utils.py)
- `requirements.txt`

## Methodology
Static review of the changed file and all direct imports within the `src/` package. Each file was scanned for OWASP Top 10 categories: injection, broken authentication, sensitive data exposure, insecure design, security misconfiguration, vulnerable components, identification failures, integrity failures, logging failures, and SSRF.
