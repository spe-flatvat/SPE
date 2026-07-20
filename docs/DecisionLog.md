# Decision Log

**Version:** v0.4

**Last Updated:** 2026-07-20

**Updated By:** RP-017

## Purpose

The Decision Log records **project-level architectural and modelling decisions** together with their rationale.

Its purpose is to preserve the reasoning behind accepted design choices and to prevent unnecessary reopening of settled discussions.

Documentation mistakes and factual corrections are **not** recorded here; they belong in **Errata.md**.

---

## Status Legend

| Status | Meaning |
|---------|---------|
| Accepted | Agreed and currently in effect. |
| Pending | Principle agreed, implementation details still under discussion. |
| Planned | Scheduled for a future phase. |
| Deferred | Explicitly postponed to a later phase. |

---

## Decisions

| ID | Status | Decision | Rationale | Phase |
|----|--------|----------|-----------|-------|
| **DL-001** | Approved | Adopt **SUZUME Model** as the canonical internal model name and apply the transition retrospectively to Canonical Documents only. | The GitHub repository remains the sole Canonical Source. Retrospective updates are limited to Canonical Documents, while Non-Canonical materials are preserved as historical artifacts. See detailed resolution below. | 0.5 |
| **DL-002** | Accepted | Remove the population target (85 million) as a hard evaluation constraint. | Since Specification v5, population is treated as a comparative indicator rather than a pass/fail criterion. | 0.5 |
| **DL-003** | Accepted | Fix **α = 0.35**. | Prevent unnecessary model instability. Reconsider only if Phase 2 demonstrates a concrete analytical need. | 0.5 |
| **DL-004** | Accepted | Fix **φ = 0.15**. | Same rationale as DL-003. Sensitivity analysis is intentionally deferred to Phase 2. | 0.5 |
| **DL-005** | Accepted | Use the **Noble Shift Anchor version** as the official comparison baseline. | Maintains compatibility with historical reports. Machine-calculated results remain available as a comparison reference because they indicate that the Anchor version may represent a slightly stricter scenario. | 0.5 |
| **DL-006** | Accepted | Treat the R4 Tax Leakage Resolution effect as a **reference scenario**, not the main comparison case. | Prevents self-favouring bias while preserving the hypothesis for future evaluation. | 0.5 |
| **DL-007** | Accepted | Introduce explicit Source Tags with documented classification rules. | Each tag shall include a one-line criterion defining when it applies. Current tag set: **[Document]**, **[User Design]**, **[Model Assumption]**, **[Co-design]**, **[Future Concept]**. | 0.5 |
| **DL-008** | Planned | Separate documentation into **Part A (Implemented Model)** and **Part B (Future SPE Architecture)**. | Prevent confusion between implemented simulation behaviour and future architectural concepts. | 0.5 |
| **DL-009** | Approved | Formal Freeze of Original SimulationSpecification_v5. | Original v5 is adopted as Frozen Baseline and Canonical Source. Reconstructed v5 is excluded/discarded due to Reconstruction Regression risks. | 1.0 |
| **DL-010** | Approved | Repository Governance & AI Review Policy. | Establish Authority, AI role, and Owner-confirmed snapshot requirements. | 1.0 |
| **DL-011** | Approved | Simulation Specification v5 → v6 Migration completed. | Records completion of RP-017 migration and separation of Migration (RP-017) from Authoring (RP-018). | 1.0 |

### DL-001: Model Name Transition (TSUBAME to SUZUME)

- **Status:** Approved
- **Date:** 2026-07-19
- **Resolution:**
  The transition from TSUBAME Model to SUZUME Model shall be applied retrospectively only to Canonical Documents (i.e., files maintained within the GitHub repository). Materials outside this repository—such as historical chat logs, private archives, or drafts—are classified as Non-Canonical. Mandatory updates do not apply to Non-Canonical materials, allowing them to retain their historical context.
- **Rationale:**
  The scope boundary is based on the governance principle established by DL-009 and DL-010:
  1. The GitHub repository (`main` branch) remains the sole Canonical Source.
  2. Repository consistency and integrity have priority over historical reconstruction.
  3. Non-Canonical materials are preserved as historical artifacts rather than governed specifications.
  4. Limiting retrospective updates to Canonical Documents minimizes potential copyright-related risk while ensuring that the current specifications remain coherent and consistent.

### Governance Principles (DL-010)
- AI reviews are valid only against an Owner-confirmed snapshot.
- Technical means do not imply authority to determine the canonical repository state.
- The Project Owner remains the sole authority for confirming the canonical repository state.

---

# Deferred (Phase 2)

| ID | Topic | Reason |
|----|-------|--------|
| **DF-001** | Sensitivity analysis of α and φ | Stable baseline takes priority during Phase 1. |
| **DF-002** | Population model recalibration | Requires additional demographic validation. |
| **DF-003** | GDP–Real Wage resource constraint | Future model enhancement after baseline validation. |
| **DF-004** | State Score implementation | Depends on completion of the SPE architecture. |
| **DF-005** | State Machine implementation | Depends on State Score and Engine Layer definitions. |

---

# Relationship to Other Governance Documents

| Document | Purpose |
|----------|---------|
| **Glossary.md** | Terminology and model definitions (Single Source of Truth). |
| **DecisionLog.md** | Records architectural and modelling decisions. |
| **Errata.md** | Records documentation errors and factual corrections. |

Together these documents form the project's **Governance Documents**.

---

# Maintenance Policy

- Decisions are recorded **only after consensus**.
- Documentation errors belong in **Errata.md**, not here.
- A single event may appear in both documents when a design decision requires a documentation correction.
- Deferred items are **intentional postponements**, not rejected ideas.

