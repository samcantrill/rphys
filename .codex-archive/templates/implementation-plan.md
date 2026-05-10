# Implementation Plan: <Work Package Name>

Status: draft
Roadmap item: <link>
Master plan: `docs/implementation/<roadmap-slug>/master-plan.md`
Roadmap slug: `<roadmap-slug>`
Current phase:
Blockers:

## Startup Preflight

- Git status:
- Current branch:
- Upstream:
- Worktree root:
- GitHub CLI auth:
- Git remote protocol:
- Fetch/push verification:
- Authentication or permission blockers:

## Operating Rules

- Implement phases strictly in master-plan order.
- Start phase `n + 1` only after phase `n` has merged and branch/worktree cleanup is complete.
- Human review is not a merge gate.
- Phase PRs target `main` unless a maintainer-approved exception is recorded here.
- PR creation uses explicit base, head, and title flags; opened PR targets are verified immediately with `gh pr view`.
- Merge automatically when validation and selected pathway gates pass.
- If branch protection blocks solely on human review and available authority permits, approve, admin-merge, or otherwise force merge only after automated gates pass.
- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
- Known local blockers must be resolved before PR submission. After submission, handle only remote-only blockers such as GitHub checks, branch protection, mergeability, or permissions.

## Phase Index

| Phase | Slug | Status | Branch | Worktree | Pathway | PR Target | Merge State | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `<phase-slug>` | pending | `agent/<roadmap-slug>-p1-<phase-slug>` | `../rphys-worktrees/<roadmap-slug>-p1-<phase-slug>` | standard | `main` | not started |  |

## Shared Validation

- Phase-specific commands:
- Full-suite command:
- Documentation/link checks:
- TOML/config checks:
- Evidence that must be recorded:

## Gate Budget Ledger

| Phase | Planning pass | Coding pass | Pre-submit blocker gate | Review/checklist gate | Blocker-fix cycles | PR manager pass | Merge attempt | Cleanup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | unused | unused | unused | unused | 0 / 2 | unused | unused | unused |

## Gate Terminal Actions

| Gate | Budget | Terminal action if blockers remain |
| --- | --- | --- |
| Master-plan quality gate | one review, one refinement if needed, one confirmation | stop before phase work |
| Phase planning | one manager/planner pass | mark phase blocked if scope, ownership, validation, or pathway remains unclear |
| Phase coding | one coding pass with immediate coding/test fixes | use blocker-fix budget for concrete in-scope failures or mark blocked |
| Pre-submit blocker gate | one gate before PR submission | stop before PR submission until known local blockers are resolved or recorded as blocked |
| Standard-path review | one code review and one scientific/workflow review | use blocker-fix budget or mark blocked |
| Fast-path checklist | one manager checklist | switch to standard pathway when risk, ambiguity, expanded scope, or contract impact appears |
| Blocker fixing | 0 / 2 cycles for the same concrete blocker | stop after two cycles, no concrete new remedy, or out-of-scope blocker |
| PR and merge | one PR-manager pass plus remote-only blocker handling | stop and record auth, target, CI, protection, conflict, or permission blocker |

## Phase <N>: <Phase Name>

Status: pending
Pathway: standard / fast
Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`
Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`

### Gate Budget

- Planning pass:
- Coding pass:
- Pre-submit blocker gate:
- Standard-path reviews or fast-path checklist:
- Blocker-fix cycles used:
- PR manager pass:
- Merge attempt:
- Branch cleanup:
- Worktree cleanup:
- Evidence checked before assigning another pass:

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
- Expanded-path triggers checked: public API/import path; CLI/config/schema/package behavior; documented contracts; scientific/data/validation/reproducibility/workflow contracts; package/import boundaries; dependency/security/release/CI; persistence/serialization/provenance/cache/migration/compatibility; concurrency/retry/resume/order/data-loss risk; multi-module behavior; ambiguous acceptance criteria.
- Criteria that force standard pathway:
- Fast-path checklist, if used:
  - Narrow scope and clear file ownership:
  - No public import path, API, CLI, config, schema, package behavior, or documented contract change:
  - No scientific, data, validation, reproducibility, or workflow contract change:
  - No dependency, security, release, or CI behavior change:
  - Straightforward targeted and full-suite validation:
  - Separate automated review agents would not materially reduce risk because:
- Pathway switches:

### Validation

| Command | Result | Evidence |
| --- | --- | --- |
|  |  |  |

### Pre-Submit Blocker Gate

- Implementation plan checked:
- Diff checked:
- Draft PR body or summary checked:
- Validation evidence checked:
- Scope boundaries checked:
- Future-phase exclusions checked:
- Assumptions and risks checked:
- Selected pathway still valid:
- Known local blockers before PR submission:
- Blocker resolution used:
- Gate result:

### Review Or Checklist Summary

- Code review:
- Scientific/workflow review:
- Fast-path manager checklist:
- Unresolved blockers:

### PR And Merge

- PR:
- Base branch:
- Head branch:
- Intended PR title:
- PR creation command:
- Target verification command:
- Target verification result:
- Checks:
- Post-submit remote-only blockers:
- Merge command:
- Merge result:
- Branch cleanup:
- Worktree cleanup:

### Phase Notes

- Implementation summary:
- Commits:
- Assumptions and risks:
- Follow-up:
