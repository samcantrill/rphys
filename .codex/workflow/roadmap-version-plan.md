# Roadmap Version To Implementation Plan

Use this entrypoint as:

```text
@.codex/workflow/roadmap-version-plan.md | @docs/roadmap.md v<N>
```

`v<N>` maps to `docs/roadmap/stage-<N>/`.

## Goal

Convert one roadmap version into an approved implementation plan. The managing agent should discuss decisions with the maintainer only after specialist subagents have explored the repository, drafted functional requirements, proposed implementation shape, and pressure-tested design implications.

## Inputs

- `AGENTS.md`
- `docs/roadmap.md`
- Selected roadmap version `v<N>`
- `docs/features/**`, if present
- Current docs, code, tests, configs, and archived discussions that clarify intent
- Existing files under `docs/roadmap/stage-<N>/`, if any
- Templates:
  - `.codex/templates/roadmap-stage-planning.md`
  - `.codex/templates/roadmap-stage-implementation-plan.md`

## Outputs

- `docs/roadmap/stage-<N>/planning.md`
- `docs/roadmap/stage-<N>/implementation-plan.md`

Keep discussion records, approvals, defaults, concerns, validation findings, examples, and implementation-plan review notes inside those two files unless the maintainer asks for another artifact.

## Operating Rules

- The managing agent owns synthesis, maintainer discussion, approvals, conflict resolution, and final judgment.
- Subagents are bounded helpers with sequential write ownership. Do not let two subagents edit `planning.md` at the same time.
- Each subagent must follow its prompt exactly and return concise evidence: files read, files changed, decisions, risks, open questions, and recommended next gate.
- Update `planning.md` after each meaningful discussion round, including a `Stage Readbacks` row for every completed gate.
- Ask maintainer questions in small decision packets.
- Auto-approved design decisions must still be recorded. They may skip individual maintainer discussion only when they are low impact, clearly recommended by repository evidence and rphys design principles, and pass adversarial review with no meaningful refactor risk.
- Treat user workflow feedback as process input. Route reusable workflow feedback to `.codex` workflow/prompt/template/agent artifacts; route current-session facilitation preferences to `planning.md`; keep both separate from product requirements.
- Do not implement code in this workflow.
- Do not move to the next gate without explicit maintainer approval.
- If manual context compaction is unavailable, write a resume checkpoint and ask the maintainer to continue in a fresh chat with the same invocation plus the current artifact path.

## Agent Passes

Use these role prompts and agent definitions:

| Pass | Agent | Prompt | Writes |
| --- | --- | --- | --- |
| Context scaffold | `roadmap_stage_context_planner` | `.codex/prompts/roadmap-stage-context-planner.md` | `planning.md` |
| Functionality map | `roadmap_stage_functionality_mapper` | `.codex/prompts/roadmap-stage-functionality-mapper.md` | `planning.md` |
| Design proposal | `roadmap_stage_design_proposer` | `.codex/prompts/roadmap-stage-design-proposer.md` | `planning.md` |
| Design implication review | `roadmap_stage_design_implication_reviewer` | `.codex/prompts/roadmap-stage-design-implication-reviewer.md` | `planning.md` |
| Functionality/decision audit | `roadmap_stage_functionality_decision_auditor` | `.codex/prompts/roadmap-stage-functionality-decision-auditor.md` | `planning.md` |
| Validation planning | `roadmap_stage_validation_planner` | `.codex/prompts/roadmap-stage-validation-planner.md` | `planning.md` |
| Phase shaping | `roadmap_stage_phase_shaper` | `.codex/prompts/roadmap-stage-phase-shaper.md` | `planning.md` |
| Plan quality review | `roadmap_stage_plan_quality_reviewer` | `.codex/prompts/roadmap-stage-plan-quality-reviewer.md` | `planning.md` |
| Implementation planning | `roadmap_stage_implementation_planner` | `.codex/prompts/roadmap-stage-implementation-planner.md` | `implementation-plan.md` |

## Stages

### 1. Context Scaffold

Spawn `roadmap_stage_context_planner`.

The subagent must:

1. Read the selected roadmap version, related feature docs if present, relevant architecture/design docs, code/tests/configs, and archived discussions only when they clarify intent.
2. Create `docs/roadmap/stage-<N>/` if needed.
3. Create or refresh `planning.md` from the planning template.
4. Record source evidence, exploration coverage, roadmap extraction, version overview, likely impacted modules, known constraints, assumptions, and open questions.
5. Stop without asking the maintainer questions.

The managing agent then gives a comprehensive briefing and explicitly invites clarifying questions. Record resolved clarifications in `planning.md` before continuing.

Gate: roadmap briefing delivered, clarification window completed, user-visible outcome, target audience, and planning priority or optimization target confirmed.

### 2. Capability Triage And Module Behavior Discovery

Spawn `roadmap_stage_functionality_mapper`.

The subagent must:

1. Read `planning.md` and the same source set needed to understand the roadmap section.
2. Propose candidate capabilities and sort them into `include`, `maybe`, `defer`, and `out of scope`.
3. Define what functionality and behavior means for each relevant module.
4. Explain what the roadmap section should do and what it enables in the codebase.
5. Break included capabilities into a small set of concrete functional requirements.
6. Record capability triage, module behavior, and requirement packets in `planning.md`.

The managing agent then briefs the maintainer on the capability triage, stage behavior, why it exists, what modules it affects, what it enables, non-goals, and uncertainty.

Gate: wait for approval to discuss functionality and behavior.

### 3. Functional Requirement Discussion

Walk through each functional requirement in `planning.md`.

Use this packet shape:

- What:
- Why:
- Scope:
- User-visible behavior:
- Agent/system behavior:
- Codebase capability enabled:
- Impact:
- Out of scope:
- Validation:
- Recommendation:
- Decision requested:

Record each answer immediately in `planning.md`.

Gate: functionality and behavior baseline approved.

Checkpoint: update `planning.md` with a resume note, then compact context or ask for a fresh-chat continuation if compaction is unavailable.

### 4. Design Proposal

Spawn `roadmap_stage_design_proposer`.

The subagent must:

1. Read the approved behavior baseline, architecture/style docs, public contracts, current code/tests, and relevant archived material.
2. Infer the likely implementation approach needed to satisfy the functionality.
3. Draft likely modules, classes, functions, interfaces, data flow, and boundaries.
4. Define design decisions based on that proposed implementation approach.
5. Classify each decision as `auto-approved candidate`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`.
6. Nominate `auto-approved candidate` only when all criteria hold:
   - no public API, import-path, schema, config, scientific/workflow, dependency, serialization, persistence, or compatibility impact
   - localized implementation choice with straightforward validation
   - consistent with approved behavior and rphys design principles
   - traceable to an approved functional requirement
   - low future refactor risk and no meaningful downstream extension consequence
7. Record options, recommendation, adversarial assumptions considered, validation/documentation obligation, and residual risk in `planning.md`.

### 5. Deep Design Implication Review

Spawn `roadmap_stage_design_implication_reviewer`.

The subagent must:

1. Review the proposed design decisions against the approved functionality.
2. Pressure-test modularity, decoupling, base classes/protocols, inheritance or composition, future extension, maintainability, complexity, and future refactor risk.
3. Try to overturn every `auto-approved candidate` using adversarial examples and refactor-risk analysis.
4. Identify unclear contracts, accidental coupling, missing extension points, over-generalization, under-specified failure behavior, and decisions that conflict with rphys architecture.
5. Reclassify decisions as `auto-approved`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`.
6. Update `planning.md` with findings, recommended revisions, and design packets that need maintainer discussion.

### 6. Design Decision Discussion

The managing agent reconciles the design proposal and implication review, then walks the maintainer through each material design decision.
Discuss `needs maintainer discussion`, `blocked`, and any `recorded recommendation` with notable trade-offs. Summarize `auto-approved` decisions as a group rather than asking for individual approval.

Use this packet shape:

- What:
- Why:
- Proposed implementation shape:
- Impact:
- Options:
- Recommendation:
- Pros/cons:
- Limitation or trade-off:
- Validation/documentation obligation:
- Residual risk:
- Decision requested:

Record each answer immediately in `planning.md`.

Gate: design decisions approved, with no unresolved `blocked` decisions and no unresolved `needs maintainer discussion` decisions.

Checkpoint: update `planning.md` with a resume note, then compact context or ask for a fresh-chat continuation if compaction is unavailable.

### 7. Functionality/Decision Audit And Examples

Spawn `roadmap_stage_functionality_decision_auditor`.

The subagent must:

1. Review approved functionality, design decisions, implication review, assumptions, and deferrals.
2. Verify that auto-approved decisions remain traceable to approved behavior and passed adversarial review.
3. Verify that included capabilities map to requirements, design decisions, examples, and validation needs.
4. Find conflicts, missing requirements, decisions not supported by behavior, excessive scope, and unclear failure modes.
5. Propose project-context examples that demonstrate the functionality across the intended workflow.
6. Update `planning.md` with audit findings, resolved or unresolved concerns, and example/demo candidates.

The managing agent briefs the maintainer on the behavior being validated and the examples that will demonstrate it.

Gate: planning document and example set approved for validation planning.

### 8. Validation Strategy

Spawn `roadmap_stage_validation_planner`.

The subagent must:

1. Review approved functionality, design decisions, audit findings, and examples.
2. Define tests and checks for behavior, edge cases, failure modes, integration boundaries, examples, docs/templates/workflows, and scientific/workflow contracts.
3. Update `planning.md` with required and optional validation coverage.

The managing agent reconciles findings, records the accepted validation strategy in `planning.md`, and asks for approval.

Gate: validation strategy approved.

### 9. Phase Shaping

Spawn `roadmap_stage_phase_shaper`.

The subagent must:

1. Review approved functionality, design decisions, examples, validation strategy, assumptions, and deferrals.
2. Propose implementation phase order, phase boundaries, dependencies, review boundaries, acceptance criteria, test expectations, design impact, future compatibility, and phase risks.
3. Keep phases reviewable and coherent; split broad phases before they can become implementation-plan work.
4. Update `planning.md` with the phase sketch.

The managing agent discusses phase order, granularity, dependencies, and review boundaries with the maintainer.

Gate: phase shaping approved.

### 10. Plan Quality Gate

Spawn `roadmap_stage_plan_quality_reviewer`.

The subagent must:

1. Review `planning.md` for traceability from roadmap extraction through capabilities, requirements, design decisions, examples, validation, and phase shaping.
2. Check extensibility, maintainability, scientific/workflow contract clarity, plan reviewability, unresolved ambiguity, unresolved `blocked` decisions, and unresolved `needs maintainer discussion` decisions.
3. Record pass/block findings in `planning.md`.

Gate: plan quality gate passed or blockers explicitly returned to earlier planning stages.

### 11. Implementation Plan

Spawn `roadmap_stage_implementation_planner`.

The subagent must:

1. Read the approved `planning.md` and implementation-plan template.
2. Create or update `implementation-plan.md`.
3. Refuse to create phases if phase shaping is not approved, the plan quality gate has not passed, any design decision is `blocked`, any `needs maintainer discussion` decision is unresolved, or any auto-approved decision lacks traceability and adversarial review evidence.
4. Convert functionality, design decisions, examples, and validation into sequential phases.
5. Identify likely file/module ownership, dependencies, tests/checks, risks, assumptions, and stop conditions.
6. Keep phases small and implementation-ready.

The managing agent reviews the implementation plan automatically, fixes clear planning issues, records remaining concerns in the plan, and presents only material questions or blockers to the maintainer.

Gate: implementation plan approved.

## Exit Criteria

- `planning.md` records roadmap extraction, source evidence, stage readbacks, capability triage, module behavior, approved functionality, design decisions, implication review, audit findings, examples, validation strategy, phase shaping, plan quality gate, assumptions, and deferrals.
- `implementation-plan.md` records phased implementation work with clear ownership, validation, examples, risks, and stop conditions.
- No unresolved blocker remains unless explicitly accepted as deferred.
