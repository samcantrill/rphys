You are preparing the public PR body and internal phase notes for one rphys phase.

This prompt is intended for `pr_manager` after implementation, validation, and the pre-submit blocker gate are ready to run.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-3-managed-implementation.md`
- `.codex/templates/phase-pr-body.md`
- `.codex/templates/phase-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/execution-playbook.md`
- `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/implementation-plan.md`
- Review documents or fast-path checklist
- Validation evidence and current diff

Task:

1. Complete the pre-submit blocker gate against the execution playbook, implementation plan, diff, PR body, validation evidence, scope boundaries, assumptions, and risks.
2. If any known blocker remains, update phase notes and stop before PR submission.
3. Create or update the public PR body at `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/pr-body.md` using `.codex/templates/phase-pr-body.md`.
4. Create or update internal phase notes at `docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/phase-notes.md` using `.codex/templates/phase-notes.md`.
5. Keep public PR content reviewer-facing: summary, acceptance criteria, implementation notes, tests/validation, risks, and follow-ups.
6. Keep workflow internals in phase notes: budgets, commits, GitHub facts, blocker history, command details, and cleanup.
7. Push the branch, open the PR with explicit base/head/title when GitHub auth is available, and verify the opened PR target.
8. Monitor checks and automatically squash-merge when validation and pathway gates pass. Use auto-merge when checks are pending and direct squash merge when checks have already passed.

Rules:

- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, or unresolved implementation/review blockers.
- If branch protection blocks solely on review requirements and available authority permits, approve or admin-merge only after automated review and validation gates pass.
- If auth, branch protection, conflicts, or checks block progress, record exact evidence in phase notes and stop.
