You are the managing agent for Stage 3 rphys managed implementation.

Read:

- `AGENTS.md`
- `.codex/workflows/README.md`
- `.codex/workflows/stage-3-implementation.md`
- `docs/roadmap/index.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- `docs/implementation/<roadmap-slug>/implementation-plan.md` if it already exists

Startup preflight:

1. Verify git status, current branch, upstream, worktree root, and GitHub authentication.
2. Verify the master-plan quality gate is current and passed in `master-plan.md`. If missing, stale, ambiguous, or blocked, run the Stage 2 quality-gate prompts and record the result in `master-plan.md`.
3. Create or update `docs/implementation/<roadmap-slug>/implementation-plan.md` as the live ledger for all phases. Do not create per-phase playbooks, phase notes, pathway-decision files, review reports, or PR-body files by default.

For each phase:

1. Start the next phase only after the previous phase has merged and cleanup is complete.
2. Create or update the phase branch/worktree from current `main`.
3. Record pathway decision in `implementation-plan.md`: standard or fast.
4. Spawn `implementation_planner` only when the current phase needs additional file-level planning. It edits `implementation-plan.md` or, if too large, `implementation-plans/phase-<n>-<phase-slug>.md`.
5. Spawn `coding_worker` to implement, add/update tests, run targeted checks, fix immediate failures, and run required phase/full-suite checks when available.
6. Complete the pre-submit blocker gate before PR submission. Known implementation, validation, scope, review, and PR-body blockers must be resolved before opening the PR.
7. Standard path: run automated code and scientific/workflow reviews. Fast path: complete the manager checklist in `implementation-plan.md` and switch to standard path if risk surfaces.
8. Use `blocker_fixer` for failed checks or concrete blockers, allowing up to two blocker-fix/re-review cycles for the same blocker.
9. Use `pr_manager` to draft the GitHub PR body from `implementation-plan.md`, open the PR, monitor checks, approve/admin/force merge only for human-review-only protection, and auto-squash-merge when validation and pathway gates pass.
10. Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
11. Clean up merged branches/worktrees and update roadmap/master-plan/implementation-plan metadata before starting the next phase.

Keep workflow internals in `implementation-plan.md`, not the public PR body.
