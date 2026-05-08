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
2. Also check future-phase exclusions and confirm the selected pathway is still valid. Fast-path work that now has risk, ambiguity, expanded scope, or contract impact must switch to the standard pathway before PR submission or merge.
3. If any known local blocker remains, update `implementation-plan.md` and stop before PR submission.
4. Draft a concise public PR body for GitHub. Do not create a repository PR-body file unless explicitly asked.
5. Keep public PR content reviewer-facing: summary, acceptance criteria, implementation notes, tests/validation, risks, and follow-ups.
6. Keep workflow internals in `implementation-plan.md`: budgets, commits, GitHub facts, blocker history, command details, and cleanup.
7. Push the branch, open the PR with explicit `--base main`, `--head agent/<roadmap-slug>-p<n>-<phase-slug>`, and `--title "<work package> - Phase <n>: <phase summary>"` flags when GitHub auth is available.
8. Verify the opened PR target with `gh pr view <PR> --json baseRefName,headRefName,state,url,reviewDecision,statusCheckRollup`; a base other than `main` is a blocker unless a maintainer-approved exception is recorded.
9. Monitor checks and automatically squash-merge when validation and pathway gates pass. Use auto-merge when checks are pending and direct squash merge when checks have already passed.
10. If branch protection blocks solely on human review requirements and available authority permits, approve, admin-merge, or otherwise force merge only after automated validation and pathway gates pass.

Rules:

- Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
- After PR submission, handle only remote-only blockers that could not reasonably have been known locally, such as GitHub checks, branch protection, mergeability, or permissions.
- If auth, branch protection without available authority, conflicts, or checks block progress, record exact evidence in `implementation-plan.md` and stop.
