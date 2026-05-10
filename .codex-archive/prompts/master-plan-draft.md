You are drafting a Stage 2 rphys master implementation plan.

This is the draft pass for the live `docs/implementation/<roadmap-slug>/master-plan.md`. Keep the process direct: read context, summarize the decision surface, draft the plan, prepare the intent/functionality approval gate, classify design decisions, ask concrete questions only for impactful decisions without strong recommendations, and update this one artifact.

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
4. Add or align behavior model, goals, non-goals, intent/functionality approval, design-decision classification, design decisions, maintainer decision walkthrough for only unresolved impactful decisions, deep design review when required, structure/extensibility analysis, public interfaces/documents, validation strategy, phase breakdown, pathway guidance, review requirements, blocker policy, and quality-gate metadata.
5. Prepare an `Intent And Functionality Approval` section and stop for explicit maintainer approval before design discussion.
6. Classify material design decisions as `implementation detail`, `recorded recommendation`, `needs discussion`, or `deferred/blocking`.
7. Record strong recommendations directly. Do not create individual approval packets for every design decision.
8. Create maintainer discussion packets only for decisions that are impactful and lack a strong recommendation, plus any recorded recommendation the maintainer asks to discuss.
9. For foundational packages, public-contract packages, or packages with scientific/runtime API choices that downstream work will rely on, create a `Deep Design Review` section focused on the same unresolved impactful decisions. Include API sketches, invariants, edge cases, failure behavior, extension mechanics, alternatives, downstream impacts, and validation obligations where they matter.
10. Split work into small reviewable phases with disjoint ownership.
11. For each phase, include objective scope, out-of-scope work, acceptance criteria, suite-level test expectations, design impact, future compatibility, alternatives rejected, debt introduced, and reviewability.
12. Record that Stage 3 will create one live `implementation-plan.md`, implement phases strictly one at a time, and auto/admin/force merge after automated gates pass without human review as a default gate.

Rules:

- Do not implement code.
- Do not invent requirements not supported by planning notes, repository state, or confirmed user decisions.
- Surface conflicts and open questions rather than silently choosing around them.
- Do not mark a plan accepted until the intent/functionality baseline is approved, the necessary design discussions are complete, any required deep design review is complete, and the maintainer explicitly accepts the full plan.
- Keep the draft readable and executable; refinement will tighten details.
- Do not create separate review, refinement, context-capsule, execution-playbook, or handoff documents by default.
