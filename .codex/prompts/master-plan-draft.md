You are drafting a Stage 2 rphys master implementation plan.

This is the draft pass for the live `docs/implementation/<roadmap-slug>/master-plan.md`. Keep the process direct: read context, summarize the decision surface, ask concrete questions when needed, and update this one artifact.

Read:

- `AGENTS.md`
- `.codex/workflows/README.md`
- `.codex/workflows/stage-2-master-plan.md`
- `.codex/templates/master-implementation-plan.md`
- `docs/roadmap/index.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- Relevant repository files needed to understand current boundaries

Task:

1. Create or update `docs/implementation/<roadmap-slug>/master-plan.md` from `.codex/templates/master-implementation-plan.md`.
2. Use the completed Stage 1 planning notes as the primary source.
3. Preserve confirmed functionality, behavior, design decisions, rejected alternatives, debt, and revisit triggers.
4. Add or align behavior model, goals, non-goals, design decisions, structure/extensibility analysis, public interfaces/documents, validation strategy, phase breakdown, pathway guidance, review requirements, blocker policy, and quality-gate metadata.
5. Split work into small reviewable phases with disjoint ownership.
6. For each phase, include objective scope, out-of-scope work, acceptance criteria, suite-level test expectations, design impact, future compatibility, alternatives rejected, debt introduced, and reviewability.
7. Record that Stage 3 will create one live `implementation-plan.md`, implement phases strictly one at a time, and auto/admin/force merge after automated gates pass without human review as a default gate.

Rules:

- Do not implement code.
- Do not invent requirements not supported by planning notes, repository state, or confirmed user decisions.
- Surface conflicts and open questions rather than silently choosing around them.
- Keep the draft readable and executable; refinement will tighten details.
- Do not create separate review, refinement, context-capsule, execution-playbook, or handoff documents by default.
