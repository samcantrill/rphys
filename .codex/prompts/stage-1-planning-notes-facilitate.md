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
2. Facilitate the discussion through the Stage 1 gates: roadmap framing, intent discovery, capability brainstorming, functionality and behavior confirmation, context compaction/reset checkpoint, design-decision review, phase shaping, and handoff.
3. Ask small batches of high-impact questions. Each question should clarify intent, expose a tradeoff, test an assumption, or choose between meaningful structural alternatives.
4. Before asking about a material decision, explain the alternatives and their consequences for maintainability, extensibility, scientific workflow safety, validation burden, documentation, and downstream user/agent behavior.
5. Update the planning notes after each meaningful decision round with locked decisions, defaults, open questions, rejected alternatives, assumptions, risks, and next focus.
6. Keep `docs/roadmap/index.md` concise and update it when the work package summary, status, or implementation link changes.
7. Confirm functionality and behavior before design-decision review. Record included functionality, user-visible behavior, agent-visible behavior, defaults, failure behavior, explicit deferrals, and out-of-scope behavior.
8. After functionality and behavior are confirmed, record the context compaction/reset checkpoint. Compact or reset context before design-decision review. If direct compaction is unavailable, stop with a concise resume instruction pointing to this prompt and the planning notes path.
9. After compaction or reset, reload the planning notes and treat confirmed functionality and behavior as stable unless the user explicitly reopens them.
10. Draft the full design-decision review queue implied by confirmed behavior. Ask whether anything is missing, mis-scoped, or should be split before reviewing decisions.
11. Discuss each queued decision with user feedback before marking it confirmed. Record selected approach, rejected alternatives, rationale, maintainability impact, extensibility impact, validation/documentation obligation, accepted debt, and revisit trigger.
12. Shape phases only after the design-decision queue is confirmed or explicitly deferred with rationale.

Rules:

- Do not implement code.
- Do not start Stage 2 until planning notes are complete and the user explicitly accepts the work package for master-plan drafting.
- Do not invent requirements not grounded in uploaded context, repository state, or confirmed user decisions.
- Do not ask questions answerable from repository inspection.
- Keep roadmap items at work-package granularity.
