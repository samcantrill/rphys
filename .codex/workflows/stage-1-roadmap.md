# Stage 1: Context To Roadmap

## Purpose

Convert a large body of uploaded project context and maintainer discussion into Stage 1 planning notes and the scaffold roadmap for `rphys`.

The roadmap stays concise during Stage 1. The detailed discussion record lives in `docs/implementation/<roadmap-slug>/planning-notes.md`, using `.codex/templates/stage-1-planning-notes.md`. The roadmap should capture coherent work packages, not tiny PR tasks and not vague themes. A good work package is specific enough to plan in Stage 2 and broad enough to produce a meaningful slice of the scaffold.

Stage 1 is intentionally discussion-heavy. The agent must help the maintainer understand the emerging system, interrogate intent, compare structural options, and document the consequences of each decision. Do not rush to a polished roadmap. Prefer a long chain of clear questions, explanations, and documentation updates over premature convergence.

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
3. Facilitate the planning stages in `.codex/prompts/stage-1-planning-notes-facilitate.md`.
4. Summarize the uploaded context into durable themes, constraints, desired behaviors, validation needs, and unresolved decisions.
5. Build and explain a working model of the intended system behavior: user workflows, package boundaries, data/control flow, public contracts, extension points, validation strategy, and maintenance risks.
6. Confirm functionality and behavior before design review. Write a complete checkpoint in the planning notes.
7. Compact or reset context before design-decision review. If direct compaction is unavailable, stop with a concise resume instruction pointing to the planning notes path and `.codex/prompts/stage-1-planning-notes-resume.md`.
8. Draft the complete design-decision review queue implied by confirmed behavior, then review each decision with the maintainer.
9. Ask questions in chains. Each round should either clarify intent, expose a tradeoff, test an assumption, or choose between meaningful structural alternatives.
10. Explain the impact of each major option before asking for a decision. Cover maintainability, extensibility, scientific correctness, testing burden, documentation cost, and downstream user experience.
11. Maintain the planning notes as the visible decision ledger. Record accepted decisions, rejected alternatives, open questions, and why the choice matters.
12. Use `roadmap_planner` agents only for bounded synthesis tasks when parallel context analysis is useful.
13. Update `docs/roadmap/index.md` when work-package status or summary changes; update planning notes after each meaningful decision round.
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

- Stage gates and current stage.
- Roadmap extraction and context evidence.
- User intent, success criteria, non-goals, and constraints.
- Stage readbacks after each meaningful exchange.
- Brainstormed capabilities marked include, maybe, defer, or out of scope.
- Confirmed functionality, user-visible behavior, defaults, failure behavior, and explicit deferrals.
- Mandatory functionality/behavior checkpoint and compact/reset resume instruction.
- Design-decision review queue with decision statuses.
- Confirmed design decisions with rejected alternatives, maintainability/extensibility impact, accepted debt, and revisit triggers.
- Phase sketch and handoff inputs for Stage 2.

## Exit Criteria

- At least one roadmap work package is accepted.
- The accepted item has enough scope, goals, non-goals, behavioral expectations, structural rationale, validation expectations, and constraints to start Stage 2.
- The maintainer has been shown the expected system behavior and tradeoffs in enough detail to make an informed acceptance decision.
- Major alternatives and their maintainability/extensibility implications are documented.
- Functionality and behavior are confirmed, checkpointed, and followed by context compaction or reset before design-decision review.
- The design-decision review queue has been reviewed with the maintainer.
- Deferred or dropped ideas are recorded when they would otherwise be rediscovered.
