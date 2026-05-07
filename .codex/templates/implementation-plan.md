# Implementation Plan: <Work Package Name>

Status: draft
Roadmap item: <link>
Master plan: `docs/implementation/<roadmap-slug>/master-plan.md`
Roadmap slug: `<roadmap-slug>`
Current phase:
Blockers:

## Operating Rules

- Implement phases strictly in master-plan order.
- Start phase `n + 1` only after phase `n` has merged and branch/worktree cleanup is complete.
- Human review is not a merge gate.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.

## Phase Index

| Phase | Slug | Status | Branch | Worktree | Pathway | Merge State | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `<phase-slug>` | pending | `agent/<roadmap-slug>-p1-<phase-slug>` | `../rphys-worktrees/<roadmap-slug>-p1-<phase-slug>` | standard | not started |  |

## Shared Validation

- Phase-specific commands:
- Full-suite command:
- Documentation/link checks:
- TOML/config checks:
- Evidence that must be recorded:

## Phase <N>: <Phase Name>

Status: pending
Pathway: standard / fast
Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`
Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`

### Scope

- Goal:
- Files/modules owned:
- Out of scope:
- Public interfaces allowed to change:
- Scientific/workflow contracts:

### Plan

- Tasks:
- Ordering:
- Coding worker handoff:
- Stop conditions:

### Pathway Decision

- Selected pathway:
- Rationale:
- Criteria that force standard pathway:
- Fast-path checklist, if used:

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
|  |  |  |

### Review Or Checklist Summary

- Code review:
- Scientific/workflow review:
- Fast-path manager checklist:
- Unresolved blockers:

### PR And Merge

- PR:
- Base branch:
- Head branch:
- Checks:
- Merge command:
- Merge result:
- Branch cleanup:
- Worktree cleanup:

### Phase Notes

- Implementation summary:
- Commits:
- Assumptions and risks:
- Follow-up:
