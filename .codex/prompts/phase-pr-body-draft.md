You are preparing the public PR body for one rphys phase.

This prompt is intended for `pr_manager` after implementation, validation, and the pre-submit blocker gate are ready to run.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-3-implementation.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- `docs/implementation/<roadmap-slug>/implementation-plan.md`
- Optional `docs/implementation/<roadmap-slug>/implementation-plans/phase-<n>-<phase-slug>.md` if assigned
- Review summaries or fast-path checklist in the implementation plan
- Validation evidence and current diff

Task:

1. Complete the pre-submit blocker gate against the implementation plan, diff, PR body, validation evidence, scope boundaries, assumptions, and risks.
2. If any known blocker remains, update `implementation-plan.md` and stop before PR submission.
3. Draft a concise public PR body for GitHub. Do not create a repository PR-body file unless explicitly asked.
4. Keep public PR content reviewer-facing: summary, acceptance criteria, implementation notes, tests/validation, risks, and follow-ups.
5. Keep workflow internals in `implementation-plan.md`: budgets, commits, GitHub facts, blocker history, command details, and cleanup.
6. Push the branch, open the PR with explicit base/head/title when GitHub auth is available, and verify the opened PR target.
7. Monitor checks and automatically squash-merge when validation and pathway gates pass. Use auto-merge when checks are pending and direct squash merge when checks have already passed.
8. If branch protection blocks solely on human review requirements and available authority permits, approve, admin-merge, or otherwise force merge only after automated validation and pathway gates pass.

Rules:

- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
- If auth, branch protection without available authority, conflicts, or checks block progress, record exact evidence in `implementation-plan.md` and stop.
