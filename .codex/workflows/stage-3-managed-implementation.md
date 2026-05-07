# Stage 3: Managed Implementation

## Purpose

Implement all phases from an accepted master implementation plan using a managing agent, isolated git worktrees, durable handoffs, pathway-specific planning and coding workers, automated checks, blocker-fix loops, PRs, auto-squash-merge, and cleanup.

## Preconditions

- Roadmap work package is accepted.
- `docs/implementation/<roadmap-slug>/master-plan.md` is accepted.
- The master-plan quality gate has passed for the current master-plan content.
- `gh auth status` passes if PR creation or merge will be attempted.
- `/home/samcantrill/work/rphys-worktrees` exists and is writable.
- `main` is the foreground branch and tracks the intended upstream, or the deviation is documented.

## Canonical Prompt

Use `.codex/prompts/phase-loop-management.md` for Stage 3 management.

## Branch And Worktree Naming

- Branch: `agent/<roadmap-slug>-p<n>-<phase-slug>`.
- Worktree: `../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>`.

Phase 0 is a planning preflight and does not implement code. Implementation phases start after the Phase 0 handoff documents exist.

## Pathway Selection

Before each implementation phase, the managing agent chooses and records the pathway in `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/pathway-decision.md`.

Use the standard pathway when a phase touches public interfaces, package structure, dependency/configuration behavior, CI behavior, tests used as public contracts, scientific/workflow contracts, multi-module behavior, or any design decision with meaningful downstream impact.

Use the fast pathway only when all of these are true:

- The phase is narrowly scoped and has clear file ownership.
- The execution playbook already contains enough implementation detail.
- No public import path, API, CLI, config, schema, package behavior, or documented contract changes.
- No scientific, data, validation, reproducibility, or workflow contract changes.
- No dependency, security, release, or CI behavior changes.
- Verification is straightforward and can be completed with targeted checks plus the available full suite.
- The manager can state why separate review agents would not materially reduce risk.

If any criterion is uncertain, use the standard pathway.

## Process

1. Managing agent verifies repository status, GitHub auth, accepted roadmap item, accepted master plan, quality-gate evidence, and worktree root.
2. If the quality gate is missing, stale, ambiguous, or not passed, run the Stage 2 quality-gate sequence before selecting a phase.
3. Managing agent runs Phase 0:
   - Spawn `phase0_planner` to review the master plan and produce a compact context capsule.
   - Spawn `execution_playbook_writer` to expand the capsule into one execution playbook per planned phase.
   - Store playbooks under `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/execution-playbook.md`.
4. Managing agent starts the first implementation phase branch/worktree.
5. Commit Phase 0 playbooks as the first commit on the first implementation phase branch.
6. For each planned phase:
   - Create or update the phase branch/worktree from current `main`.
   - Choose standard pathway or fast pathway and record the decision.
   - Spawn `implementation_planner` to draft or refine the phase implementation plan from the execution playbook. In the fast pathway, this is a brief checklist-style refinement; in the standard pathway, it is a detailed plan.
   - Spawn `coding_worker` to execute the implementation plan, write or update tests, run checks, and fix immediate coding/test failures.
   - Require milestone commits for planning docs, implementation, tests, fixes, and cleanup.
   - Run phase-specific checks first, then the full available repository suite.
   - Complete the pre-submit blocker gate against the execution playbook, implementation plan, diff, public PR body, phase notes, validation evidence, scope boundaries, assumptions, and risks. Do not submit a PR with known unresolved blockers.
   - In the standard pathway, spawn `code_reviewer` and `science_reviewer`.
   - In the fast pathway, the manager completes the fast-path checklist instead of spawning separate review agents. If the checklist surfaces risk, switch to the standard pathway before merge.
   - Spawn `blocker_fixer` for failed checks, review blockers, fast-path checklist blockers, or resolvable PR/merge blockers.
   - Allow two automated blocker-fix/re-review cycles for the same blocker.
   - Spawn `pr_manager` with `.codex/prompts/phase-pr-body-draft.md` to draft the public PR body, update internal phase notes, open the PR, monitor checks, enable or perform auto-squash-merge, and clean up after merge.
   - Delete the remote/local phase branch and remove the phase worktree after merge.
7. Update `docs/roadmap/index.md` and implementation documents as phases progress.

## Review And Merge Gate

A phase must be merged automatically when the selected pathway's gates pass and GitHub permits the merge. Human review is not a gate.

All pathways require:

- Phase-specific checks have run.
- The full repository suite has run when available.
- The pre-submit blocker gate has passed.
- Public PR body links or summarizes the roadmap item, master plan, execution playbook, implementation plan, review documents or fast-path checklist, and verification evidence.
- Internal phase notes record workflow details, budget use, commits, GitHub facts, blocker history, and cleanup status.
- GitHub allows the squash merge.

Standard pathway additionally requires:

- Code review has no unresolved blocker.
- Scientific/workflow review has no unresolved blocker.

Fast pathway additionally requires:

- The manager's fast-path checklist confirms that no separate review agent is needed.
- No blocker, ambiguity, or expanded scope surfaced during implementation or verification.

The PR manager should use auto-merge when checks are pending and direct squash merge when checks have already passed. If branch protection blocks solely on review requirements and the managing account has available authority, the manager may approve or admin-merge after automated review and validation gates pass. Do not merge known failing validation, wrong-target PRs, unresolved conflicts, or unresolved implementation/review blockers.

## Exit Criteria

- All phases in the master plan are merged or an explicit blocker report explains why implementation stopped.
- Worktrees and merged branches are cleaned up.
- The roadmap item is updated to `merged`, `deferred`, or a clearly documented partial state.
