# SPE M19-FR-CV-06｜差分固定・条項横断検証報告 DRAFT

**Status:** DRAFT / REVISE / NOT APPROVED / HOLD
**Date:** 2026-10-31
**Repository:** `spe-flatvat/SPE`
**Fixed source commit:** `a00c96252ee1260a909be8775511c420685b51d8`
**Source:** `reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md`
**Verified Git blob SHA:** `b254ac774f5def5b5807bc0a172e86bcc7e52e20` (Git blob SHA-1, NOT SHA-256)
**Input draft:** `SPE_M19_FR_CV_06_Normative_Amendment_and_Traceability_DRAFT_20261031.md`
**Input draft SHA-256 (local bytes):** `e750f613a7e6137553c2faaa0246258c200f094bbc312df837f19482aeac260d`
**Owner decisions:** CV05-N01=A; CV05-N02=B; CV05-N03=A.

## 1. Verification method and limitation

Fetched the exact source candidate by repository path and fixed commit through the connected GitHub interface. Compared P-01–P-04's quoted anchors and proposed normative text with source CC-02–05, CC-09, CC-11–12, Gate A/C/B, reason taxonomy, and invariant list. The source file's Git blob SHA was returned; independent full-source byte SHA-256 and machine-applicable unified patch have **NOT** been verified. Thus the source **revision is fixed**, but a **byte-verified patch is NOT fixed**. This report performs textual/static analysis only; no engine or 29-invariant tests were executed.

## 2. Anchor checks

| Proposal | Fixed-source anchor | Result |
|---|---|---|
| P-01 | CC-03 L119: `The controller MUST NOT invent priority among competing switches. Non-discretionary switch types require separately approved contracts.` | FOUND, context matches |
| P-02 | CC-04 L152: separate authorization and `other applicable approved requirements` | FOUND, context matches; replacement span must be delimited precisely |
| P-03 | CC-04 after L152; L138–142, L150 and L152 | FOUND, context matches |
| P-04 | CC-12 L403: destination, year, attributable Trigger and Decision evidence, competing reservations | FOUND, context matches |

Line numbers are from the fetched fixed source, not from a locally byte-reconstructed patch.

## 3. Cross-clause findings

### CV06-F01 — P-01 Decision applicability / scope (Minor; REVISE)

P-01 says `otherwise required attributable Decision`, which is directionally consistent with N01, CC-03 discretionary state table and CC-12. However, a future non-discretionary contract is described as a possible exception without a fully bounded prospective change mechanism. Avoid interpreting P-01 as imposing new Decision obligations on unrelated incumbent calculation or as automatically enabling an exception upon merely identifying an external contract. **Recommendation:** retain current Decision evidence requirements for dependent switch reservation/effectuation, and state that any later waiver requires a separate Owner-approved normative amendment reconciling CC-03/05/12.

### CV06-F02 — P-02 unspecified reference and precedence (Minor; REVISE)

P-02's traceability requirements follow N02, but `determine ... any asserted precedence from those approved sources` can be read as a new precedence-resolution algorithm. CC-03 forbids invented priority among competing switches; CC-10 has an R4-specific source precedence, not a general contract hierarchy. **Recommendation:** validate only an explicitly approved, applicable precedence rule; if absent or conflicting, fail closed for the dependent operation, without synthesizing hierarchy. Identify exact replacement boundaries before producing a patch.

### CV06-F03 — P-03 newly enumerated approval attributes (Minor; REVISE)

P-03 is consistent with N03's separation of 2026 initial-state validation from transition authorization and with CC-04/05. However, `authorized source and creator` might be a new approval attribute not expressly present in N03 or the fixed source. **Recommendation:** require an attributable authorization basis for candidate creation/use, destination, effective year and applicable checks; retain audit provenance but do not invent a new mandatory `creator` authorization schema without separate approval. Ensure no prohibition of otherwise authorized 2026 initialization or incumbent calculations.

### CV06-F04 — P-04 future exception versus present CC-12 MUST (Minor; REVISE)

CC-12 currently requires attributable Trigger and Decision evidence before scheduling. P-04 allows discussion of a future Decision exception; without specifying that such an exception requires future amendment of CC-12 itself, a reviewer could interpret it as silently weakening CC-12. **Recommendation:** state no present waiver exists; a future exception requires separate normative Owner approval **and explicit CC-12 amendment/reconciliation**, plus Gate B and reservation validation. Do not treat a prospective contract's existence alone as waiver.

### CV06-F05 — Source/patch byte verification (Evidence gap; STOP for formal dispatch)

Source Git blob SHA returned and anchors found. Independent source SHA-256, exact unified diff applied to a locally verified source, output SHA-256, and zero-context-drift check remain undone. The prior CV-06 document explicitly labels itself a proposal, not a machine-applicable patch. **Recommendation:** construct byte-exact patch after source materialization and verify both before claiming patch fixed or issuing review distribution.

## 4. Invariant and mechanism impact (static only)

| Source invariant(s) | Mechanism | Assessment |
|---|---|---|
| 2, 18, 19 | 2026 baseline and Gate A→C→B | P-03 preserves intended boundary, subject to F03 |
| 5, 6, 7 | Trigger/Decision and no invented priority | P-01/P-02/P-04 preserve direction, subject to F01/F02/F04 |
| 9, 22 | Observation validity and Decision request | No direct proposed waiver identified; runtime not tested |
| 11, 25 | Reservation lifecycle and Decision persistence | P-04 must not change reservation resolution; runtime not tested |
| 12 | Dependency-scoped failure | P-01/P-03 explicit; no global stop should be introduced |
| 17, 20 | Immutable audit and Gate B applicability | P-02/P-04 add traceability; no approved schema implied |
| 1, 3, 4, 8, 10, 13–16, 21, 23–24, 26–29 | Other invariants | No direct intended modification; NOT EXECUTED, NOT CERTIFIED |

CC-09 governance traceability and the explicit Freeze prerequisites remain unaffected in intent. Historical D25/O/GATE/COMP/R/6D original evidence and separate external approval contracts remain NOT VERIFIED. Prospective CV05 decisions do not retroactively authenticate them.

## 5. Recommended bounded repair instructions

1. P-01: tighten `otherwise required` to current approved switch/reservation requirements; any future Decision-free pathway must receive explicit separate normative approval and CC-12 reconciliation.
2. P-02: require immutable source/version/approval/applicability; reject inferred precedence, not create a general priority system.
3. P-03: remove or qualify the unapproved `authorized creator` field; preserve 2026 initial-state / transition distinction and dependency-scoped fail-closed.
4. P-04: distinguish existing CC-12 MUST from a **future** separately approved CC-12 amendment; do not allow current waiver.
5. Construct exact unified patch, independently hash source and patched output, and perform clause-level static checks; preserve any remaining evidence gaps.

These are review recommendations, **not approved normative amendments**. The four CV06 findings are local verification observations, **not** additions to the original 32 or new 8 formal independent-review Finding registers.

## 6. Disposition and STOP

**Overall: REVISE.** Textual anchor matching and cross-clause static review completed. Exact byte-level diff fixation, source SHA-256, patch application, tests, independent review, Owner acceptance, DecisionLog update, Finding Close and Freeze **NOT COMPLETED**. GitHub remains read-only; M19–25 and RP-023 HOLD. Next: repair P-01–P-04 as DRAFT, construct a reproducible exact patch, then rerun verification; do not dispatch to 4AI as a byte-fixed packet yet.
