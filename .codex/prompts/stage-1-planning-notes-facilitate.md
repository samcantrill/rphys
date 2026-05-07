You are facilitating Stage 1 rphys scaffold planning.

This prompt turns uploaded project context and maintainer discussion into durable planning notes and concise roadmap updates. The planning notes are not the final implementation plan. They are the decision log and source material for Stage 2.

Read before asking design questions:

- `AGENTS.md`
- `.codex/workflows/README.md`
- `.codex/workflows/stage-1-roadmap.md`
- `.codex/templates/stage-1-planning-notes.md`
- `docs/roadmap/index.md`
- Any uploaded context or existing `docs/implementation/<roadmap-slug>/planning-notes.md`

Task:

1. Create or update `docs/implementation/<roadmap-slug>/planning-notes.md` from `.codex/templates/stage-1-planning-notes.md`.
2. Give a concise context readout before asking questions: what appears true, what is uncertain, and which decisions affect implementation.
3. Ask small batches of high-impact questions, preferably one to three at a time. Each question should clarify intent, expose a tradeoff, test an assumption, or choose between meaningful structural alternatives.
4. Before asking about a material decision, explain only the consequences needed to answer it: maintainability, extensibility, scientific workflow safety, validation burden, documentation, or downstream user/agent behavior.
5. Update the planning notes after each meaningful decision round with decisions, defaults, open questions, rejected alternatives, assumptions, risks, and next focus.
6. Keep `docs/roadmap/index.md` concise and update it when the work package summary, status, or implementation link changes.
7. Record included functionality, user-visible behavior, agent-visible behavior, defaults, failure behavior, explicit deferrals, and out-of-scope behavior.
8. Shape phases after the necessary behavior and design decisions are recorded or explicitly deferred with rationale.

Rules:

- Do not implement code.
- Do not start Stage 2 until planning notes are complete and the user explicitly accepts the work package for master-plan drafting.
- Do not invent requirements not grounded in uploaded context, repository state, or confirmed user decisions.
- Do not ask questions answerable from repository inspection.
- Keep roadmap items at work-package granularity.
- Do not require context compaction, reset, separate design-decision queues, or extra handoff documents by default.
