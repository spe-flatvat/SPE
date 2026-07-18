##README.md
SPE (SUZUME PolicyCraft Engine)

Everything started with a single sentence.

「フォルダ作るのメンドクサイ。」

What is SPE?

SPE (SUZUME PolicyCraft Engine) is an experimental policy design framework.

Rather than searching for a single "correct" policy, SPE is designed to:

formulate policy proposals,

simulate their long-term outcomes,

identify structural boundaries,

compare trade-offs,

document assumptions,

and continuously improve the model.

The goal is not to advocate a policy, but to provide a transparent environment for structured policy exploration.

Project Philosophy

SPE is built around a simple idea:

Good decisions come from good questions.

The engine does not attempt to determine "the answer."

Instead it tries to make explicit:

assumptions,

constraints,

trade-offs,

uncertainties,

and failure boundaries.

When the model reaches a limit, it should explain why.

Core Principles

Transparency over authority

Documentation over memory

Assumptions are explicit

Decisions are recorded

Errors are preserved and corrected

Unknowns remain unknown until verified

Project Structure

SPE/ README.md docs/ Glossary.md DecisionLog.md Errata.md specs/ SimulationSpecification.md policies/ F.md N3.md R4.md NobleShift.md history/ ... 

Governance Documents

Glossary

The project's Single Source of Truth.

Defines terminology, variables, concepts, and model language.

Decision Log

Records why important architectural or modelling decisions were made.

Purpose:

Prevent the same discussions from being repeated.

Errata

Records documentation errors and corrections.

Purpose:

Preserve transparency.

Mistakes are part of engineering.

Current Model

Current simulation model:

SUZUME Model

(Based on concepts originally developed through the TSUBAME-equivalent simulation framework, with independent extensions implemented within the SPE project.)

Current comparison scenarios include:

F

N3

R4

Noble Shift

Status Quo

Development Phases

Phase 0

Policy drafting

Phase 0.5

Repository cleanup

Glossary

Decision Log

Errata

Documentation consistency

Phase 1

Engine implementation

Planned:

State Machine

State Score

Transition Engine

Handoff Framework

Phase 2

Model refinement

Including:

sensitivity analysis

calibration

expanded demographic model

resource allocation coupling

Design Philosophy

One important concept in SPE is:

F3 is not Failure.

F3 is Boundary.

A simulation reaching its boundary is considered valuable information.

The engine should explain why that boundary exists rather than attempting to hide it.

Contributing

Questions are welcome.

Criticism is welcome.

Finding mistakes is welcome.

Changing assumptions is welcome.

The only rule is:

Document the reason.

License

To be determined.

Acknowledgements

SPE has been shaped through extensive collaborative discussions involving multiple AI systems and a human project owner.

Each participant contributed different strengths:

structural review

consistency checking

architecture

implementation support

documentation

SPE itself is therefore an experiment not only in policy design, but also in collaborative human–AI engineering.

Repository Governance

AI Collaborator Responsibilities
- Fact-Checking: Verify factual accuracy against Owner-confirmed snapshots.
- Technical Consistency: Ensure technical coherence across all documentation.
- Contradiction Identification: Proactively identify and flag internal contradictions.
- Improvement Proposals: Propose improvements to specifications and documentation.
- Rationale Disclosure: Provide clear, logical reasoning for all proposed changes.

Review Workflow
* Conflict Resolution: Should AI reviews conflict, the Project Owner holds the final authority to resolve the disagreement. No AI opinion takes precedence over another.

Finally

This repository does not exist because someone wanted to build another framework.

It exists because someone wanted to avoid doing the same tedious work twice.

"メンドクサイ" is not the opposite of engineering.

It is often where engineering begins.