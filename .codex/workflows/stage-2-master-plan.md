# Stage 2: Roadmap Item To Master Plan

## Purpose

Turn one accepted roadmap work package and confirmed Stage 1 planning notes into a decision-complete live master plan.

Stage 2 should feel direct. The agent reads context, gives the maintainer a compact readout of what matters, asks the next concrete design questions, and updates one live document as decisions settle. The maintainer should not have to keep the workflow on track or manage a pile of handoff documents.

## Default Artifacts

- Input: `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Output: `docs/implementation/<roadmap-slug>/master-plan.md`.
- Quality-gate findings, refinement notes, confirmation results, accepted risks, and blockers are recorded inside `master-plan.md`.
- Do not create separate master-plan review, refinement, context-capsule, or handoff documents by default. Create one only when the maintainer explicitly asks or when a blocker needs evidence that would make `master-plan.md` unreadable.

## Inputs

- Accepted roadmap work package from `docs/roadmap/index.md`.
- Stage 1 planning notes from `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Repository constraints from `AGENTS.md`.
- Existing code and documentation discovered by non-mutating inspection.
- `.codex/templates/master-implementation-plan.md`.

## Process

1. Read the roadmap item, Stage 1 planning notes, `AGENTS.md`, workflow docs, and only the repository files needed to understand the decision surface.
2. Give a concise context readout: current facts, constraints, likely implementation shape, known risks, and the decisions that still need maintainer input.
3. Ask targeted questions. Prefer one to three concrete questions per round. Keep the questions tied to implementation consequences, not workflow ceremony.
4. After each meaningful answer, update the live `master-plan.md`.
5. Use `master_plan_planner` agents only for bounded sidecar analysis. Their findings should be summarized into `master-plan.md`; they should not create durable side documents by default.
6. Mark the roadmap item `planning` while drafting.
7. Mark the master plan accepted only after explicit maintainer acceptance.
8. Run the master-plan quality gate before Stage 3 begins and record the result in `master-plan.md`.

## Required Decisions

The Stage 2 discussion must resolve or explicitly defer:

- Behavioral contract: what the completed work does, refuses to do, and reports on failure.
- Public surfaces: import paths, CLI or script entrypoints, docs, templates, workflow files, config files, environment expectations, and stable conventions.
- Internal structure: modules, directories, ownership boundaries, dependency direction, data flow, and extension points.
- Maintainability and extensibility: responsibilities, coupling avoided, future changes the design should absorb, and debt with revisit triggers.
- Validation: tests, static checks, docs checks, TOML/config checks, CI behavior, safe fixtures, and acceptance evidence.
- Agent behavior: what agents may do, what they read/write, where durable state lives, and how resume works after interruption or context loss.
- Implementation phases: phase order, branch/worktree names, ownership boundaries, standard/fast pathway guidance, and stop conditions.
- Merge policy: phases are implemented sequentially and are not gated by human review; automatic or admin merge is used after automated gates pass.

For each material decision, record the decision, alternatives considered, rationale, maintainability/extensibility impact, validation obligation, and residual risk.

## Quality Gate

Before Stage 3 starts, the managing agent runs a bounded quality gate:

1. Review once with `master_plan_reviewer` using `.codex/prompts/master-plan-review.md`.
2. Record findings directly in the `Master Plan Quality Gate` section of `master-plan.md`.
3. If blocking findings exist, run one refinement pass with `master_plan_refiner` using `.codex/prompts/master-plan-quality-refine.md`; the refiner edits `master-plan.md` directly.
4. Run one confirmation review and record the result in `master-plan.md`.
5. Stop before Stage 3 if blockers remain.

The gate checks maintainability, extensibility, reviewability, scientific-contract clarity, phase scope, test strategy, accepted debt, unresolved design conflict, and whether implementation can proceed without redesign.

## Exit Criteria

- `docs/implementation/<roadmap-slug>/master-plan.md` exists, is decision-complete, and is accepted.
- The implementation phases are ordered, sequential, and have disjoint ownership.
- Public surfaces, internal structure, validation, agent behavior, pathway policy, merge policy, and stop conditions are documented.
- The master-plan quality gate is recorded as passed in the master plan, or blockers are recorded with exact findings.
- Stage 3 can create or update `docs/implementation/<roadmap-slug>/implementation-plan.md` without asking further design questions.
