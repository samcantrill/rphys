# Roadmap Stage Functionality Mapper Handoff

You are `roadmap_stage_functionality_mapper` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap/stage-<N>/planning.md`, and the source files listed in its evidence table.
2. Inspect any additional docs/code/tests needed to understand what this roadmap section should enable.
3. Propose candidate capabilities grounded in the roadmap, feature docs, architecture docs, and current codebase.
4. Sort candidate capabilities into `include`, `maybe`, `defer`, and `out of scope`, with rationale.
5. Define what functionality and behavior means for each relevant module or repo area.
6. Explain what the roadmap section should do, why it exists, and what higher-level codebase capability it unlocks.
7. Break included capabilities into a small set of concrete functional
   requirements.
8. For each requirement, record what, why, scope, user-visible behavior,
   agent/system behavior, capability enabled, impact, out-of-scope behavior,
   validation idea, recommended default, dependencies, and the related
   functionality-agreement queue item.
9. Draft the `Functionality Agreement Queue` in dependency order. For each
   queue item, record related requirement IDs, impact, what is being locked,
   why it matters, recommended answer, trade-offs or rejected branches, repo
   evidence or direct resolution, exact feedback needed, and state.
10. Mark queue items `repo-resolved` when repository evidence answers them,
    `needs maintainer discussion` only when a real ambiguous choice remains, and
    `blocked` only when evidence is missing or contradictory. If repository
    evidence clearly supports one option, record it directly and do not invent a
    question.
11. Update only `docs/roadmap/stage-<N>/planning.md`.
12. Do not ask the maintainer questions and do not implement code.

Return:

- Files read.
- Files changed.
- Module behavior map summary.
- Capability triage summary.
- Functional requirements drafted.
- Functionality-agreement queue drafted, with dependency ordering.
- Requirements recorded as recommended defaults or repo-resolved branches.
- Requirements that need maintainer decision, with the ambiguity and
  recommendation.
- Risks and open questions.
