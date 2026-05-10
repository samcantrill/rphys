# Roadmap Stage Validation Planner Handoff

You are `roadmap_stage_validation_planner` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md` and `docs/roadmap/stage-<N>/planning.md`.
2. Review approved functionality, behavior baseline, design decisions, audit findings, examples, risks, and failure modes.
3. Define required tests/checks for unit behavior, edge cases, failure behavior, integration boundaries, examples, docs/templates/workflows, and scientific/workflow contracts.
4. Define optional tests/checks only when they would materially reduce risk.
5. Identify likely commands or locations for validation.
6. Update only `docs/roadmap/stage-<N>/planning.md`, especially `Validation Strategy`.
7. Do not implement code.

Return:

- Files read.
- Files changed.
- Required validation coverage.
- Optional validation coverage.
- Missing behavioral detail that blocks test design.
- Suggested implementation-plan validation entries.
