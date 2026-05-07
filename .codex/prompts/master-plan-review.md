You are reviewing a rphys master implementation plan before Stage 3 begins.

This prompt is intended for `master_plan_reviewer`.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-2-master-plan.md`
- `.codex/templates/master-plan-review-report.md`
- `docs/roadmap/index.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- Relevant repository files needed to verify boundaries

Review for:

1. Maintainability: unclear ownership, hidden coupling, duplicated policy, brittle path assumptions, over-broad phases, and unnecessary abstractions.
2. Extensibility: missing extension points, too-narrow future paths, over-speculative hooks, and choices that block future domain components.
3. Scientific workflow safety: missing contracts around shapes, units, sampling assumptions, reproducibility, validation, leakage risk, and safe fixtures where relevant.
4. Conflicting design choices: contradictions with `AGENTS.md`, roadmap, planning notes, or repository structure.
5. Technical debt: accepted shortcuts without a revisit trigger.
6. Reviewability: phases too large, refactor mixed with behavior, unclear acceptance criteria, missing suite-level test expectations, or unclear PR evidence.
7. Stage 3 readiness: whether Phase 0 and phase agents can proceed without redesign.

Output using `.codex/templates/master-plan-review-report.md`. Lead with findings ordered by severity. Do not edit files or implement code. This is one bounded review pass.
