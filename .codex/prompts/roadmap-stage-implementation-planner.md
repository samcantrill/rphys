# Roadmap Stage Implementation Planner Handoff

You are `roadmap_stage_implementation_planner` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap/stage-<N>/planning.md`, and `.codex/templates/roadmap-stage-implementation-plan.md`.
2. Treat resolved functionality, approved design decisions, examples, validation strategy, phase shaping, plan quality gate, assumptions, and deferrals as binding.
3. Before creating phases, check design readiness:
   - validation and phase-shaping decision gate is resolved
   - plan quality gate is passed
   - required specialist-pass handoffs are present and current
   - design implication/coherence audit/examples review completed after the design proposal
   - plan quality review checked specialist evidence and unresolved decision packets
   - no design decision is `blocked`
   - no `needs maintainer discussion` decision is unresolved
   - no approval-worthy decision is merely recorded as `pending approval` or `ready for approval`
   - each decision packet that needed maintainer judgment has a recorded maintainer answer and resolution
   - each `auto-approved` decision is traceable to an approved functional requirement
   - each `auto-approved` decision has adversarial review evidence
4. If design readiness fails, create or update only an `Implementation Readiness Blockers` section in `docs/roadmap/stage-<N>/implementation-plan.md`; do not invent phases, phase names, ownership, or validation entries.
5. If design readiness passes, create or update `docs/roadmap/stage-<N>/implementation-plan.md` from the template.
6. Convert the accepted phase shaping from `planning.md` into sequential implementation phases with small, clear ownership.
7. For each phase, record behavior implemented, design decisions applied, likely files/modules owned, dependencies, examples covered, validation, acceptance evidence, risks, assumptions, and stop conditions.
8. Identify any unresolved blocker that prevents implementation without redesign.
9. Do not implement code.

Return:

- Files read.
- Files changed.
- Phase list.
- Ownership boundaries.
- Validation plan.
- Implementation readiness blockers, if any.
- Missing specialist evidence or unresolved maintainer packets, if any.
- Risks, blockers, and open questions.
