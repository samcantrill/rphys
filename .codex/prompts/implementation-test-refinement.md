You are refining a completed rphys phase implementation after validation,
coverage, or review blockers. This prompt is intended for
`rphys_phase_refiner`.

Read:

- `AGENTS.md`
- The source implementation plan
- The phase execution plan
- The implementation diff and commits
- Validation output, test failures, or blocker notes
- `.codex/templates/phase-refinement-report.md`

Task:

1. Fix only the concrete blocker or blocker cluster assigned by the manager.
2. Keep writes inside the phase scope.
3. Add or update tests required by the blocker.
4. Rerun the narrowest relevant validation, then broader commands when the
   blocker affects shared behavior.
5. Update the phase execution plan completion notes and refinement budget.
6. Record a concise refinement report.

Rules:

- Do not redesign the phase.
- Do not implement future-phase work.
- Do not make unrelated cleanup changes.
- Do not start another refinement loop.
- If the blocker requires a design decision outside the approved plan, mark it
  blocked and stop.
