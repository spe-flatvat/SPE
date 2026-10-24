# M19-25 — Four-AI Re-review Request Packet (Rev.2)

**Status:** REVIEW REQUEST DRAFT / NON-CANONICAL / NOT FROZEN / NOT REVIEWED
**Prepared:** 2026-10-24
**Repository:** `spe-flatvat/SPE`
**Owner-confirmed repository review baseline (D22-01):** `e2238922193107f204805d9f25d6ddd6f764eced`
**Owner-confirmed review attachment:** `M19_Control_Contract_v0.4_DRAFT_Rev2.md`
**Attachment SHA-256:** `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea`
**Attachment status:** exact bytes confirmed by Owner for re-review, not approved as normative/canonical contract.
**Reference traceability:** `M19_25_Findings_Traceability_DRAFT.md` (supporting context, not normative authority)
**Internal V&V reference:** `M19_25_Internal_VV_Round2_DRAFT.md` (internal static checks only)

## 1. Purpose
Independently re-review the owner-adjudicated revision of M19 control semantics for annual simulation and conditional policy transitions (2026–2055). Evaluate whether D25-01 through D25-12 were incorporated consistently, whether original four-AI findings were resolved in the text, and whether any new normative gaps or contradictions were introduced. Do not treat previous internal static PASS as review acceptance.

## 2. In scope
- CC-01–CC-13; six control domains and Control Action; Trigger/Decision/Transition combinations.
- 2026 baseline initial-state contract; 2027+ inheritance; year-by-year sequencing and Gate A/B/C applicability.
- Trigger determinability vs mandatory observation validity; stop scope; reason codes.
- Transition reservation scheduling, finality, evidence, and audit.
- R4 Ch4/Ch5 source precedence over Ch10, including explicitly stated major-shock exception, separate political Decision, and unresolved AND/OR rules.
- Individual comparison eligibility vs pairwise comparability; comparison publication hold.
- F3 policy vs future F3 Boundary namespace; append-only provenance and Freeze/DecisionLog separation.
- Regressions from v0.3 FRC, including IVV-01 through IVV-03 wording changes.

## 3. Out of scope
- Numerical coefficients, invented initial-state values or policy effects, and policy merits.
- Implementation APIs, machine-readable schema, full reason-code enum, new engine code, test execution, numeric V&V.
- M10/M14/M17/M18 calculation semantics; R4 metric/observation contract implementation.
- N3 2035 numeric freeze, KL-007/KL-008, R4→F3 special-switch design, post-switch wage/Gini anchors.
- Repository writes, commit, PR, canonical DecisionLog update, or formal Freeze.

## 4. Reviewer instructions (same for ChatGPT / Claude / Gemini / Grok)
1. Verify attachment identity by filename and full SHA-256. If byte-level verification is not available, explicitly state **digest not independently verified**; do not claim verification.
2. Read the complete Rev.2 attachment. Consult the reference traceability matrix and baseline Canonical documents only as supplied/verified; identify unavailable source evidence.
3. Evaluate normative consistency and coverage. For each finding, report ID, severity (Critical/Major/Minor/Editorial), exact CC section or passage, reproducible conflict/example, impact, and minimal proposed correction.
4. Explicitly test: `Trigger=met, Decision=not_required` transient vs settled Gate B; `not_evaluated` vs `unknown`; normal-year Gate B nonapplicability; 2026 initial state; reservation cancellation and reschedule; R4 shock exception; pairwise comparison hold; CC-04 year sequencing.
5. Check for unapproved new semantics beyond D25-01–D25-12; identify any requirement for fresh Owner adjudication.
6. Give one overall verdict: **Accepted / Revision Recommended / Rejected**, plus remaining blocking items and a finding-to-decision cross-reference.
7. Do not infer that prior adjudication equals closure of findings; closure requires verified text and review.

## 5. Independence and evidence
- Run four separate reviews, without sharing reviewers' outputs before their initial verdicts.
- Preserve each raw response unchanged with reviewer identity, submission/receipt timestamps, attachment name and claimed/verified digest, and any inability to inspect the attachment.
- Keep the Owner-confirmed SHA separate from the GitHub baseline commit SHA.
- Do not assert consensus until actual reviewer verdicts are received and Owner resolves divergences per `docs/Workflow.md`.
- Waivers, if necessary, are Owner-only and require recorded reasons.

## 6. Submission cover text (copy for each reviewer)
> SPE M19-25 independent re-review. Review the attached `M19_Control_Contract_v0.4_DRAFT_Rev2.md` against SHA-256 `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea` and the attached traceability matrix. Repository baseline SHA is `e2238922193107f204805d9f25d6ddd6f764eced`. Assess control-contract normative consistency and whether D25-01–D25-12 are reflected; use the review packet scope and exclusions. Report Accepted / Revision Recommended / Rejected with exact findings, severity, clause references, and minimal changes. Do not assume a SHA was independently checked unless you actually checked it. No GitHub writes or Freeze are authorized.

## 7. Required outputs and current gates
- Four independent raw reviews: **PENDING**.
- Cross-review consolidation and discrepancy adjudication: **PENDING**.
- Owner decision on any new normative changes: **PENDING**.
- Candidate freeze-readiness decision: **PENDING**.
- Canonical DecisionLog / GitHub update authorization: **NOT GRANTED**.
- Formal Freeze: **HOLD**.

## 8. Pre-submission checklist
- [x] Owner explicitly confirmed the Rev.2 digest as review target.
- [x] Local Rev.2 digest re-measured and matched.
- [x] Re-review scope, exclusions, expected verdict and source SHA stated.
- [ ] Original four-AI raw reviews and original v0.3 FRC bytes/digest independently reconciled.
- [ ] All four reviewers supplied the same immutable Rev.2 bytes and supporting documents.
- [ ] Four independent verdicts collected.
