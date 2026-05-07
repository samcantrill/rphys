# rphys Scaffold Workflow Index

This directory defines the short user-facing entrypoints for rebuilding `rphys` as a clean base library for remote physiological measurement research.

Keep these entrypoints concise. Canonical behavior lives in `.codex/prompts/`, durable artifact schemas live in `.codex/templates/`, and agent role authority lives in `.codex/agents/`.

## Workflow Set

- `stage-1-roadmap.md`: facilitate uploaded-context planning notes, behavior confirmation, design-decision review, and roadmap updates.
- `stage-2-master-plan.md`: draft, refine, review, and quality-gate one accepted roadmap work package into a decision-complete master implementation plan.
- `stage-3-implementation.md`: run all phases from a quality-gated master plan through worktrees, pathway selection, planning/coding workers, automated checks, PRs, auto-squash-merge, and cleanup.

## Operating Model

Repository docs are canonical. Keep durable planning state lean: `planning-notes.md`, the live `master-plan.md`, and the live `implementation-plan.md`. GitHub PRs track implementation state and link back to those documents. GitHub issues are not used by default.

The main Codex agent is responsible for orchestration, user discussion, approvals, integration, pathway selection, and final judgment. Subagents provide bounded work products: roadmap synthesis, planning-note support, master-plan drafting/refinement/review, implementation-plan refinement, coding and tests inside isolated worktrees, automated review, blocker fixes, and PR management.

Human acceptance is required after Stage 1 behavior/design planning and after Stage 2 master-plan drafting/refinement. Stage 3 proceeds autonomously one phase at a time after the master plan passes its quality gate. Human review is not a merge gate. Stage 3 uses automatic merge, approval, or admin/force merge after automated gates pass when branch protection is blocking only on human review. Stage 3 stops only when authentication, branch protection without available authority, repeated blockers, unresolved checks, merge conflicts, or a required change to accepted design decisions prevents autonomous progress.

## Required Environment

- Main checkout: `/home/samcantrill/work/rphys`.
- Worktree root: `/home/samcantrill/work/rphys-worktrees`.
- GitHub CLI: `gh` authenticated with `gh auth login -h github.com` before autonomous PR creation or merge.
- Codex writable root includes `/home/samcantrill/work/rphys-worktrees`, or the session is launched with `--add-dir /home/samcantrill/work/rphys-worktrees`.
- Core agents should use GPT-5.5 with high reasoning unless a task explicitly calls for a cheaper/default model.

## Default Order

1. Upload or paste project context.
2. Run Stage 1 with `.codex/prompts/stage-1-planning-notes-facilitate.md`; maintain `docs/implementation/<roadmap-slug>/planning-notes.md` and keep `docs/roadmap/index.md` concise.
3. Run Stage 2 directly: read context, give a concise readout, ask targeted design questions, and maintain `docs/implementation/<roadmap-slug>/master-plan.md`.
4. Run the master-plan quality gate with `.codex/prompts/master-plan-review.md`, `.codex/prompts/master-plan-quality-refine.md` if needed, and a confirmation review; record results in `master-plan.md`.
5. After the quality gate passes, run Stage 3.
6. Stage 3 creates or updates `docs/implementation/<roadmap-slug>/implementation-plan.md`.
7. Implement phases sequentially. For each phase, choose the standard or fast pathway, run the planning/coding/check loop, open the PR, auto/admin/force merge after automated gates pass, delete the branch, clean up the worktree, then start the next phase.
