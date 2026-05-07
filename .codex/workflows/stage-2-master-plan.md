# Stage 2: Roadmap Item To Master Implementation Plan

## Purpose

Turn one accepted scaffold roadmap work package and confirmed Stage 1 planning notes into a decision-complete master implementation plan.

The master plan is the single Stage 2 implementation design artifact for this work. It must document every design decision needed by implementation agents so Stage 3 can proceed without redesigning the work.

Stage 2 is a collaborative design interrogation, not a quick implementation breakdown. The agent must teach the maintainer how the proposed system will behave, pressure-test every important design choice, and revise the plan as decisions change. The default posture is to keep asking and documenting until the plan explains not only what will be built, but why that structure is maintainable and extensible.

## Inputs

- Accepted roadmap work package from `docs/roadmap/index.md`.
- Stage 1 planning notes from `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Repository constraints from `AGENTS.md`.
- Existing code and documentation discovered by non-mutating inspection.
- `.codex/prompts/master-plan-draft.md`.
- `.codex/prompts/master-plan-refine.md`.
- `.codex/templates/master-implementation-plan.md`.

## Process

1. Read the roadmap item, Stage 1 planning notes, `AGENTS.md`, workflow docs, and relevant repository files.
2. Present a behavioral model of the completed work package before decomposing implementation: inputs, outputs, affected workflows, user/agent interactions, file boundaries, lifecycle, failure behavior, and unsupported behavior.
3. Ask targeted design questions until the plan is decision-complete. Expect multiple rounds. Do not compress unrelated decisions into one broad question when separate answers would affect implementation.
4. For every material choice, explain alternatives and consequences before asking the maintainer to decide.
5. Draft `docs/implementation/<roadmap-slug>/master-plan.md` with `.codex/prompts/master-plan-draft.md`.
6. Refine the same master-plan artifact with `.codex/prompts/master-plan-refine.md`.
7. Update `docs/implementation/<roadmap-slug>/master-plan.md` after each meaningful decision round. The document is the living design ledger.
8. Use `master_plan_planner` agents for bounded design support when helpful.
9. Include implementation phases, ownership boundaries, public APIs or docs allowed to change, standard/fast pathway guidance, verification gates, review or checklist requirements, and rollback/stop conditions.
10. Mark the roadmap item `planning` while drafting.
11. Mark the master plan accepted only after explicit maintainer acceptance.
12. Run the master-plan quality gate before Stage 3 begins.

## Design Interrogation Requirements

The Stage 2 discussion must explicitly resolve or document:

- Behavioral contract: what the completed scaffold does, what it refuses to do, how users and agents experience it, and how failure states are reported.
- Public surfaces: import paths, CLI or script entrypoints, docs, templates, workflow files, config files, environment expectations, and any stable conventions downstream work will rely on.
- Internal structure: modules, directories, ownership boundaries, dependency direction, data flow, control flow, and where future extension points live.
- Maintainability: how the design avoids ambiguous responsibilities, duplicated policy, brittle path assumptions, over-coupling, and unreviewable phases.
- Extensibility: how later domain components can plug in without changing the scaffold's core contracts.
- Validation: tests, static checks, docs checks, TOML/config checks, CI behavior, synthetic fixtures, and acceptance evidence for each phase.
- Agent behavior: which agents act, what documents they read/write, how handoffs remain durable, what the manager decides, and how resume works after context compaction.
- Pathway policy: which phases are standard, which are fast-path eligible, and what condition forces escalation from fast path to standard path.
- Risk handling: blocker loops, stop conditions, rollback strategy, merge policy, auth/protection failures, and design-change escalation.

For each decision, record:

- Decision and status.
- Alternatives considered.
- Rationale.
- Effect on structure, maintainability, extensibility, validation, and user/agent behavior.
- Files or artifacts affected.
- Follow-up verification needed.

## Master Plan Requirements

The plan must specify:

- Work-package goal and success criteria.
- In-scope and out-of-scope behavior.
- Design principles and tradeoffs chosen.
- Behavioral model and user/agent interaction model.
- Decision ledger with alternatives and rationale.
- Structure, maintainability, and extensibility analysis.
- File/module ownership by phase.
- Phase order and branch/worktree names.
- Documentation and public-interface changes.
- Validation and test commands.
- Standard-path code-review and scientific/workflow-review focus.
- Fast-path eligibility criteria and checklist requirements.
- Blocker-fix policy and stop conditions.
- Plan quality gate status, review findings, refinement summary, accepted risks, and confirmation review result.

## Quality Gate

Before Stage 3 starts, the managing agent must run the master-plan quality gate:

1. Review once with `master_plan_reviewer` using `.codex/prompts/master-plan-review.md`.
2. If blocking findings exist, refine once with `master_plan_refiner` using `.codex/prompts/master-plan-quality-refine.md`.
3. Run one confirmation review with `master_plan_reviewer`.
4. Stop before Stage 3 if blocking findings remain.

The gate must check maintainability, extensibility, reviewability, scientific-contract clarity, phase scope, test strategy, accepted debt, unresolved design conflict, and whether Stage 3 agents can proceed without redesign.

## Exit Criteria

- `docs/implementation/<roadmap-slug>/master-plan.md` exists and is accepted.
- The implementation phases are ordered and have disjoint ownership.
- The maintainer has reviewed the behavioral model, key alternatives, and consequences of design choices.
- Public surfaces, internal structure, validation, agent behavior, pathway policy, and stop conditions are documented.
- The master-plan quality gate is passed or blocked with exact findings.
- Stage 3 can create Phase 0 playbooks without asking further design questions.
