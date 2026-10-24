# M19-24 — Owner Decision Traceability (Review Attachment)

**Status:** candidate evidence, not canonical DecisionLog; baseline SHA `e2238922193107f204805d9f25d6ddd6f764eced`.

| Owner decision | Contract location | Review check |
|---|---|---|
| M19-12 approved principles | CC-03, CC-07, CC-10 | no auto priority, branch/path stop, R4 rejected→N3, no auto re-review |
| D18-01 | CC-04–05 | independent Gates A/B/C |
| D18-02 | CC-05, CC-07 | no silent required-value fallback |
| D18-03 | CC-05, CC-07 | dependency-scoped stops |
| D19-19-01 | CC-02 | 3 machines + 3 result domains |
| D19-19-02 | CC-04–05 | observation check separate from transition gates |
| D19-19-03 | Status, Freeze boundary | control before numerical/implementation freeze |
| D20-01 | CC-02–04 | state transition semantics |
| D20-02 | CC-03, Reason taxonomy | normal resolution vs error |
| D20-03 | CC-09 | three linked audit classes |
| D21-01 | CC-02, CC-12 | `not_required` meaning; append-only invalidation |
| D21-02 | CC-06, CC-08 | prefix identity; comparison status vs action |
| D21-03 | CC-09 | immutable references |
| D22-01 | Status | Owner-confirmed repository SHA |
| D22-02 | Freeze boundary | control only; numeric/implementation excluded |
| D23-01 | CC-11 | determinability distinct from mandatory observation validation |
| D23-02 | CC-12 | invalidated reservation cannot revive |
| D23-03 | CC-08, CC-13 | eligibility only by approved comparison contract |

**Caveat:** these are chat-approved design decisions, not yet registered as canonical DecisionLog entries. This matrix documents their intended mapping; a reviewer must check the actual normative language and any conflicts with the Owner-confirmed repository snapshot.
