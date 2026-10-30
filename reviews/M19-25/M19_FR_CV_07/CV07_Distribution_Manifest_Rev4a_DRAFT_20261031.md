# SPE M19-FR-CV-07 Distribution Manifest Rev.4a DRAFT

**Status:** DRAFT / NOT APPROVED / NOT DISTRIBUTED
**Repository:** `spe-flatvat/SPE`
**Purpose:** Common packet for four independent AI reviews
**Payload count:** 13 files, excluding this Manifest
**Total distribution files:** 14, including this Manifest

## Fixed source and candidate

- Fixed source commit: `a00c96252ee1260a909be8775511c420685b51d8`
- Original source SHA-256: `4a1f70e0c517c0a3e5d0389bb5176db2336bcdd935f2d34f1abf7a5b5f538ed2`
- Rev.2 candidate SHA-256: `94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd`

## Payload SHA-256 inventory

Paths are relative to this Manifest's directory.
The Manifest's own SHA-256 must be recorded separately in the
distribution issuance record and reviewer receipt. It must not
be inserted into itself.

```text
62f56b0fda4c2c9df922ef8460eb62057cb7ec89798f3708ca2b06971a730363  ./CV07_Common_Review_Request_DRAFT.md
c1fc4d9fc9a354579684b201d596d96654444d08e3575a413f7d987b35decc2e  ./CV07_Reviewer_Checklist_DRAFT.md
e1230cf31f684b1f95dde41bc2093e2d7fedf148ca682ad2193c1f4555b1a8ac  ./SPE_M19_FR_CV_05_N01-N03_Integrated_Owner_Decision_Register_DRAFT_20261031.md
6e8fa6a515c3c95642e6cbae7a42e14b1a3f9e74d974ebf640ad086cfe73049d  ./SPE_M19_FR_CV_05_N01_Owner_Decision_Receipt_20261031.md
ac63247a04901364335189cb6ace5799846b7e577eeecb7f8a48ea13d02f5f0f  ./SPE_M19_FR_CV_05_N02_Owner_Decision_Receipt_20261031.md
f7c183bed4fc395ee334dc96212cc40a3c0a0f12a55494c7e93a208900d2eab4  ./SPE_M19_FR_CV_05_N03_Owner_Decision_Receipt_20261031.md
e333b41e24b04d91112fa7a66689bf18c88fc91e5abb0362e844b0873e229293  ./SPE_M19_FR_CV_05_Prospective_Normative_Decision_Packet_DRAFT_20261031.md
ddb86d6946cb86184940b8e08fa084901010a96391f5c5df4f58e528a607ad87  ./SPE_M19_FR_CV_06_Clause_Cross_Validation_Report_DRAFT_20261031.md
e750f613a7e6137553c2faaa0246258c200f094bbc312df837f19482aeac260d  ./SPE_M19_FR_CV_06_Normative_Amendment_and_Traceability_DRAFT_20261031.md
94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd  ./SPE_M19_FR_CV_06_Rev2_Convergence_Candidate_DRAFT_20261031.md
68a3247b00e413f988df72ede14ce012c23be441c8ea20026478ad5ff7e4f87e  ./SPE_M19_FR_CV_06_Rev2_Exact_DIFF_DRAFT.patch
9b6ed7f58377aae44c6710d49a65c9d4c077ae1d74c463706324495e9d7a59b3  ./SPE_M19_FR_CV_06_Rev2_Strict_Diff_Verification_Receipt_DRAFT_20261031.md
4a1f70e0c517c0a3e5d0389bb5176db2336bcdd935f2d34f1abf7a5b5f538ed2  ./references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md
```

## Evidence boundaries

- CV05-N01: Option A adopted; future exception requires separate authorization.
- CV05-N02: Option B adopted for drafting only, not normative adoption.
- CV05-N03: Option A adopted; 2026 initial-state validation is not transition authorization.
- Owner utterances in receipts are attributed transcriptions; independent primary-record authentication remains unverified.
- Prospective decisions do not retroactively prove historical approvals.
- Missing historical evidence must not be interpreted as proof of nonexistence.
- CV-06 strict diff verification is not substantive review acceptance.
- Existing OPEN and unadjudicated Findings remain subject to separate disposition.
- No GitHub write, independent review commencement, Finding closure, formal approval, Freeze, or HOLD release is authorized.

## Distribution requirements

1. Preserve all 13 payload bytes and this Manifest after fixation.
2. Record this Manifest's SHA-256 externally in the issuance record.
3. Distribute the same fixed GitHub commit to ChatGPT, Claude, Gemini and Grok.
4. Require each reviewer to report actual byte-verification coverage and limitations.
5. Preserve reviewer originals without pre-submission cross-disclosure.
6. Require separate Owner authorization for GitHub publication and review commencement.
