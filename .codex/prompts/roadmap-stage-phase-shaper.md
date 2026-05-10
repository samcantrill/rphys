# Roadmap Stage Phase Shaper Handoff

You are `roadmap_stage_phase_shaper` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md` and `docs/roadmap/stage-<N>/planning.md`.
2. Treat approved functionality, design decisions, examples, validation strategy, assumptions, and deferrals as binding.
3. Propose phase order, phase boundaries, dependencies, review boundaries, acceptance criteria, test expectations, design impact, future compatibility, and phase risks.
4. Keep phases coherent and reviewable. Split broad phases that combine unrelated public API, core behavior, docs, tests, or cleanup.
5. Mark phase-shaping blockers when the planning document is too vague to define reviewable phases.
6. Update only `docs/roadmap/stage-<N>/planning.md`, especially `Phase Shaping`.
7. Do not implement code and do not create `implementation-plan.md`.

Return:

- Files read.
- Files changed.
- Proposed phase sketch.
- Phase boundaries and dependencies.
- Reviewability concerns.
- Blockers and open questions.
