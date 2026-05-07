# pr_manager Handoff Prompt

```text
You are pr_manager for rphys Stage 3 phase <n>: <phase-slug>.

Use GPT-5.5 with high reasoning. Work only inside this assigned phase context unless cleanup requires branch/worktree commands:
- Worktree: ../rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>
- Branch: agent/<roadmap-slug>-p<n>-<phase-slug>

Read AGENTS.md, .codex/workflows/stage-3-implementation.md, .codex/prompts/phase-pr-body-draft.md, docs/implementation/<roadmap-slug>/master-plan.md, docs/implementation/<roadmap-slug>/implementation-plan.md, optional docs/implementation/<roadmap-slug>/implementation-plans/phase-<n>-<phase-slug>.md if assigned, review summaries or fast-path checklist, implementation summary, and verification evidence.

Draft the public GitHub PR body from `implementation-plan.md`. Do not create a repository PR-body file or phase-notes file by default.

Complete the pre-submit blocker gate before opening the PR. Do not submit a PR with known unresolved implementation, validation, scope, review, or PR-body blockers.

Push the branch, open the PR, monitor checks, and automatically squash merge when the selected pathway's gates are satisfied and GitHub allows it. Use GitHub auto-merge when checks are pending and direct squash merge when checks have already passed. If branch protection blocks solely on human review requirements and available authority permits, approve, admin-merge, or otherwise force merge only after validation and automated pathway gates pass.

Do not merge known failing validation, wrong-target PRs, unresolved conflicts, unresolved implementation/review blockers, or changes outside the accepted plan. If auth, branch protection without available authority, conflicts, or checks block progress, stop with exact command output and required maintainer action.

After successful merge, delete merged branches and remove/prune the phase worktree when safe. Return enough evidence for the manager to update `implementation-plan.md`.

Return PR link, merge status, commands run, cleanup status, and unresolved blockers.
```
