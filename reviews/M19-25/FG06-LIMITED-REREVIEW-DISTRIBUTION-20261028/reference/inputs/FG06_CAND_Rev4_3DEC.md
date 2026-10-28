# SPE M19 Control Contract v0.4 — Owner-Adjudicated Revision DRAFT Rev.4 Candidate

- Document ID: `M19-CC-v0.4-DRAFT`
- Status: **DRAFT / NON-CANONICAL / NOT FROZEN / NOT REVIEW-ACCEPTED**
- Project: SPE (SUZUME PolicyCraft Engine)
- Repository: `spe-flatvat/SPE`
- Owner-confirmed repository review baseline (D22-01): `e2238922193107f204805d9f25d6ddd6f764eced`
- Source review candidate: `M19_Control_Contract_v0.3_FRC-1.md`, recovered from GitHub history at `0b27c2fe952ab05ea744c265e34f83f0e1ae01f5`; not currently on `main`.
- Historical review-candidate digest (reported, not independently reverified): `f61f7df247b4aa3cca884379bd9fb0593df2f8d7fbc8fea9db452e7098951e2d`
- Immediate source: `M19_Control_Contract_v0.4_DRAFT_Rev3.md`
- Authority basis: Owner adjudications D25-01–12, O-01–05, GATE-01, COMP-01, R-01–07, 6D27-01–02, and 6D38-01.
- Canonical DecisionLog correspondence: pending.
- Scope: annual simulation and conditional policy-transition control semantics, 2026–2055.
- Version note: `v0.4` and `Rev.4` are working labels, not approved version designations.

## 0. Status, precedence, definitions, and namespaces

This document is a candidate normative control contract, not an implemented engine, numerical model, or frozen canonical specification.

`MUST` denotes a mandatory requirement; `MUST NOT` a prohibition; `MAY` a permitted action only within an expressly authorized contract.

Approval of individual Owner adjudications does not imply approval of this consolidated wording. Review, revision, repository writing, DecisionLog modification, and Freeze remain separate acts.

GitHub `main` is the sole canonical repository source under `docs/Workflow.md`. The repository review baseline and exact bytes/digest of any separately authored draft MUST be independently confirmed before formal review. A moving branch reference is not an immutable contract reference.

A **path** is a complete simulation trajectory. A **branch** is a contingent continuation from shared history. A **segment** is a continuous interval governed by one policy contract.

A **transition reservation** is an immutable scheduling event with a unique ID and append-only lifecycle evidence, not a mutable authorization flag.

**Dependency scope** identifies operations actually dependent on a requirement. A **contract reference** identifies an immutable version or artifact-plus-digest.

**Namespace separation and F3 policy-source boundary (D25-01):**

`F3` denotes the Flat 3 Lines policy scenario. `policies/Flat3linesPolicies.md` is the currently identified candidate source for its substantive policy definition.

`F3 Boundary` denotes the distinct, unimplemented future architectural boundary concept described in `docs/Glossary.md`, Part B.

These concepts MUST remain typed or namespace-qualified, MUST NOT be equated, and MUST NOT silently rename or redefine the F3 policy set.

This Control Contract MUST NOT independently redefine or approve F3's substantive policy content, numerical coefficients, activation conditions, or policy effects.

Before a dependent operation uses an F3 policy definition, the applicable policy-source artifact, immutable version or digest, and required Owner approval status MUST be validated.

Identification and digest verification of a policy-source candidate MUST NOT, by themselves, establish its Owner approval status. Approval MUST be determined from applicable attributable governance evidence.

An absent, ambiguous, or unauthorized F3 policy-source reference MUST fail closed within the affected dependency scope. Independently valid operations MUST remain executable.

The machine-readable namespace syntax and policy-input mapping remain subject to separate approval.

## CC-01 — Responsibilities and authority

The controller MUST select explicitly defined policy paths, validate boundary conditions, determine execution and comparison dispositions, and emit attributable audit evidence.

It MUST NOT invent political approvals, economic coefficients, policy effects, observations, initial-state values, numerical anchors, or Trigger evaluation rules.

It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics.

Controller metadata MUST remain outside existing strict annual-result schemas unless separately authorized.

Policy-set identifiers and future architectural concepts MUST remain distinct.

## CC-02 — Six separate domains and Control Action

|Domain|Allowed values|Nature|
|---|---|---|
|Trigger|`not_evaluated`, `met`, `not_met`, `unknown`|State machine|
|Decision|`not_required`, `pending`, `approved`, `rejected`|State machine|
|Transition|`not_scheduled`, `scheduled`, `effective`|State machine|
|Contract|`valid`, `incomplete`, `invalid`|Validation result|
|Execution|`continue`, `stop_branch`, `stop_path`|Execution disposition|
|Comparison|`eligible`, `ineligible`, `not_assessed`|Comparison eligibility|

`not_evaluated` means evaluation has not occurred. `unknown` means evaluation occurred but logical truth could not be established under the approved rule. Neither is an alias for the other.

`not_required` means no currently effective Decision request; it does not establish that an unevaluated Trigger is false.

Immediately after `Trigger=met`, `Decision=not_required` MAY exist only transiently while a Decision request is created. It MUST NOT persist as a settled dependent Gate B state.

**Control Action** is a separate command classification, not a seventh domain. `HOLD_COMPARISON` is the sole currently approved Control Action. It MUST NOT substitute for or modify any of the six domain states.

Additional Control Actions require separate normative Owner approval.

The current validity of a reservation MUST be reconstructed from its original scheduling event and relevant ordered lifecycle-resolution events. A historical `scheduled` record alone does not establish a live reservation.
## CC-03 — Trigger, Decision, and transition authorization

For a discretionary policy switch, a transition candidate requires:

- `Trigger=met`;
- `Decision=approved`;
- an expressly authorized destination and effective year;
- no unresolved competing transition.

This combination does not itself authorize `Transition=effective`. CC-05 and CC-12 remain applicable.

The following table governs dependent discretionary-transition evaluation at the applicable checkpoint. Transient combinations MUST NOT be treated as settled Gate B outcomes.

|Trigger|Decision|Normative disposition|
|---|---|---|
|`not_evaluated`|`not_required`|No transition. Required but unperformed evaluation blocks the dependent operation with `STOP_TRIGGER_NOT_EVALUATED`.|
|`unknown`|`not_required`|No transition. Required indeterminate determination blocks the dependent branch with `STOP_TRIGGER_UNKNOWN`.|
|`not_met`|`not_required`|Continue independently valid incumbent policy; no discretionary switch.|
|`met`|`not_required`|Transient only while requesting Decision; MUST settle to `pending`, `approved`, or `rejected` before dependent Gate B completion. Persistent occurrence fails closed for the dependent switch.|
|`met`|`pending`|No switch; dependent branch stops or remains held pending an attributable Decision.|
|`met`|`approved`|Reservation candidate permitted after target, year, authority, evidence, and conflict validation.|
|`met`|`rejected`|Continue independently valid incumbent policy; record normal branch resolution such as `BRANCH_DECISION_REJECTED`.|
|Other combinations|Any|Invalid for the discretionary class unless an expressly approved transition contract authorizes them; fail closed within dependency scope.|

An invalid combination for dependent discretionary-transition authorization MUST NOT, by itself, invalidate, cancel, expire, or otherwise alter a separately authorized ongoing Decision process.

The validity and continuation of an existing pending Decision MUST be assessed independently from whether the current Trigger/Decision combination authorizes a transition.

Before a Trigger is due for evaluation, independent incumbent calculations MUST NOT require an unrelated settled discretionary-transition pair.

Trigger satisfaction MUST NOT imply political approval. Discretionary approval MUST be attributable to an authorized decision maker. Rejection MUST NOT be recorded as an execution error.

The controller MUST NOT invent priority among competing switches. Non-discretionary switch types require separately approved contracts.

**Multiyear pending Decision:** An attributable `Decision=pending` MAY persist across annual boundaries only within its expressly approved decision process, authority, scope, and validity conditions.

A subsequent Trigger result of `not_met` or `unknown`, or a subsequent Trigger status of `not_evaluated`, MUST NOT, by itself, automatically approve, reject, cancel, expire, or renew the existing pending Decision.

Historical Decision status and evidence MUST remain distinguishable from the current Trigger result and the Decision's current applicability.

At each checkpoint where dependent transition authorization is applicable, the controller MUST validate the Trigger requirements prescribed by the approved transition contract, the current applicability of the Decision, reservation validity where relevant, and all other applicable Gate requirements.

A historical pending Decision MUST NOT substitute for a currently satisfied Trigger or an attributable approved Decision.

Where an existing pending Decision remains valid as an ongoing decision process but current transition requirements are not satisfied, the dependent transition MUST fail closed within its dependency scope. Independently valid incumbent continuation MUST NOT be blocked solely by that failure.

This clarification does not authorize automatic Trigger re-review, Decision renewal, reservation renewal, or transition effectuation. Such actions require separate express authorization.

For the 2040 R4 review, explicit rejection means N3 continuation in 2041. Pending or indeterminate review stops the dependent branch. Automatic re-review requires separate authorization. Shock exceptions are governed by CC-10.
## CC-04 — Annual sequencing and the 2026 boundary

**Initialization:** Year 2026 MUST be validated under an Owner-approved Baseline Initial-State Contract, not a fictitious 2025 final-state record.

The contract MUST identify the baseline year, required variables, values, units, provenance, distinctions between document anchors and inferred values, and Owner approval ID.

Missing or contradictory required fields fail closed within dependency scope. Scenarios sharing a baseline MUST share identical approved 2026 initial-prefix data and immutable references.

This clause approves no numerical initial values.

**Continuation:** From 2027 onward, Gate A MUST validate the actual finalized preceding-year state and required history. A year MUST NOT silently inherit an unrelated policy baseline.

**Year-entry sequence:** For each year `t` in 2026–2055, the controller MUST evaluate Gate A, then Gate C, then Gate B where applicable.

Where a valid transition candidate targets `t`, Gate C MUST validate the candidate destination policy's target-year numerical contract against the actual authorized preceding-year state and applicable segment references.

Gate C validation MUST NOT itself authorize or effectuate the transition or finalize the candidate policy's calculation.

Gate B MUST subsequently validate applicable authorization and reservation evidence. The transition MAY become effective only after all applicable gates pass and before the authorized year-`t` calculation.

An independently valid incumbent continuation MUST NOT be blocked solely by an unrelated failed transition.

**Calculation attempts and finalization:** For each year `t`, where applicable entry gates pass and the execution context is independently authorized and executable, the engine MUST calculate and finalize the year-`t` state under its authorized effective policy.

This obligation is subject to expressly authorized dependency-scoped stop or failure-resolution pathways. It MUST NOT require fabrication of a result where valid calculation cannot be completed.

Calculation attempts MUST remain distinguishable from finalized annual results.

A repairable failed or incomplete attempt MAY be retried before successful formal year-end only within the approved input contract and with attributable audit evidence.

For a given execution/path/year context, there MUST be at most one finalized annual result and at most one successful formal year-end event.

A retry MUST NOT create a duplicate finalized result.

**Post-year decision boundary:** Following an authorized finalized annual result, the controller MUST validate required year-end observation contracts separately from Trigger truth, evaluate applicable Triggers, request and record required attributable Decisions, and append authorized reservation or resolution events.

Scheduling a future transition MUST NOT calculate a future year or make that transition effective.

Where calculation cannot be finalized, the controller MUST NOT fabricate observations, Trigger outcomes, or Decisions.

**Formal year-end:** The formal year-end operation MUST identify its authorized actor, authority, prerequisites, annual disposition, and applicable reservation-resolution evidence.

The authorized annual disposition and successful formal year-end event MUST be recorded atomically and idempotently for the same context.

A failed partial operation MUST NOT count as a successful formal year-end. Successful formal year-end MUST NOT be duplicated.

After successful formal year-end, further calculation retries and competing finalization actions for the same context are prohibited.

Formal year-end MUST NOT require every transition-dependent gate to pass where an expressly authorized no-effect, failure, or stop-resolution process applies.

Where an annual calculation cannot be finalized, formal year-end MAY occur only through such an expressly authorized resolution process.

**Abnormal year-end and subsequent numerical continuation (6D38-01):** A successful formal year-end event following an expressly authorized failure or stop resolution MUST NOT be represented as a finalized annual numerical result.

Such an event MUST NOT, by itself, satisfy the preceding-year finalized-state requirement of Gate A for year `t+1`.

Any subsequent dependent numerical continuation requires an expressly approved recovery or reinitialization contract with sufficient validated numerical state and provenance.

Approval of abnormal formal year-end MUST NOT be interpreted as approval of numerical recovery, reconstruction, or continuation.

This control contract does not itself authorize or define a recovery or reinitialization mechanism.

No Decision or transition may rewrite an earlier finalized annual result. Implementation optimizations MAY be used only while preserving observable sequencing, audit, and historical immutability.

The mechanisms for atomicity, idempotence, and recovery require separate implementation-contract approval.
## CC-05 — Independent boundary gates and failure scope

**Gate A — state/history:** In 2026, validate the Owner-approved Baseline Initial-State Contract. From 2027 onward, validate the actual finalized preceding-year state and required history.

**Gate C — numerical continuation:** Validate required numerical inputs, policy effects, approved segment anchors, coverage, units, provenance, and immutable numerical-contract references.

For a candidate transition, Gate C MUST validate the destination-policy contract before Gate B and before effectuation. Missing required values MUST NOT be silently defaulted.

**Gate B — authorization where applicable:** Validate the dependent Trigger, mandatory observation contract, attributable Decision authority and evidence, live reservation, destination, effective year, and competing-transition conflicts.

Gate B audit MUST separately identify applicability, whether the formal evaluation checkpoint was reached, and the evaluated result.

Where Gate A and Gate C pass, the formal Gate B checkpoint is reached, and Gate B is established as nonapplicable, the controller MUST record `NOT_APPLICABLE` with an attributable reason.

It MUST NOT record an artificial PASS or imply political approval.

Where the formal checkpoint was not reached, the evaluation status MUST remain `NOT_EVALUATED`. Nonapplicability MUST NOT be inferred solely from the absence of a result.

Where Gate B applies and is formally evaluated, the result MUST be PASS or FAIL with attributable evidence and dependency scope.

These classifications are audit attributes, not additional domain enum values.

All applicable gates MUST pass before the dependent calculation or transition becomes effective.

An invalid common required state or contract results in `stop_path` for affected continuations. An invalid branch-specific dependency results in `stop_branch` for that branch.

Independently valid operations MUST remain executable.

A missing output-only indicator need not stop unrelated GDP calculation but MUST block any evaluation or comparison requiring that indicator.

Mandatory observation-contract failure blocks dependent Gate B even when Trigger truth is logically determinable.

A failed mandatory observation contract also prohibits issuance of a new dependent formal Decision request based on that defective context.

Gate applicability, results, reasons, and dependency scope MUST be independently auditable. Ambiguous dependent authorization MUST fail closed without automatically stopping unrelated operations.

## CC-06 — No anticipation and segment isolation

A later contingent Decision MUST NOT change pre-branch states, derived indicators, or numerical-contract provenance.

Branches sharing a finalized prefix MUST preserve identical prefix data and immutable references.

Future contingent anchors MUST NOT enter interpolation for a pre-branch segment.

An ex-ante approved anchor applicable to an incumbent segment MAY be used only within that segment's approved contract.

Upon switching, a new anchor schedule MUST be expressly authorized and rebased on the actual preceding-year result.

Another scenario's baseline MUST NOT be silently substituted.

Gate C prevalidation of a candidate destination contract MUST NOT authorize premature effectuation, target-policy calculation, or historical rewriting.
## CC-07 — Execution stops and comparison holds

- `stop_path` / `STOP_PATH`: invalid common required state or contract prevents affected dependent continuations.
- `stop_branch` / `STOP_BRANCH`: unresolved or invalid branch-specific Trigger, Decision, reservation, observation, or numerical dependency.
- `HOLD_COMPARISON`: distinct Control Action associated with withholding formal comparison finalization/publication; not an Execution or Comparison state.

Stop scope MUST follow actual dependency boundaries. Unaffected operations MUST remain executable.

Stopped branches MUST NOT silently restart.

Missing required values MUST NOT become zero, prior-policy anchors, extrapolations, or interpolations without authorization.

Approved optional-field defaults in existing calculation contracts do not authorize defaults for different required policy fields.

Reasons, applicability, and dependencies MUST be recorded.

Mandatory withholding of unvalidated formal comparison output MUST NOT be confused with mandatory issuance of a `HOLD_COMPARISON` action.

A comparison hold does not invalidate otherwise valid completed individual calculations.

Natural-language references to holding a dependent branch MUST be resolved into an existing authorized Execution disposition and reason code, not a new domain value.

## CC-08 — Individual eligibility and pairwise comparability

A path's Comparison state is `not_assessed` until the designated comparison validation operation evaluates an expressly approved immutable comparison contract.

Only that operation MAY assign `eligible` following successful validation or `ineligible` following assessed failure.

Calculation completion or M18 endpoint evaluation MUST NOT imply eligibility.

Pairwise or multipath comparability is a separate comparison-operation-level determination, not a seventh domain or additional Comparison enum value.

The approved comparison contract MUST identify an immutable contract ID and version, evaluation period, metrics, units, baseline and initial-state compatibility, methodology, and required dependencies.

The comparison operation MUST validate the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, plus all expressly required contract conditions.

Each comparison result MUST have a distinct immutable result ID and attributable references to relevant annual calculations, M18 evaluations, and input contracts.

Before formal finalization or publication, the comparison operation MUST verify that the individual eligibility and mutual comparability determinations apply to the exact approved contract and dependency versions.

Changed dependencies MUST undergo explicit impact analysis. Affected determinations MUST be revalidated.

Where non-impact cannot be established, formal comparison finalization and publication MUST remain withheld.

Historical results MUST NOT be silently overwritten. Replacement determinations require new attributable records.

Comparison validation outcomes, publication dispositions, and withholding reasons MUST be audited whether or not `HOLD_COMPARISON` is issued.

Issuance of `HOLD_COMPARISON` is MAY. If issued, it MUST be audited under CC-09.

Issuance MUST NOT rewrite individual eligibility or invalidate otherwise valid calculations.

Independent calculations MAY continue where their own requirements remain satisfied.
## CC-09 — Three audit record classes, action audit, and immutability

1. **Annual Calculation Record:** Execution/path/record ID, year, policy-set namespace and segment, approved initial/prior-state reference, immutable input and numerical-contract references, calculation-attempt identity and disposition, output reference, finalized-result identity where applicable, formal year-end status, authorized actor and authority, prerequisites, retry linkage, and attributable failure or resolution evidence.

2. **Transition Decision Record:** Execution/path/record ID, year, Trigger observations and evaluation-contract version, mandatory observation-contract validity, attributable Decision authority and evidence, historical Decision identity and current applicability, destination/effective year, immutable reservation ID, creation/checkpoint validation evidence, linked lifecycle-resolution events, and applicable R4 source section or exception.

3. **Execution / Comparison Record:** Execution/path/record ID, year, dependency scope, Gate A/C/B sequence, Gate B applicability, formal evaluation status and result, Execution disposition, immutable comparison-contract ID/version, comparison-result ID where applicable, calculation and M18 references, individual Comparison state, mutual comparability outcome, dependency-impact analysis, revalidation disposition, publication disposition, withholding reason, issued Control Action if any, and applicable reason codes.

All references MUST resolve to immutable versions or digests.

Audit records MUST be append-only. Corrections require new linked records.

Reservation IDs MUST NOT be reused. Formal year-end recording MUST be atomic and idempotent for the same context.

Partial failed attempts MUST NOT count as successful year-end events.

Comparison validation outcomes and withholding reasons MUST be audited even when no `HOLD_COMPARISON` action is issued.

If issued, the action MUST identify its reason, target, related Comparison state, comparison-contract ID, and applicable result reference.

**Governance traceability:** Original Owner decisions, preserved reviewer responses, independently verified artifact hashes, secondary evidence, derived summaries, and unverified historical assertions MUST remain distinguishable.

A governance traceability entry MUST identify the decision reference, issue, selected option, normative effect, evidence type, source, established receipt or retrieval date, original timestamp verification status, and review status.

Before formal Freeze, adopted Owner decisions MUST be reconciled with applicable D22/D23/D24 predecessor decisions, the four independent review originals, individual finding dispositions, the final contract version and digest, and canonical DecisionLog correspondence.

Secondary evidence MAY support provisional reconstruction where original evidence is unavailable.

Missing or unverified originals MUST be identified by evidence status rather than treated as verified.

Acceptance of irretrievable secondary evidence for formal Freeze requires separate Owner adjudication.

Original reviewer responses MUST be preserved without silent normalization. Derived summaries MUST remain source-traceable.

DecisionLog updates, repository writes, finding closure, and formal Freeze require separate authorization.

These are normative reproducibility requirements, not claims of completed replay or V&V.
## CC-10 — R4 source precedence and shock exception

For `policies/Reboot4linesPolicies.md`, Chapter 4 is the canonical source for the 2040 activation-review Trigger.

Chapter 5 is the canonical source for exit/scale-down conditions and subsequent authorized decisions.

Chapter 10 is reference simulation material and MUST NOT silently override Chapters 4–5.

Contrary Chapter 10 numerical thresholds or combination rules are not operative without separate Owner approval.

Chapter 4 specifies a default review condition involving at least two distinct indicator clusters and permits consideration of one cluster plus a major external shock.

These are conditions for consideration, not automatic activation.

The approved rule's AND/OR structure MUST be explicit. The controller MUST NOT invent boolean structure, severity thresholds, shock-recognition criteria, or missing-observation semantics.

A shock alone MUST NOT automatically establish Trigger satisfaction, political Decision, or transition effectuation.

An exception MAY be evaluated only to the extent its recognition, evidence, and authorization are expressly approved.

Otherwise the dependent determination fails closed without stopping unrelated operations.

`not_evaluated` MUST remain distinct from evaluated but indeterminate `unknown`.

Activation, exit, extension, scale-down, and release requiring political authorization MUST record the attributable Decision and source clause.

Chapter 5's exit conditions MUST NOT be replaced by Chapter 10 reference values.

Where a machine-decidable condition remains undefined, the dependent transition MUST fail closed pending a separately approved contract.

R4→F3 special-switch terms remain unapproved.

N3 2035 numerical freeze criteria and post-switch wage/Gini anchors remain outside this draft's Freeze scope.

## CC-11 — Trigger determinability versus mandatory observation validity

`unknown` means Trigger truth cannot be determined from admissible evidence under the approved rule after evaluation.

`not_evaluated` means evaluation was not performed.

Missing observations do not necessarily imply `unknown` when the approved rule permits logical truth to be determined from remaining admissible evidence.

Logical determinability MUST NOT waive mandatory observation-contract requirements.

The controller MUST separately record Trigger truth/determinability, evaluation performed/not performed, and mandatory observation-contract validity.

A failed mandatory observation contract MUST block dependent Gate B even when Trigger truth is logically `met` or `not_met`.

Where mandatory observation validity is incomplete or invalid, the controller MUST NOT issue a new dependent formal Decision request or create a reservation based on that defective context.

Existing Decision records retain historical identity; further use remains subject to approved scope and checkpoint validation.

The controller MUST NOT fabricate a Decision or reinterpret Trigger truth to bypass missing observations.

Dependency-scoped stop behavior follows CC-05.
## CC-12 — Transition reservation lifecycle and finality

`Trigger=met` and `Decision=approved` do not automatically imply `Transition=effective`.

Before scheduling, the controller MUST validate the approved destination, effective year, attributable Trigger and Decision evidence, and competing reservations.

A valid candidate MUST receive a unique immutable reservation ID and append-only `scheduled` event.

At the applicable target-year checkpoint, current reservation validity MUST be reconstructed from scheduling and relevant ordered lifecycle-resolution events.

Effectuation requires a live reservation and successful applicable Gate A/C/B validation.

Cancellation, expiry, rejection, invalidation, or other formal resolution MUST be recorded by linked append-only events without adding Transition enum values.

A resolved reservation MUST NOT be resurrected or its ID reused.

A target-year Gate failure MUST be recorded but MUST NOT itself constitute formal year-end or automatically invalidate the underlying Decision.

A reservation that does not become effective MUST be explicitly resolved under the applicable authorized year-end process and MUST NOT silently persist as live in a later year.

Replacement reservation: A replacement reservation MUST receive a new immutable reservation ID and fresh reservation-specific attributable evidence.

Its authorization basis MAY refer to an existing approved Decision only within that Decision's expressly approved scope and validity.

The controller MUST revalidate the authorization basis, target, effective year, and competing-transition constraints when creating the replacement reservation and at the applicable Gate B checkpoint.

Reservation expiry MUST NOT by itself imply expiry of the underlying Decision.

An effective transition is historical fact and MUST NOT be retroactively rewritten.

Failure consequences MUST remain dependency-scoped.

## CC-13 — Authority to mark comparison eligible

Only the designated comparison validation operation, acting under an expressly approved immutable comparison contract, MAY assign individual "Comparison=eligible".

Validation MUST record contract ID/version, authority, outcome, relevant input and annual calculation references, and applicable M18 evaluation references.

No calculation engine or endpoint evaluator MAY infer eligibility from computation success.

A separate comparison operation MUST determine pairwise or multipath comparability under CC-08.

Formal comparison finalization and publication MUST NOT proceed without successful required validation.

Validation outcomes and withholding reasons MUST be audited even when no dedicated Control Action is issued.

`HOLD_COMPARISON` MAY be issued as a separately audited Control Action.

If issued, it MUST identify the comparison target, reason, related Comparison state, comparison-contract ID, and applicable result reference.

The MAY governing issuance MUST NOT permit publication of unvalidated comparisons or rewriting individual eligibility.

## Reason taxonomy and error separation

- "BRANCH_*": normal branch resolution, including `BRANCH_DECISION_REJECTED`.
- "STOP_*": dependency-scoped execution halt, including `STOP_TRIGGER_NOT_EVALUATED`, `STOP_TRIGGER_UNKNOWN`, "STOP_DECISION_PENDING", "STOP_TRANSITION_CONFLICT", and "STOP_NUMERIC_MISSING".
- "HOLD_*": formal comparison withholding reasons, including "HOLD_COMPARISON_NOT_ASSESSED" and "HOLD_COMPARISON_INELIGIBLE".

Reason codes are audit attributes, not Trigger states or Control Actions.

`not_evaluated` MUST NOT be silently recast as `unknown`.

The identifiers above are normative examples, not a complete machine-readable enumeration.

Exhaustive schemas and APIs require separate implementation-contract approval.

## Required invariant checks for future V&V

1. No same-year retroactive effects or historical output rewriting.
2. Approved 2026 initial-state contract; exact prior-year finalized state from 2027 onward.
3. Identical common scenario prefixes and provenance where required.
4. No contingent transition from `unknown` or `not_evaluated`.
5. "met/not_required" is transient; settled dependent Gate B requires attributable Decision.
6. No discretionary switch without "met/approved", valid reservation, target/year, and applicable Gate approvals.
7. No unresolved competing transitions or invented priority.
8. No unauthorized fallback for missing required numerical or observation data.
9. Trigger truth, evaluation execution, and mandatory observation validity remain distinct.
10. No anticipation across branches, segments, or anchors.
11. No resurrection or reuse of resolved reservation IDs.
12. Independently valid operations continue outside failed dependency scope.
13. Individual eligibility does not imply mutual comparability.
14. `HOLD_COMPARISON` is a separately audited Control Action, not a state rewrite.
15. R4 Chapter 4/5 precedence and shock exception do not create automatic activation.
16. `STOP_TRIGGER_NOT_EVALUATED` and `STOP_TRIGGER_UNKNOWN` remain distinguishable.
17. Immutable end-to-end provenance and governance traceability.
18. Gate A → Gate C → Gate B ordering.
19. Candidate destination numerical contract is prevalidated without premature effectuation.
20. Gate B applicability, checkpoint reachability, and evaluated result remain distinct.
21. Multiyear pending Decision does not automatically change status or renew authority.
22. Mandatory observation failure prohibits new dependent formal Decision requests.
23. Calculation attempts and unique finalized annual results remain distinct.
24. Formal year-end requires authorized actor, prerequisites, atomicity, and idempotence.
25. Reservation expiry does not automatically expire the underlying Decision.
26. Comparison contract/result IDs remain immutable and affected dependencies require revalidation.
27. Comparison withholding and its audit are mandatory; dedicated Control Action issuance is optional.
28. Abnormal formal year-end does not imply a finalized numerical result or satisfy the next year's Gate A.
29. Subsequent numerical recovery or reinitialization requires separately approved contract and validated provenance.

These are future V&V obligations, not executed or certified tests.

## Freeze boundary, exclusions, and governance HOLDs

Proposed control-semantics scope only: CC-01–CC-13, six domains, Control Action, initialization, gates, nonanticipativity, dependency-scoped stops, reservation lifecycle, R4 source precedence, comparison distinctions, audit requirements, and reason-code namespaces.

Not frozen / not authorized: Numerical coefficients and policy effects; approved 2026 baseline numerical contract itself; R4 metric implementation or shock-recognition thresholds; N3 2035 numerical freeze Trigger (KL-007); Noble nonregular-employment linkage (KL-008); R4→F3 special switch/VAT schedule; post-transition wage/Gini anchors; M10 adapter; M18 integration; machine-readable schemas and exhaustive reason-code list; five-policy 2026–2055 integrated run; actual V&V; formal comparison; architectural `F3 Boundary` implementation; and numerical recovery/reinitialization mechanism.

Approval or Freeze of this Control Contract MUST NOT constitute approval or Freeze of the F3 substantive policy definition or the architectural `F3 Boundary` implementation.

Any such approval requires a separately identified artifact, applicable evidence, and express Owner authorization.

Existing fiscal indicator "bonds" remains a funding-gap proxy, not verified actual bond issuance or primary-balance compliance (DL-012).

Review and Freeze acceptance: The Owner MUST independently confirm the exact candidate bytes/digest and review baseline.

Review MUST follow `docs/Workflow.md`, including the applicable four-AI review or documented Owner waiver.

Review findings and dispositions MUST be individually traceable.

Original decisions and reviewer responses MUST remain distinguishable from secondary evidence and summaries.

Acceptance of irretrievable secondary evidence for Freeze requires separate Owner adjudication.

Applicable review consensus or documented waiver, explicit Owner final resolution, and DecisionLog correspondence are prerequisites to formal Freeze.

Editorial repairs and static validation do not substitute for substantive re-review.

"FREEZE_READY" is not "FROZEN".

Canonical DecisionLog updates, repository writes, and formal Freeze each require separate explicit authorization.

## Editorial / evidence notes pending verification

- The historical FRC filename contains "v0.3_FRC-1"; aliases remain reference-only until approved.
- One canonical review-packet artifact should be identified; duplicates remain labeled rather than silently removed.
- The date "2026-10-24" associated with the Claude review is recorded from the D25-12 adjudication context. It MUST NOT be represented as an independently verified original receipt date. The review's self-reported document date and actual receipt date remain distinct and require reconciliation against original evidence before canonical logging.
- Grok's asserted review SHA and repository baseline MUST NOT be represented as independently verified without supporting evidence.
- This draft consolidates Owner-adjudicated directions but does not certify that every historical review original and source line has been independently reverified.
- The 18 Rev.2 re-review findings remain open until individually verified and formally resolved.
- The five Step 6D-35 integration-audit findings are separate from those 18 review findings.
- No GitHub publication, DecisionLog modification, implementation, formal finding closure, or Freeze is authorized by this draft.