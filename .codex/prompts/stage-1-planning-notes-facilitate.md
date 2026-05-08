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
2. Start the discussion with a comprehensive briefing before asking the maintainer to confirm functionality, behavior, or design principles. The briefing must cover what the work package is, why it exists, what current or future work it impacts or links to, likely public API, documentation, workflow, scientific-contract, and durable-artifact surfaces, why the planning structure appears appropriate, visible constraints, assumptions, risks, and which decisions still need maintainer input.
3. Explicitly invite clarifying questions about that briefing. Answer from repository evidence where possible, state when you are making an assumption, and record resolved clarifications in the planning notes before advancing.
4. Ask small batches of high-impact questions, preferably one to three at a time. Each question should clarify intent, expose a tradeoff, test an assumption, or choose between meaningful structural alternatives.
5. Before asking about a material functionality, behavior, or design-principle decision, give a short decision brief: what is being decided, why it matters, expected impact, relevant tradeoffs, and the recommended default when repository evidence supports one.
6. Update the planning notes after each meaningful decision round with decisions, defaults, open questions, rejected alternatives, assumptions, risks, and next focus.
7. Keep `docs/roadmap/index.md` concise and update it when the work package summary, status, or implementation link changes.
8. Record included functionality, user-visible behavior, agent-visible behavior, defaults, failure behavior, explicit deferrals, and out-of-scope behavior.
9. After functionality and behavior are confirmed, write a context checkpoint in the planning notes that records the locked behavior baseline, defaults, deferrals, open questions, and resume instructions for design-decision review. Compact or reset context only when the current conversation is large enough that doing so materially improves reliability.
10. Before phase shaping, draft a design-decision review queue implied by the confirmed functionality and behavior. Include only decisions that could materially affect maintainability, extensibility, public/scientific/workflow contracts, durable artifact structure, validation strategy, agent behavior, or future expansion paths.
11. Classify each queued decision before discussing it:
    - `recorded recommendation`: meaningful impact, but repository evidence gives a clear default. Record the selected approach, rationale, rejected alternatives, debt, and revisit trigger without asking the maintainer to confirm it individually.
    - `needs discussion`: high impact and no strong repository-supported default. Discuss it with the maintainer before marking it confirmed.
    - `implementation detail`: low maintainability and extensibility impact. Omit it from the user-facing queue or record it as non-blocking context.
12. Present the `needs discussion` queue to the maintainer, ask whether any high-impact decision is missing or mis-scoped, then discuss only those decisions in small batches.
13. For each confirmed design decision, record the selected approach, user feedback if any, rejected alternatives, rationale, maintainability impact, extensibility and future-expansion impact, validation or documentation obligation, accepted debt, and revisit trigger.
14. Shape phases only after the necessary behavior and design decisions are recorded or explicitly deferred with rationale.

Stage gates:

1. Roadmap framing: startup briefing delivered, clarifying questions answered or recorded, target audience and planning priority confirmed.
2. Intent discovery: goals, non-goals, success criteria, constraints, and scientific workflow obligations confirmed.
3. Capability brainstorming: candidate functionality sorted into include, maybe, defer, and out of scope.
4. Functionality and behavior: included behavior, defaults, failure behavior, deferrals, and out-of-scope behavior confirmed.
5. Context checkpoint: locked behavior baseline and resume instructions recorded in the planning notes.
6. Design decision review: decision queue classified, repo-supported recommendations recorded, high-impact unresolved choices discussed with the maintainer, and confirmed decisions recorded.
7. Phase shaping: phase order, boundaries, acceptance criteria, validation expectations, reviewability, and handoff inputs confirmed.

Rules:

- Do not implement code.
- Do not start Stage 2 until planning notes are complete and the user explicitly accepts the work package for master-plan drafting.
- Do not invent requirements not grounded in uploaded context, repository state, or confirmed user decisions.
- Do not ask questions answerable from repository inspection.
- Keep roadmap items at work-package granularity.
- Do not ask the maintainer about low-impact implementation details that the codebase already answers.
- Do not create extra handoff documents by default; keep the briefing, checkpoint, decision queue, recommendations, and handoff inside `planning-notes.md`.
