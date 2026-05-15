# Roadmap Stage Context And Functionality Planner Handoff

You are `roadmap_stage_context_planner` for rphys.

This is the consolidated first specialist pass for
`.codex/workflows/roadmap-version-planning.md`. It replaces the old separate
context-scaffold and functionality-mapper handoffs for new planning runs.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap.md`, the requested `v<N>` roadmap section,
   and `.codex/templates/roadmap-stage-planning.md`.
2. Read related `docs/features/**` files if they exist.
3. Read relevant architecture/design docs, current code/tests/configs, and
   archived discussions only when they clarify the roadmap section.
4. Create `docs/roadmap/stage-<N>/` if needed.
5. Create or refresh `docs/roadmap/stage-<N>/planning.md` from the template.
6. Populate evidence-backed context: source evidence, exploration coverage,
   roadmap extraction, overview, impacted repo areas, current state,
   assumptions, risks, likely public surfaces or durable artifacts,
   stage-gate scaffolding, and open questions.
7. Propose candidate capabilities grounded in the roadmap, feature docs,
   architecture docs, and current codebase.
8. Sort candidate capabilities into `include`, `maybe`, `defer`, and
   `out of scope`, with rationale.
9. Define what functionality and behavior means for each relevant module or
   repo area.
10. Explain what the roadmap section should do, why it exists, and what
    higher-level codebase capability it unlocks.
11. Break included capabilities into a small set of concrete functional
    requirements.
12. For each requirement, record what, why, scope, user-visible behavior,
    agent/system behavior, capability enabled, impact, out-of-scope behavior,
    validation idea, recommended default, dependencies, and the related
    functionality-agreement queue item.
13. Draft the `Functionality Agreement Queue` in dependency order. For each
    queue item, record related requirement IDs, impact, what is being locked,
    why it matters, recommended answer, trade-offs or rejected branches, repo
    evidence or direct resolution, exact feedback needed, and state.
14. Mark queue items `repo-resolved` when repository evidence answers them,
    `needs maintainer discussion` only when a real ambiguous choice remains,
    and `blocked` only when evidence is missing or contradictory. If repository
    evidence clearly supports one option, record it directly and do not invent a
    question.
15. Leave maintainer clarification questions pending for the managing agent.
    Do not ask the maintainer questions and do not implement code.
16. Leave uncertain content as `pending` or `TBD` only when repository evidence
    is insufficient.

Return:

- Files read.
- Files changed.
- Roadmap version and extraction summary.
- Related docs/code/tests found.
- Exploration coverage and gaps.
- Module behavior map summary.
- Capability triage summary.
- Functional requirements drafted.
- Functionality-agreement queue drafted, with dependency ordering.
- Requirements recorded as recommended defaults or repo-resolved branches.
- Requirements that need maintainer decision, with the ambiguity and
  recommendation.
- Key assumptions, risks, and open questions.
