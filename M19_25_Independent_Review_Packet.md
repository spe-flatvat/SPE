# SPE M19-25 — Independent Reviewer Instructions

## Authority and inputs
- Repository: `spe-flatvat/SPE`
- Owner-confirmed repository snapshot: `e2238922193107f204805d9f25d6ddd6f764eced`
- Owner-confirmed candidate: `M19_Control_Contract_v0.3_FRC.md`
- Candidate SHA-256: `f61f7df247b4aa3cca884379bd9fb0593df2f8d7fbc8fea9db452e7098951e2d`
- Supporting documents: `M19_24_Traceability.md`, `M19_24_Review_Request.md`
- Scope: normative control semantics CC-01–13; do not change numeric policy calibration or implementation.

## Request
Conduct an **independent** static review of the exact candidate document. Assess: consistency of six state/result domains; discretionary switch versus ordinary continuation; trigger/observation validity; Gate A/B/C; year boundary; nonanticipativity; dependency-scoped stops; comparison eligibility; reservation lifecycle and append-only audit; R4 trigger/decision separation; 2026 initialization; governance and freeze boundaries. Do not assume another reviewer's conclusions. Cite clause IDs and concrete counterexamples. Do not modify the document.

## Required response
1. Reviewer and review date.
2. Exact reviewed filename, SHA-256 and repository baseline; explicitly flag if not verified.
3. Verdict: `Accepted`, `Revision Recommended`, or `Rejected`.
4. Findings table: local ID, severity (Critical/Major/Minor/Editorial), clause, issue, concrete counterexample, minimum remedy.
5. Known non-blocking issues, exclusions, and any unresolved disagreement.
6. Whether the fixed candidate is acceptable for freeze **as written**, with rationale.

## Governance
Per `docs/Workflow.md`, no AI review outranks another; Owner resolves disagreements; unavailable reviewer may be waived only by Owner with reason recorded. This request does not authorize a waiver, modification, GitHub commit, or formal freeze.

## Reviewer isolation
Provide the contract and supporting docs first. Withhold `M19_25_ChatGPT_Review.md` and `M19_25_Findings_Register.md` until the independent report is finalized to reduce anchoring. Afterwards, use those documents for consolidation.
