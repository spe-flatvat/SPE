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
### 4.1 Policy Scenarios
(Scenario details migrated from v5. Formal specification deferred to RP-018.)
- **F-Scenario**: Progressive fiscal stimuli.
- **N3-Scenario**: Phased tax increases.
- **R4-Scenario**: GDP/Wage triggers.
- **Noble Shift**: Fixed growth anchor.
- **Status Quo**: Baseline growth.

## Appendix: Administrative Records
(References and Constraints moved to Annex and Errata.)
