# Stage 1: Context To Roadmap

## Purpose

Convert a large body of uploaded project context and maintainer discussion into Stage 1 planning notes and the scaffold roadmap for `rphys`.

The roadmap stays concise during Stage 1. The detailed discussion record lives in `docs/implementation/<roadmap-slug>/planning-notes.md`, using `.codex/templates/stage-1-planning-notes.md`. The roadmap should capture coherent work packages, not tiny PR tasks and not vague themes. A good work package is specific enough to plan in Stage 2 and broad enough to produce a meaningful slice of the scaffold.

Stage 1 is direct context-to-questions work. The agent gives the maintainer a comprehensive startup briefing, invites clarifying questions, asks the next concrete questions, records decisions, and moves toward an accepted roadmap work package. Do not make the maintainer manage workflow mechanics.

## Inputs

- Uploaded or pasted project context.
- Maintainer discussion in the current chat.
- Current `docs/roadmap/index.md`.
- Repository constraints from `AGENTS.md`.
- `.codex/prompts/stage-1-planning-notes-facilitate.md`.
- `.codex/templates/stage-1-planning-notes.md`.

## Process

1. Read `AGENTS.md`, `.codex/workflows/README.md`, and `docs/roadmap/index.md`.
2. Create or update `docs/implementation/<roadmap-slug>/planning-notes.md`.
3. Summarize the uploaded context into durable themes, constraints, desired behaviors, validation needs, and unresolved decisions.
4. Start with a comprehensive briefing before asking the maintainer to confirm functionality, behavior, or design direction. Cover what the work package is, why it exists, what it impacts or links to, likely public/scientific/workflow surfaces, durable artifacts, structure rationale, visible constraints, assumptions, and risks.
5. Explicitly invite clarifying questions about the briefing. Answer from repository evidence where possible, and record resolved clarifications in `planning-notes.md` before moving on.
6. Ask one to three high-impact questions per round. Each question should clarify intent, expose a tradeoff, test an assumption, or choose between meaningful structural alternatives.
7. Before each material functionality, behavior, or design-principle question, give a short decision brief: what is being decided, why it matters, expected impact, relevant tradeoffs, and the recommended default when repository evidence supports one.
8. Maintain `planning-notes.md` as the decision ledger. Record accepted decisions, rejected alternatives, open questions, assumptions, risks, defaults, and why the choice matters.
9. After functionality and behavior are confirmed, record a complete context checkpoint in `planning-notes.md` before starting design-decision review. Compact or reset context only when the conversation is large enough that doing so improves reliability.
10. Draft a design-decision review queue limited to choices that could materially affect maintainability, extensibility, public/scientific/workflow contracts, durable artifact structure, validation strategy, or agent behavior.
11. Classify each candidate decision before discussing it:
    - `recorded recommendation`: meaningful impact, but repository evidence gives a clear default. Record the recommendation, rationale, rejected alternatives, debt, and revisit trigger without asking the maintainer to decide it individually.
    - `needs discussion`: high impact and no strong repository-supported default. Discuss it with the maintainer before marking it confirmed.
    - `implementation detail`: low maintainability and extensibility impact. Omit it from the user-facing queue or record it as a non-blocking implementation detail.
12. Use `roadmap_planner` agents only for bounded synthesis tasks when parallel context analysis is useful; fold their output into planning notes instead of creating side documents.
13. Update `docs/roadmap/index.md` when work-package status or summary changes.
14. Keep roadmap items at work-package granularity.
15. Mark a work package `accepted` only after explicit maintainer acceptance.

## Discussion Requirements

The Stage 1 agent must repeatedly cover:

- System behavior: what the scaffold makes possible, how future contributors interact with it, and what behavior is intentionally not supported.
- Structure: package/module boundaries, documentation layout, workflow artifacts, agent responsibilities, and how boundaries reduce coupling.
- Maintainability: which choices minimize churn, hidden dependencies, ambiguous ownership, and future migration pain.
- Extensibility: how future datasets, transforms, models, metrics, training utilities, and analysis tools can be added without redesigning the scaffold.
- Validation: what should be enforced by tests, docs, templates, checks, CI, typed interfaces, or review gates.
- Scientific workflow safety: how the scaffold prevents unclear units, shapes, sampling assumptions, leakage risks, and reproducibility gaps when domain features arrive later.
- Automation behavior: what agents may do autonomously, what must be documented, what stops progress, and what can use the fast path.

For each substantial decision, document:

- Decision.
- Classification as `recorded recommendation`, `needs discussion`, or `implementation detail` when the decision appears in the design-decision review queue.
- Alternatives considered.
- Rationale.
- Impact on maintainability and extensibility.
- Validation or documentation obligation created by the decision.
- Remaining risk or follow-up question.

## Roadmap Item Requirements

Each roadmap work package should include:

- Name and stable slug.
- Status.
- Context evidence from uploaded notes or discussion.
- Target direction and expected behavior.
- Structural impact and affected scaffold boundaries.
- Maintainability/extensibility rationale.
- Validation needs.
- Key decisions and rejected alternatives.
- Link to the master implementation plan when Stage 2 exists.
- Open questions or accepted assumptions.

## Planning Notes Requirements

Stage 1 planning notes should include:

- Current status.
- Roadmap extraction and context evidence.
- Startup briefing, visible assumptions, and resolved clarification questions.
- User intent, success criteria, non-goals, and constraints.
- Stage readbacks after each meaningful exchange.
- Brainstormed capabilities marked include, maybe, defer, or out of scope.
- Confirmed functionality, user-visible behavior, defaults, failure behavior, and explicit deferrals.
- Context checkpoint after functionality and behavior confirmation.
- Design-decision review queue with classification and status.
- Confirmed design decisions with rejected alternatives, maintainability/extensibility impact, accepted debt, and revisit triggers.
- Phase sketch and handoff inputs for Stage 2.

## Exit Criteria

- At least one roadmap work package is accepted.
- The accepted item has enough scope, goals, non-goals, behavioral expectations, structural rationale, validation expectations, and constraints to start Stage 2.
- The maintainer has received a startup briefing, had a chance to ask clarifying questions, and has been shown the expected system behavior and tradeoffs needed to make an informed acceptance decision.
- Major alternatives and their maintainability/extensibility implications are documented.
- The design-decision queue is complete enough that Stage 2 can distinguish accepted design decisions from implementation details.
- Functionality, behavior, major design decisions, assumptions, and validation goals are recorded.
- Deferred or dropped ideas are recorded when they would otherwise be rediscovered.
