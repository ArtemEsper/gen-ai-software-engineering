# Pitfalls & Bugs

Bugs, gotchas, and traps discovered during this course.
Add entries with: `bash course-memory/scripts/07-record-note.sh pitfall "<text>"`

---

## 2026-04-23 — Float decimal validation false negative (Homework 1)

**Problem:** `Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)` does NOT
reject 3-decimal-place inputs like `10.123` — both `round(10.123, 2)` and
`float(Decimal('10.12'))` evaluate to `10.12`, so the condition never fires.

**Fix:** Use `Decimal(str(v)).as_tuple().exponent < -2` — checks the actual exponent
of the decimal representation, immune to floating-point rounding side-effects.

```python
if Decimal(str(v)).as_tuple().exponent < -2:
    raise ValueError("Amount must have at most 2 decimal places")
```

---

## 2026-04-23 — macOS BSD `head -n -1` incompatibility

**Problem:** `head -n -1` (print all lines except the last) works on Linux GNU `head`
but exits with an error on macOS BSD `head`. Used to separate `curl` response body
from the HTTP status code line — caused `$BODY` to always be empty, making all
content assertions silently pass regardless of actual response.

**Fix:** Use `curl -o <tmpfile> -w "%{http_code}"` to write body and status separately:
```bash
STATUS=$(curl -s -o "$_TMPFILE" -w "%{http_code}" "$URL")
BODY=$(cat "$_TMPFILE")
```

---

## 2026-04-23 — DSPy generator wrong ROOT path

**Problem:** The generated `dspy_generate_homework.py` had `ROOT = Path(__file__).parent`
pointing to `src/`, but `TASKS.md` and `OUTPUT_DIR` need to be one level up in `homework-1/`.

**Fix:** `ROOT = Path(__file__).parent.parent`

---

## 2026-04-23 — MemPalace cloud save requires paid API key

**Problem:** `npx mempalace save` returns 403 after `init`. The `init` command registers
a Palace ID locally but save/recover against `m.cuer.ai` requires account credentials.

**Fix:** Implemented local vault fallback in `_vault.sh` — blobs stored as
`course-memory/vault/<sha256[:8]>.json` with `L-` prefixed IDs.

---

## 2026-04-23 — DSPy model ID `claude-sonnet-4-5-20250929` does not exist

**Problem:** The generated DSPy script used model `anthropic/claude-sonnet-4-5-20250929`
which is not a valid model ID and causes a LiteLLM error at runtime.

**Fix:** Use `anthropic/claude-sonnet-4-6` (current production Sonnet model).

---
