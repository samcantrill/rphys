# Phase Implementation Workflow

## Purpose

Implement one accepted RFC through small, reviewable phases. Each phase uses its own git branch and worktree so implementation agents can work independently.

## Preconditions

- RFC is accepted.
- Phase plan exists and is accepted.
- GitHub CLI is authenticated if issues or PRs will be created.
- Worktree root exists at `/home/samcantrill/work/rphys-worktrees`.
- Codex can write to the worktree root.

## Branch And Worktree Setup

Use one phase per branch and worktree:

```bash
mkdir -p /home/samcantrill/work/rphys-worktrees
git fetch --all --prune
git switch main
git pull --ff-only
git worktree add -b agent/<issue>-<component>-p<n>-<slug> ../rphys-worktrees/<issue>-<component>-p<n>-<slug> main
```

If the repository is not yet connected to a valid remote or `main` has no upstream, skip `git pull --ff-only` and record the reason in the phase plan.

## Implementation Process

1. Main agent verifies the accepted RFC and phase plan.
2. Main agent creates the phase worktree and branch.
3. Main agent starts the phase worker in the worktree with exact ownership boundaries.
4. Phase worker implements only the assigned phase.
5. Phase worker runs the tests specified by the phase plan and records results.
6. Main agent reviews the diff and reconciles any conflicts or incomplete work.
7. Scientific reviewer checks the PR against the RFC and legacy evidence.
8. Main agent updates docs, templates, or roadmap status if the phase changes public behavior.
9. Push branch and open PR with `gh pr create`.
10. Squash merge after review.
11. Delete remote/local branch and remove the worktree.

## Phase Worker Handoff

The handoff must include:

- Worktree path and branch.
- RFC path and phase plan path.
- Exact file/module ownership.
- Public APIs allowed to change.
- Tests to add or update.
- Commands to run.
- Expected output format.
- Instruction not to modify unrelated files or other agents' work.

## PR Requirements

Every PR should include:

- Linked issue, RFC, and phase plan.
- Summary of implementation behavior.
- Scientific contract notes.
- Tests run and results.
- Legacy parity evidence where applicable.
- Known gaps and follow-up phases.

## Cleanup

After squash merge:

```bash
git fetch --all --prune
git worktree remove ../rphys-worktrees/<issue>-<component>-p<n>-<slug>
git branch -d agent/<issue>-<component>-p<n>-<slug>
git worktree prune
```

If the branch has unmerged local commits, stop and inspect rather than forcing deletion.
