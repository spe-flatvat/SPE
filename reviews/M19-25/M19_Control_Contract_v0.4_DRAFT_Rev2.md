# SPE M19 Control Contract v0.4 — Owner-Adjudicated Revision DRAFT Rev.2

- Document ID: `M19-CC-v0.4-DRAFT`
- Status: **DRAFT / NON-CANONICAL / NOT FROZEN / NOT REVIEW-ACCEPTED**
- Project: SPE (SUZUME PolicyCraft Engine)
- Repository: `spe-flatvat/SPE`
- Owner-confirmed repository review baseline (D22-01): `e2238922193107f204805d9f25d6ddd6f764eced`
- Source review candidate: `M19_Control_Contract_v0.3_FRC-1.md`, recovered from GitHub history at `0b27c2fe952ab05ea744c265e34f83f0e1ae01f5`; the source candidate is **not currently on main**.
- Original review-candidate digest (reported in prior review context; not independently reverified here): `f61f7df247b4aa3cca884379bd9fb0593df2f8d7fbc8fea9db452e7098951e2d`
- Authority: Owner chat decisions D25-01 through D25-12; **these decisions have not been entered into the canonical DecisionLog**.
- Scope: control semantics for annual simulation and conditional policy transitions, 2026–2055.
- Version note: `v0.4` and `Rev.2` are **working draft labels**, not formally approved version designations.
- Revision scope: internal V&V IVV-01 through IVV-03 clarification only; no new Owner approval or numerical authority is claimed.

## 0. Status, precedence, definitions, and namespaces

This document is a **candidate normative control contract**, not an implemented engine, a numerical model, or a frozen canonical specification. `MUST` is mandatory, `MUST NOT` is prohibited, and `MAY` is permitted only within an expressly authorized contract. Owner approval of individual decisions does not imply approval of this consolidated wording. Review, revision, repository write authorization, and formal Freeze are distinct acts.

The GitHub `main` branch is the sole canonical repository source under `docs/Workflow.md`. The repository baseline SHA and the exact bytes/digest of this separately authored draft MUST each be confirmed for any formal review. A moving `main` link is not an immutable contract reference.

A **path** is a full simulation trajectory; a **branch** is a contingent continuation from a common history; a **segment** is a continuous interval under one policy contract. A **transition reservation** is an immutable scheduling event with its own ID, not a mutable flag. **Dependency scope** identifies the paths, branches, calculations, or outputs that actually depend on a missing or invalid requirement. A **contract reference** identifies an immutable version or artifact-plus-digest.

**Namespace separation (D25-01).** The policy-set identifier `F3` refers to the F3 policy scenario. `F3 Boundary` refers to the future architectural boundary concept in `docs/Glossary.md`, Part B. They MUST be typed or namespace-qualified in contracts and audit records, MUST NOT be equated, and MUST NOT silently rename the F3 policy set. A future architecture term MUST NOT be treated as an implemented policy transition merely because its text contains `F3`. The exact machine-readable namespace syntax is deferred to implementation-contract approval.

## CC-01 — Responsibilities and authority

The controller MUST select only explicitly defined policy paths, validate boundary conditions, determine execution/comparison dispositions, and emit auditable evidence. It MUST NOT invent political approvals, economic coefficients, policy effects, observations, initial-state values, numerical anchors, or Trigger evaluation rules. It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics. Controller metadata MUST reside outside existing strict annual-result schemas unless separately approved. It MUST preserve the distinction between policy-set identifiers and future architectural concepts.

## CC-02 — Six separate domains and Control Action

| Domain | Allowed values | Nature |
|---|---|---|
| Trigger | `not_evaluated`, `met`, `not_met`, `unknown` | state machine |
| Decision | `not_required`, `pending`, `approved`, `rejected` | state machine |
| Transition | `not_scheduled`, `scheduled`, `effective` | state machine |
| Contract | `valid`, `incomplete`, `invalid` | validation result |
| Execution | `continue`, `stop_branch`, `stop_path` | execution disposition |
| Comparison | `eligible`, `ineligible`, `not_assessed` | comparison eligibility |

`not_evaluated` means evaluation has not occurred; `unknown` means evaluation occurred but logical truth cannot be determined under the approved rule. Neither is an alias for the other. `not_required` means no currently effective Decision request; it is not a declaration that an unevaluated Trigger is false. Immediately after `Trigger=met`, `Decision=not_required` MAY exist only as a transient state pending the creation of a Decision request (D25-03); it MUST NOT persist as a settled Gate B state.

**Control Action** is a distinct command classification, **not a seventh domain** and not a state value of any of the six domains. The sole currently approved Control Action is `HOLD_COMPARISON`, which withholds finalization/publication of formal comparison output without modifying or substituting the Comparison state. Its issue reason, comparison target, related Comparison state, and comparison-contract ID MUST be audited. Additional Control Actions require separate normative Owner approval (D25-09).

A historical `scheduled` record does not prove a reservation remains live; all later resolution records MUST be consulted.

## CC-03 — Trigger, Decision, and transition authorization

For a **discretionary** policy switch, the only authorized route to a transition candidate is `Trigger=met` AND `Decision=approved` AND an explicitly authorized destination and effective year AND no unresolved competing transition. Even this combination does **not** itself authorize `Transition=effective`; CC-05 and CC-12 still apply.

The following table governs **dependent discretionary-transition evaluation at the applicable control checkpoint**. A row marked transient describes an intermediate event, not a permissible settled Gate B result. Before a Trigger is due for evaluation, ordinary incumbent-policy calculations do not require a settled discretionary-transition pair unless they depend on that determination. At the required checkpoint, any unlisted or unauthorized settled combination is invalid **unless an expressly approved transition contract authorizes it**; failures are confined to the actual dependency scope and MUST NOT halt unrelated normal continuation.

| Trigger | Decision | Normative disposition |
|---|---|---|
| `not_evaluated` | `not_required` | No transition; evaluate before a dependent switch; if evaluation is required but not performed, hold/stop the dependent operation with `STOP_TRIGGER_NOT_EVALUATED`. |
| `unknown` | `not_required` | No transition; stop the dependent branch where the determination is required, using `STOP_TRIGGER_UNKNOWN`. |
| `not_met` | `not_required` | Continue incumbent policy; no discretionary switch. |
| `met` | `not_required` | **Transient only** while requesting Decision; no switch; MUST settle to `pending`, `approved`, or `rejected` before Gate B completion. Persistent occurrence fails closed for the dependent switch. |
| `met` | `pending` | No switch; stop/hold dependent branch pending an attributable Decision. |
| `met` | `approved` | Eligible to create a transition reservation candidate after target, year, authority, evidence, and conflict validation; not automatically effective. |
| `met` | `rejected` | Continue incumbent policy; record a normal branch resolution such as `BRANCH_DECISION_REJECTED`. |
| Any other combination | Any | Invalid/inconsistent for the discretionary class; fail closed within the dependency scope, with an explicit reason and audit record. |

A discretionary approval MUST be attributable to the authorized decision maker; Trigger satisfaction alone MUST NOT imply approval. A rejection MUST NOT be recorded as an execution error. No controller-defined priority between competing switches is permitted. A non-discretionary switch type requires a separately approved contract rather than implicit relaxation of this table. Independent non-switching calculations MUST continue when their own applicable requirements are satisfied.

For the 2040 R4 review, explicit rejection means N3 continuation in 2041; pending/indeterminate review stops the dependent branch; automatic re-review is prohibited without separate authorization. R4 shock exceptions are governed by CC-10 and are not automatic approvals.

## CC-04 — Annual sequencing and the 2026 boundary

**Initialization:** The year **2026** is validated under an **Owner-approved Baseline Initial-State Contract**, not a fictitious 2025 final-state record. The contract MUST identify the baseline year, required variables, values, units, provenance, distinctions between document anchors and inferred values, and Owner approval ID. Missing or contradictory required fields fail closed within their dependency scope. Scenarios sharing an initial baseline MUST share the identical approved 2026 initial prefix and immutable references. This clause does not itself approve any numerical initial values.

**Continuation:** For **2027 onward**, Gate A validates the actual finalized preceding-year state and required history. No year may silently inherit an unrelated policy's baseline.

**Single-year execution boundary:** For each year `t` in 2026–2055, the engine MUST calculate and finalize the year-`t` state **exactly once** under its authorized effective policy. Before that calculation, it MUST (1) validate Gate A against the approved 2026 initial-state contract or, for 2027+, the finalized `t-1` state/history; (2) validate Gate C for year `t`; and (3) validate Gate B **only where a dependent authorization or transition applies at the year-`t` boundary**, including any live reservation scheduled in an earlier year. Any transition into `t` becomes `effective` only after its applicable gates pass, and before calculating `t`. An unrelated normal continuation does not acquire a Gate B political-approval requirement.

**Post-year decision boundary:** After finalizing year `t`, the controller MUST (4) validate required year-end observation contracts separately from Trigger truth; (5) evaluate applicable Triggers; (6) request and record any required attributable Decision; and (7) append any authorized reservation or resolution event for a possible future effective year (including `t+1`). Such scheduling MUST NOT itself calculate `t+1` or make its transition effective. At the next annual iteration, the applicable gates and live reservation are rechecked at that year's entry boundary before the one permitted calculation. Annual calculation records and transition/decision records MUST be append-only and linked to their actual events; audit persistence MUST NOT imply a second annual calculation. Implementations MAY optimize execution only while preserving these observable boundaries and audit semantics.

No Decision or transition in year `t` can rewrite finalized states of year `t` or earlier. A non-switching year does not require unrelated political approval but still requires its own applicable annual state and numerical validations.

## CC-05 — Independent boundary gates and failure scope

- **Gate A — state/history:** In 2026, validate the Owner-approved Baseline Initial-State Contract; in 2027 onward, validate the actual prior-year final state and required indicator/history references.
- **Gate B — authorization (only where applicable):** Validate the dependent Trigger, mandatory observation contract, Decision authority/evidence, transition reservation status, target, effective year, and competing-transition conflicts. **Normal continuation without a dependent discretionary switch MUST NOT be blocked for lacking unrelated Decision approval.** A nonapplicable Gate B MUST be logged as nonapplicable with reason, not fabricated as a passing authorization.
- **Gate C — numerical continuation:** Validate required numerical inputs, policy effects, approved segment anchors, coverage, units, provenance, and applicable numerical-contract references. No missing required value may be silently defaulted.

All applicable gates MUST pass before the dependent calculation or transition becomes effective. Gate results, nonapplicability, failures, reason codes, and dependency scope MUST be independently auditable. An invalid common required state/contract results in `stop_path` for all affected continuations; an invalid branch-specific dependency results in `stop_branch` for that branch. Nondependent calculations/outputs continue if independently valid. A missing output-only indicator need not stop unrelated GDP calculation but MUST block any evaluation or comparison requiring that indicator. Mandatory observation failure blocks the dependent Gate B even if the Trigger truth is logically determinable (CC-11).

## CC-06 — No anticipation and segment isolation

A later contingent Decision MUST NOT change pre-branch states, derived indicators, or numerical-contract provenance. Branches from the same finalized prefix MUST share the same prefix data and immutable contract references. Future contingent anchors MUST NOT enter interpolation for a pre-branch segment. An ex-ante approved anchor applicable to an incumbent segment MAY be used only within that approved segment's contract. Upon switching, a new anchor schedule MUST be expressly authorized and rebased on the actual preceding year-end result; no silent restart from another scenario's baseline is allowed.

## CC-07 — Execution stops and comparison holds

- `stop_path` (`STOP_PATH`): invalid common required state/contract prevents all dependent continuations.
- `stop_branch` (`STOP_BRANCH`): unresolved or invalid branch-specific Trigger, Decision, transition, observation, or numerical dependency.
- `HOLD_COMPARISON`: independent Control Action withholding formal comparison finalization/publication; **not** an Execution or Comparison state.

Stop scope MUST follow actual dependency boundaries. Independent unaffected paths MUST remain executable. Stopped branches MUST NOT silently restart; missing required values MUST NOT silently become zero, prior-policy anchors, extrapolation, or interpolation without authorization. Approved optional-field defaults in existing calculation contracts do not permit defaults for different required policy fields. Reasons and gate applicability MUST be recorded. A comparison hold does not invalidate completed individual calculations.

## CC-08 — Individual eligibility and pairwise comparability

A path's Comparison state is `not_assessed` until an expressly approved comparison contract is evaluated. It is `eligible` **only** after successful validation by the designated comparison validation operation, and `ineligible` if assessed and failed. Calculation completion or M18 endpoint evaluation MUST NOT grant eligibility by implication.

**Pairwise or multipath comparability is a separate comparison-operation-level check, not a seventh Comparison state and not a new value of the existing Comparison enum.** Individual `eligible` states do not guarantee that two paths may be compared. The comparison operation MUST validate the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, plus all expressly required contract conditions. If the comparison contract is unapproved, unassessed, or failed, formal comparison finalization/publication MUST be withheld. Where an explicit comparison-output hold is issued, `HOLD_COMPARISON` is the approved Control Action and MUST be audited under CC-09; withholding publication is mandatory regardless of whether an action record is needed for a particular workflow. The comparison operation and its result MUST be audited separately from individual path eligibility. Independent calculations remain valid and may continue.

## CC-09 — Three audit record classes, action audit, and immutability

1. **Annual Calculation Record:** execution/path/record ID, year, policy-set namespace and segment, initial/prior-result reference, input/numerical-contract version, output reference, and calculation disposition.
2. **Transition Decision Record:** execution/path/record ID, year, Trigger observations and evaluation-contract version, separate observation-contract validity, Decision authority/evidence, target/effective year, reservation ID, linked resolution events, and R4 source section/exception where relevant.
3. **Execution / Comparison Record:** execution/path/record ID, year, dependency scope, applicable/nonapplicable Gate results and reasons, Execution disposition, comparison-contract version, individual Comparison state, comparison-operation validation result, Control Action (if any), and reason codes.

All references MUST resolve to immutable versions/digests. Audit entries MUST be append-only; corrections use new linked records. Reservation lifecycle events MUST preserve the original reservation ID without reuse, and any new reservation MUST use a new ID. `HOLD_COMPARISON` MUST record the action reason, comparison target, related Comparison state, and comparison-contract ID. A run MUST be traceable to actual inputs, calculations, approvals, stop causes, and comparison determinations. This is a normative reproducibility requirement, **not** a claim of tested replay.

**Governance traceability (D25-11/D25-12):** Before formal Freeze, the adopted Owner decisions, their references to D22/D23/D24 decisions, the four independent review originals, finding dispositions, final contract version/digest, and DecisionLog correspondence MUST be checked. The canonical DecisionLog is updated **only under separate explicit write authorization**. Review-original date labels and receipt dates MUST remain distinct; unverified reviewer claims of baseline or digest verification MUST be marked as such. No editorial normalization may silently change control semantics.

## CC-10 — R4 source precedence and shock exception

For `policies/Reboot4linesPolicies.md`, **Chapter 4** is the canonical source for the 2040 activation-review Trigger; **Chapter 5** is the canonical source for exit/scale-down conditions and subsequent authorized decisions; **Chapter 10** is reference simulation material and MUST NOT silently override Chapters 4–5. Any contrary Chapter 10 numerical threshold or combination rule is not an operative control rule absent separate Owner approval.

Chapter 4 specifies a default review condition involving **at least two distinct indicator clusters** under its approved wording, and explicitly permits consideration of **one cluster plus a major external shock**. These are *conditions for consideration*, not automatic policy activation. The approved rule's AND/OR structure MUST be explicit; the controller MUST NOT infer additional boolean structure, severity thresholds, shock recognition criteria, or missing observation semantics. A shock alone MUST NOT automatically satisfy Trigger, produce political Decision, or effect a switch. An exception may be evaluated only to the extent its recognition, evidence, and authorization are explicitly approved; otherwise the dependent determination fails closed without affecting unrelated calculations.

Any activation, exit, extension, scale-down, or release requiring political authorization MUST record the relevant attributable Decision and source clause; no silent auto-Decision or auto-switch is permitted. Chapter 5's exit conditions and approvals MUST NOT be replaced with Chapter 10's reference values. Where the text leaves a needed machine-decidable condition undefined, the dependent transition MUST fail closed pending a separately approved contract; the controller MUST NOT invent one.

R4→F3 special-switch terms are **not approved** by this contract. N3 2035 numeric freeze criteria and post-switch wage/Gini anchors remain outside this draft's freeze scope.

## CC-11 — Trigger determinability versus mandatory observation validity

`unknown` means the logical truth of a Trigger cannot be determined from admissible evidence under the approved rule **after evaluation**. `not_evaluated` means the evaluation was not performed. Missing observations do not necessarily imply `unknown` when the rule's truth can be determined from the remaining admissible evidence. Logical determinability MUST NOT waive a mandatory observation-contract requirement. The controller MUST record separately (a) Trigger truth/determinability, (b) evaluation performed/not performed, and (c) mandatory observation-contract validity. A failed mandatory observation contract MUST block the dependent Gate B even when Trigger is logically `met` or `not_met`. The controller MUST NOT fabricate a Decision or reinterpret Trigger merely to bypass a missing observation. Dependency-scoped stop behavior follows CC-05.

## CC-12 — Transition reservation lifecycle and finality

`Trigger=met` and `Decision=approved` do **not** automatically imply `Transition=effective`. Before scheduling, the controller MUST validate the approved destination, effective year, attributable Trigger and Decision evidence, and competing reservations. A valid candidate generates a **unique immutable reservation ID** and an append-only `scheduled` event. A reservation may become `effective` only at the approved target year after all applicable Gate A/B/C checks and reservation integrity checks succeed.

Cancellation, expiry, rejection, or invalidation MUST be recorded by linked append-only resolution events; they MUST NOT overwrite the historical `scheduled` record or add unapproved cancellation/expiry values to the Transition enum. Such a reservation MUST NOT be resurrected or its ID reused. Rescheduling requires a **new** reservation ID and newly attributable authorization evidence. The controller MUST validate the reservation-to-Trigger/Decision/target-year/gate linkage before effectuation. An `effective` transition is historical fact and MUST NOT be retroactively edited. Failure stops only dependent execution as specified in CC-05.

## CC-13 — Authority to mark comparison eligible

Only the designated comparison validation operation, against an expressly approved immutable comparison contract, MAY assign individual `eligible`. It MUST record contract version, validation outcome, relevant input references, and authority. No calculation engine or endpoint evaluator MAY infer formal eligibility from computation success. A separate comparison operation MUST decide whether eligible paths are actually mutually comparable under CC-08. Formal comparison publication MUST NOT proceed without the required successful comparison-operation validation under CC-08. `HOLD_COMPARISON` MAY be issued as the separately audited Control Action to enforce that prohibition; its issuance MUST NOT rewrite individual eligibility. This MAY governs issuance of an action record, **not** permission to publish an unvalidated comparison.

## Reason taxonomy and error separation

- `BRANCH_*`: normal branch resolution, including explicit rejection (`BRANCH_DECISION_REJECTED`).
- `STOP_*`: dependency-scoped execution halt, including **required-but-unperformed Trigger evaluation** (`STOP_TRIGGER_NOT_EVALUATED`), **evaluated but indeterminate Trigger** (`STOP_TRIGGER_UNKNOWN`), pending Decision (`STOP_DECISION_PENDING`), transition conflict (`STOP_TRANSITION_CONFLICT`), or required numeric absence (`STOP_NUMERIC_MISSING`).
- `HOLD_*`: withheld formal comparison, including `HOLD_COMPARISON_NOT_ASSESSED` and `HOLD_COMPARISON_INELIGIBLE`.

A reason code is an audit attribute, not a Trigger state or Control Action. `not_evaluated` MUST NOT be automatically recast as `unknown`. Namespaces and identifiers above are normative **examples**, not a complete machine-readable enumeration. Exhaustive schemas and APIs require separate implementation-contract approval.

## Required invariant checks for future V&V

1. No same-year retroactive effects or historical output rewriting.
2. 2026 uses an approved initial-state contract; 2027+ inherits exact prior-year final state.
3. Common scenario prefixes and provenance are identical where required.
4. No contingent transition from `unknown` or `not_evaluated`.
5. `met/not_required` is transient only; settled dependent Gate B requires an attributable Decision state.
6. No discretionary switch without `met/approved`, valid reservation, target/year, and applicable Gate approvals.
7. No unresolved simultaneous competing transitions or invented priority.
8. No missing required numerical or mandatory observation fallback.
9. Trigger logical truth is separate from observation-contract validity and evaluation-execution status.
10. No anticipation across branches, segments, or anchors.
11. No resurrection/reuse of invalidated reservations; lifecycle audit remains append-only.
12. Nondependent paths and calculations continue when independently valid.
13. Individual comparison eligibility does not imply pairwise comparability.
14. `HOLD_COMPARISON` is a separately audited action, not a state rewrite.
15. R4 Ch4/Ch5 source precedence and explicit shock exception are preserved without auto-switch.
16. `STOP_TRIGGER_NOT_EVALUATED` and `STOP_TRIGGER_UNKNOWN` remain distinguishable.
17. Immutable end-to-end provenance, review dispositions, and Owner decisions remain traceable.

These are **future test obligations**, not executed or certified tests.

## Freeze boundary, exclusions, and governance HOLDs

**Proposed control-semantics scope only:** CC-01–CC-13, six domains, Control Action, 2026 initialization boundary, gates, nonanticipativity, dependency-scoped stops, reservation lifecycle, R4 source precedence, individual/pairwise comparison distinction, audit requirements, and reason-code namespaces.

**Not frozen / not authorized:** numerical coefficients or policy effects; approved 2026 baseline numerical contract itself; R4 observation-metric implementation or shock-recognition thresholds; N3 2035 numeric freeze trigger (KL-007); Noble nonregular-employment linkage (KL-008); R4→F3 special switch/VAT schedule; post-transition wage/Gini anchors; M10 adapter; M18 integration; machine-readable schema and exhaustive reason-code list; five-policy 2026–2055 integrated run; actual V&V; formal comparison; future architectural `F3 Boundary` implementation. Existing fiscal indicator `bonds` is a model funding-gap proxy, not verified bond issuance or PB compliance (DL-012).

**Review and Freeze acceptance:** The Owner MUST confirm the exact draft bytes/digest and review baseline independently. Four-AI review must follow `docs/Workflow.md` or an Owner-documented waiver, with findings and dispositions recorded. A review consensus and explicit Owner final resolution are prerequisites to a formal Freeze decision. Editorial repairs cannot substitute for substantive re-review. `FREEZE_READY` is not `FROZEN`. Canonical DecisionLog changes, GitHub writes, and formal Freeze each require separate explicit authorization.

## Editorial / evidence notes pending verification

- The historical FRC filename contains `v0.3_FRC-1`; any dotted/underscored aliases are reference-only until a canonical filename is separately approved.
- One canonical review-packet artifact should be identified; duplicates are preserved as labeled copies, not silently removed.
- Claude review's self-reported document date must be distinguished from the actual receipt date. The date `2026-10-24` is taken from the D25-12 adjudication context and requires reconciliation with original receipt evidence before canonical logging.
- Grok's asserted review SHA and repository baseline were not independently verified as part of the original review; do not mislabel them as verified.
- This draft is a consolidation of Owner-adjudicated directions; it is **not** a certification that all four review originals and every source line have been rechecked against their raw artifacts.
