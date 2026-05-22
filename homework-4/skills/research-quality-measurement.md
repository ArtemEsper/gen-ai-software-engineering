# Skill: Research Quality Measurement

## Purpose

Provides a standardised framework for evaluating the quality of codebase
research documents produced by a Bug Researcher agent. The Research Verifier
agent must apply this skill when writing `verified-research.md`.

---

## Quality Levels

| Level | Label | Criteria |
|-------|------------|-------------------------------------------------------------------------|
| 5 | **Excellent** | All file:line references verified and accurate. All code snippets match source verbatim. Root cause correctly identified. Impact assessment is complete and realistic. No discrepancies. |
| 4 | **Good** | All file:line references verified. Code snippets match with only trivial whitespace differences. Root cause is correct. Minor omissions in impact assessment. 0-1 minor discrepancies. |
| 3 | **Adequate** | Most references verified (>=80%). Snippets substantially match source. Root cause is plausible but may be imprecise. Impact partially assessed. 1-3 minor discrepancies. |
| 2 | **Poor** | Several references unverified or wrong (>20% failure rate). Snippets diverge from actual source. Root cause is speculative. Impact missing or misleading. Multiple discrepancies. |
| 1 | **Failing** | Majority of references invalid. Snippets do not match source. Root cause is wrong or absent. Impact not assessed. Critical discrepancies throughout. |

---

## Required Output Sections

Every `verified-research.md` produced using this skill must contain exactly
these sections, in this order:

### 1. Verification Summary
- Overall pass/fail status
- Research Quality level (1-5) and label from the table above
- Count of references checked vs. verified vs. failed
- One-sentence quality justification

### 2. Verified Claims
For each claim in the original research:
- Claim text (quoted or paraphrased)
- File:line reference
- Verification status: VERIFIED / PARTIALLY VERIFIED / FAILED
- Evidence (actual code at that location, if different from claim)

### 3. Discrepancies Found
For each discrepancy:
- Discrepancy ID (D-1, D-2, ...)
- Severity: CRITICAL / MAJOR / MINOR
- What the research claims vs. what the source actually shows
- File:line of the discrepancy

### 4. Research Quality Assessment
- Quality level (1-5) and label
- Reasoning: why this level was chosen (reference specific criteria from the table)
- Strengths of the research
- Weaknesses / gaps

### 5. References
- List of all source files read during verification
- Line ranges inspected

---

## Verification Checklist

The verifier must check each of these for every research document:

- [ ] Every `file:line` reference points to a real file that exists in the project
- [ ] Every `file:line` reference points to a line number within the file's range
- [ ] Every code snippet matches the actual content at the referenced location
- [ ] The root cause description is consistent with the actual code behaviour
- [ ] The impact assessment is proportional and realistic
- [ ] No fabricated or hallucinated references
