# Stage 3: Managed Implementation

## Purpose

Implement the accepted master plan one phase at a time using isolated worktrees, one live implementation plan, automated checks, automated review or checklist gates, PRs, automatic merge, and cleanup.

Stage 3 should not wait for human review. Human input is needed only for missing credentials, branch protection that cannot be bypassed with available authority, repeated unresolved blockers, failing validation that cannot be fixed, merge conflicts, or a required change to accepted design decisions.

## Preconditions

- Roadmap work package is accepted.
- `docs/implementation/<roadmap-slug>/master-plan.md` is accepted.
- The master-plan quality gate is recorded as passed in the current `master-plan.md`.
- `gh auth status` passes if PR creation or merge will be attempted.
- `/home/samcantrill/work/rphys-worktrees` exists and is writable.
- `main` is the foreground branch and tracks the intended upstream, or the deviation is documented.

## Canonical Prompt

Use `.codex/prompts/phase-loop-management.md` for Stage 3 management.

## Default Artifact

Use one live implementation plan:

`docs/implementation/<roadmap-slug>/implementation-plan.md`

This file is the Stage 3 ledger for all phases: phase plan, pathway decisions, fast-path checklist, coding handoff, validation evidence, review summaries, PR facts, blocker history, merge result, cleanup, and current status.

If the single file becomes unreviewably large, move phase-specific plans under:

`docs/implementation/<roadmap-slug>/implementation-plans/phase-<n>-<phase-slug>.md`

Keep `implementation-plan.md` as the index, status ledger, and source of truth for current phase state. Do not create per-phase execution playbooks, pathway-decision files, phase notes, PR-body files, review reports, or context capsules by default.

## Branch And Worktree Naming

- Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`.
- Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`.

## Sequential Phase Rule

Implement phases strictly in master-plan order.

- Start phase `n + 1` only after phase `n` has been merged and the branch/worktree cleanup is complete.
- If a phase blocks, stop the sequence and record the blocker in `implementation-plan.md`.
- Do not run multiple implementation phases in parallel unless the maintainer explicitly overrides this workflow.

## Pathway Selection

Before each phase, the manager records the pathway in `implementation-plan.md`.

Use the standard pathway when a phase touches public interfaces, package structure, dependency/configuration behavior, CI behavior, tests used as public contracts, scientific/workflow contracts, multi-module behavior, or any design decision with meaningful downstream impact.

Use the fast pathway only when all of these are true:

- The phase is narrowly scoped and has clear file ownership.
- `implementation-plan.md` already contains enough implementation detail.
- No public import path, API, CLI, config, schema, package behavior, or documented contract changes.
- No scientific, data, validation, reproducibility, or workflow contract changes.
- No dependency, security, release, or CI behavior changes.
- Verification is straightforward and can be completed with targeted checks plus the available full suite.
- The manager can state why separate automated review agents would not materially reduce risk.

If any criterion is uncertain, use the standard pathway.

## Process

1. Verify repository status, GitHub auth, accepted roadmap item, accepted master plan, quality-gate status, and worktree root.
2. Create or update `implementation-plan.md` from the accepted master plan. Include all phases, ownership, pathway defaults, validation commands, review/checklist requirements, stop conditions, PR plan, and merge policy.
3. For each planned phase, in order:
   - Create or update the phase branch/worktree from current `main`.
   - Refresh only that phase section in `implementation-plan.md`.
   - Choose standard or fast pathway and record the decision.
   - Use `implementation_planner` only when the phase needs additional file-level planning; the planner edits `implementation-plan.md` or the optional centralized `implementation-plans/phase-*.md` file.
   - Use `coding_worker` to implement exactly the current phase, add or update tests/docs, run checks, and fix immediate coding/test failures.
   - Run phase-specific checks first, then the full available repository suite.
   - Complete the pre-submit blocker gate against the implementation plan, diff, PR summary, validation evidence, scope boundaries, assumptions, and risks.
   - Standard pathway: run `code_reviewer` and `science_reviewer` as automated review gates. Record summaries and blocker status in `implementation-plan.md`.
   - Fast pathway: complete the manager checklist in `implementation-plan.md`. If risk surfaces, switch to the standard pathway before merge.
   - Use `blocker_fixer` for failed checks, review blockers, fast-path checklist blockers, or resolvable PR/merge blockers. Allow two automated blocker-fix/re-review cycles for the same blocker.
   - Use `pr_manager` to draft the GitHub PR body from the implementation plan, open the PR, monitor checks, automatically squash-merge when gates pass, and clean up after merge.
   - Update `implementation-plan.md`, `master-plan.md` status, and `docs/roadmap/index.md` as needed.
   - Delete the remote/local phase branch and remove the phase worktree after merge.
4. Continue to the next phase only after the previous phase is merged and cleaned up.

## Review And Merge Gate

A phase must be merged automatically when the selected pathway's automated gates pass and GitHub permits the merge. Human review is not a gate.

All pathways require:

- Phase-specific checks have run.
- The full repository suite has run when available.
- The pre-submit blocker gate has passed.
- The PR body summarizes the roadmap item, master plan, implementation plan, implementation, validation evidence, assumptions, and risks.
- `implementation-plan.md` records workflow details, budget use, commits, GitHub facts, blocker history, review summaries or fast-path checklist, merge result, and cleanup status.
- GitHub allows squash merge or available authority can bypass only a human-review requirement.

Standard pathway additionally requires:

- Automated code review has no unresolved blocker.
- Automated scientific/workflow review has no unresolved blocker.

Fast pathway additionally requires:

- The manager's fast-path checklist confirms that no separate automated review agent is needed.
- No blocker, ambiguity, or expanded scope surfaced during implementation or verification.

The PR manager should use auto-merge when checks are pending and direct squash merge when checks have already passed. If branch protection blocks solely on human review requirements and the managing account has available approval or admin authority, approve, admin-merge, or otherwise force the merge after automated review and validation gates pass. Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.

## Exit Criteria

- All phases in the master plan are merged sequentially, or `implementation-plan.md` explains exactly why the sequence stopped.
- Worktrees and merged branches are cleaned up after each merged phase.
- `implementation-plan.md`, `master-plan.md`, and `docs/roadmap/index.md` reflect the final state.
