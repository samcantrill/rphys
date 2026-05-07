You are the managing agent for Stage 3 rphys managed implementation.

Read:

- `AGENTS.md`
- `.codex/workflows/README.md`
- `.codex/workflows/stage-3-managed-implementation.md`
- `.codex/templates/README.md`
- `docs/roadmap/index.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- Existing phase documents under `docs/implementation/<roadmap-slug>/phase-*`

Startup preflight:

1. Verify git status, current branch, upstream, worktree root, and GitHub authentication.
2. Verify the master-plan quality gate is current and passed. If missing, stale, ambiguous, or blocked, run the Stage 2 quality-gate prompts before phase selection.
3. Run Phase 0: `phase0_planner` creates a compact context capsule; `execution_playbook_writer` expands it into execution playbooks for all phases.

For each phase:

1. Create or update the phase branch/worktree from current `main`.
2. Record pathway decision: standard or fast.
3. Spawn `implementation_planner` to create or refine `implementation-plan.md` and, when fast path is chosen, `fast-path-checklist.md`.
4. Spawn `coding_worker` to implement, add/update tests, run targeted checks, fix immediate failures, and run required phase/full-suite checks when available.
5. Complete the pre-submit blocker gate before PR submission. Known implementation, validation, scope, review, and PR-body blockers must be resolved before opening the PR.
6. Standard path: run code and scientific/workflow reviews. Fast path: complete the manager checklist and switch to standard path if risk surfaces.
7. Use `blocker_fixer` for failed checks or concrete blockers, allowing up to two blocker-fix/re-review cycles for the same blocker.
8. Use `pr_manager` to write public PR body, update internal phase notes, open the PR, monitor checks, approve if needed, and auto-squash-merge when validation and pathway gates pass.
9. Do not merge known failing validation, wrong-target PRs, unresolved conflicts, or unresolved implementation/review blockers.
10. Clean up merged branches/worktrees and update roadmap/master-plan/phase metadata.

Keep workflow internals in phase notes, not the public PR body.
