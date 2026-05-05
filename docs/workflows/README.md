# rphys Workflow Index

This directory defines the repeatable workflows used to port the legacy rphys implementation into a modern research base library.

## Workflow Set

- `legacy-audit-roadmap.md`: inspect the old repository, map capabilities, and decide what to port, redesign, drop, or defer.
- `component-rfc.md`: turn one roadmap item into a full scientific/software design before implementation.
- `phase-implementation.md`: split an accepted RFC into PR-sized phases, implement in isolated worktrees, review, and merge.
- `scientific-review.md`: review implementation changes for scientific correctness, reproducibility, and pipeline semantics.
- `bootstrap.md`: prepare the repo, GitHub auth, worktree root, and Codex config before porting work begins.

## Operating Model

Repository docs are canonical. GitHub issues and PRs track execution state and link back to the relevant docs.

The main Codex agent is responsible for orchestration and final decisions. Subagents provide bounded work products: evidence gathering, RFC support, phase plans, implementation inside isolated worktrees, and scientific review.

## Required Environment

- Main checkout: `/home/samcantrill/work/rphys`.
- Worktree root: `/home/samcantrill/work/rphys-worktrees`.
- Legacy repo input: `LEGACY_REPO_PATH`.
- GitHub CLI: `gh` authenticated with `gh auth login -h github.com`.
- Codex writable root includes `/home/samcantrill/work/rphys-worktrees`, or the session is launched with `--add-dir /home/samcantrill/work/rphys-worktrees`.

## Default Order

1. Bootstrap repository and workflow files.
2. Run legacy audit and produce roadmap entries.
3. Draft and review a component RFC.
4. Create a phase plan from the accepted RFC.
5. Implement each phase in a separate worktree and PR.
6. Run code review and scientific review.
7. Squash merge, delete branch, and prune worktree.
