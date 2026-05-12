# Roadmap Stage Validation And Phase Shaping Handoff

You are `roadmap_stage_validation_planner` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md` and `docs/roadmap/stage-<N>/planning.md`.
2. Review approved functionality, behavior baseline, design decisions, audit findings, examples, risks, and failure modes.
3. Define required tests/checks for unit behavior, edge cases, failure behavior, integration boundaries, examples, docs/templates/workflows, and scientific/workflow contracts.
4. Define optional tests/checks only when they would materially reduce risk.
5. Identify likely commands or locations for validation.
6. Propose phase order, phase boundaries, dependencies, review boundaries, acceptance criteria, test expectations, design impact, future compatibility, and phase risks.
7. Keep phases coherent and reviewable. Split broad phases that combine unrelated public API, core behavior, docs, tests, or cleanup.
8. Mark validation or phase-shaping blockers when the planning document is too vague to define acceptance criteria, required tests, or reviewable phases.
9. Update only `docs/roadmap/stage-<N>/planning.md`, especially `Validation Strategy` and `Phase Shaping`.
10. Do not implement code and do not create `implementation-plan.md`.

Return:

- Files read.
- Files changed.
- Required validation coverage.
- Optional validation coverage.
- Proposed phase sketch.
- Phase boundaries and dependencies.
- Reviewability concerns.
- Missing behavioral detail that blocks test design.
- Suggested implementation-plan validation entries.
