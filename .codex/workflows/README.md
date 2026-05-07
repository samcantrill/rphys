# rphys Scaffold Workflow Index

This directory defines the short user-facing entrypoints for rebuilding `rphys` as a clean base library for remote physiological measurement research.

Keep these entrypoints concise. Canonical behavior lives in `.codex/prompts/`, durable artifact schemas live in `.codex/templates/`, and agent role authority lives in `.codex/agents/`.

## Workflow Set

- `stage-1-roadmap.md`: facilitate uploaded-context planning notes, behavior confirmation, design-decision review, and roadmap updates.
- `stage-2-master-plan.md`: draft, refine, review, and quality-gate one accepted roadmap work package into a decision-complete master implementation plan.
- `stage-3-managed-implementation.md`: run all phases from a quality-gated master plan through worktrees, pathway selection, planning/coding workers, automated checks, PRs, auto-squash-merge, and cleanup.

## Operating Model

Repository docs are canonical. GitHub PRs track implementation state and link back to the relevant roadmap, planning notes, master plan, handoff, review, PR body, phase notes, and verification documents. GitHub issues are not used by default.

The main Codex agent is responsible for orchestration, user discussion, approvals, integration, pathway selection, and final judgment. Subagents provide bounded work products: roadmap synthesis, planning-note support, master-plan drafting/refinement/review, Phase 0 execution playbooks, phase implementation planning, coding and tests inside isolated worktrees, optional review, blocker fixes, and PR management.

Human acceptance is required after Stage 1 behavior/design planning and after Stage 2 master-plan drafting/refinement. Stage 3 proceeds autonomously across all planned phases after the master plan passes its quality gate. Human review is not a merge gate. Stage 3 stops only when authentication, branch protection, repeated blockers, unresolved checks, or a required change to accepted design decisions prevents autonomous progress.

## Required Environment

- Main checkout: `/home/samcantrill/work/rphys`.
- Worktree root: `/home/samcantrill/work/rphys-worktrees`.
- GitHub CLI: `gh` authenticated with `gh auth login -h github.com` before autonomous PR creation or merge.
- Codex writable root includes `/home/samcantrill/work/rphys-worktrees`, or the session is launched with `--add-dir /home/samcantrill/work/rphys-worktrees`.
- Core agents should use GPT-5.5 with high reasoning unless a task explicitly calls for a cheaper/default model.

## Default Order

1. Upload or paste project context.
2. Run Stage 1 with `.codex/prompts/stage-1-planning-notes-facilitate.md`; maintain `docs/implementation/<roadmap-slug>/planning-notes.md` and keep `docs/roadmap/index.md` concise.
3. Run Stage 2 with `.codex/prompts/master-plan-draft.md` and `.codex/prompts/master-plan-refine.md`; produce `docs/implementation/<roadmap-slug>/master-plan.md`.
4. Run the master-plan quality gate with `.codex/prompts/master-plan-review.md`, `.codex/prompts/master-plan-quality-refine.md` if needed, and a confirmation review.
5. After the quality gate passes, run Stage 3.
6. Stage 3 creates Phase 0 execution playbooks, then implements each phase in a separate branch and worktree.
7. For each phase, choose the standard or fast pathway, run the required planning/coding/check loop, prepare the public PR body with `.codex/prompts/phase-pr-body-draft.md`, auto-merge the PR when GitHub permits, delete the branch, and clean up the worktree.
