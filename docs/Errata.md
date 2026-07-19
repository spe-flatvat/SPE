# Errata

**Version:** 0.3   
**Last Updated:** 2026-07-19

---

# Purpose

This document records factual corrections, documentation inconsistencies, and known documentation issues discovered during development.

Unlike **DecisionLog.md**, this document does **not** record design decisions. It records *what was incorrect*, *what was corrected*, and *where follow-up work remains*.

---

# Editorial Note

**ER-003 through ER-009 refer to the unpublished _Glossary v0.1_ draft.**

ER-010 documents the **Reconstruction Regression** that led to the formal adoption of the **Original SimulationSpecification_v5.md** as the canonical Frozen Baseline.

These items should be interpreted as **pre-release draft revision items**, not defects in released documentation.

Their inclusion is intended to preserve review history and improve traceability before public release.

---

# Status Legend

- **Open** — Issue identified, correction pending
- **Fixed** — Corrected in documentation
- **Won't Fix** — Intentional behavior
- **Superseded** — Replaced by newer implementation

---

# Errata

| ID | Document | Issue | Status |
|----|----------|-------|--------|
| **ER-001** | Simulation Specification v5 | R4 wage anchor incorrectly described as "inherits N3". Actual implementation uses R4 document's own downward-case wage index scaled from the 2026 baseline. | Open |
| **ER-002** | Simulation Specification v5 | Specification implied an economic linkage between GDP and wages. No such resource-allocation constraint is currently implemented. | Open |
| **ER-003** | Glossary v0.1 (Draft) | α definition was overly generic and did not reflect the model-specific implementation. | Open |
| **ER-004** | Glossary v0.1 (Draft) | φ definition should reference the implemented wage–birth elasticity rather than a generic demographic elasticity. | Open |
| **ER-005** | Glossary v0.1 (Draft) | Initial implementation version for α and φ should reference v2 rather than later revisions. | Open |
| **ER-006** | Glossary v0.1 (Draft) | Aging Drag should distinguish IPSS source data from implementation methodology. | Open |
| **ER-007** | Glossary v0.1 (Draft) | Noble Shift status and reference model description require clarification. | Open |
| **ER-008** | Glossary v0.1 (Draft) | Implemented TSUBAME/SUZUME model concepts and future SPE architecture should be separated into independent sections. | Open |
| **ER-009** | Glossary v0.1 (Draft) | Source tag definitions require explicit inclusion criteria for each category. | Open |
| **ER-010** | Discarding SimulationSpecification_v5_Reconstructed | Reconstruction regression risks identified. Original SimulationSpecification_v5.md adopted as the formal Frozen Baseline. | 2026-07-18 |

---

# Known Limitations

The following are **intentional limitations**, not documentation errors.

| ID | Limitation | Planned Phase |
|----|------------|---------------|
| **KL-001** | GDP–wage resource allocation coupling is not yet implemented. | Phase 2 |
| **KL-002** | α and φ sensitivity analysis deferred until Phase 2. | Phase 2 |
| **KL-003** | State Machine remains conceptual and is not yet implemented in the simulation engine. | Future |
| **KL-004** | Extended State Score remains under design. | Future |
| **KL-005** | Snapshot Confirmation criteria | Formal criteria for snapshot confirmation have not yet been defined. The operational definition of an Owner-confirmed snapshot will be specified in a future Workflow document. Until then, an Owner-confirmed snapshot is defined solely by explicit confirmation provided by the Project Owner during the review process. | 2026-07-18 |
| **KL-006** | URL Snapshot Caching | Snapshots retrieved via URL (including AI reviewer fetch tools) may be affected by caching at various points in the retrieval chain (e.g., browser cache, AI retrieval tools, or repository-side caching). Retrieved content may therefore differ from the Owner-confirmed review snapshot, even though the GitHub repository remains the Canonical Source. For review purposes, always use the Owner-confirmed snapshot rather than independently retrieved repository content. | 2026-07-19 |

---

# Maintenance Policy

- **DecisionLog.md** records **why** decisions were made.
- **Errata.md** records **what** required correction.
- A single topic may legitimately appear in both documents when a design decision results from correcting an identified issue.
- Draft review findings may be recorded here for traceability until the corresponding document reaches its first public release.
