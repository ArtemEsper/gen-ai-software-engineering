## Summary

Complete specification-driven design package for **Virtual Card Lifecycle and Spending Controls** — a regulated FinTech product operating under PCI-DSS v4.0, PSD2, GDPR, and EU Anti-Money Laundering Directive constraints.

**This is a documentation-only submission. No implementation code is required or included.**

### What was produced

| File | Lines | Purpose |
|---|---|---|
| `homework-3/specification.md` | 1,903 | Master layered specification — 19 sections |
| `homework-3/agents.md` | 247 | 3-agent workflow with personas, operating rules, entry/exit criteria |
| `homework-3/rules/.cursorrules` | 199 | 28 AI/editor rules enforcing FinTech security and domain conventions |
| `homework-3/README.md` | 170 | Rationale, performance target justification, 10 industry best practices |
| `homework-3/docs/*.md` | ~2,600 | Working documents from each agent pass (planning, foundation, compliance overlay) |

### Specification depth

- **7 mid-level objectives** (OBJ-01–07), each with measurable success criteria
- **43 functional requirements** (REQ-xx.xx) across 5 subsystems + 2 cross-cutting
- **34 atomic tasks** in 7 groups, each with OBJ link, REQ link, input, output, acceptance criteria, and edge case references
- **15 API contracts** with request/response schemas, error codes, SCA/idempotency requirements
- **7 logical data models** with per-field sensitivity classification and retention rules
- **4 Mermaid state machines** (card lifecycle, freeze flow, transaction FSM, spending limit evaluation)
- **22 edge cases + 10 failure modes**, each with trigger, behavior, audit implication, and verification method
- **21 non-functional requirements** (latency, availability, consistency, idempotency, rate limiting, retry, retention, observability)
- **12 compliance assumptions** (PCI-DSS, PSD2, GDPR, AMLD) with Hard Req vs Assumption labels
- **12 security requirements** with specific acceptance criteria
- **29 audit event types** with a 17-field tamper-evident schema (SHA-256 hash chaining)
- **Full traceability matrix**: OBJ → REQ → TASK → EDGE/FAIL → NFR/SEC/COMP — zero orphan IDs

## AI Tools Used

### Multi-agent workflow (Claude Opus 4.6 via Claude Code CLI)

The specification was produced using a **6-phase multi-agent conversation workflow**:

1. **Phase 1 — Foundation (Agent 1):** Scope evaluation, 7 objectives, subsystem map, traceability skeleton
2. **Phase 2 — Compliance Overlay (Agent 2):** 12 COMP + 12 SEC + 29 AUD + 21 NFR + 9 FRAUD + 10 FAIL
3. **Phase 3 — Deep Specification (Agent 1):** Full 19-section specification integrating compliance overlay
4. **Phase 4 — QA Review (Agent 3):** Gap report identifying 7 CRITICAL, 9 MAJOR, 6 MINOR issues
5. **Phase 5 — Remediation (Agent 1+2):** Created missing deliverables; patched all CRITICAL/MAJOR gaps
6. **Phase 6 — Final Hardening:** 19 cross-file consistency fixes; zero orphan IDs confirmed

Each agent has a distinct persona and decision authority:
- **Agent 1** (Product Architect) — scope, decomposition, API contracts, task granularity
- **Agent 2** (Compliance Reviewer) — security veto power, audit event registry, NFRs, fraud scenarios
- **Agent 3** (QA Evaluator) — review-only, never edits; produces gap reports with severity classification

### What was verified by the human

- Domain choice and scope boundaries
- Approval of each agent's output before proceeding to the next phase
- Final deliverable review before submission

## Challenges Encountered

1. **Traceability count drift:** Agent 1 Pass 2 claimed task ranges (e.g., TASK-01.01–01.12) that exceeded actual task counts. Agent 3 caught this in Phase 4; fixed in Phase 5.
2. **Audit field count mismatch:** Schema table had 17 rows but text claimed "16 fields." Propagated across 4 locations. Fixed globally in Phase 5.
3. **API renumbering cascade:** Adding 3 missing endpoints (Delete Limit, Terminate Card, Deregister Webhook) shifted section numbers and broke cross-references. Fixed in Phase 6.
4. **FROZEN vs SUSPENDED semantic distinction:** Required explicit specification to satisfy compliance — different unfreeze paths, different regulatory implications, different GDPR erasure eligibility.

## How to Verify

This is a documentation-only submission. To review:

1. **Start with** `homework-3/README.md` — rationale, domain justification, and 10 best practices with section references
2. **Read** `homework-3/specification.md` top-to-bottom — the 19-section structure follows a funnel from vision to tasks
3. **Check traceability:** §17 maps every OBJ → REQ → TASK → EDGE/FAIL → NFR/SEC/COMP
4. **Check agents:** `homework-3/agents.md` defines the 3-agent workflow and operating rules
5. **Check AI rules:** `homework-3/rules/.cursorrules` — 28 testable rules with spec ID references
6. **Working documents** in `homework-3/docs/` show the intermediate outputs from each agent pass

## Key Industry Practices Incorporated

| Practice | Where in spec |
|---|---|
| PAN Tokenization (Token Requestor) | §2.4, §7.1 COMP-01/02, §7.4 SEC-03/04, §12.1 |
| Idempotent API Design | §8 NFR-11, §11 all mutating endpoints |
| Append-Only Audit with Hash Chaining | §7.2, §7.5 AUD-RET-03/04, §9.5 |
| GDPR x AMLD Erasure Conflict Resolution | §7.1 COMP-06/09, §9.5, §13 EDGE-19/22 |
| Actor-Typed Freeze Audit Trail | §6 OBJ-02, §9.2.1, §10.1/10.2 |
| Pre-Auth Spending Control Enforcement | §8 NFR-03, §9.3, §10.4 |
| UTC Sliding Window Velocity Counters | §9.3 REQ-03.03, §13 FAIL-09 |
| Optimistic Locking for Concurrency | §6 OBJ-06, §12.1 version field |
| Webhook Replay Protection (HMAC-SHA256) | §7.4 SEC-07, §9.4, §11.13 |
| Structured Machine-Readable Errors | §9.3 decline codes, §11 error tables |

## Test plan

- [x] `specification.md` contains all 19 required sections
- [x] `agents.md` defines 3 agents with distinct responsibilities
- [x] `rules/.cursorrules` contains 28 testable rules
- [x] `README.md` includes rationale, performance justification, and best practices
- [x] Traceability matrix (§17) has zero orphan IDs
- [x] All NFRs have measurable targets with verification methods
- [x] All edge cases have trigger, behavior, and verification columns
- [x] No vague adjectives without attached numbers
- [x] 17-field count consistent across §7.2, §12.4, §15.3, §16.1
- [x] 15 API endpoint count consistent across §11, §15.3, TASK-07.05

Generated with [Claude Code](https://claude.com/claude-code)
