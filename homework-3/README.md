# Homework 3: Specification-Driven Design
# Virtual Card Lifecycle and Spending Controls

---

## Student & Task Summary

**Domain:** Virtual Card Lifecycle and Spending Controls

**Summary:** This specification package defines a regulated FinTech product that enables a financial institution to issue, manage, and govern virtual payment cards. The system covers five subsystems: virtual card creation, freeze/unfreeze, spending controls, transaction visibility, and audit/compliance operations. It is designed for a regulated environment operating under PCI-DSS v4.0, PSD2, GDPR, and EU Anti-Money Laundering Directive constraints.

**Deliverables:**

| File | Purpose |
|---|---|
| `specification.md` | Master layered specification — 19 sections, 1,900+ lines, 15 API contracts |
| `agents.md` | Three-agent workflow definition with personas, responsibilities, and operating rules |
| `rules/.cursorrules` | 28 AI/editor rules enforcing FinTech security and domain conventions |
| `README.md` | This file |

**Supporting artefacts (working documents, not final deliverables):**

| File | Purpose |
|---|---|
| `hw3-planning-architecture.md` | Phase 1 output — scope evaluation, agent definitions, workflow design |
| `hw3-agent1-phase1-foundation.md` | Agent 1 Pass 1 — objectives, subsystem map, traceability skeleton |
| `hw3-agent2-compliance-overlay.md` | Agent 2 Pass 1 — compliance, security, NFR, fraud, failure mode overlay |
| `TASKS.md` | Original homework assignment brief |

---

## Rationale

### Why this domain was chosen

Virtual card lifecycle management sits at the intersection of all the properties the homework asks for: regulated data (PAN, CVV), multi-actor permissions (cardholder, fraud ops, compliance), auditability requirements (financial record-keeping), real-time operational constraints (authorisation decision ≤ 200ms), and a natural state machine (card lifecycle). The domain is rich enough to require genuine decomposition but bounded enough to avoid specification sprawl.

### How the specification was structured

The specification uses a **six-layer funnel**:

```
Vision (HLO-01)
  ↓
Mid-level objectives (OBJ-01–07, each with measurable success criteria)
  ↓
Functional requirements per subsystem (REQ-xx.xx)
  ↓
Low-level implementation tasks (TASK-xx.xx, atomic, agent-executable)
  ↓
Edge cases and failure modes (EDGE-xx, FAIL-xx, with trigger/behavior/verification)
  ↓
Verification strategy (unit → integration → security → performance → chaos)
```

Every layer is connected by traceable IDs (OBJ → REQ → TASK → EDGE → TEST/NFR). The traceability matrix in §17 makes this linkage explicit and machine-checkable.

### How performance targets were chosen

Performance targets are grounded in real FinTech operational constraints, not made-up numbers:

| Target | Value | Rationale |
|---|---|---|
| Auth decision latency | ≤ 200ms p99 | Visa/Mastercard network timeout is 2,000ms; 200ms leaves 1,800ms for routing, stand-in processing, and retry |
| Freeze propagation | ≤ 2,000ms p99 | Fraud response window — a card must be unfusable before the next auth attempt arrives after a fraud signal |
| Card creation | ≤ 3,000ms p99 | PAN Vault round-trip (typically 500–800ms) + DB write + audit write; 3s is the UX threshold for "still feels responsive" |
| Spending limit evaluation | ≤ 50ms added latency p99 | Limit evaluation is on the critical auth path; it cannot consume more than ~25% of the 200ms budget |
| Transaction feed | ≤ 1,000ms p95 | Nielsen's 1-second rule for perceived instant response in UI contexts |
| Auth path availability | ≥ 99.95% monthly | ≤ 21.9 min downtime/month — aligned with card network SLA expectations for issuers |
| Audit log availability | ≥ 99.9% monthly | Compliance read is not on the transaction critical path; slightly lower SLO is acceptable |

All targets are labelled as "assumed targets" in the specification (§8) with explicit rationale, per the homework instructions.

### Why a multi-agent workflow was used

The three-agent structure separates concerns that conflict when combined:

- **Agent 1** optimises for product completeness and decomposability — its incentive is to specify everything clearly.
- **Agent 2** optimises for compliance correctness — its incentive is to add constraints, even when they complicate the product.
- **Agent 3** optimises for specification quality — its incentive is to find gaps, not to fill them.

Keeping these roles separate prevents the common failure mode where a single author writes a spec that is internally consistent but systematically avoids hard compliance constraints. Agent 2 has veto authority on any security, privacy, or regulated-data requirement — this veto cannot be overridden by Agent 1's product priorities.

---

## Industry Best Practices

The following FinTech industry practices are explicitly incorporated into this specification, with section references:

### 1. PAN Tokenization (Token Requestor Pattern)

**Practice:** Virtual card systems never store raw PANs. The system acts as a Token Requestor, delegating PAN custody entirely to a PCI-DSS-certified vault.

**Where it appears:** §2.4 (Data Classification Matrix), §7.1 (COMP-01, COMP-02), §7.4 (SEC-03, SEC-04), §9.1 (SYS-01 security rules), §12.1 (VirtualCard model — no PAN/CVV fields), `rules/.cursorrules` Rules 1–3.

---

### 2. Idempotent API Design

**Practice:** All mutating financial operations accept an `Idempotency-Key` header. Mobile clients and payment systems retry on network failure; idempotency prevents duplicate card creation or duplicate freeze operations.

**Where it appears:** §8 (NFR-11), §11 (all mutating API contracts), §14 (TASK-01.04, TASK-06.02), `rules/.cursorrules` Rule 11.

---

### 3. Append-Only Audit Log with Hash Chaining

**Practice:** Financial audit logs must be tamper-evident. Every audit event is linked to the previous event's hash — any modification breaks the chain and is detectable. This satisfies PCI-DSS audit trail requirements and enables forensic investigation.

**Where it appears:** §7.2 (integrity_hash field), §7.5 (AUD-RET-03, AUD-RET-04), §9.5 (REQ-05.01), §14 (TASK-05.01, TASK-05.02).

---

### 4. GDPR × AMLD Erasure Conflict Resolution

**Practice:** In regulated financial systems, GDPR right-to-erasure cannot simply delete records — financial record-keeping obligations (EU AMLD, 7 years) take precedence. The correct approach is pseudonymisation: replace PII with irreversible hashes while retaining the transaction facts.

**Where it appears:** §7.1 (COMP-06, COMP-09), §9.5 (REQ-05.06), §14 (TASK-05.03), §13 (EDGE-19, EDGE-22), §18 Glossary (Pseudonymisation).

---

### 5. Actor-Typed Freeze Audit Trail

**Practice:** In card fraud operations, it is legally significant whether a card was frozen by the cardholder or by an internal fraud analyst. Different freeze initiators have different unfreeze paths and different regulatory implications (a fraud-frozen card cannot be self-service unfrozen).

**Where it appears:** §6 (OBJ-02 success criteria), §9.2 (§9.2.1 FROZEN vs. SUSPENDED semantics, REQ-02.01–02.05), §10.1 (valid transition table — actor column), §10.2 (Unfreeze Permission Guard), `agents.md` Agent 2 Rule 2.

---

### 6. Pre-Authorisation Spending Control Enforcement

**Practice:** Spending limits must be evaluated before the authorisation request reaches the card network, not after settlement. Post-auth enforcement is too late — funds have already been reserved. Pre-auth enforcement requires the limit evaluation to complete within the card network's 2-second timeout window.

**Where it appears:** §2.3 (Boundary Conditions), §6 (OBJ-03), §8 (NFR-03: ≤ 50ms limit evaluation), §9.3 (REQ-03.06), §10.4 (Spending Limit Evaluation Decision Model flowchart).

---

### 7. UTC Sliding Window Velocity Counters

**Practice:** Velocity limits based on calendar-day resets (midnight local time) are exploitable — a cardholder can spend the daily limit at 23:59 and again at 00:01. UTC sliding windows (24-hour rolling from each transaction's timestamp) prevent this pattern.

**Where it appears:** §6 (OBJ-03 success criteria), §9.3 (REQ-03.03), §14 (TASK-03.01), §13 (FAIL-09: clock skew handling), `rules/.cursorrules` Rule 21.

---

### 8. Optimistic Locking for Concurrent State Changes

**Practice:** Payment systems receive concurrent requests on the same resource (e.g., two fraud signals arriving simultaneously for the same card). Last-write-wins is unsafe — it produces non-deterministic outcomes. Optimistic locking (compare-and-swap on a version field) guarantees exactly one transition succeeds with an auditable conflict record.

**Where it appears:** §6 (OBJ-06), §9.2 (REQ-02.07), §12.1 (VirtualCard.version field), §14 (TASK-02.03), `rules/.cursorrules` Rule 19.

---

### 9. Webhook Replay Protection

**Practice:** Webhooks carrying financial event data (transaction.authorised, transaction.settled) must be signed and carry a timestamp. Without replay protection, an attacker who intercepts a signed webhook payload can replay it indefinitely. The 300-second rejection window matches industry standard (Stripe uses the same value).

**Where it appears:** §7.4 (SEC-07), §9.4 (REQ-04.06), §11.13 (Register Webhook contract), §14 (TASK-04.03), `rules/.cursorrules` Rule 14.

---

### 10. Structured, Machine-Readable Error Responses

**Practice:** FinTech APIs consumed by mobile clients and third-party integrations require machine-readable error codes (not HTTP status codes alone) so clients can programmatically distinguish `CARD_FROZEN` from `LIMIT_EXCEEDED` without parsing human-readable messages. This enables intelligent retry and user messaging.

**Where it appears:** §9.3 (Decline Reason Codes table), §11 (error code tables per endpoint), `rules/.cursorrules` Rule 12.

---

*End of README — SPEC-VCLS-001*
