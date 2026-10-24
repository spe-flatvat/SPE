# SPE M19 Control Contract v0.3 — Final Review Candidate

- Document ID: `M19-CC-v0.3-FRC`
- Status: **Final Review Candidate — NOT FROZEN**
- Project: SPE (SUZUME PolicyCraft Engine)
- Repository: `spe-flatvat/SPE`
- Owner-confirmed repository review baseline (D22-01): `e2238922193107f204805d9f25d6ddd6f764eced`
- Scope: control semantics for annual simulation and conditional policy transitions, 2026–2055
- Authority: design decisions approved in chat during M19-12, M19-18–M19-23; **not yet committed to the canonical repository**
- Revision: v0.3 FRC; full-document SHA-256 is recorded separately in the manifest

## 0. Status, precedence, and definitions

This document is a **candidate normative control contract**, not an implemented engine, a numerical model, or a frozen canonical specification. `MUST` is mandatory, `MUST NOT` is prohibited, and `MAY` is permitted only within an expressly authorized contract. The repository at the Owner-confirmed SHA is the baseline for repository-source review; this newly authored document must separately be confirmed as the review attachment by the Owner. Review, freeze, and repository write authorization are distinct actions.

A **path** is a full simulation trajectory; a **branch** is a contingent continuation from a common history; a **segment** is a continuous interval under one policy contract. A **transition reservation** is an immutable scheduling event with its own ID, not a mutable flag. **Dependency scope** is the set of paths/branches/outputs that actually require an invalid or missing input. A **contract reference** identifies an immutable content version or an immutable artifact plus digest; a moving `main` link alone is insufficient.

## CC-01 — Responsibilities and authority

The controller MUST select only explicitly defined policy paths, validate boundary conditions, determine execution/comparison dispositions, and emit auditable evidence. It MUST NOT invent political approvals, economic coefficients, policy effects, observations, or numerical anchors. It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics. Controller metadata MUST reside outside existing strict annual-result schemas unless separately approved.

## CC-02 — Six separate domains

| Domain | Allowed values | Nature |
|---|---|---|
| Trigger | `not_evaluated`, `met`, `not_met`, `unknown` | state machine |
| Decision | `not_required`, `pending`, `approved`, `rejected` | state machine |
| Transition | `not_scheduled`, `scheduled`, `effective` | state machine |
| Contract | `valid`, `incomplete`, `invalid` | validation result |
| Execution | `continue`, `stop_branch`, `stop_path` | execution disposition |
| Comparison | `eligible`, `ineligible`, `not_assessed` | comparison eligibility |

`not_required` means **no currently effective decision request**, not a declaration that an unevaluated Trigger is false. `HOLD_COMPARISON` is an output-control action, not a Comparison value. A `scheduled` historical record does not by itself prove that a reservation remains live; all later resolution records MUST be consulted.

## CC-03 — Trigger, Decision, and transition authorization

For a **discretionary** policy switch, the only authorized route to a transition candidate is `Trigger=met` AND `Decision=approved` AND an explicitly specified destination and effective year AND no unresolved competing transition. The following disposition matrix is normative for the discretionary transition class:

| Trigger | Decision | Disposition |
|---|---|---|
| `not_evaluated` | `not_required` | no transition; evaluation required before dependent switch |
| `unknown` | `not_required` | `stop_branch` if the branch depends on this determination |
| `not_met` | `not_required` | continue incumbent policy |
| `met` | `pending` | `stop_branch` pending authorized decision |
| `met` | `approved` | transition candidate; subject to all boundary gates |
| `met` | `rejected` | normal incumbent-policy continuation; record `BRANCH_*` reason |
| other inconsistent pairs | any | invalid contract/control combination; fail closed in dependency scope |

A discretionary approval MUST be attributable to the authorized decision maker; Trigger satisfaction alone MUST NOT imply approval. A rejection MUST NOT be recorded as an execution error. No controller-defined priority between competing switches is permitted. Any non-discretionary switch type requires a separately authorized contract, not implicit relaxation of this table.

For the 2040 R4 review: explicit rejection means N3 continuation in 2041; pending/indeterminate review stops the dependent branch; automatic re-review is prohibited without separate authorization.

## CC-04 — Annual sequencing and temporal boundary

For year `t`: (1) validate and compute the authorized year-t state, (2) validate year-end observations, (3) evaluate Trigger, (4) record the authorized discretionary Decision, (5) resolve a possible transition for `t+1`, (6) validate Gate A/B/C for that continuation, (7) apply an authorized effective policy for `t+1` and calculate it, (8) append audit records. The year-end observation-validation stage is separate from the next-year transition gates. No approval in year `t` can rewrite a previously finalized state of year `t` or earlier. Non-switching years still require validation of their required annual inputs.

## CC-05 — Independent boundary gates

- **Gate A — inherited state and history:** validate year-t final state and every required indicator/history reference for the next continuation.
- **Gate B — authorization:** validate Trigger and Decision evidence, authority, target, effective year, reservation status, and absence of unresolved conflicts.
- **Gate C — numerical continuation:** validate approved year-t+1 numerical inputs, effects, segment-specific anchors, their provenance and required coverage.

Every applicable gate MUST pass before the corresponding transition is made effective or the dependent year-t+1 calculation is run. Gate results MUST be independently auditable. Failure MUST be scoped by actual dependency, not by convenience. A missing output-only indicator need not stop unrelated GDP calculations, but MUST block an evaluation that requires that indicator.

## CC-06 — No anticipation and segment isolation

A later contingent Decision MUST NOT change pre-branch states, derived indicators, or numerical-contract provenance. Branches from the same finalized prefix MUST share the same prefix data and contract references. Future **contingent** anchors MUST NOT enter interpolation for a pre-branch segment. An ex-ante approved anchor applicable to an incumbent segment may be used only within that approved segment's contract. Upon switching, any new anchor schedule MUST be explicitly authorized and re-based on the actual preceding year-end result; no silent restart from an unrelated scenario's baseline is allowed.

## CC-07 — Execution stops and comparison holds

- `stop_path` (`STOP_PATH`): invalid common required state/contract prevents all dependent continuations.
- `stop_branch` (`STOP_BRANCH`): unresolved or invalid branch-specific Trigger, Decision, transition, or numerical dependency.
- `HOLD_COMPARISON`: formal comparison publication is withheld; this action is distinct from numerical execution and Comparison state.

Stop scope MUST follow dependency boundaries. Independent unaffected paths MUST remain executable. Stopped branches MUST NOT be silently restarted, and missing required values MUST NOT be silently substituted with zero, previous-policy anchors, extrapolation, or interpolation without authorization. An approved optional-field default in an existing calculation contract is not permission to default a different required policy field.

## CC-08 — Comparison eligibility

Comparison is `not_assessed` until an expressly approved comparison contract has been evaluated. It is `eligible` **only** after successful validation against that contract, and `ineligible` when assessed and failed. M18 endpoint output, completed annual computation, or an M18 metric alone MUST NOT grant `eligible`. `HOLD_COMPARISON` MUST prevent formal comparison publication when comparison is unassessed or ineligible; the action and its reason MUST be audited independently of the comparison status.

## CC-09 — Three audit record classes and immutability

1. **Annual Calculation Record:** execution/path/record ID, year, policy and segment, prior-result reference, input/numerical-contract version, output reference, and calculation disposition.
2. **Transition Decision Record:** execution/path/record ID, year, Trigger observations and evaluation-contract version, Decision authority/evidence, target/effective year, reservation ID and any resolution record.
3. **Execution / Comparison Record:** execution/path/record ID, year, dependency scope, gate results, execution disposition, comparison-contract version, eligibility status, action, and reason code.

Every reference MUST resolve to an immutable version or content digest. Audit entries MUST be append-only; correction uses a new linked record. A run MUST be traceable to the inputs, calculations, decisions, stop causes, and comparison decisions it actually used. This is a **normative reproducibility requirement**, not a claim of tested replay.

## CC-10 — R4 source precedence and exclusion boundary

For the R4 policy document, Chapter 4 governs the 2040 activation review, Chapter 5 governs the exit conditions, and Chapter 10 is reference simulation material that MUST NOT silently override Chapters 4–5. Chapter 4's cross-cluster trigger logic and major-shock exception require a separate authorized political Decision; no automatic activation is permitted. If necessary observations or their approved evaluation semantics are missing, the controller MUST apply CC-11 and CC-07 rather than invent values. R4→F3 special-switch terms are **not approved** by this contract. N3 2035 numeric freeze criteria and post-switch wage/Gini anchors remain outside this freeze scope.

## CC-11 — Trigger determinability versus observation-contract validity

`unknown` means the truth value of the Trigger cannot be determined from the available admissible evidence under the approved logical rule. A missing observation alone does not necessarily force `unknown` if the rule's truth is already logically determined. However, logical determinability MUST NOT waive a mandatory observation-contract requirement. The controller MUST record separately (a) Trigger truth/determinability and (b) observation-contract validity; an invalid mandatory observation contract MUST prevent dependent authorized transition even when a logical truth value can be deduced.

## CC-12 — Reservation finality

An expired, cancelled, rejected, or otherwise invalidated reservation MUST NOT be resurrected. Any later reservation MUST have a new reservation identifier and newly attributable Trigger/Decision/authorization evidence. The historical `scheduled` event remains append-only; a later resolution record controls current validity. An `effective` transition is historical fact and MUST NOT be retroactively edited.

## CC-13 — Authority to mark comparison eligible

Only the designated comparison validation operation, running against an expressly approved and immutable comparison contract, MAY assign `eligible`. The operation MUST record contract version, validation result, relevant input references, and authority. No calculation engine or endpoint evaluator MAY infer formal comparison eligibility from computation success alone.

## Reason taxonomy and error separation

- `BRANCH_*`: normal branch resolution, including explicit rejection (`BRANCH_DECISION_REJECTED`).
- `STOP_*`: execution halt with explicit path/branch scope, including unresolved Trigger (`STOP_TRIGGER_UNKNOWN`), pending Decision (`STOP_DECISION_PENDING`), transition conflict (`STOP_TRANSITION_CONFLICT`), or required numeric absence (`STOP_NUMERIC_MISSING`).
- `HOLD_*`: withheld formal comparison, including `HOLD_COMPARISON_NOT_ASSESSED` and `HOLD_COMPARISON_INELIGIBLE`.

These are **normative namespaces and illustrative identifiers**. Exhaustive machine-readable enumerations, field schemas, and transport APIs are deferred to implementation-contract approval. No unapproved code may alter the normative meaning.

## Required invariant checks for future V&V

1. No same-year retroactive effects.
2. No rewriting finalized historical outputs.
3. No contingent transition from `unknown` or `not_evaluated`.
4. No discretionary transition without explicit `approved` Decision.
5. No unresolved simultaneous competing transitions.
6. No automatic priority among transitions.
7. Exact previous-year-end state inheritance.
8. No implicit required-numeric fallback.
9. Nonanticipativity across branches and anchors.
10. No silent revival of stopped branches or invalidated reservations.
11. Calculation success does not imply comparison eligibility.
12. Immutable end-to-end provenance and audit links.
13. Separate logical Trigger determinability and mandatory observation-contract validity.

These are future test obligations, **not executed or certified tests**.

## Freeze boundary and known HOLDs

**Candidate to freeze:** CC-01–CC-13 normative semantics, six domains, gates, no-anticipation rules, stop/comparison semantics, audit classes and immutability, and reason namespaces.

**Not frozen / not authorized by this contract:** numerical coefficients and policy effects; R4 observation-metric implementation; N3 2035 freeze numeric trigger (KL-007); Noble nonregular employment linkage (KL-008); R4→F3 special switch and its VAT schedule; post-transition wage/Gini anchor schedules; M10 adapter; M18 integration; machine-readable schema and exhaustive code list; five-policy 2026–2055 integrated run; actual V&V and formal comparison. Existing fiscal indicator `bonds` is a model funding-gap proxy, not verified bond issuance or PB compliance (DL-012). Historical PB wording is not reinstated.

## Review and freeze acceptance

The Owner MUST confirm the **exact document bytes or digest** to be reviewed, separately from the repository baseline SHA. The review request MUST name scope, exclusions, expected verdict, baseline, attachment and version. Review must follow `docs/Workflow.md` including available multi-AI review or documented waiver, disposition of findings, and Owner resolution. `FREEZE_READY` is not `FROZEN`. Formal freeze and canonical repository commit each require separate explicit authorization. No GitHub writes, code changes, numerical execution, or tests are implied by this document.
