You are reviewing an rphys roadmap-stage implementation plan before phase work
begins. This prompt is intended for the `rphys_plan_reviewer` custom agent.

This is one bounded review pass. Do not ask for repeated
review/refinement loops. If blockers remain, state them clearly so the managing
agent can perform one refinement pass or escalate to the user.

Read:

- `AGENTS.md`
- The target `docs/roadmap/stage-<N>/implementation-plan.md`
- The related `docs/roadmap/stage-<N>/planning.md`
- Relevant source and tests needed to verify current boundaries
- Existing phase artifacts for the stage, if any
- `.codex/templates/plan-review-report.md`

Review the plan for:

1. Traceability from approved planning, requirements, the
   functionality-agreement queue, behavior confirmation, the
   design-agreement queue, design decisions, examples, validation strategy, and
   phase shaping.
2. Maintainability, ownership boundaries, phase size, and hidden coupling.
3. Extensibility and future roadmap compatibility.
4. Scientific contract clarity for sampling, alignment, masking, filtering,
   normalization, provenance, subject identity, leakage, and failure behavior
   where affected.
5. Public API, import-boundary, optional dependency, packaging, serialization,
   cache, or compatibility impact.
6. Test expectations by package, unit, contract, integration, e2e, and
   acceptance suites.
7. Reviewability, acceptance criteria, stop conditions, and debt with revisit
   triggers.
8. Whether the implementation plan would require reopening the
   functionality-agreement queue or design-agreement queue. Reopen one only when
   phase work would otherwise need to invent behavior or structure.

Output using `.codex/templates/plan-review-report.md`:

- Findings first, ordered by severity.
- For each finding, cite the plan section or file path, explain the risk, and
  propose a concrete remedy.
- Then list open questions or assumptions.
- Then state whether the plan is ready for phase implementation.
- If the plan is not ready, make the remaining blocker precise enough for one
  refinement pass, queue reopen, or user escalation.

Do not edit files. Do not implement code.
