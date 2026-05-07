# Execution Playbook: <Work Package> Phase <N> <Phase Name>

Status: draft
Master plan: <link>
Roadmap item: <link>
Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`
Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`
Phase notes: `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/phase-notes.md`
Public PR body: `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/pr-body.md`
Quality gate:
Blockers:

## Compact Context Capsule

Summarize only the context needed for this phase: goal, accepted decisions, constraints, and relevant prior phase outputs.

## Ownership

- Files/modules owned by this phase:
- Files/modules explicitly out of scope:
- Public interfaces allowed to change:
- Other active branches/worktrees to avoid:

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
- Existing tests or harness behavior:
- Import-boundary or dependency constraints:
- Scientific contract constraints:

## Scope Contract

Define the public behavior, module boundaries, data shapes, error behavior, edge cases, and scientific assumptions the implementation must not redesign. If no public or scientific contract changes are in scope, state that explicitly.

## Tasks

- <Task 1>
- <Task 2>
- <Task 3>

## Pathway Eligibility

- Recommended pathway: standard | fast
- Fast-path rationale, if applicable:
- Criteria that would force standard pathway:

## Implementation Plan Output

- Detailed implementation plan path: `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/implementation-plan.md`
- Fast-path checklist path, if used: `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/fast-path-checklist.md`

## Expected Commits

- Planning/handoff documents.
- Implementation.
- Tests and validation.
- Review fixes.
- Cleanup.

## Design Impact

- Maintainability:
- Extensibility:
- Scientific workflow safety:
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

## Verification

- Phase-specific commands:
- Full-suite command:
- Expected evidence to record:

### Suite Obligations

- Package:
- Unit:
- Contract:
- Integration:
- E2E:
- Opt-in:

## Review Focus

- Standard pathway code review:
- Standard pathway scientific/workflow review:
- Fast-path manager checklist:

## Stop Conditions

- <Condition that requires manager or maintainer intervention>

## Budget Status

- Implementation blocker cycles used:
- Code review:
- Scientific/workflow review:
- Fast-path checklist:
- Pre-submit blocker gate:

## Completion Notes

- Implementation summary:
- Validation summary:
- Review summary:
- PR preparation:
- Merge and cleanup:
- Remaining blockers:
