# M18-R2 — Retained-Model Regression Acceptance Record

**Status:** TECHNICAL PASS / RECORD APPROVED / COMMIT PENDING
**Scope:** R01–R04
**Tested revision:** `f45f80a788fbb3cc755545bf5e29a35089514dd9`
**Branch:** `main`
**Historical baseline:** `1358b1c`
**Authority:** `specifications/RP-022.md`, Sections 50.2, 50.6, 51.4–51.6

## 1. Purpose

Verify that the retained SPE fiscal model preserves the existing `bonds` calculation, result validation, scenario comparison, and M16/M17 compatibility contracts following RP-022 closure.

This record documents execution evidence. It does not modify or reopen RP-022.

## 2. Verification Results

### R01 — M10 Output and Legacy Compatibility

**Result: PASS**

Evidence:
- M10 source inspection confirmed the retained formula: `bonds = max(expenditure - tax_revenue, 0)`.
- Historical comparison between `1358b1c` and the tested revision passed for two scenarios, four years each.
- Nine common annual output fields were compared across eight scenario-years.
- Current M10 outputs were validated across three tracked scenarios and twelve scenario-years.
- Direct execution of the M10 `bonds` output expression passed three boundary cases: deficit, balance, and surplus.

Limitations:
- Historical output equivalence is limited to the compared scenarios and fields.
- The surplus boundary was tested by executing the extracted M10 expression, not through an end-to-end surplus scenario.
- The three current tracked scenarios contained no surplus years.

### R02 — M12 Bonds Validation

**Result: PASS**

Evidence:
- Confirmed required-field, numeric, finite, nonnegative, and formula-consistency validation.
- Normal deficit and surplus examples were accepted.
- Missing, nonnumeric, negative, inconsistent, and nonfinite `bonds` values were rejected.
- A noncontiguous-year input was rejected.
- Existing formula tolerance was preserved: relative `1e-10`, absolute `1e-9`.

Limitations:
- Representative positive and negative cases were tested; exhaustive input-space verification was not performed.

### R03 — M10/M11 Scenario Comparison

**Result: PASS**

Evidence:
- Existing M10/M11 regression commands completed successfully.
- M10 comparison retained the expected baseline-versus-test behavior.
- M11 batch comparison retained scenario-registry and M12-validation dependencies.
- `bonds` remained a model-defined output used for descriptive scenario comparison.

Limitations:
- Results establish compatibility for the tested scenario registry and existing regression conditions.

### R04 — M16/M17 Result Compatibility

**Result: PASS**

Evidence:
- Six representative compatibility cases passed.
- Valid M16 and M17 results were accepted.
- Missing M16 wage and invalid M17 Gini values were rejected.
- Malformed `bonds` values were rejected through the delegated M12 validation path for both M16 and M17.
- Existing M16/M17 schema contracts and base-field delegation were preserved.

Limitations:
- Testing covered representative schema and validation cases rather than all possible optional-field combinations.

## 3. Fiscal Interpretation Boundary

The retained `bonds` indicator is defined as:

`bonds = max(expenditure - tax_revenue, 0)`

It represents SPE's model-defined nonnegative fiscal funding gap.

It must not be presented as verified total Japanese government bond issuance, outstanding government debt, principal redemption, interest expenditure, or Primary Balance.

Annual and 2055 `bonds` values may be used as model outputs and descriptive cross-scenario comparison inputs.

No independent PB calculation, PB compliance judgment, fiscal sustainability certification, or unapproved automatic fiscal divergence pass/fail threshold is authorized.

## 4. Repository Integrity

At the final observed test checkpoint:

- Branch: `main`
- HEAD: `f45f80a788fbb3cc755545bf5e29a35089514dd9`
- Worktree status: `?? engine/m18_evaluate.py`
- No commit or push performed during M18-R2 testing.
- The protected untracked M18 implementation file was excluded from inspection, modification, staging, and committing.

## 5. Acceptance Decision

**R01: PASS**
**R02: PASS**
**R03: PASS**
**R04: PASS**

**M18-R2 technical verification: PASS**

The acceptance record is approved by the project owner. Repository commit and push remain pending.

## 6. Residual Boundaries and Handover

- R05–R06 require a separately authorized M18 evaluation-contract and implementation compatibility review.
- R07–R08 remain documentary audit requirements with the limitations recorded by RP-022.
- Historical G0/G1/G2 and V11/V12 migration-gate dispositions remain unchanged.
- RP-022 remains CLOSED.
- M18 implementation remains SUSPENDED.
- No authorization to inspect or modify `engine/m18_evaluate.py` is implied.
- M18 resumption requires completion of the applicable compatibility review and explicit project-owner authorization.
