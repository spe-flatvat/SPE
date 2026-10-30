# SPE M19-FR-CV-06｜Owner裁定反映修文案・差分・根拠追跡表 DRAFT

**Status:** DRAFT / NOT APPROVED / NO CANONICAL CHANGE / HOLD
**Date:** 2026-10-31
**Repository:** `spe-flatvat/SPE`
**Fixed source commit:** `a00c96252ee1260a909be8775511c420685b51d8`
**Source candidate:** `reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md`
**Source Git blob SHA (not SHA-256):** `b254ac774f5def5b5807bc0a172e86bcc7e52e20`
**Owner decisions:** CV05-N01=A; CV05-N02=B; CV05-N03=A. Refer to original Owner messages and individual receipts; this draft does not replace them.

## 1. Scope and method

This document is a **proposed clause-level amendment**, not an applied diff against the canonical repository. Quoted anchor clauses and line numbers refer to the fixed source candidate. Surrounding context must be checked against the exact fixed bytes before any patch is applied. No historic Owner decision is deemed verified by these prospective decisions.

## 2. Amendment proposals (English normative draft)

### P-01 — CC-03, after L119 (CV05-N01)

**Existing anchor:** `The controller MUST NOT invent priority among competing switches. Non-discretionary switch types require separately approved contracts.`

**Proposed addition (not approved):**

> Until an applicable non-discretionary switch contract is separately approved, identified by immutable contract reference and attributable Owner approval evidence, and verified for consistency with CC-12 reservation requirements and the applicable Gate controls, the controller MUST NOT omit an otherwise required attributable Decision for a policy-switch reservation or effectuation. A claimed non-discretionary classification alone MUST NOT constitute such authorization. A switch operation dependent on an unverified exception MUST fail closed within its dependency scope; independently authorized incumbent-policy calculation MUST NOT be blocked solely by that exception's absence.

**Interpretation limit:** N01 preserves the current prohibition; it does not approve any future exception, and does not invent a new universal Decision requirement for unrelated operations. A future exception requires separate approval and normative reconciliation.

### P-02 — CC-04, L152, reference clause (CV05-N02)

**Existing anchor:** `... separately authorized under applicable approved contracts and, where required by those contracts or other applicable approved requirements, attributable Decisions, with all required reservation, numerical-contract, and Gate validations. No such separate authorization is established by this clause.`

**Proposed replacement for the reference portion only (not approved):**

> ... separately authorized under applicable approved contracts identified by immutable contract ID and version, attributable approval evidence, and an explicitly validated scope of applicability. Any other applicable approved requirement MUST likewise be identified by its authoritative source, version or digest, approval evidence, and applicability to the candidate and effective year. The controller MUST determine Decision applicability and any asserted precedence from those approved sources; it MUST NOT infer approval, waive a Decision, or invent a precedence rule from an unspecified reference. All applicable reservation, numerical-contract, and Gate validations remain mandatory. No separate authorization is established by this clause.

**Interpretation limit:** This is a drafting proposal for traceable references, **not** an assertion that a precedence rule, contract register, or exception has already been approved. If the approved sources conflict or cannot establish necessary precedence, the dependent operation remains unresolved/fail-closed; no new ordering is created here.

### P-03 — CC-04, after L152 (CV05-N03)

**Existing anchors:** L138–142 initial-state validation; L150 Gate C for candidate targeting 2026; L152 explicitly does not authorize creation/use/reservation/effectuation of 2026 candidate.

**Proposed addition (not approved):**

> Validation of the Owner-approved 2026 Baseline Initial-State Contract is not authorization to create, use, reserve, schedule, or effectuate a policy-transition candidate targeting 2026. Such operations MUST NOT proceed unless separately attributable approval evidence establishes the candidate's authorized source and creator, destination policy, effective year, applicable Decision requirements, reservation conditions, numerical contract, and Gate requirements. Where a required authorization or validation is absent, contradictory, or unverified, the dependent transition operation MUST fail closed. This restriction MUST NOT be interpreted as prohibiting otherwise authorized 2026 initialization or incumbent-policy calculation. A fictitious 2025 finalized state MUST NOT be introduced as a substitute for the 2026 baseline.

**Interpretation limit:** No new candidate pathway is authorized; N03 is a prospective fail-closed control, not proof of prior approval of baseline values or switch rights.

### P-04 — CC-12, after L403 (cross-clause guard; CV05-N01/N02/N03)

**Existing anchor:** `Before scheduling, the controller MUST validate the approved destination, effective year, attributable Trigger and Decision evidence, and competing reservations.`

**Proposed addition (not approved):**

> The controller MUST NOT treat a reference to an unspecified external requirement, a non-discretionary label, or the 2026 initial-state validation rule as a waiver of this clause's applicable Trigger, Decision, reservation, and competing-reservation evidence requirements. Any proposed exception to a Decision requirement MUST have separate attributable Owner approval and an approved normative reconciliation with this clause before use. The controller MUST retain the evidence references and the result of the applicability validation for audit.

**Interpretation limit:** Preserve CC-12; do not declare all possible future non-discretionary designs invalid, nor permit them without a new approval.

## 3. Traceability matrix

| Proposal | Owner authority | Source anchor | Evidence / limitation | Review target |
|---|---|---|---|---|
| P-01 | CV05-N01=A | CC-03 L105–119 | E-1 separate approved non-discretionary contract NOT LOCATED; absence not proved | Decision omission, fail-closed scope, CC-12 and Gate B |
| P-02 | CV05-N02=B | CC-04 L152 | Contract IDs, approval IDs and precedence not established by this draft | Undefined external reference, hierarchy conflicts, CC-09 provenance |
| P-03 | CV05-N03=A | CC-04 L138–152 | E-2 2026 candidate authorization NOT LOCATED; initial-state contract actual approval not independently verified | 2026 vs 2027+, Gate A/C/B, incumbent continuity |
| P-04 | N01/N02/N03 cross-check | CC-12 L403 | No waiver of Trigger/Decision evidence; any exception requires separate approval | Scheduling, competing reservations, audit |

## 4. Dependency and consistency checks (document review only)

| Related clause / mechanism | Expected effect | Status |
|---|---|---|
| CC-03 | No unapproved non-discretionary Decision omission | Text proposal only; no execution verification |
| CC-04 | Baseline 2026 distinct from 2026 candidate authorization | Text proposal only |
| CC-05 | Fail-closed restricted to dependent operation; avoid global halt | Text proposal only; original failure taxonomy not reverified in full |
| CC-09 | Attributable approval and historical decision reconciliation preserved | Text proposal only; historic D25/O/GATE/COMP/R/6D mapping incomplete |
| CC-12 | Trigger/Decision/reservation and competing-reservation checks not weakened | Text proposal only |
| Gate A→C→B | Gate C validation never itself authorizes a switch | Text proposal only; test not executed |
| 29 invariants | No invariant-by-invariant execution performed | NOT VERIFIED |
| Finding register | 32 original OPEN / 0 closed; 8 new unadjudicated; CLD3-01 Major OPEN | No disposition changed |

## 5. Review-ready evidence requirements / STOP gates

1. Preserve actual Owner original messages and CV05-N01/N02/N03 receipts, with independently calculated byte SHA-256 at distribution; do not substitute summaries for originals.
2. Freeze an immutable source candidate and an **exact** proposed patch; validate line anchors, full-context consistency, and byte hashes. This document is not a validated machine-applicable patch.
3. For each normative addition, verify no accidental conflict with existing CC-01–13, the approved simulation specification, and prior Owner decisions. In particular, don't silently add an implementation schema or precedence policy.
4. Maintain a separate list of unlocated historical approvals and external contracts; no prospective Owner decision retroactively authenticates them.
5. Verify applicable invariants and tests before claiming PASS. Review findings remain OPEN until individually adjudicated.
6. Obtain distinct Owner authorization for repository writes, independent 4AI packet issuance, clause acceptance, DecisionLog update, and Freeze.

## 6. Completion status

**CV-06 DRAFT drafting complete; independent validation NOT COMPLETE.** Proposed amendments P-01–P-04 and traceability recorded. No GitHub write, canonical change, review dispatch, finding closure, or HOLD release. Next recommended gate: Owner examination of this DRAFT, then exact diff construction and cross-clause review under separately authorized scope.
