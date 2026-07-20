# Simulation Specification v6

Version: v1.0

Status: Fixed

Last Updated: 2026-07-20

Updated By: RP-017

## Chapter 1: Scope & Objectives
### 1.1 Purpose
The SUZUME PolicyCraft Engine (SPE) provides a canonical, reproducible simulation environment. v6 formalizes governance and strictly separates canonical logic from administrative data.

## Chapter 2: Theoretical Foundations
### 2.1 Variable Architecture
All variables are defined in [Glossary.md](Glossary.md).
### 2.2 Core Assumptions
- **Production Function**: $Real GDP(t) = Base Growth + Stimuli(t) + Investment(t) + Education(t) - Risk(t) + (1-\alpha) \times Labor Growth(t)$.
- **Demographics**: $Population(t) = Pop(t-1) + (Births(t) - Deaths(t)) + Net Migration(t)$.
- **Birth Logic**: $Births(t) = Births(t-1) \times 0.975 \times (1 + \phi \times Real Wage Growth(t))$.
- **Constants**: $\alpha=0.35, \phi=0.15$ (Ref: [Glossary.md](Glossary.md)).

## Chapter 3: Policy Simulation Logic
*Shared logic across all scenarios.*
### 3.1 State Transitions
- **Tax/Fiscal**: $Revenue(t) = Revenue(t-1) \times (1 + Nominal GDP Growth(t) \times \epsilon(t))$.
  - Note: Tax elasticity ($\epsilon$) is defined per scenario baseline.
- **Constraints**: $Revenue(t) \le 0.30 \times Nominal GDP(t)$.
### 3.2 Operational Guardrails
- Deficits exceeding canonical thresholds trigger [Errata.md](Errata.md) review.

## Chapter 4: Comparative Framework
*Scenario-specific parameterizations.*
### Authoring Baseline

As of RP-019, this document enters the Scenario Parameter Authoring phase.

The repository governance baseline established by RP-018 is considered frozen for the duration of Authoring.

Scenario specifications shall be authored incrementally, one scenario at a time, following the RP-019 Authoring Rules.

No untagged speculative parameter values shall be introduced. Any model assumption must be explicitly identified using an approved source classification (Document, User Design, or Model Assumption).

Repository governance documents shall remain frozen unless an explicit exception is approved by the Project Owner.

### 4.1 Policy Scenarios
(Scenario details migrated from v5. Formal specification begins under RP-019.)
- **F-Scenario**: Progressive fiscal stimuli.
- **N3-Scenario**: Phased tax increases.
- **R4-Scenario**: GDP/Wage triggers.
- **Noble Shift**: Fixed growth anchor.
- **Status Quo**: Baseline growth.

#### 4.1.1 F-Scenario

##### Inputs

**Initial State Values (2026)** [Document]  
- Nominal GDP  
- Real GDP  
- Policy Interest Rate  
- Bond Issuance  
- Tax Revenue  
- Shareholder Dividends  
- Retained Earnings  
- Nominal Median Wage  
- Real Median Wage  
- Median Income  
- Gini Coefficient  
- Engel Coefficient  
- Population  
- Deaths  
- Births  
  
**Common Risk Events (All Scenarios)** [Document]  
- Oil Shock (onset year, Real GDP impact)  
- Cross-Strait Conflict (onset year, Real GDP impact)  
- Nankai Trough Earthquake (onset year, Real GDP impact, tax revenue impact)  
- Mid-Scale Disaster (recurrence interval, Real GDP impact)  
- Climate Change Drag (recurrence interval, Real GDP impact)  
  
**Policy Effect Schedule (F-Scenario Specific)** [Document]  
- Consumption Stimulus Effect (applicable period segments)  
- Investment Promotion Effect (applicable period segments)  
- Education Effect (applicable period segments)  
  
**Fiscal Parameters (F-Scenario Specific)** [Document]  
- Tax Elasticity (period segments)  
- Expenditure Growth Rate (period segments)  
  
**Demographic Parameters** [Document / Model Assumption]  
- Death Rate Coefficient [Document]  
- Birth Rate Coefficient [Document]  
- Birth–Real Wage Feedback Elasticity φ [Model Assumption] (see Glossary.md)  
- Immigration Schedule (F-Scenario steady-state value) [Document]  
  
**Labor Parameters** [Model Assumption]  
- Capital Share α (see Glossary.md)  
- Aging Drag (period-specific values; source is IPSS data, integration method is [Model Assumption])  
  
**Anchor References (F-Scenario Specific)** [Document]  
- Real Median Wage Anchor Years  
- Gini Coefficient Anchor Years  

##### Outputs

##### State Variables

##### Transition Rules

##### Evaluation Metrics

##### Open Assumptions

- Inclusion of the F-Scenario Sequencing Variant (political adjustment case) in Inputs remains undecided; not included in this listing.  

## Appendix: Administrative Records
(References and Constraints moved to Annex and Errata.)
