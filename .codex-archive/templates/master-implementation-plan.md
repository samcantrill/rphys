# Master Implementation Plan: <Work Package Name>

Status: draft
Roadmap item: <link>
Roadmap slug: `<roadmap-slug>`
Planning notes: <link>
Owner: <name or agent>
Draft pass:
Refine pass:
Quality gate:
Blockers:
Implementation plan: `docs/implementation/<roadmap-slug>/implementation-plan.md`

## Summary

Describe the work package, why it belongs in the scaffold, and what successful completion changes for future contributors and agents.

## Behavior Model

- User-visible behavior:
- Agent-visible behavior:
- Supported workflows:
- Unsupported workflows:
- Failure and stop behavior:
- Resume behavior after interruption or context loss:
- Stage 3 operating model: one live implementation plan, sequential phases, automatic/admin merge after automated gates, no human-review merge gate.

## Goals

- <Goal 1>
- <Goal 2>

## Non-Goals

- <Explicitly out-of-scope behavior>

## Intent And Functionality Approval

- Approval status:
- Approval date:
- Current round:
- Approval rule: design discussion must not start until the maintainer explicitly approves the intent/functionality baseline below.

| Packet | Topic | Functionality Baseline | Implementation Consequence | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | <topic> | <what this stage does/refuses/validates> | <consequence> | <pending/response> | <update> | pending |

Approved functionality baseline:

- <Included functionality>

Approved non-goals and stop behavior:

- <Unsupported behavior or stop condition>

## Design Decision Classification

- Classification status:
- Current review round:
- Classification rule: discuss only impactful decisions that lack a strong recommendation, plus any recorded recommendation the maintainer asks to discuss. Record strong recommendations without separate walkthrough.

| Decision | Classification | Why It Matters | Recommendation | User Discussion Needed | Status |
| --- | --- | --- | --- | --- | --- |
| <Decision> | needs discussion | <Impact> | <Recommendation> | <Question> | pending |

Recorded recommendations:

- <Decision and rationale>

Needs discussion:

- <Decision packet>

Deferred or blocking decisions:

- <Decision and reason>

## Design Decisions

| Decision | Status | Alternatives Considered | Rationale | Maintainability/Extensibility Impact | Validation Obligation | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| <Decision> | accepted | <Alternatives> | <Why> | <Impact> | <Tests/docs/checks> | <Risk> |

## Maintainer Decision Walkthrough

- Walkthrough status:
- Current round:
- Approval rule: the master plan is not accepted until each material packet below is accepted, revised into an accepted decision, or explicitly deferred with a reason Stage 3 can proceed.

| Packet | Topic | Proposal | Implementation Consequence | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | <topic> | <proposal> | <consequence> | <pending/response> | <update> | pending |

Accepted package-level assumptions:

- <Assumption accepted by maintainer or recorded as safe default>

Unresolved decision packets:

- <Packet or question that still blocks acceptance>

## Deep Design Review

- Review status:
- Review required because:
- Current design packet:
- Approval rule: the master plan is not accepted until each required deep design packet is accepted, revised into the plan, or explicitly deferred with a reason Stage 3 can proceed.

| Packet | Topic | Design Surface | Key Questions | Maintainer Response | Plan Update | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | <topic> | <API/invariants/failure modes/downstream impact> | <questions> | <pending/response> | <update> | pending |

Design examples or sketches discussed:

- <Concrete example, pseudo-signature, invariant, or failure case>

Unresolved deep design blockers:

- <Blocker>

## Structure And Extensibility

- Directory/module structure:
- Ownership boundaries:
- Dependency direction:
- Extension points:
- Coupling intentionally avoided:
- Expected future changes this structure should absorb:

## Public Interfaces And Documents

- Files or docs allowed to change:
- Public behavior or conventions introduced:
- Compatibility constraints:

## Validation Strategy

- Behavior that must be tested:
- Behavior that must be documented:
- Behavior guarded by templates or workflow checks:
- Synthetic fixtures or safe test data:
- CI/static/check commands:
- Acceptance evidence required before merge:

## Implementation Phases

| Phase | Slug | Status | Branch | Worktree | Ownership | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `<phase-slug>` | pending | `agent/<roadmap-slug>-p1-<phase-slug>` | `../rphys-worktrees/<roadmap-slug>-p1-<phase-slug>` | <files/modules> | <outcome> |

For each phase, record:

- Goal:
- Scope:
- Out of scope:
- Acceptance criteria:
- Test expectations by package, unit, contract, integration, e2e, and opt-in suites:
- Design impact:
- Future compatibility:
- Alternatives rejected:
- Debt introduced:
- Reviewability:
- Completion summary:

Phase execution rule: implement one phase at a time. Phase `n + 1` may start only after phase `n` has merged and branch/worktree cleanup is complete.

## Pathway Guidance

- Standard pathway phases:
- Fast-path eligible phases:
- Criteria that force standard pathway:

## Validation And Tests

- Phase-specific commands:
- Full-suite command:
- Documentation/link checks:
- TOML/config checks:

## Review Requirements

- Standard pathway code review focus:
- Standard pathway scientific/workflow review focus:
- Fast-path manager checklist:
- Review or checklist recording location: `implementation-plan.md` unless the maintainer explicitly asks for a separate document.

## Merge Policy

- Human review is not a default merge gate.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated validation and pathway gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside this accepted plan.

## Discussion History

- Major question rounds:
- Decisions changed during discussion:
- Open questions intentionally deferred:
- Maintainer concerns addressed:

## Master Plan Quality Gate

- Initial review:
- Refinement pass:
- Confirmation review:
- Gate result:
- Blocking findings:
- Accepted risks and revisit triggers:
- Separate quality-gate documents created: no by default

## Blocker Policy

The manager may attempt two automated blocker-fix and re-review cycles for the same blocker. PRs should be auto-merged after pathway gates pass. Human review is not a merge gate. If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge after automated gates pass. Stop for maintainer intervention only if the blocker remains, GitHub auth is invalid, branch protection blocks merge without available authority, validation is failing, conflicts remain unresolved, or the implementation would require changing accepted design decisions.

## Open Questions Or Accepted Assumptions

- <Question or assumption>
