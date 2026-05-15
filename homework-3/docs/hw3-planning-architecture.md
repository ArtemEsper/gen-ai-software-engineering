# HW3 Specification Package — Architecture & Planning

---

## 1. Scope Evaluation

**Verdict: Well-chosen. Moderate narrowing recommended.**

| Dimension | Assessment |
|---|---|
| Domain richness | High — cards touch auth, fraud, compliance, state machines |
| Decomposability | Excellent — 5 distinct subsystems, clean boundaries |
| Regulatory realism | Strong — PCI-DSS, PSD2, GDPR all apply naturally |
| Risk of over-scoping | Medium — "transaction visibility" could balloon |
| Homework fit | Strong match for layered objectives + traceability |

**Recommended narrowing:**

- Scope **transaction visibility** to: real-time status, 30-day history, webhook push. Exclude reconciliation, chargebacks, disputes — those are separate bounded contexts.
- Scope **audit/compliance** to: immutable event log, role-based access to audit records, data retention policy enforcement. Exclude full SOC 2 reporting pipeline.
- Keep all 5 subsystems but bound each with explicit **out-of-scope** clauses in the spec.

---

## 2. Recommended Specification Architecture

The package uses a **layered funnel**: business objectives → functional requirements → low-level tasks → verification.

```
Layer 0 — Vision & Constraints
  │  Product purpose, regulatory context, non-functional requirements
  ▼
Layer 1 — Business Objectives (5–7 objectives)
  │  Each objective: owner, priority, measurable success criterion
  ▼
Layer 2 — Functional Specification (per subsystem)
  │  State machines, API contracts, data models, rules
  ▼
Layer 3 — Low-Level Implementation Tasks
  │  Atomic, verifiable, ID-tagged, mapped to Layer 1 objectives
  ▼
Layer 4 — Edge Cases & Failure Modes
  │  Per-subsystem, classified by severity
  ▼
Layer 5 — Verification & Acceptance
     Test strategy, measurable targets, rubric checklist
```

**Traceability IDs** thread all layers:

```
OBJ-01  → REQ-01.x  → TASK-01.x.x  → EDGE-01.x  → TEST-01.x
```

---

## 3. Agent Definitions & Responsibilities

---

### Agent 1 — Product Specification Architect

**Persona:** Senior product engineer who has shipped card-issuing products at a Tier-1 neobank.

**Inputs:** Domain scope, business goals, homework rubric.

**Outputs:** `specification.md` skeleton, task decomposition, traceability matrix.

**Responsibilities:**

| Area | Detail |
|---|---|
| Business objectives | Define 5–7 layered objectives with measurable success criteria |
| Subsystem decomposition | Break each of the 5 features into bounded contexts with clear interfaces |
| State machine design | Card lifecycle FSM (PENDING → ACTIVE → FROZEN → TERMINATED), transaction FSM |
| Low-level tasks | Atomic tasks with IDs, inputs, outputs, acceptance criteria |
| API contracts | Endpoint signatures, request/response schemas, error codes |
| Data models | Card entity, spending limit entity, transaction record, audit event |
| Beginning/ending context | Warm-up context block, exit condition per task |
| Traceability | OBJ → REQ → TASK mapping table |

**Decision authority:** Scope inclusions/exclusions, naming conventions, task granularity.

---

### Agent 2 — FinTech Compliance & Risk Reviewer

**Persona:** Former payments compliance officer with PCI-DSS QSA certification and fraud engineering background.

**Inputs:** Agent 1 output, regulatory framework list, threat model.

**Outputs:** Compliance annotations on `specification.md`, dedicated sections in `agents.md`, non-functional requirements block.

**Responsibilities:**

| Area | Detail |
|---|---|
| Regulatory mapping | PCI-DSS scope (card data tokenization), PSD2 SCA triggers, GDPR data minimization |
| Security controls | Vault tokenization for PANs, TLS requirements, key rotation policy |
| Fraud edge cases | Velocity checks, geography anomalies, merchant category blocks |
| Auditability | Immutable event log schema, retention periods, who-can-read rules |
| Privacy | PII fields, masking rules, right-to-erasure boundary for card data |
| Operational controls | Rate limiting, idempotency keys, circuit breakers |
| Failure modes | What happens on issuer timeout, network partition, duplicate auth request |
| NFRs | Latency SLAs, availability targets, RPO/RTO for card freeze operations |

**Decision authority:** Any requirement that touches security, privacy, or regulated data handling.

---

### Agent 3 — Specification QA & Rubric Evaluator

**Persona:** Staff engineer who reviews PRDs and technical specs for a bank's architecture review board.

**Inputs:** Outputs from Agents 1 and 2, homework rubric.

**Outputs:** Gap report, ambiguity flags, rubric score estimate, final checklist.

**Responsibilities:**

| Area | Detail |
|---|---|
| Completeness check | Does every subsystem have: objectives, tasks, edge cases, tests? |
| Measurability audit | Are all success criteria quantified? (no "fast", "secure", "reliable") |
| Consistency check | Do task IDs match traceability matrix? Are API contracts internally consistent? |
| Ambiguity detection | Flag underspecified terms: "appropriate limit", "reasonable time", "valid card" |
| Rubric alignment | Map each rubric criterion to a spec section; flag gaps |
| Verification quality | Are test cases deterministic? Do they cover failure paths? |
| AI-rule quality | Are editor/AI rules specific, testable, and non-contradictory? |
| README completeness | Does README give a new reader full orientation in < 5 minutes? |

**Decision authority:** Final sign-off gate before submission. Outputs a scored gap report.

---

## 4. Recommended Agent Workflow

```
Phase 1 — Foundation (Agent 1, pass 1)
  └─ Draft: vision, constraints, business objectives, subsystem map, traceability IDs

Phase 2 — Compliance Overlay (Agent 2, pass 1)
  └─ Annotate Agent 1 output with: NFRs, security controls, regulatory assumptions,
     fraud edge cases, failure modes, audit schema

Phase 3 — Deep Specification (Agent 1, pass 2)
  └─ Incorporate Agent 2 feedback
  └─ Write: state machines, API contracts, data models, low-level tasks,
     beginning/ending contexts, acceptance criteria

Phase 4 — QA Review (Agent 3, pass 1)
  └─ Gap report: missing sections, unmeasured claims, traceability breaks

Phase 5 — Remediation Loop (Agent 1 + Agent 2)
  └─ Fix gaps identified by Agent 3
  └─ Targeted passes only — no full rewrites

Phase 6 — Final QA Gate (Agent 3, pass 2)
  └─ Rubric score estimate
  └─ Final sign-off or escalation list
```

**Key discipline:** Agents 1 and 2 never both edit the same section simultaneously. Agent 3 never edits — review only.

---

## 5. Proposed Folder/File Structure

```
homework-3/
├── README.md                    # Orientation, scope summary, how to read the spec
├── specification.md             # Master specification document
├── agents.md                    # Agent definitions, workflow, prompts
├── rules/
│   ├── .cursorrules             # Cursor AI editor rules
│   ├── ai-review.md             # AI-assisted review instructions
│   └── traceability-rules.md    # ID conventions, linking rules
├── diagrams/
│   ├── card-lifecycle-fsm.md    # State machine (text/mermaid)
│   ├── agent-workflow.md        # Multi-agent workflow diagram
│   └── data-model.md            # Entity relationship sketch
└── verification/
    └── test-strategy.md         # Test cases, coverage targets, tooling
```

`specification.md` internal structure:

```
0. Document Control (version, date, authors, review status)
1. Vision & Product Context
2. Regulatory & Non-Functional Constraints
3. Business Objectives (with traceability IDs)
4. Subsystem Specifications
   4.1 Virtual Card Creation
   4.2 Freeze / Unfreeze
   4.3 Spending Controls
   4.4 Transaction Visibility
   4.5 Audit & Compliance Operations
5. Low-Level Implementation Tasks (ID-tagged)
6. Edge Cases & Failure Modes
7. Verification Strategy & Acceptance Criteria
8. Traceability Matrix
9. Glossary
10. Out-of-Scope Declarations
```

---

## 6. High-Scoring Submission Checklist

**Decomposition & Traceability**
- [ ] Every objective has a unique ID (OBJ-01 … OBJ-07)
- [ ] Every task traces to ≥ 1 objective via ID
- [ ] Every edge case traces to ≥ 1 task
- [ ] Every test case traces to ≥ 1 requirement
- [ ] Traceability matrix is explicit (table or appendix), not implicit

**Specification Quality**
- [ ] State machine for card lifecycle is fully enumerated (all states, all transitions, all guards)
- [ ] Every API endpoint has: method, path, request schema, response schema, error codes
- [ ] Every low-level task has: inputs, outputs, preconditions, postconditions, acceptance criterion
- [ ] Beginning context and ending context defined for each major task group
- [ ] No unmeasured adjectives: every "fast", "secure", "reliable" has a number attached

**FinTech Realism**
- [ ] PCI-DSS scope declared (are PANs stored? tokenized? out-of-scope?)
- [ ] Idempotency strategy defined for all mutating operations
- [ ] Concurrent freeze/transaction race condition addressed
- [ ] Spending limit enforcement point declared (pre-auth vs. post-auth)
- [ ] Audit log is append-only with tamper evidence strategy named

**Edge Cases & Failure Modes**
- [ ] ≥ 3 edge cases per subsystem
- [ ] Each failure mode has: trigger, detection mechanism, system response, user-facing behavior
- [ ] Clock skew / timezone edge cases covered for spending limits
- [ ] Partial system failure (e.g., auth service up, ledger service down) addressed

**Agents & AI Rules**
- [ ] Each agent has: name, persona, inputs, outputs, responsibilities, decision authority
- [ ] AI rules are specific and testable (not "write good code")
- [ ] Review loop is described with entry/exit criteria
- [ ] Agents have non-overlapping authorities

**Verification**
- [ ] Test categories: unit, integration, contract, compliance
- [ ] Measurable coverage targets stated
- [ ] Performance tests defined with pass/fail thresholds
- [ ] At least one chaos/fault-injection scenario described

---

## 7. Critical FinTech Edge Cases to Include

**Card Creation**
- Duplicate card creation request (idempotency key reuse vs. new request)
- Card creation during KYC re-verification window
- Currency mismatch between card and user account denomination

**Freeze/Unfreeze**
- Transaction in-flight at exact moment of freeze (auth already sent to network)
- Freeze request from two concurrent sessions (last-write-wins vs. reject-second)
- Freeze triggered by fraud system simultaneously with user unfreeze
- Card frozen due to account suspension vs. user-initiated freeze (different unfreeze paths)

**Spending Controls**
- Limit set to zero (should block all transactions, not be treated as "no limit")
- Spending limit currency vs. transaction currency conversion at limit evaluation time
- Rolling window reset at midnight vs. 24-hour sliding window (ambiguity that must be resolved)
- Pre-authorization hold that crosses a limit reset boundary
- Merchant category code (MCC) block with fallback merchant category

**Transaction Visibility**
- Transaction showing as "pending" indefinitely (settlement timeout)
- Refund appearing before original transaction in feed (reversal before settlement)
- Declined transaction visibility (show or hide declined attempts to user?)
- Timezone of transaction timestamp (merchant local? UTC? cardholder local?)

**Audit & Compliance**
- Audit record for a freeze that was immediately reversed (should both events appear?)
- Right-to-erasure request for a card with active compliance hold
- Export of audit records during active fraud investigation (access restriction)
- Retention period boundary: what happens to records at day 2556 (7 years)?

---

## 8. Measurable Performance Targets to Define

| Operation | Suggested Target | Rationale |
|---|---|---|
| Card creation API p99 latency | < 800ms | Downstream issuer processor SLA |
| Freeze operation end-to-end | < 2 seconds (p99) | Fraud response window |
| Transaction auth decision | < 200ms (p99) | Visa/Mastercard network timeout = 2s, buffer needed |
| Spending limit evaluation | < 50ms added latency | Must not dominate auth path |
| Audit log write | < 100ms (p99), async acceptable | Non-blocking on critical path |
| Transaction feed query (30 days) | < 1 second (p95) | UX threshold for perceived instant |
| Card state consistency after freeze | < 500ms global propagation | Multi-region card network update |
| System availability (card auth path) | 99.95% monthly | 4.4 hours downtime/year budget |
| Audit log availability (read) | 99.9% monthly | Less critical than auth path |
| Idempotency window | 24 hours minimum | Retry storm protection |

---

## 9. Recommendations for AI-Assisted Review Loops

**Loop 1 — Completeness Sweep (Agent 3 prompt template)**

After each major section is drafted, run Agent 3 with this probe:
> *"For each subsystem in section 4.x, check: does it have a state machine or decision table? At least 3 edge cases? A measurable acceptance criterion? A failure mode with system response defined? Flag every gap as CRITICAL, MAJOR, or MINOR."*

**Loop 2 — Measurability Audit**

Run a targeted Agent 3 pass scanning only for qualitative language:
> *"Scan the entire spec for adjectives without attached numbers: fast, slow, secure, reliable, appropriate, reasonable, valid, standard. For each, either propose a specific measurable replacement or flag it for author decision."*

**Loop 3 — Traceability Integrity Check**

After traceability matrix is drafted:
> *"Verify that every TASK-xx.x.x ID referenced in the traceability matrix appears exactly once in section 5. Verify every OBJ-xx ID in the matrix appears in section 3. Report orphans and broken links."*

**Loop 4 — Regulatory Reality Check (Agent 2)**

Before finalizing:
> *"Assume this system will be audited by a PCI-DSS QSA and a GDPR supervisory authority. List every claim in the spec that would require documentary evidence during audit and flag whether that evidence type is defined in the spec."*

**Loop 5 — Rubric Simulation (Agent 3)**

Final pass before submission:
> *"Score this specification against the homework rubric criteria: [paste rubric]. For each criterion, give a score of 0/1/2 and cite the specific section that earns that score. For any criterion scoring below 2, give the minimum addition needed to reach full marks."*

---

## Next Steps

When you're ready to proceed, I recommend this sequence:

1. **Confirm the scope narrowing** — approve/adjust the out-of-scope boundaries above
2. **Run Agent 1, pass 1** — I'll generate the objectives, subsystem map, and traceability skeleton
3. **Run Agent 2, pass 1** — compliance overlay and NFR block
4. **Run Agent 1, pass 2** — full specification body with tasks, state machines, API contracts
5. **Run Agent 3, pass 1** — gap report
6. **Remediation + final QA gate**
