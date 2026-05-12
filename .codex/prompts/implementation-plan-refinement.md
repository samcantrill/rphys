You are refining an rphys roadmap-stage implementation plan after a bounded
quality-gate review. This prompt is intended for the `rphys_plan_reviewer` or a
manager-assigned refinement role.

Read:

- `AGENTS.md`
- The target `docs/roadmap/stage-<N>/implementation-plan.md`
- The related `docs/roadmap/stage-<N>/planning.md`
- The plan review findings from `rphys_plan_reviewer`
- `.codex/templates/plan-refinement-summary.md`

Task:

1. Resolve only concrete blockers or concerns found by the review.
2. Preserve approved functionality, design decisions, validation strategy,
   phase shaping, assumptions, and deferrals from `planning.md`.
3. Keep phases small and reviewable.
4. Add or clarify ownership, acceptance criteria, validation expectations,
   scientific contract obligations, stop conditions, and revisit triggers.
5. Do not invent new product behavior, public APIs, or design decisions.
6. Update the Implementation Plan Review section with the refinement result.
7. Record a concise refinement summary using
   `.codex/templates/plan-refinement-summary.md`.

Rules:

- Edit only the selected implementation plan unless the manager explicitly
  assigns another workflow artifact.
- Do not implement code.
- Do not add another automated review loop.
- If a blocker requires changing approved planning decisions, record it as
  blocked and stop for the manager.
