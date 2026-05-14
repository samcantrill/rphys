# Phase <P> Execution Plan: <Title>

## Metadata

- Status: draft phase execution plan
- Roadmap stage: `v<N>`
- Feature focus:
- Stage descriptor:
- Phase descriptor:
- PR title: `Stage <N> <Stage-Descriptor> - Phase <M>: <Phase-Descriptor>`
- Branch: `agent/<roadmap-slug>-p<p>-<phase-slug>`
- Worktree: `/home/samcantrill/work/rphys-worktrees/<roadmap-slug>-p<p>-<phase-slug>`
- Phase execution plan path: `docs/roadmap/stage-<N>/phases/<phase-slug>.md`
- Full plan: `docs/roadmap/stage-<N>/implementation-plan.md`
- Planning document: `docs/roadmap/stage-<N>/planning.md`
- Source phase:
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path / expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate:
- Draft pass:
- Refine pass:
- Setup limitations:
- Blockers:

## Objective

State the phase objective in one concise paragraph.

## Full-Plan Context

Summarize how this phase fits into earlier and later phases. Name future-phase
work that must remain out of scope.

## Source Phase Summary

- Goal:
- Required scope:
- Required checkpoints:
- Acceptance criteria:

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
- Existing tests or harness behavior:
- Import-boundary or dependency constraints:

## Phase Isolation State

- Control checkout dirty-state review:
- Dedicated branch/worktree status:
- Current `develop` base:
- Earlier phase dependency status:
- Push/PR infrastructure status:
- Stop condition if isolation cannot be maintained:

## In-Scope Work

- TBD

## Out-of-Scope Work

- TBD

## Assumptions

- TBD

## Scope Contract

Define the public behavior, module boundaries, data shapes, error behavior,
scientific semantics, and edge cases the executor must not redesign. If no
public contract changes are in scope, state that explicitly.

## Scientific Contract Notes

- Sampling and temporal alignment:
- Field roles, locators, schemas, and provenance:
- Masking, filtering, normalization, and aggregation order:
- Subject identity, splits, leakage, and grouping:
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices:

## Design Impact

- Maintainability:
- Extensibility:
- Lightweight import policy:
- Source-tree boundaries:

## Future Compatibility

- TBD

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
|  |  |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
|  |  |  |

## Reviewability

- Expected PR size and shape:
- Files and areas to inspect:
- Scope-control checks:

## Implementation Steps

List three to six small, reviewable implementation slices. Avoid line-by-line
instructions unless needed to prevent a public-contract or scope error.

1. TBD

## Test Plan

### Package Suite

- Status: required/deferred
- Expected paths:
- Required assertions or deferral reason:

### Unit Suite

- Status: required/deferred
- Expected paths:
- Required assertions or deferral reason:

### Contract Suite

- Status: required/deferred
- Expected paths:
- Required assertions or deferral reason:

### Integration Suite

- Status: required/deferred
- Expected paths:
- Required assertions or deferral reason:

### E2E Suite

- Status: required/deferred
- Expected paths:
- Required assertions or deferral reason:

### Acceptance Suite

- Status: required/deferred
- Markers affected:
- Required assertions or deferral reason:

## Risks

- TBD

## Validation Commands

Targeted development commands:

```sh

```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices:
- Tests to run with each slice:
- Decisions the executor must not revisit:
- Conditions that require stopping for the manager:

## Refinement And Review Budget Status

- Phase execution plan refinement: unused / not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan:
- Final phase execution plan:
- Implementation summary:
- Implementation validation:
- Refinement summary:
- Pre-submit blocker gate:
- PR preparation:
- Automated review:
- Merge result:
- Cleanup:
- Remaining blockers:
