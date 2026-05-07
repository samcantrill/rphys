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

## Summary

Describe the work package, why it belongs in the scaffold, and what successful completion changes for future contributors and agents.

## Behavior Model

- User-visible behavior:
- Agent-visible behavior:
- Supported workflows:
- Unsupported workflows:
- Failure and stop behavior:
- Resume behavior after context compaction:

## Goals

- <Goal 1>
- <Goal 2>

## Non-Goals

- <Explicitly out-of-scope behavior>

## Design Decisions

| Decision | Status | Alternatives Considered | Rationale | Maintainability/Extensibility Impact | Validation Obligation | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| <Decision> | accepted | <Alternatives> | <Why> | <Impact> | <Tests/docs/checks> | <Risk> |

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
- Required review or checklist documents:

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

## Blocker Policy

The manager may attempt two automated blocker-fix and re-review cycles for the same blocker. PRs should be auto-merged after pathway gates pass. Stop for maintainer intervention only if the blocker remains, GitHub auth is invalid, branch protection blocks merge, repository-required review is enforced by repository policy, or the implementation would require changing accepted design decisions.

## Open Questions Or Accepted Assumptions

- <Question or assumption>
