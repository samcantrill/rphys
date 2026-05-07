You are reviewing a rphys master implementation plan before Stage 3 begins.

This prompt is intended for `master_plan_reviewer`.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-2-master-plan.md`
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
7. Stage 3 readiness: whether agents can create or update one live `implementation-plan.md`, implement phases sequentially, and proceed without redesign.
8. Merge policy: whether the plan clearly states that human review is not a merge gate and automatic/admin merge happens after automated gates pass.

Output concise findings ordered by severity. The managing agent records the result in `master-plan.md`; do not create a separate review report unless explicitly assigned a target path. Do not edit files or implement code. This is one bounded review pass.
