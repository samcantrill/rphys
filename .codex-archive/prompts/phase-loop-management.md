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
4. Record startup preflight evidence in `implementation-plan.md`: git status, current branch, upstream, worktree root, `gh auth status`, git remote protocol, and any authentication or permission blocker.

GitHub authentication handling:

- Check `gh auth status` before fetch, push, PR creation, PR inspection, merge, or remote branch cleanup.
- In sandboxed Codex sessions, `gh auth status` can report an invalid token when network access is restricted. If it fails with a likely sandbox or network restriction, rerun it with approved network access before marking credentials unavailable.
- If GitHub CLI authentication is still invalid, stop before GitHub-dependent work and ask the user to repair authentication with `gh auth login -h github.com` followed by `gh auth setup-git`.
- If `gh` is authenticated but git remote operations fail through SSH, run or ask to run `gh auth setup-git`, then retry. If the repository still cannot push through SSH, record the exact blocker and either switch `origin` to the HTTPS remote form with user approval or stop for maintainer direction.
- Do not open a PR, push a branch, poll checks, merge, or delete remote branches until authentication and the target remote behavior are verified or the blocker is recorded.

Budget accounting:

- Record gate and blocker budgets in `implementation-plan.md` before assigning work for a phase.
- Before assigning a reviewer, planner, coding worker, PR manager, or blocker fixer, check the current thread and `implementation-plan.md` for evidence that the relevant budget has already been consumed.
- Treat ambiguous history as consumed and ask the maintainer before starting another automated pass.
- Do not use a different agent name, a local review, or a renamed blocker to bypass a consumed budget.
- Allow at most two automated blocker-fix and re-review cycles for the same concrete blocker. A cycle must cite the blocker, bound the write scope, require relevant validation, and update `implementation-plan.md`.
- Stop and report the blocker when it remains after two cycles, no concrete new remedy exists, the fix would change accepted design decisions, or the fix exceeds the assigned phase scope.

Gate terminal actions:

| Gate | Automated budget | Terminal action if blockers remain |
| --- | --- | --- |
| Master-plan quality gate | One review, one refinement pass if needed, one confirmation review | Mark the master plan or next phase blocked, record the exact blocker, and stop |
| Phase planning | One manager or planner pass, plus optional centralized phase plan only when the live plan is too large | Mark the phase blocked if scope, ownership, validation, or pathway cannot be made implementation-ready |
| Phase coding | One coding-worker pass with immediate coding/test fixes | Use blocker-fix budget for concrete in-scope failures, or mark blocked when the issue changes accepted design or exceeds phase scope |
| Pre-submit blocker gate | One manager or PR-manager pass before PR submission | Stop before PR submission until known local implementation, validation, scope, review, and PR-body blockers are resolved or marked blocked |
| Standard-path review | One code review and one scientific/workflow review | Use blocker-fix budget for concrete in-scope blockers, or mark blocked when review blockers remain |
| Fast-path checklist | One manager checklist | Switch to standard pathway when risk, ambiguity, expanded scope, or contract impact surfaces |
| Blocker fixing | Two cycles for the same concrete blocker | Stop when two cycles are used, no concrete new remedy exists, or the blocker is out of scope |
| PR and merge | One PR-manager pass plus remote-only blocker handling | Stop and record GitHub auth, target branch, CI, conflict, or permission blockers only when they prevent every automated approval/admin/force-merge path |

Pathway decision rules:

- Use the standard pathway when a phase touches public import paths, APIs, CLI/config/schema/package behavior, documented contracts, scientific/data/validation/reproducibility/workflow contracts, package/import boundaries, dependencies, security, release, CI, persistence, serialization, provenance, caches, migration, compatibility, concurrency, retry/resume/order behavior, data-loss risk, multi-module behavior, or ambiguous accepted design.
- Use the fast pathway only for narrow, clear, low-risk phases with explicit file ownership, no contract impact, straightforward validation, and a recorded explanation for why separate automated review agents would not materially reduce risk.
- If any criterion is uncertain, choose the standard pathway. If fast-path work later reveals risk, ambiguity, expanded scope, or contract impact, switch to the standard pathway before PR submission or merge.

PR target and submission rules:

- rphys phase PRs target `main` unless the maintainer explicitly records a different target in `implementation-plan.md`.
- Use explicit GitHub CLI flags for PR creation: `--base main`, `--head agent/<roadmap-slug>-p<n>-<phase-slug>`, and an explicit phase title.
- Immediately verify opened or discovered PRs with `gh pr view <PR> --json baseRefName,headRefName,state,url,reviewDecision,statusCheckRollup`. Treat a base other than `main` as a blocker unless the implementation plan records a maintainer-approved exception.
- Keep workflow internals in `implementation-plan.md`, not the public PR body. Public PR bodies should contain only reviewer-facing summary, acceptance criteria, implementation notes, tests/validation, risks, and follow-ups.
- Known implementation, validation, scope, review, and PR-body blockers must be resolved before PR submission. Do not open a PR to let GitHub review or CI rediscover known local blockers.
- After PR submission, handle only blockers that could not reasonably have been known before submission, such as GitHub check state, branch protection, mergeability, or remote permissions.

For each phase:

1. Start the next phase only after the previous phase has merged and cleanup is complete.
2. Create or update the phase branch/worktree from current `main`.
3. Record the phase budget state in `implementation-plan.md`: planning pass, coding pass, pre-submit blocker gate, standard-path reviews or fast-path checklist, blocker-fix cycles used, PR manager pass, merge attempt, branch cleanup, and worktree cleanup.
4. Record pathway decision in `implementation-plan.md`: standard or fast, trigger criteria considered, fast-path checklist if used, and any reason to switch from fast to standard.
5. Record the PR plan in `implementation-plan.md`: base branch, head branch, intended title, merge policy, target-verification command, and wrong-target stop condition.
6. Spawn `implementation_planner` only when the current phase needs additional file-level planning. It edits `implementation-plan.md` or, if too large, `implementation-plans/phase-<n>-<phase-slug>.md`.
7. Spawn `coding_worker` to implement, add/update tests, run targeted checks, fix immediate failures, and run required phase/full-suite checks when available.
8. Complete the pre-submit blocker gate before PR submission against the implementation plan, diff, draft PR body or summary, validation evidence, scope boundaries, assumptions, risks, future-phase exclusions, and selected pathway.
9. Resolve known implementation, validation, scope, review, and PR-body blockers before opening the PR. If a blocker cannot be fixed within budget and phase scope, mark the phase blocked and stop before PR submission.
10. Standard path: run automated code and scientific/workflow reviews. Fast path: complete the manager checklist in `implementation-plan.md` and switch to standard path if risk surfaces.
11. Use `blocker_fixer` for failed checks or concrete blockers only within the recorded two-cycle budget.
12. Use `pr_manager` to draft the GitHub PR body from `implementation-plan.md`, open the PR with explicit base/head/title flags, verify the opened PR target, monitor checks, submit an automated approving review when review-only protection requires approval, use admin/force merge if GitHub rejects automated approval, and auto-squash-merge when validation and pathway gates pass.
13. Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan.
14. Clean up merged branches/worktrees and update roadmap/master-plan/implementation-plan metadata before starting the next phase.

Keep workflow internals in `implementation-plan.md`, not the public PR body.
