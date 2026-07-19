Repository overview: [README.md](../README.md)

# Workflow

## 1. Overview
This document defines the Standard Operating Procedure (SOP) for the SPE repository. It establishes the mandatory protocols for governance, review, and maintenance.

## 2. Governance Principles
- **Canonical Source**: The GitHub repository (`main` branch) is the sole Canonical Source.
- **Canonical vs. Non-Canonical**: Only repository-maintained files are Canonical. Historical archives and private logs are excluded from mandatory updates.
- **Decision Log**: All governance-level resolutions must be recorded in `DecisionLog.md`.

## 3. Owner-confirmed Snapshot
All repository reviews shall be conducted against an **Owner-confirmed snapshot**. An Owner-confirmed snapshot is established only after explicit confirmation by the Project Owner (e.g., "Review this version."). Content independently retrieved via URLs, AI tools, or browser caches is not authoritative for review purposes. The Owner-confirmed snapshot serves as the operational review baseline.

## 4. AI Review Procedure
The review process follows these mandatory steps:

1. **Preparation**: Owner prepares a draft and confirms the snapshot.
2. **Submission**: Owner submits a Review Request using the standardized template.
3. **Execution**: Multi-AI review (ChatGPT, Claude, Gemini, Grok).
4. **Resolution & Revision**: Reviewers provide their assessment:
   - `Accepted`: Proposal is approved.
   - `Revision Recommended`: Proposal requires specific adjustments.
   - `Rejected`: The proposal cannot be accepted in its current form.

   No individual AI review has precedence over another.

   If reviewers reach different conclusions, the Project Owner shall determine the final resolution. The Owner shall integrate feedback, revise the draft, and re-submit until reviewers reach consensus.
5. **Waived Review**: If a reviewer is unavailable due to operational constraints, the Owner may waive that review. The reason for the waiver shall be recorded in the corresponding RP review record or commit log. A waived review does not invalidate the review process.
6. **Consensus**: Final consensus is obtained among available reviewers.

### Review Template
- **Subject**: RP number and title.
- **Purpose/Scope**: Definition of changes.
- **Out of Scope**: Explicit list of excluded items.
- **Expected Output**: Accepted, Revision Recommended, or Rejected.
- **Attachment**: The Owner-confirmed snapshot/draft document.

## 5. Repository Update Flow
1. **Drafting**: Create/Update content in `docs/`.
2. **Snapshot**: Establish the Owner-confirmed snapshot.
3. **Review**: Submit per the Review Procedure.
4. **Validation**: Before committing, the Owner must:
   - Review `git diff`.
   - Verify Markdown formatting.
   - Confirm document consistency.
5. **Implementation**: Merge/Commit changes.
6. **Logging**: Update `DecisionLog.md` or `Errata.md` as required.

## 6. Standardized Out of Scope
Reviewers and Contributors shall not:
- Redesign specifications outside the RP scope.
- Reopen previously Approved governance decisions.
- Review unrelated repository areas.
- Revisit materials explicitly classified as Non-Canonical.

## 7. Document Roles
- **ProjectRoadmap**: Future implementation planning.
- **DevelopmentStory**: Historical context.
- **Errata**: Technical limitations and observations.
- **DecisionLog**: Formal governance resolutions.
