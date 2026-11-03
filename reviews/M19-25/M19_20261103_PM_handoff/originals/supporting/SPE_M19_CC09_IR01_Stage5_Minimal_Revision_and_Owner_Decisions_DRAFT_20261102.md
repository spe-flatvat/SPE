# SPE M19-CC09-IR-01｜工程5 限定修文再調整・Owner裁定必要事項 DRAFT

**Status:** DRAFT / NON-CANONICAL / READ-ONLY ANALYSIS / OWNER DECISION PENDING  
**Date:** 2026-11-02  
**Repository:** `spe-flatvat/SPE`  
**Preservation commit:** `049f47309df8d4c09610a1ce47f68bdfc71f35f2`  
**Rev.2 baseline:** `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`  
**Integrated amendment:** `edc47652f986b75341404154bfd3057da89e9329`  
**Inputs:** Stage 3 Limited Amendment DRAFT; Stage 4 Delta/Side-Effect Review DRAFT; the Rev.2 CC-09 and integrated-draft CC-01/03/04/05/08/09/10/12 excerpts reviewed in this workstream.  
**Authority:** Analysis and new DRAFT only; no Owner decision, GitHub write, DecisionLog edit, Finding Close, Freeze or HOLD release.

## 1. Scope and decision principle

SPE is a simulation tool. **Calculation reproducibility and correctness of execution-state interpretation** are the priority. This does not mean all other existing requirements are deleted: applicable authorizations, Gate checks, comparison eligibility and reservation lifecycle requirements remain in force until separately amended. It does mean that historical political/governance evidence collection must not be treated as an automatic dependency of every simulation execution.

Distinguish:

1. **Normative/model references:** immutable engine, policy-source, numerical, initial-state and comparison definitions relevant to the operation.
2. **Run inputs:** user-specified values and scenario choices, which should be identified with their results; a new normative contract or Owner approval for each run is **not inferred**.
3. **Execution records:** attempt/result IDs, success/failure, applied version refs and relevant transition/comparison disposition.
4. **Governance evidence:** applicable approval/authority where actually required, distinct from exhaustive historical chat and review reauthentication.

The existing draft has not yet been shown to define a separate exploratory-Player execution mode. This Stage 5 DRAFT **does not authorize one**, reinterpret formal R4 transition requirements, or add an Owner=Player identity rule. Owner/Player separation and exploratory simulation are deferred design topics for v7+ unless an actual blocker to the initial simulation run is demonstrated.

## 2. P-01–P-06 disposition

| Proposal | Stage 5 disposition | Minimal action | Owner decision now? |
|---|---|---|---|
| P-01 CC-09 receipt placement | **OWNER DECISION** | Keep CC-09 Reserved/Deleted. Move the existing three provisional-receipt paragraphs **verbatim** only if the appendix's normative effect and Freeze boundary are explicitly settled; otherwise retain current placement as interim DRAFT, without implying that the old CC-09 has been restored. | **Yes**, if moving or changing Freeze scope. |
| P-02 correction records | **REVISE (narrow)** | Do **not** reintroduce global CC-09 append-only audit obligations. Require only that an actual correction to a result or execution record relied on for reproduction does not silently replace the previous authoritative value, and that the effective corrected result is identifiable. First verify whether existing immutable IDs/versioned result references already guarantee this; avoid a new universal MUST if they do. | **Conditional**, if a substantive new MUST remains. |
| P-03 Trigger evaluation versions | **KEEP existing / conditional REVISE** | Retain current Trigger evaluation and observation-validity requirements. For a Trigger used to justify an actual transition, confirm that its applicable evaluation rule/observation specification can be identified from existing immutable references. Do not require new per-run Owner approval or original review-history recovery. | **Conditional**, only if a missing binding requires a new normative obligation. |
| P-04 retry linkage | **KEEP existing / conditional REVISE** | Attempt ID, disposition, input-contract ref and formal-result identity are the minimum operational focus. A dedicated `retry_of` field is **not inherently required** if existing execution/path/year and attempt identities unambiguously establish the adopted result and distinguish failed attempts. | **Conditional**, only if unresolvable ambiguity is demonstrated and new MUST proposed. |
| P-05 comparison revalidation | **KEEP existing / conditional REVISE** | Preserve CC-08 comparison-contract ID/version, relevant annual/M18/input refs, impact analysis, revalidation and publication disposition. Require no new comparison audit repository; assess whether existing IDs uniquely relate affected result, changed dependency and revalidated result. | **Conditional**, only if current requirements are demonstrably insufficient. |
| P-06 inherited Gate and editorial rules | **KEEP / EDITORIAL** | Keep CC-04/05 Gate checks and current failure scope; do not add Gate evidence fields merely to reproduce the old CC-09 list. Clean editorial identifiers/spacing separately, without retroactive alteration of Status or SHA. | **No** for purely editorial work; **yes** for substantive Gate change. |

**Interpretation rule:** A requirement's appearance in Rev.2 does not, by itself, prove it must be reinstated verbatim. Conversely, deletion of a field is not harmless if the resulting calculation or comparison cannot be interpreted unambiguously. Evaluate each case by a concrete reproducibility failure, not by a presumed obligation to preserve the historical audit schema.

## 3. Minimal proposed wording (not adopted)

### 3.1 P-01 — CC-09 / provisional receipt

**Retain:** `## CC-09 — Reserved / Deleted` and its deletion explanation. The three existing paragraphs under `M19-only provisional Owner decision receipt boundary (CC09-IR01; non-RP-023)` are **not rewritten here**; any move must be verbatim, and the Owner must settle the normative status of the new location. A layout move alone must not imply Freeze approval.

### 3.2 P-02 — conditional correction clarification

> Where an operational calculation or comparison result relied on for reproducibility is corrected, the effective result and its superseded result must remain distinguishable through existing immutable identities or versioned references. This does not impose historical governance-chat reauthentication, a new record category, or a separate audit repository.

**Status of text:** candidate only. The phrase “must remain distinguishable” may be a **substantive new MUST** if not already entailed by existing clauses. **Do not insert into canonical contract without targeted old/new obligation verification and Owner decision.** The text does not mandate a universal append-only storage architecture.

### 3.3 P-03–P-05 — interpretive notes only, not normative additions

- **Trigger:** The applicable rule and observation specification should be identifiable from existing immutable operation references when a Trigger determination is relied on for transition. Do not infer new approval per user setting.
- **Retry:** The authoritative annual result must not be confused with a failed or superseded attempt. A separate retry-link field is unnecessary if existing identities and dispositions already disambiguate the attempts.
- **Comparison:** The approved comparison contract and dependency versions relevant to a result must be identifiable. Existing impact-analysis/revalidation obligations are not enlarged into a universal governance-evidence search.

These are **review interpretations**, not replacements for existing mandatory clauses. Their sufficiency for closing CLD-06, NEW-01 or NEW-02 is **not yet established**.

## 4. Owner decision register — minimum only

| ID | Question | Choices / consequence | Recommendation | Status |
|---|---|---|---|---|
| OD5-01 | Where do the three M19 provisional Owner receipt paragraphs live, and are they within the Freeze boundary? | A: preserve current DRAFT placement until separately approved; B: move verbatim to a separately identified normative appendix with explicitly stated Freeze status. Neither option reactivates old CC-09. | **A as interim** to avoid an unapproved normative-location change; submit B if a clean separation is required. | **OPEN — Owner** |
| OD5-02 (conditional) | Does a concrete reproducibility gap require a new correction-record MUST? | A: existing immutable result IDs/version references suffice; B: authorize a narrowly scoped no-silent-replacement/old-new distinguishability rule. | **A unless a concrete counterexample establishes a gap.** | **NOT TRIGGERED pending gap test** |
| OD5-03 (conditional) | Does a concrete gap require new Trigger/retry/comparison link fields or Gate evidence duties? | A: existing references suffice; B: approve only the minimum operation-specific addition shown necessary. | **A unless a concrete ambiguity is demonstrated.** | **NOT TRIGGERED pending gap test** |

B-OD-01 through B-OD-05 are preserved as prior decisions; this register does **not** reopen them. In particular: no universal reauthentication; seven-field provisional receipt with conditional `target_ref`; closed three operational traceability categories; Workflow/DecisionLog unchanged; CC-09 reserved/deleted.

## 5. Focused acceptance tests before any further normative expansion

The following are **review examples**, not new permanent audit steps or a mandate to implement tests in this stage:

1. **Annual retry:** Can the system identify the final annual result, the adopted successful attempt, the failed attempt and the exact inputs/model version without using an Owner chat transcript? If yes, do not mandate a new `retry_of` field.
2. **Trigger:** Can the applied rule and observation validity for a relied-upon R4 Trigger determination be reconstructed from the run's existing immutable refs? If yes, do not require a new Trigger-version field merely because old CC-09 listed one.
3. **Comparison:** Can a comparison result be tied to the exact comparison-contract version, annual results and changed dependencies, and can the applicable revalidation/publication disposition be distinguished? If yes, no new evidence class or historical review recovery.
4. **User settings:** Does a new user-specified parameter produce an input snapshot/result association rather than a new normative Owner-approved contract? This is a **future UI/exploratory-mode design expectation**, not proof of existing implementation or authorization to bypass current formal Gate/contract rules.

## 6. Finding mapping (provisional; no formal Close)

| Finding | Stage 5 status |
|---|---|
| CLD-01 | KEEP existing Owner receipt reliance boundaries; no eighth issuer field or universal history search. |
| CLD-02 | REVISE narrowly; additional MUST conditional on demonstrated correction ambiguity. |
| CLD-03 | OPEN Owner decision on receipt placement/Freeze. |
| CLD-04 | KEEP explanation that receipt is not a political execution Decision. |
| CLD-05 | KEEP current Gate requirements; do not infer extra Gate record schema. |
| CLD-06 | KEEP existing Trigger obligations; verify version-identifiability before any change. |
| CLD-07 | EDITORIAL pending complete text cleanup. |
| NEW-01 | CONDITIONAL; no mandatory dedicated retry link absent demonstrated ambiguity. |
| NEW-02 | CONDITIONAL; no new comparison record class absent demonstrated ambiguity. |

## 7. Limits and STOP

This is a **bounded Stage 5 DRAFT**, not a complete line-by-line amended Control Contract. The available Stage 3/4 documents and consulted fixed-source excerpts support the disposition analysis, but a full-file mechanically verified diff, runtime replay and implementation V&V have **not** been completed. Accordingly no Finding is formally closed and no claim is made that existing IDs definitively resolve every edge case.

**STOP after Stage 5 DRAFT.** No GitHub writes, canonical DecisionLog changes, Owner adjudication, Freeze, M19–25/RP-023 HOLD release, or v7 redesign authorization.
