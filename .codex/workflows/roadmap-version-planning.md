# Roadmap Version To Implementation Plan

Use this entrypoint as:

```text
@.codex/workflows/roadmap-version-planning.md | @docs/roadmap.md v<N>
```

`v<N>` maps to `docs/roadmap/stage-<N>/`.

## Goal

Convert one roadmap version into an approved implementation plan. The managing agent should raise only ambiguous choices, blockers, or material trade-offs to the maintainer, and should do so only after specialist subagents have explored the repository, drafted functional requirements, proposed implementation shape, and pressure-tested design and coherence implications.

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
- Update `planning.md` after each meaningful discussion round, including a `Stage Readbacks` row for every completed decision gate.
- Record every material functional requirement, design decision, validation concern, phase-shaping concern, default, assumption, and deferral in `planning.md`; discussion is narrower than recording.
- Raise only items with an ambiguous choice, unresolved blocker, or material trade-off that requires maintainer judgment. Ambiguity includes product/scientific intent, public API or durable artifact shape, workflow semantics, downstream compatibility, meaningful future-refactor risk, or insufficient repository evidence for a clear default.
- Do not walk the maintainer through deterministic or evidence-backed items one by one. Record the default or recommendation, then summarize those items as a group at the relevant gate.
- Ask maintainer questions one at a time. For each raised item, explain what the item is, why it matters, the options or trade-off, the recommendation, the impact or residual risk, and the exact decision requested.
- After each maintainer answer, immediately record the decision, rationale, default or deferral, and any follow-up in `planning.md` before raising the next item.
- Auto-approved design decisions must still be recorded. They may skip individual maintainer discussion only when they are low impact, clearly recommended by repository evidence and rphys design principles, and pass adversarial review with no meaningful refactor risk.
- Treat user workflow feedback as process input. Route reusable workflow feedback to `.codex` workflow/prompt/template/agent artifacts; route current-session facilitation preferences to `planning.md`; keep both separate from product requirements.
- Do not implement code in this workflow.
- Do not pause for routine approval after every specialist pass. Continue through evidence-backed defaults when no maintainer decision, blocker, material design trade-off, or explicit approval point remains.
- Do not move past unresolved maintainer decisions, unresolved blockers, design approval, or final implementation-plan approval.
- If manual context compaction is unavailable, write a resume checkpoint and ask the maintainer to continue in a fresh chat with the same invocation plus the current artifact path.

## Agent Passes

Use these role prompts and agent definitions:

| Pass | Agent | Prompt | Writes |
| --- | --- | --- | --- |
| Context scaffold | `roadmap_stage_context_planner` | `.codex/prompts/roadmap-stage-context-planner.md` | `planning.md` |
| Functionality map | `roadmap_stage_functionality_mapper` | `.codex/prompts/roadmap-stage-functionality-mapper.md` | `planning.md` |
| Design proposal | `roadmap_stage_design_proposer` | `.codex/prompts/roadmap-stage-design-proposer.md` | `planning.md` |
| Design implication, coherence audit, and examples | `roadmap_stage_design_implication_reviewer` | `.codex/prompts/roadmap-stage-design-implication-reviewer.md` | `planning.md` |
| Validation and phase shaping | `roadmap_stage_validation_planner` | `.codex/prompts/roadmap-stage-validation-planner.md` | `planning.md` |
| Plan quality review | `roadmap_stage_plan_quality_reviewer` | `.codex/prompts/roadmap-stage-plan-quality-reviewer.md` | `planning.md` |
| Implementation planning | `roadmap_stage_implementation_planner` | `.codex/prompts/roadmap-stage-implementation-planner.md` | `implementation-plan.md` |

Fallback roles remain available when a stage is unusually broad or risky:

- Use `roadmap_stage_functionality_decision_auditor` as a standalone audit only when the combined design review finds unresolved traceability, example, or coherence risk that needs another pass.
- Use `roadmap_stage_phase_shaper` as a standalone phase-shaping pass only when combined validation and phase shaping cannot produce reviewable implementation phases without deeper decomposition.

## Stages

### 1. Context Scaffold

Spawn `roadmap_stage_context_planner`.

The subagent must:

1. Read the selected roadmap version, related feature docs if present, relevant architecture/design docs, code/tests/configs, and archived discussions only when they clarify intent.
2. Create `docs/roadmap/stage-<N>/` if needed.
3. Create or refresh `planning.md` from the planning template.
4. Record source evidence, exploration coverage, roadmap extraction, version overview, likely impacted modules, known constraints, assumptions, and open questions.
5. Stop without asking the maintainer questions.

The managing agent then gives a concise briefing and explicitly invites clarifying questions only when the scaffold leaves product, scientific, audience, or optimization-target ambiguity. Record resolved clarifications in `planning.md` before continuing.

Decision gate: resolve user-visible outcome, target audience, and planning priority or optimization target only when they are ambiguous or contradicted by evidence. Otherwise record the evidence-backed default and continue.

### 2. Capability Triage And Module Behavior Discovery

Spawn `roadmap_stage_functionality_mapper`.

The subagent must:

1. Read `planning.md` and the same source set needed to understand the roadmap section.
2. Propose candidate capabilities and sort them into `include`, `maybe`, `defer`, and `out of scope`.
3. Define what functionality and behavior means for each relevant module.
4. Explain what the roadmap section should do and what it enables in the codebase.
5. Break included capabilities into a small set of concrete functional requirements.
6. For each requirement, identify whether it is a clear recommended default, needs maintainer decision, or is blocked; explain the ambiguity only when escalation is needed.
7. Record capability triage, module behavior, and requirement packets in `planning.md`.

The managing agent then reconciles the capability triage, stage behavior, affected modules, enabled capabilities, non-goals, recorded defaults, and only the uncertainty that may require discussion.

Decision gate: raise only ambiguous functionality and behavior choices, blockers, or material scope trade-offs. If no such items remain, record the recommended functional baseline and continue.

### 3. Functional Requirement Discussion

Review the functional requirements in `planning.md`, but raise only requirements marked `needs maintainer decision`, `blocked`, or otherwise ambiguous after manager reconciliation. Do not walk through every requirement by default.

Summarize clear recommended defaults as a group and record them in `planning.md`. Ask the maintainer only about requirements marked `needs maintainer decision`, `blocked`, or materially ambiguous after reconciliation.

Use this packet shape for one raised requirement at a time:

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

Record each answer immediately in `planning.md` before raising the next requirement.

Decision gate: functionality and behavior baseline has no unresolved maintainer decisions or blockers.

Checkpoint: update `planning.md` with a resume note, then compact context or ask for a fresh-chat continuation if compaction is unavailable.

### 4. Design Proposal

Spawn `roadmap_stage_design_proposer`.

The subagent must:

1. Read the approved behavior baseline, architecture/style docs, public contracts, current code/tests, and relevant archived material.
2. Infer the likely implementation approach needed to satisfy the functionality.
3. Draft likely modules, classes, functions, interfaces, data flow, and boundaries.
4. Define design decisions based on that proposed implementation approach.
5. Classify each decision as `auto-approved candidate`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`, where `recorded recommendation` means a clear default that does not require individual maintainer discussion unless a material unresolved trade-off remains.
6. Nominate `auto-approved candidate` only when all criteria hold:
   - no public API, import-path, schema, config, scientific/workflow, dependency, serialization, persistence, or compatibility impact
   - localized implementation choice with straightforward validation
   - consistent with approved behavior and rphys design principles
   - traceable to an approved functional requirement
   - low future refactor risk and no meaningful downstream extension consequence
7. Record options, recommendation, adversarial assumptions considered, validation/documentation obligation, residual risk, and whether maintainer escalation is actually needed in `planning.md`.

### 5. Design Implication, Coherence Audit, And Examples

Spawn `roadmap_stage_design_implication_reviewer`.

The subagent must:

1. Review the proposed design decisions against the approved functionality.
2. Pressure-test modularity, decoupling, base classes/protocols, inheritance or composition, future extension, maintainability, complexity, and future refactor risk.
3. Try to overturn every `auto-approved candidate` using adversarial examples and refactor-risk analysis.
4. Identify unclear contracts, accidental coupling, missing extension points, over-generalization, under-specified failure behavior, and decisions that conflict with rphys architecture.
5. Reclassify decisions as `auto-approved`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`.
6. Verify every auto-approved decision is traceable to approved behavior and has adversarial review evidence.
7. Verify each included capability maps to at least one functional requirement, design decision, example, and validation need.
8. Find conflicts, missing requirements, unsupported decisions, excessive scope, unclear failure modes, validation gaps, and downstream impacts.
9. Propose project-context examples that demonstrate the functionality across the intended workflow.
10. Classify audit findings and example choices as recorded concern, needs maintainer decision, or blocker.
11. Update `planning.md` with findings, recommended revisions, recorded defaults, audit/example evidence, and only the packets that need maintainer discussion because they remain ambiguous, blocked, or materially risky.

### 6. Design Decision Discussion

The managing agent reconciles the design proposal and implication review, then raises only design decisions that remain `needs maintainer discussion`, `blocked`, or have a material unresolved trade-off after review.
Summarize `auto-approved` decisions and clear `recorded recommendation` defaults as a group rather than asking for individual approval.

Use this packet shape for one raised design decision at a time:

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

Record each answer immediately in `planning.md` before raising the next design decision.

Decision gate: design decisions approved, with no unresolved `blocked` decisions and no unresolved `needs maintainer discussion` decisions. This is the required explicit design approval point.

Checkpoint: update `planning.md` with a resume note, then compact context or ask for a fresh-chat continuation if compaction is unavailable.

### 7. Validation And Phase Shaping

Spawn `roadmap_stage_validation_planner`.

The subagent must:

1. Review approved functionality, design decisions, audit findings, and examples.
2. Define tests and checks for behavior, edge cases, failure modes, integration boundaries, examples, docs/templates/workflows, and scientific/workflow contracts.
3. Define optional tests/checks only when they would materially reduce risk.
4. Propose implementation phase order, phase boundaries, dependencies, review boundaries, acceptance criteria, test expectations, design impact, future compatibility, and phase risks.
5. Keep phases reviewable and coherent; split broad phases before they can become implementation-plan work.
6. Update `planning.md` with required and optional validation coverage plus the phase sketch.

The managing agent reconciles validation coverage and phase shaping. Raise individual choices only when coverage scope, scientific/workflow contract, cost, ordering, boundaries, acceptance criteria, or reviewability remain ambiguous or blocked.

Decision gate: validation strategy and phase shaping have no unresolved maintainer decisions or blockers.

### 8. Plan Quality Gate

Spawn `roadmap_stage_plan_quality_reviewer`.

The subagent must:

1. Review `planning.md` for traceability from roadmap extraction through capabilities, requirements, design decisions, examples, validation, and phase shaping.
2. Check extensibility, maintainability, scientific/workflow contract clarity, plan reviewability, unresolved ambiguity, unresolved `blocked` decisions, and unresolved `needs maintainer discussion` decisions.
3. Record pass/block findings in `planning.md`.

Decision gate: plan quality gate passed or blockers explicitly returned to earlier planning stages. Raise only quality-gate blockers or ambiguous return-to-planning choices.

### 9. Implementation Plan

Spawn `roadmap_stage_implementation_planner`.

The subagent must:

1. Read the approved `planning.md` and implementation-plan template.
2. Create or update `implementation-plan.md`.
3. Refuse to create phases if the validation and phase-shaping decision gate is unresolved, the plan quality gate has not passed, any design decision is `blocked`, any `needs maintainer discussion` decision is unresolved, or any auto-approved decision lacks traceability and adversarial review evidence.
4. Convert functionality, design decisions, examples, and validation into sequential phases.
5. Identify likely file/module ownership, dependencies, tests/checks, risks, assumptions, and stop conditions.
6. Keep phases small and implementation-ready.

The managing agent reviews the implementation plan automatically, fixes clear planning issues, records remaining concerns in the plan, and presents only material questions or blockers to the maintainer.

Gate: implementation plan approved.

## Exit Criteria

- `planning.md` records roadmap extraction, source evidence, stage readbacks, capability triage, module behavior, approved functionality, design decisions, implication review, audit findings, examples, validation strategy, phase shaping, plan quality gate, assumptions, and deferrals.
- `implementation-plan.md` records phased implementation work with clear ownership, validation, examples, risks, and stop conditions.
- No unresolved blocker remains unless explicitly accepted as deferred.
