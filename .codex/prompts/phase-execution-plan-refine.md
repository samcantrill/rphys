You are refining an existing rphys phase execution plan on the expanded path.
This prompt is intended for the `rphys_phase_planner` custom agent.

Read:

- `AGENTS.md`
- The selected implementation plan
- The existing phase execution plan
- Any manager notes explaining the expanded-path trigger
- `.codex/templates/phase-execution-plan.md`

Task:

1. Make the existing phase execution plan scope-complete for safe
   implementation.
2. Clarify only the areas that triggered expanded path: public API,
   scientific contract, import boundary, dependency, serialization, provenance,
   cache, compatibility, cross-module behavior, or ambiguous acceptance
   criteria.
3. Tighten acceptance criteria, suite obligations, stop conditions, and review
   focus.
4. Preserve the assigned branch, worktree, base, target, and phase scope.
5. Mark the refine pass completed and leave implementation/refinement/review
   budgets unused.

Rules:

- Do not implement code.
- Do not broaden scope or add future-phase work.
- Do not produce exhaustive file-by-file rewrite instructions when existing
  code patterns are sufficient.
- Commit only phase execution plan refinements with a `plan:` commit.
