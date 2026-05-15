# Agent 1 — Product Specification Architect
## Phase 1 Foundation Output: Virtual Card Lifecycle and Spending Controls

---

## 0. Document Control

| Field | Value |
|---|---|
| Document ID | SPEC-VCLS-001 |
| Version | 0.1-FOUNDATION |
| Status | DRAFT — Agent 1 Pass 1 |
| Domain | Virtual Card Lifecycle and Spending Controls |
| Author | Agent 1: Product Specification Architect |
| Review Status | Pending Agent 2 (Compliance) and Agent 3 (QA) |
| Classification | Internal — Restricted |
| Regulatory Context | PCI-DSS v4.0, PSD2, GDPR Art. 17/25 |

---

## 1. Vision and Product Context

### 1.1 Product Purpose

This system enables a regulated financial institution to issue, manage, and control virtual payment cards for individual cardholders within a multi-tenant card program. It provides cardholder-facing self-service controls, program-level operational tools, and a tamper-evident audit record sufficient for internal compliance review and external regulatory inspection.

Virtual cards operate as **non-physical card credentials** — a 16-digit Primary Account Number (PAN), expiry, and CVV — issued against an underlying funding account. All card credentials are tokenized at rest and in transit. The raw PAN is never stored within this system's application layer.

### 1.2 Regulatory Context

The system operates within the following regulatory framework:

- **PCI-DSS v4.0**: Card credential handling, tokenization, and access control requirements apply. This system is a Token Requestor and delegates PAN storage to a certified vault provider. The system itself is **not** a PCI-DSS Cardholder Data Environment (CDE).
- **PSD2 (EU) / Open Banking equivalents**: Strong Customer Authentication (SCA) triggers apply to card issuance and spending limit modifications above defined thresholds. Specific SCA implementation is handled by the upstream authentication service (out of scope); this system consumes SCA outcomes as boolean signals.
- **GDPR / Data Protection**: Transaction records and audit logs contain personal data. Retention periods, access controls, and right-to-erasure boundaries are defined in Section 2.3.

### 1.3 Stakeholder Perspectives

| Stakeholder | Primary Need | Key Interaction Points |
|---|---|---|
| Cardholder | Self-service card control, real-time spend visibility | Card creation, freeze/unfreeze, spending limits, transaction feed |
| Program Manager | Fleet-level controls, compliance reporting | Bulk freeze, audit export, spending policy enforcement |
| Fraud Operations | Rapid card suspension, event investigation | System-initiated freeze, audit log query, event feed |
| Compliance Officer | Immutable audit records, retention enforcement | Audit log access, data retention policy, export API |
| Card Network (Visa/Mastercard) | Authorisation decision within network timeout | Transaction auth endpoint, spending limit evaluation |
| External Auditor | Evidence of controls, tamper-evident records | Audit log read, access control records |

---

## 2. Final Narrowed Scope

### 2.1 In-Scope Subsystems

| Subsystem ID | Name | Brief Description |
|---|---|---|
| SYS-01 | Virtual Card Creation | Issuance of virtual card credentials against a validated funding account |
| SYS-02 | Card Freeze and Unfreeze | Cardholder and system-initiated suspension and reinstatement of card authorisation |
| SYS-03 | Spending Controls | Per-card rules governing transaction amount, velocity, and merchant category |
| SYS-04 | Transaction Visibility | Real-time authorisation status, 30-day settled transaction history, webhook event delivery |
| SYS-05 | Audit and Compliance Operations | Append-only event log, role-gated read access, data retention policy execution |

### 2.2 Explicit Out-of-Scope Boundaries

The following are explicitly excluded from this specification. Any request to extend scope into these areas requires a separate bounded context document and formal scope change approval.

| Excluded Area | Rationale | Responsible System |
|---|---|---|
| Dispute and chargeback processing | Separate regulated workflow with network-specific rules | Disputes Platform |
| Settlement and reconciliation | Downstream of authorisation; handled by ledger service | Payments Ledger |
| SOC 2 Type II reporting pipeline | Organisational-level control reporting | Security & Compliance Platform |
| Full AML / KYC platform | Cardholder onboarding and ongoing due diligence | Identity and Compliance Platform |
| Physical card issuance | Different fulfilment and personalisation workflow | Card Fulfilment Service |
| Foreign exchange and currency conversion | FX rate management is a separate service | Treasury / FX Service |
| Instalment and credit features | Requires credit decisioning and regulatory credit permissions | Credit Platform |
| Push-to-card / money movement | Funding account top-up is upstream of card issuance | Payments Platform |
| Fraud scoring and ML model inference | Fraud signals are consumed by this system, not produced | Fraud Intelligence Service |
| Transaction history beyond 30 days | Long-term archival is handled by data warehouse | Data Platform |
| SCA / MFA implementation | SCA outcomes are consumed; SCA execution is upstream | Authentication Service |

### 2.3 Boundary Conditions

- **Transaction Visibility**: Real-time authorisation status (accept/decline, pending/settled), 30-day rolling settled transaction history, webhook event delivery for state changes. No dispute workflow, no pre-30-day history query, no reconciliation feed.
- **Audit Log**: Event log covers all state-changing operations within this system's five subsystems only. Cross-system audit correlation is performed by the SIEM layer, which is out of scope.
- **Spending Limits**: Evaluated at authorisation time (pre-auth). Post-auth adjustments, refund impact on limits, and limit-based credit decisions are out of scope.

---

## 3. High-Level Objective

> **HLO-01**: Provide a regulated, auditable, and cardholder-controlled virtual card management system that enables real-time card issuance, suspension, and spending governance, while maintaining a tamper-evident compliance record sufficient for PCI-DSS and GDPR regulatory inspection — with card freeze operations completing end-to-end within 2 seconds at the 99th percentile and authorisation decisions completing within 200ms at the 99th percentile.

---

## 4. Mid-Level Business Objectives

Each objective is independently observable and testable. Success criteria are measurable. Every objective maps to one or more subsystems and generates a set of traceable requirements.

---

### OBJ-01 — Virtual Card Issuance

**Statement:** A cardholder with a validated, active funding account can request and receive a virtual card credential within 3 seconds (p99), with the issued card credential tokenized before delivery and immediately usable for authorised transactions.

**Success Criteria:**
- `POST /cards` returns a tokenized card reference (not raw PAN) within 3,000ms at p99 under nominal load (≤ 500 concurrent requests).
- The issued card enters `ACTIVE` state as its initial state.
- A `card.created` audit event is written within 500ms of credential issuance.
- Duplicate creation requests carrying the same idempotency key return the original response without creating a second card record.
- Card creation is rejected with HTTP 422 if the funding account status is not `ACTIVE`.

**Subsystems:** SYS-01, SYS-05

**Traceability:** OBJ-01 → REQ-01.x → TASK-01.x.x

---

### OBJ-02 — Card Freeze and Unfreeze

**Statement:** A cardholder or an authorised system actor (fraud operations, program manager) can suspend a card's authorisation capability within 2 seconds end-to-end (p99), with all subsequent authorisation requests declined for the duration of the freeze, and with distinct audit trails for cardholder-initiated versus system-initiated freeze events.

**Success Criteria:**
- `POST /cards/{id}/freeze` completes and propagates to the authorisation decision engine within 2,000ms at p99.
- Any authorisation request received ≥ 500ms after freeze confirmation is declined with reason code `CARD_FROZEN`.
- Cardholder-initiated and system-initiated freeze events are recorded as distinct event types in the audit log.
- A card in `FROZEN` state cannot be unfrozen by a cardholder if the freeze was system-initiated by fraud operations (requires fraud operations actor to unfreeze).
- Unfreeze operation returns card to `ACTIVE` state; a `card.unfrozen` audit event is written within 500ms.

**Subsystems:** SYS-02, SYS-05

**Traceability:** OBJ-02 → REQ-02.x → TASK-02.x.x

---

### OBJ-03 — Spending Controls Enforcement

**Statement:** Program managers and cardholders (within program-defined permission boundaries) can configure per-card spending rules — including single-transaction amount limits, daily/weekly rolling velocity limits, and merchant category code (MCC) allow/block lists — with enforcement applied atomically at authorisation time without adding more than 50ms to the authorisation decision latency at p99.

**Success Criteria:**
- Authorisation requests exceeding a configured single-transaction limit are declined with reason code `LIMIT_EXCEEDED` before forwarding to the card network.
- Velocity limit counters use a 24-hour sliding window anchored to UTC, not a calendar-day reset.
- MCC block rules decline transactions with reason code `MCC_BLOCKED` within the same authorisation latency budget.
- Spending limit changes take effect for authorisations received ≥ 200ms after the successful limit update API response.
- Spending limit evaluation adds ≤ 50ms at p99 to the end-to-end authorisation latency.
- A `card.limit_updated` audit event is written for every spending control modification.

**Subsystems:** SYS-03, SYS-05

**Traceability:** OBJ-03 → REQ-03.x → TASK-03.x.x

---

### OBJ-04 — Real-Time Transaction Visibility

**Statement:** A cardholder can retrieve the real-time authorisation status of any card transaction and query a 30-day rolling history of settled transactions via API, with each settled transaction entry containing sufficient detail for cardholder recognition, and with state-change events delivered via webhook within 10 seconds of the triggering event at p95.

**Success Criteria:**
- `GET /cards/{id}/transactions` returns settled transactions within the trailing 30-day window in ≤ 1,000ms at p95.
- Each transaction record includes: transaction ID, merchant name, MCC, amount, currency, authorisation timestamp, settlement timestamp (if settled), and status (`PENDING` / `SETTLED` / `DECLINED` / `REVERSED`).
- Declined transaction attempts are visible in the feed with status `DECLINED` and a non-sensitive decline reason code.
- Webhook events for `transaction.authorised`, `transaction.settled`, `transaction.declined`, and `transaction.reversed` are delivered within 10,000ms of the event at p95.
- Webhook delivery includes at least 3 retry attempts with exponential backoff before marking delivery as `FAILED`.

**Subsystems:** SYS-04, SYS-05

**Traceability:** OBJ-04 → REQ-04.x → TASK-04.x.x

---

### OBJ-05 — Immutable Audit Log

**Statement:** Every state-changing operation within this system generates an append-only, tamper-evident audit event that is readable by authorised compliance and operations roles within 1 second of write, retained for a minimum of 7 years, and exportable in a machine-readable format within 60 seconds for any 90-day query window.

**Success Criteria:**
- Audit events are written as append-only records; no update or delete operation exists on the audit store for compliance-classified events.
- Each audit event includes: event ID, event type, actor identity (cardholder ID or system actor ID), actor role, card ID, timestamp (UTC, millisecond precision), before-state, after-state, and request correlation ID.
- Audit log read access is restricted to actors with `COMPLIANCE_READ` or `OPERATIONS_READ` roles; cardholder actors cannot access other cardholders' audit records.
- Export of a 90-day audit window for a single card completes within 60 seconds and returns valid JSON Lines or CSV format.
- Audit records for cards subject to a compliance hold are not eligible for deletion under right-to-erasure requests for the duration of the hold.
- Audit log availability is ≥ 99.9% measured monthly on a rolling 12-month basis.

**Subsystems:** SYS-05

**Traceability:** OBJ-05 → REQ-05.x → TASK-05.x.x

---

### OBJ-06 — Card Lifecycle State Integrity

**Statement:** The virtual card lifecycle state machine enforces valid state transitions only, with every transition recorded atomically with its audit event, such that no card ever exists in an undefined or unrecoverable state, and concurrent state-change operations on the same card are serialised with the outcome deterministic and auditable.

**Success Criteria:**
- The state machine defines exactly 5 states: `PENDING_ACTIVATION`, `ACTIVE`, `FROZEN`, `SUSPENDED`, `TERMINATED`.
- All invalid state transition attempts return HTTP 409 with a machine-readable error code identifying the disallowed transition.
- Concurrent state-change requests on the same card ID (e.g., simultaneous freeze from two sessions) result in exactly one transition succeeding; the other returns HTTP 409 with a conflict reason.
- State and audit event are written in the same atomic transaction; no card state change is persisted without a corresponding audit event.
- A `TERMINATED` card cannot transition to any other state. Termination is irreversible.

**Subsystems:** SYS-01, SYS-02, SYS-05

**Traceability:** OBJ-06 → REQ-06.x → TASK-06.x.x

---

### OBJ-07 — Operational and Program-Level Controls

**Statement:** Authorised program managers can perform fleet-level operations — including bulk freeze of all cards within a program, export of spending control configurations, and retrieval of aggregated transaction summaries per card — with bulk freeze of up to 10,000 cards completing within 30 seconds and individual card operation APIs remaining available throughout the bulk operation.

**Success Criteria:**
- `POST /programs/{id}/freeze-all` initiates bulk freeze; returns a job ID immediately (async).
- Bulk freeze job status is queryable; job reaches terminal state (`COMPLETED` or `PARTIAL_FAILURE`) within 30 seconds for a program of ≤ 10,000 cards.
- Partial failures in bulk freeze are reported per-card in the job result; successfully frozen cards are not rolled back on partial failure.
- Individual card API endpoints (`/cards/{id}/*`) maintain p99 latency SLAs during bulk freeze operations.
- Program manager actions are recorded in the audit log with actor role `PROGRAM_MANAGER` and the program ID as a context field.

**Subsystems:** SYS-01, SYS-02, SYS-03, SYS-05

**Traceability:** OBJ-07 → REQ-07.x → TASK-07.x.x

---

## 5. Subsystem Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL ACTORS & DEPENDENCIES                   │
│                                                                     │
│  Cardholder   Program Manager   Fraud Ops   Compliance   Card Network│
│      │              │              │             │             │     │
└──────┼──────────────┼──────────────┼─────────────┼─────────────┼────┘
       │              │              │             │             │
       ▼              ▼              ▼             │             ▼
┌─────────────────────────────────────────┐       │   ┌──────────────────┐
│           API Gateway / Auth Layer      │       │   │  Card Network    │
│   (SCA outcome consumption, role RBAC)  │       │   │  Auth Interface  │
└────────┬────────────────────────────────┘       │   └────────┬─────────┘
         │                                        │            │
   ┌─────▼──────┐  ┌──────────────┐  ┌──────────▼──────┐     │
   │  SYS-01    │  │   SYS-02     │  │    SYS-03        │◄────┘
   │  Virtual   │  │  Freeze /    │  │   Spending       │
   │   Card     │  │  Unfreeze    │  │   Controls       │
   │  Creation  │  │              │  │   Enforcement    │
   └─────┬──────┘  └──────┬───────┘  └──────────┬───────┘
         │                │                      │
         └────────────────┼──────────────────────┘
                          │
              ┌───────────▼──────────┐
              │  Card State Machine  │  ← SYS-06 (cross-cutting)
              │  & Lifecycle Engine  │     enforces OBJ-06
              └───────────┬──────────┘
                          │
         ┌────────────────┼──────────────────────┐
         │                │                      │
   ┌─────▼──────┐  ┌──────▼───────┐  ┌──────────▼───────┐
   │  SYS-04    │  │   SYS-05     │  │   External        │
   │ Transaction│  │  Audit &     │  │   Dependencies    │
   │ Visibility │  │  Compliance  │  │  (Vault, Auth,    │
   │            │  │  Operations  │  │   Fraud Signal,   │
   └────────────┘  └──────────────┘  │   Webhook Infra)  │
                                     └───────────────────┘
```

### 5.1 Subsystem Interface Summary

| Interface | Producer | Consumer | Protocol | Contract |
|---|---|---|---|---|
| Card credential delivery | SYS-01 | Cardholder, SYS-03, SYS-04 | HTTPS REST | Tokenized card reference, never raw PAN |
| Freeze signal | SYS-02 | Card State Machine, Card Network | Internal event | `card.frozen` event with actor and reason |
| Spending rule lookup | SYS-03 | Card Network Auth Interface | Synchronous RPC | ≤ 50ms budget |
| Transaction event stream | Card Network Auth Interface | SYS-04, SYS-05 | Async event bus | Exactly-once delivery guaranteed by consumer |
| Webhook dispatch | SYS-04 | Cardholder-registered endpoints | HTTPS POST | Signed payload, retry policy defined |
| Audit event write | All SYS-01..05 | SYS-05 Audit Store | Internal, synchronous | Atomic with state transition |
| Audit export | SYS-05 | Compliance Officer, External Auditor | HTTPS REST | JSON Lines or CSV, paginated |

---

## 6. Traceability ID Convention

### 6.1 Identifier Scheme

```
OBJ-{nn}              High-Level and Mid-Level Objectives
                       nn = 01..07

REQ-{nn}.{mm}         Functional Requirements
                       nn = parent OBJ number
                       mm = sequential within objective (01..99)

TASK-{nn}.{mm}.{kk}   Low-Level Implementation Tasks
                       nn = parent OBJ number
                       mm = parent REQ number
                       kk = sequential within requirement (01..99)

EDGE-{nn}.{ee}        Edge Cases
                       nn = parent OBJ or SYS number
                       ee = sequential within subsystem (01..99)

TEST-{nn}.{tt}        Test Cases / Acceptance Criteria
                       nn = parent OBJ or REQ number
                       tt = sequential (01..99)

NFR-{nn}              Non-Functional Requirements
                       nn = sequential, assigned by Agent 2
```

### 6.2 Linking Rules

- Every `REQ-xx.xx` must cite exactly one `OBJ-xx` parent.
- Every `TASK-xx.xx.xx` must cite exactly one `REQ-xx.xx` parent.
- Every `EDGE-xx.xx` must cite at least one `TASK-xx.xx.xx` it affects.
- Every `TEST-xx.xx` must cite at least one `REQ-xx.xx` or `TASK-xx.xx.xx` it validates.
- `NFR-xx` entries are standalone but must be cross-referenced in any `TASK` or `TEST` where they impose a constraint.

### 6.3 Traceability Example (illustrative)

```
OBJ-02 (Freeze/Unfreeze)
  └── REQ-02.01 (Cardholder-initiated freeze API)
        └── TASK-02.01.01 (Define freeze endpoint contract)
        └── TASK-02.01.02 (Propagate freeze to auth engine within 2s)
        └── TASK-02.01.03 (Write card.frozen audit event atomically)
              └── EDGE-02.01 (Freeze request while auth in-flight)
              └── TEST-02.01 (Freeze propagation latency under load)
```

---

## 7. Initial Traceability Skeleton

> **Note:** REQ and TASK identifiers are placeholders at this phase. Agent 1 Pass 2 will expand each row into full requirement and task definitions.

| OBJ ID | Objective Name | REQ Range (reserved) | TASK Range (reserved) | EDGE Range (reserved) | TEST Range (reserved) |
|---|---|---|---|---|---|
| OBJ-01 | Virtual Card Issuance | REQ-01.01–01.09 | TASK-01.01.x–01.09.x | EDGE-01.01–01.06 | TEST-01.01–01.12 |
| OBJ-02 | Card Freeze and Unfreeze | REQ-02.01–02.08 | TASK-02.01.x–02.08.x | EDGE-02.01–02.07 | TEST-02.01–02.10 |
| OBJ-03 | Spending Controls Enforcement | REQ-03.01–03.10 | TASK-03.01.x–03.10.x | EDGE-03.01–03.08 | TEST-03.01–03.14 |
| OBJ-04 | Real-Time Transaction Visibility | REQ-04.01–04.07 | TASK-04.01.x–04.07.x | EDGE-04.01–04.06 | TEST-04.01–04.10 |
| OBJ-05 | Immutable Audit Log | REQ-05.01–05.08 | TASK-05.01.x–05.08.x | EDGE-05.01–05.05 | TEST-05.01–05.08 |
| OBJ-06 | Card Lifecycle State Integrity | REQ-06.01–06.06 | TASK-06.01.x–06.06.x | EDGE-06.01–06.05 | TEST-06.01–06.08 |
| OBJ-07 | Operational and Program-Level Controls | REQ-07.01–07.06 | TASK-07.01.x–07.06.x | EDGE-07.01–07.04 | TEST-07.01–07.08 |

### 7.1 Cross-Cutting Requirement Zones

| Zone ID | Zone Name | Applies To | Notes |
|---|---|---|---|
| CCZ-AUTH | Authorisation and RBAC | All OBJs | Role definitions owned by upstream auth service; this system consumes roles |
| CCZ-IDEM | Idempotency | OBJ-01, OBJ-02, OBJ-03, OBJ-07 | All mutating operations must accept and honour idempotency keys |
| CCZ-AUDIT | Audit Event Schema | OBJ-05, all OBJs | Common event envelope; per-event payload varies |
| CCZ-LATENCY | Latency SLA Enforcement | OBJ-01, OBJ-02, OBJ-03, OBJ-04 | NFRs assigned by Agent 2; referenced in task acceptance criteria |
| CCZ-TOKEN | PAN Tokenization | OBJ-01, OBJ-04 | Raw PANs never traverse application layer |

---

## 8. Beginning Context

> **Purpose:** Defines the preconditions that must be true before any implementation or verification task within this specification begins. An agent or implementer encountering this system should be able to read this section and understand the full environmental state assumed by the specification.

### 8.1 System Preconditions

The following services, data states, and configurations are assumed to be in place before any subsystem in this specification is built or tested:

**Infrastructure**
- A cloud-hosted, multi-region environment with at least two availability zones is provisioned and reachable.
- A secrets management vault (e.g., HashiCorp Vault or equivalent) is operational and accessible by all subsystems for cryptographic key retrieval.
- An event bus (e.g., Kafka or equivalent) is operational with topics for: `card-state-changes`, `transaction-events`, `audit-events`.
- A webhook delivery infrastructure with retry capability is provisioned.

**External Service Dependencies**
- The PAN Vault service (external, PCI-certified) is operational and its tokenization API is reachable. The system holds a valid service credential for it.
- The card network authorisation interface is configured and the BIN (Bank Identification Number) range for this card program is registered.
- The upstream Authentication and Identity service is operational and can issue role-bearing tokens consumable by this system's RBAC layer.
- The Fraud Intelligence Service is operational and can push freeze signals to SYS-02.

**Data Preconditions**
- At least one card program record exists in the program registry with status `ACTIVE`.
- At least one cardholder account exists with funding account status `ACTIVE` for integration test execution.
- Role definitions (`CARDHOLDER`, `PROGRAM_MANAGER`, `FRAUD_OPS`, `COMPLIANCE_READ`, `OPERATIONS_READ`) are registered in the RBAC system.

**Specification Preconditions**
- The card lifecycle state machine (defined in Section 6 of the full specification) is agreed and signed off before any freeze/unfreeze or lifecycle task is implemented.
- The audit event schema (defined in Section 5 of the full specification) is finalised before any subsystem writes its first audit event, to prevent schema fragmentation.
- The traceability ID convention (Section 6 of this foundation document) is agreed and in use across all contributing agents and implementers.

### 8.2 Actor Preconditions

| Actor | Precondition |
|---|---|
| Cardholder | Has an authenticated session with role `CARDHOLDER`; funding account status is `ACTIVE` |
| Program Manager | Has an authenticated session with role `PROGRAM_MANAGER` and is authorised for the target program ID |
| Fraud Operations | Has an authenticated session with role `FRAUD_OPS` |
| Compliance Officer | Has an authenticated session with role `COMPLIANCE_READ` |
| Card Network | Has a registered authorisation endpoint registered with the system |
| Webhook Consumer | Has a registered HTTPS endpoint and a valid shared secret for signature verification |

---

## 9. Ending Context

> **Purpose:** Defines the postconditions and completion criteria that must be true when all work within this specification is done. Used to determine when the system is complete, when a sprint or task group is done, and what state the system leaves behind for downstream systems and auditors.

### 9.1 System Postconditions (Full Specification Complete)

**Functional Completeness**
- All five subsystems (SYS-01 through SYS-05) are implemented, deployed, and returning expected responses for all happy-path and defined failure-path scenarios.
- Every objective in OBJ-01 through OBJ-07 has at least one passing automated test validating its measurable success criterion.
- The card lifecycle state machine rejects 100% of invalid transition attempts in automated test runs.

**Audit Completeness**
- The audit log contains an event record for every state-changing operation executed during integration testing, with no gaps detectable by log-sequence analysis.
- All audit events conform to the agreed schema; zero schema validation errors in the test run.

**Traceability Completeness**
- Every `REQ-xx.xx` in the traceability matrix has at least one corresponding `TASK-xx.xx.xx` marked `IMPLEMENTED`.
- Every `TASK-xx.xx.xx` marked `IMPLEMENTED` has at least one corresponding `TEST-xx.xx` marked `PASSED`.
- No orphaned `TASK` or `TEST` IDs exist (every ID is reachable from an `OBJ`).

**Security Postconditions**
- No raw PAN appears in any application log, API response, or audit record across all test executions.
- All endpoints require a valid bearer token; unauthenticated requests return HTTP 401 in 100% of test cases.
- Role enforcement is validated: `CARDHOLDER` role cannot access another cardholder's resources (HTTP 403 in 100% of cross-cardholder test cases).

**Performance Postconditions**
- Load tests confirm p99 latencies meet the targets in Section 4 for all four latency-bounded objectives (OBJ-01, OBJ-02, OBJ-03, OBJ-04) at the defined load levels.
- Bulk freeze (OBJ-07) completes within 30 seconds for a 10,000-card program in performance test.

**Handoff Artefacts**
- A completed traceability matrix (Section 8 of the full specification) is exported and reviewed.
- All edge cases (EDGE-xx.xx) are tagged as either `COVERED_BY_TEST`, `MITIGATED_BY_DESIGN`, or `ACCEPTED_RISK` with sign-off.
- The audit log export function has been demonstrated to an authorised reviewer with a real 90-day dataset.

---

## 10. Proposed Low-Level Task Groups

> **Note:** These are task group headings only. Full task decomposition with IDs, inputs, outputs, preconditions, postconditions, and acceptance criteria will be produced in Agent 1 Pass 2, after Agent 2's compliance overlay is incorporated.

### Task Group TG-01: Virtual Card Issuance

```
TG-01.A  Define card creation API contract
           → Method, path, request schema, response schema, error codes
TG-01.B  Define idempotency key handling for card creation
           → Key format, window duration, collision behavior
TG-01.C  Define funding account validation rules at issuance
           → Required account states, rejection criteria, error responses
TG-01.D  Define tokenization flow at credential generation
           → Interaction with PAN Vault, token format, delivery to cardholder
TG-01.E  Define initial card state assignment
           → Entry state, conditions for bypassing PENDING_ACTIVATION
TG-01.F  Define card creation audit event schema
           → Required fields, actor capture, before/after state
TG-01.G  Define card creation rate limits and abuse controls
           → Per-cardholder, per-program limits; lockout behavior
```

### Task Group TG-02: Card Freeze and Unfreeze

```
TG-02.A  Define cardholder-initiated freeze API contract
TG-02.B  Define system-initiated (fraud ops, program manager) freeze API contract
TG-02.C  Define freeze signal propagation to authorisation engine
           → Propagation SLA, confirmation mechanism, timeout handling
TG-02.D  Define freeze actor distinction in audit log
           → Event type differentiation, actor role field
TG-02.E  Define unfreeze permission matrix
           → Who can unfreeze cardholder-initiated vs. system-initiated freezes
TG-02.F  Define behavior of in-flight authorisations at freeze time
           → Accept/decline boundary, grace window, idempotency
TG-02.G  Define concurrent freeze/unfreeze conflict resolution
           → Serialisation mechanism, HTTP 409 contract, audit trail
```

### Task Group TG-03: Spending Controls

```
TG-03.A  Define spending limit data model
           → Limit types (single-transaction, daily velocity, weekly velocity, MCC)
           → Currency, window definition, cardholder vs. program-level scope
TG-03.B  Define spending limit CRUD API contracts
TG-03.C  Define velocity counter schema and reset logic
           → Sliding window mechanics, UTC anchoring, counter persistence
TG-03.D  Define authorisation-time limit evaluation logic
           → Evaluation order, short-circuit rules, latency budget allocation
TG-03.E  Define MCC allow/block list management
           → MCC format (ISO 18245), precedence rules, wildcard support
TG-03.F  Define spending limit conflict resolution (cardholder vs. program limits)
           → More restrictive wins rule, override permissions
TG-03.G  Define spending limit change audit event schema
TG-03.H  Define behavior for limit-set-to-zero edge case
TG-03.I  Define pre-auth hold interaction with velocity counters
           → Hold counting, release behavior, settlement reconciliation
```

### Task Group TG-04: Transaction Visibility

```
TG-04.A  Define transaction record schema
           → Required fields: ID, merchant, MCC, amount, currency,
             auth timestamp, settlement timestamp, status, decline reason code
TG-04.B  Define transaction feed API contract
           → Pagination, date range constraints (max 30 days), sort order
TG-04.C  Define declined transaction visibility rules
           → What is shown, what is suppressed (non-sensitive reason codes only)
TG-04.D  Define transaction status lifecycle
           → PENDING → SETTLED, PENDING → REVERSED, PENDING → DECLINED (terminal states)
TG-04.E  Define webhook event contracts
           → Event types, payload schema, signature scheme, delivery SLA
TG-04.F  Define webhook retry policy
           → Retry count, backoff schedule, dead-letter behavior
TG-04.G  Define transaction timestamp timezone handling
           → Storage in UTC, display conversion rules, API field naming
```

### Task Group TG-05: Audit and Compliance Operations

```
TG-05.A  Define audit event envelope schema (common to all subsystems)
           → event_id, event_type, actor_id, actor_role, resource_id,
             timestamp_utc_ms, before_state, after_state, correlation_id
TG-05.B  Define per-subsystem audit event type registry
           → Enumerated event types for SYS-01 through SYS-05
TG-05.C  Define audit store write characteristics
           → Append-only, no-update, no-delete contract, storage technology constraints
TG-05.D  Define audit log read API contract
           → Query parameters, pagination, role-gating, cross-cardholder isolation
TG-05.E  Define audit export API contract
           → Format (JSON Lines / CSV), query window limit (90 days), response time SLA
TG-05.F  Define data retention policy execution
           → Retention period (7 years), automated deletion boundary,
             compliance hold override behavior
TG-05.G  Define right-to-erasure interaction with audit log
           → Which fields are erasable, which are legally protected, PII masking vs. deletion
TG-05.H  Define tamper-evidence strategy
           → Hash chaining or equivalent, verification mechanism for auditors
```

### Task Group TG-06: Card Lifecycle State Machine

```
TG-06.A  Define all card states with entry and exit conditions
           → PENDING_ACTIVATION, ACTIVE, FROZEN, SUSPENDED, TERMINATED
TG-06.B  Define all valid state transitions with guards
           → Transition table: from-state × to-state × actor × guard condition
TG-06.C  Define all invalid transition rejection behavior
           → HTTP 409 contract, error body schema, audit logging of rejected attempts
TG-06.D  Define atomicity mechanism for state + audit event co-write
           → Transaction scope, rollback behavior on audit write failure
TG-06.E  Define concurrent transition serialisation mechanism
           → Optimistic locking, compare-and-swap, or equivalent
TG-06.F  Define TERMINATED state immutability enforcement
```

### Task Group TG-07: Program-Level Operations

```
TG-07.A  Define bulk freeze API contract (async job pattern)
           → Request, job ID response, status polling endpoint
TG-07.B  Define bulk freeze job execution model
           → Parallelism, partial failure semantics, rollback scope
TG-07.C  Define bulk freeze observability
           → Progress reporting, per-card result in job output
TG-07.D  Define program-level spending control export
           → Format, scope (all cards in program), access control
TG-07.E  Define program manager audit trail
           → Program ID as context field, bulk operation as single job-level event
           + per-card child events
TG-07.F  Define individual API SLA protection during bulk operations
           → Resource isolation or rate-limiting strategy
```

---

## 11. Summary: Foundation Artefacts Produced

| Artefact | Status | Notes |
|---|---|---|
| Narrowed scope with out-of-scope boundary table | Complete | 10 excluded areas explicitly named |
| High-level objective (HLO-01) | Complete | Measurable, includes latency targets |
| Mid-level objectives (OBJ-01 through OBJ-07) | Complete | All include measurable success criteria |
| Subsystem map (SYS-01 through SYS-05) | Complete | Interface summary included |
| Traceability ID convention | Complete | 6 ID types, linking rules defined |
| Traceability skeleton | Complete | Range reservations for all OBJs |
| Cross-cutting concern zones (CCZ) | Complete | 5 zones identified |
| Beginning context | Complete | Infrastructure, actor, and spec preconditions |
| Ending context | Complete | Functional, audit, security, performance postconditions |
| Low-level task groups (TG-01 through TG-07) | Complete (headings) | Full task decomposition reserved for Pass 2 |

---

**Agent 1 Pass 1 — COMPLETE**

**Recommended next action:** Route this foundation document to **Agent 2 (FinTech Compliance & Risk Reviewer)** for compliance overlay, NFR assignment, fraud edge-case injection, and regulatory annotation before Agent 1 returns for Pass 2 to write full task decompositions, state machines, and API contracts.
