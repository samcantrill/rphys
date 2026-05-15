# Roadmap Version To Implementation Plan

Use this entrypoint as:

```text
@.codex/workflows/roadmap-version-planning.md | @docs/roadmap.md v<N>
```

`v<N>` maps to `docs/roadmap/stage-<N>/`.

## Goal

Convert one roadmap version into an approved implementation plan after shared
consensus on functionality and design is recorded in the stage planning
artifact. The workflow uses a smaller set of required specialist passes:
combined context/functionality mapping, independent design proposal,
independent adversarial design review, combined validation/phase-shaping/plan
quality review, and implementation-plan drafting.

The managing agent owns synthesis, maintainer discussion, approvals, conflict
resolution, and final judgment. Specialists provide bounded evidence and update
the durable artifacts; they do not make final approval decisions.

## Inputs

- `AGENTS.md`
- `docs/roadmap.md`
- Selected roadmap version `v<N>`
- `docs/features/**`, if present
- Current docs, code, tests, configs, and archived discussions that clarify
  intent
- Existing files under `docs/roadmap/stage-<N>/`, if any
- Templates:
  - `.codex/templates/roadmap-stage-planning.md`
  - `.codex/templates/roadmap-stage-implementation-plan.md`

## Outputs

- `docs/roadmap/stage-<N>/planning.md`
- `docs/roadmap/stage-<N>/implementation-plan.md`

Keep functionality agreement, design agreement, discussion records, approvals,
defaults, concerns, validation findings, examples, plan-quality findings, and
implementation-plan review notes inside those two files unless the maintainer
asks for another artifact.

Future planning runs use the consolidated pass structure below. Existing
in-progress artifacts that already contain legacy standalone mapper or quality
reviewer handoffs may continue from their recorded state without retrofitting.

## Operating Rules

- Subagents are bounded helpers with sequential write ownership. Do not let two
  subagents edit `planning.md` at the same time.
- Each required specialist pass must follow its prompt exactly and return
  concise evidence: files read, files changed, decisions, risks, open
  questions, and recommended next gate.
- Required specialist passes are hard gates. The managing agent may synthesize,
  reconcile, and challenge specialist output, but must not replace a required
  specialist pass with manager-only analysis.
- A required specialist pass may be skipped only when the maintainer explicitly
  approves an override and the override is recorded in `planning.md` with the
  reason, accepted risk, and next gate affected.
- Update `planning.md` after each meaningful discussion round, including
  `Stage Gates`, `Stage Readbacks`, and any affected queue rows.
- Record every material candidate requirement, functionality-agreement queue
  item, behavior lock, design decision, design-agreement queue item,
  validation concern, phase-shaping concern, plan-quality finding, default,
  assumption, and deferral in `planning.md`; discussion is narrower than
  recording.
- Maintain `Functionality Agreement Queue` and `Design Agreement Queue` as
  dependency-ordered queues in `planning.md`. Resolve repo-answerable branches
  directly and record them. Downstream planning must not begin while either
  queue has unresolved high-impact blockers.
- Raise only items with an ambiguous choice, unresolved blocker, or material
  trade-off that requires maintainer judgment. Ambiguity includes
  product/scientific intent, public API or durable artifact shape, workflow
  semantics, downstream compatibility, meaningful future-refactor risk, or
  insufficient repository evidence for a clear default.
- Do not walk the maintainer through deterministic or evidence-backed items one
  by one. Record the default or recommendation, then summarize those items as a
  group at the relevant gate.
- Ask maintainer questions one at a time. For each raised queue item, explain
  what is being locked, why it matters, the recommendation, trade-offs, impact
  or residual risk, and the exact feedback needed.
- After each maintainer answer, immediately record the decision, rationale,
  default or deferral, queue-state update, and any follow-up in `planning.md`
  before raising the next item.
- Recording a decision as `pending approval`, `ready for approval`, or
  `needs maintainer discussion` is not approval. If maintainer judgment is
  required, the managing agent must raise the decision packet in conversation
  before moving to the next gate.
- Auto-approved design decisions must still be recorded. They may skip
  individual maintainer discussion only when they are low impact, clearly
  recommended by repository evidence and rphys design principles, and pass
  adversarial review with no meaningful refactor risk.
- Treat user workflow feedback as process input. Route reusable workflow
  feedback to `.codex` workflow/prompt/template/agent artifacts; route
  current-session facilitation preferences to `planning.md`; keep both separate
  from product requirements.
- If design review exposes a missing functionality decision that cannot be
  resolved from repository evidence, reopen only the relevant
  functionality-agreement queue item and return to the functionality-agreement
  substage before continuing.
- If validation, plan quality, or implementation-plan review finds that
  accepted planning would force downstream agents to invent behavior or
  structure, reopen only the relevant agreement queue and return to that gate.
- Do not implement code in this workflow.
- Do not pause for routine approval after every specialist pass. Continue
  through evidence-backed defaults when no maintainer decision, blocker,
  material design trade-off, or explicit approval point remains.
- Do not move past unresolved maintainer decisions, unresolved blockers,
  unresolved agreement queues, design approval, plan quality approval, or final
  implementation-plan approval.
- If manual context compaction is unavailable, write a resume checkpoint and ask
  the maintainer to continue in a fresh chat with the same invocation plus the
  current artifact path.

## Agent Passes

Use these role prompts and agent definitions:

| Pass | Agent | Prompt | Writes |
| --- | --- | --- | --- |
| Context scaffold, capability triage, and candidate requirements | `roadmap_stage_context_planner` | `.codex/prompts/roadmap-stage-context-planner.md` | `planning.md` |
| Functionality-agreement review | managing agent | `.codex/prompts/roadmap-stage-functionality-agreement.md` | `planning.md` |
| Design proposal | `roadmap_stage_design_proposer` | `.codex/prompts/roadmap-stage-design-proposer.md` | `planning.md` |
| Design implication, future-roadmap safety, coherence audit, and examples | `roadmap_stage_design_implication_reviewer` | `.codex/prompts/roadmap-stage-design-implication-reviewer.md` | `planning.md` |
| Design-agreement review | managing agent | `.codex/prompts/roadmap-stage-design-agreement.md` | `planning.md` |
| Validation, phase shaping, and plan quality gate | `roadmap_stage_validation_planner` | `.codex/prompts/roadmap-stage-validation-planner.md` | `planning.md` |
| Implementation planning | `roadmap_stage_implementation_planner` | `.codex/prompts/roadmap-stage-implementation-planner.md` | `implementation-plan.md` |

Fallback roles remain available when a stage is unusually broad, risky, or
blocked:

- Use `roadmap_stage_functionality_mapper` as a standalone legacy/fallback pass
  only when the consolidated context/functionality pass is incomplete, stale,
  or explicitly split by maintainer override.
- Use `roadmap_stage_functionality_decision_auditor` as a standalone audit only
  when the design review finds unresolved traceability, example, or coherence
  risk that needs another pass.
- Use `roadmap_stage_phase_shaper` as a standalone phase-shaping pass only when
  combined validation and phase shaping cannot produce reviewable implementation
  phases without deeper decomposition.
- Use `roadmap_stage_plan_quality_reviewer` as a standalone fallback only when
  the combined validation/quality pass cannot complete the plan-quality gate or
  when the maintainer requests an extra independent readiness review.

## Required Specialist Evidence And Hard Gates

The following evidence is mandatory unless a maintainer-approved override is
recorded in `planning.md`:

- A completed handoff from each required specialist pass listed in Agent
  Passes.
- `Stage Gates` and `Stage Readbacks` rows updated for completed gates,
  including locked decisions, defaults, open questions, blockers, and next
  focus.
- `Functionality Agreement Queue` populated in dependency order with
  recommended answers, state, trade-offs, repo-resolved branches, and exact
  feedback needed where maintainer input is required.
- `Behavior Confirmation` populated from the resolved functionality-agreement
  queue.
- `Design Agreement Queue` populated in dependency order with recommended
  answers, state, trade-offs, repo-resolved branches, and exact feedback needed
  where maintainer input is required.
- `Design Decision Triage` final classifications after design implication
  review, not only after design proposal.
- `Future Roadmap And Reuse Safety Review` evidence that material design
  decisions were checked against later roadmap items and that
  interface/adapter/protocol generality, reuse, and explicit revisit triggers
  were considered.
- `Functionality And Decision Audit` evidence that all included capabilities
  map to requirements, design decisions, examples, and validation needs.
- `Validation Strategy`, `Phase Shaping`, and `Plan Quality Gate` evidence
  from the combined validation/quality pass, including unresolved ambiguity,
  blockers, `needs maintainer discussion` rows, reopened queues, and missing or
  stale specialist evidence checks.

Hard gate rules:

- Functionality-agreement review must not begin until source evidence,
  capability triage, module behavior, candidate requirements, and the initial
  functionality-agreement queue are recorded by the consolidated
  context/functionality pass.
- Behavior confirmation must not pass while any high-impact functionality queue
  item is `needs maintainer discussion` or `blocked`.
- Design proposal must not begin until the functionality-agreement queue has no
  unresolved high-impact blockers and the behavior confirmation gate has passed.
- Design-agreement review must not begin until both the design proposal and
  design implication/future-roadmap safety/coherence audit/example passes have
  completed, and their findings are recorded in `planning.md`.
- Design-agreement review must not pass while any high-impact design queue item
  is `needs maintainer discussion` or `blocked`.
- Validation, phase shaping, and plan quality must not be treated as approved
  while either agreement queue is reopened or the design-agreement gate is
  unresolved.
- The combined validation/quality pass must block when required specialist
  evidence is missing, stale, manager-authored only, or inconsistent with the
  current `planning.md`.
- Implementation planning must not create phases while the plan quality gate
  has not passed, specialist evidence is missing, either agreement queue has
  unresolved items, decision packets are unresolved, or any approval gate is
  only recorded as pending or ready for approval.

## Stages

### 1. Context, Capability Triage, And Candidate Requirements

Spawn `roadmap_stage_context_planner`.

The subagent must:

1. Read the selected roadmap version, related feature docs if present, relevant
   architecture/design docs, code/tests/configs, and archived discussions only
   when they clarify intent.
2. Create `docs/roadmap/stage-<N>/` if needed.
3. Create or refresh `planning.md` from the planning template.
4. Record source evidence, exploration coverage, roadmap extraction, version
   overview, likely impacted modules, known constraints, assumptions, risks,
   and open questions.
5. Propose candidate capabilities and sort them into `include`, `maybe`,
   `defer`, and `out of scope`.
6. Define what functionality and behavior means for each relevant module or
   repo area.
7. Break included capabilities into a small set of concrete functional
   requirements.
8. Draft the initial `Functionality Agreement Queue` in dependency order,
   including recommended answers, trade-offs, repo-resolved branches, and exact
   feedback needed only when maintainer input appears necessary.
9. Record capability triage, module behavior, functional requirements, and the
   initial queue in `planning.md`.
10. Stop without asking the maintainer questions.

The managing agent gives a concise briefing, reconciles the combined pass, and
raises only product, scientific, audience, behavior, or scope ambiguity that
requires maintainer judgment. Record resolved clarifications in `planning.md`
before continuing.

Decision gate: candidate requirements and the initial
functionality-agreement queue are recorded. Raise only ambiguous functionality
and behavior choices, blockers, or material scope trade-offs. If no such items
remain, continue to the agreement substage.

### 2. Functionality-Agreement Review

Use `.codex/prompts/roadmap-stage-functionality-agreement.md`.

The managing agent must:

1. Draft or refresh the functionality-agreement queue before asking the
   maintainer anything.
2. Resolve repo-answerable branches directly and record them as queue
   resolutions.
3. Ask only one unresolved high-impact requirement question at a time.
4. Continue until there are no unresolved high-impact functionality blockers.
5. Keep low-impact defaults grouped and recorded without turning them into
   routine confirmation questions.

Decision gate: the functionality-agreement queue is dependency ordered,
repo-answerable branches are resolved directly, and no unresolved high-impact
requirement blocker or maintainer packet remains.

### 3. Behavior Confirmation

The managing agent confirms the resolved functionality baseline in
`Behavior Confirmation`.

1. Summarize included behavior, default behavior, failure behavior,
   unsupported behavior, resume/interruption behavior, downstream implications,
   and explicit deferrals.
2. Record a stage readback that states what is being built and why.
3. Raise another maintainer question only if confirmation exposes a new
   high-impact functionality blocker. Otherwise record the locked baseline and
   continue.

Decision gate: the agreed functionality and behavior baseline is explicitly
locked before design work begins.

Checkpoint: update `planning.md` with a resume note, then compact context or
ask for a fresh-chat continuation if compaction is unavailable.

### 4. Context Checkpoint If Applicable

If the conversation history, source discovery, or new maintainer input makes the
planning state hard to carry forward, refresh the checkpoint before design work.
If no checkpoint is needed, record `not needed` in `Stage Gates` and
`Stage Readbacks` and continue.

Decision gate: the context checkpoint is cleared or explicitly marked
`not needed`.

### 5. Design Proposal

Spawn `roadmap_stage_design_proposer`.

The subagent must:

1. Read the confirmed behavior baseline, architecture/style docs, public
   contracts, current code/tests, and relevant archived material.
2. Infer the likely implementation approach needed to satisfy the
   functionality.
3. Draft likely modules, classes, functions, interfaces, data flow, and
   boundaries.
4. Define design decisions based on that proposed implementation approach.
5. Draft the initial `Design Agreement Queue` in dependency order, including
   recommended answers, trade-offs, repo-resolved branches, and exact feedback
   needed only when maintainer input appears necessary.
6. Record options, recommendation, adversarial assumptions considered,
   validation/documentation obligation, residual risk, and whether maintainer
   escalation is actually needed in `planning.md`.

The managing agent must treat design-proposer classifications as provisional.
Do not ask for design approval and do not downgrade `needs maintainer
discussion` decisions until the design implication, future-roadmap safety,
coherence audit, and examples pass has reviewed them.

### 6. Design Implication, Future-Roadmap Safety, Coherence Audit, And Examples

Spawn `roadmap_stage_design_implication_reviewer`.

The subagent must:

1. Review the proposed design decisions against the confirmed functionality.
2. Pressure-test modularity, decoupling, base classes/protocols, inheritance or
   composition, interfaces/adapters, future extension, maintainability,
   complexity, and future refactor risk.
3. Try to overturn every `auto-approved candidate` using adversarial examples
   and refactor-risk analysis.
4. Check each material design decision against future roadmap items that may
   depend on, constrain, or be constrained by the current shape. Record whether
   the design should be revised now, deferred with a revisit trigger, or raised
   for maintainer judgment.
5. Review interfaces, adapters, and protocols for generic reuse across
   datasets, modalities, methods, codecs, framework integrations, and
   downstream projects while preserving domain semantics and explicit failure
   behavior.
6. Reclassify decisions and update the design-agreement queue.
7. Verify every auto-approved decision is traceable to approved behavior and
   has adversarial review evidence.
8. Verify each included capability maps to at least one functional requirement,
   design decision, example, and validation need.
9. Find conflicts, missing requirements, unsupported decisions, excessive
   scope, unclear failure modes, validation gaps, and downstream impacts.
10. Propose project-context examples that demonstrate the functionality across
    the intended workflow.
11. Reopen only the relevant functionality-agreement queue item when a missing
    behavior decision blocks design and cannot be resolved from repository
    evidence.
12. Update `planning.md` with findings, recommended revisions,
    future-roadmap safety evidence, reuse evidence, audit/example evidence, and
    only the packets that need maintainer discussion because they remain
    ambiguous, blocked, or materially risky.

Hard gate: this pass is mandatory before design-agreement review. If it is
missing, manager-authored only, stale relative to the current proposed design,
or fails to reclassify design decisions and record future-roadmap/reuse safety
findings, design approval is blocked.

### 7. Design-Agreement Review

Use `.codex/prompts/roadmap-stage-design-agreement.md`.

The managing agent must:

1. Draft or refresh the `Proposed Implementation Shape` summary first.
2. Draft or refresh the design-agreement queue before asking the maintainer
   anything.
3. Resolve repo-answerable branches directly and record them as queue
   resolutions.
4. Ask only one unresolved high-impact design question at a time.
5. Continue until there are no unresolved high-impact design blockers.
6. Ensure accepted revisions from the future-roadmap/reuse safety review are
   reflected in the proposed implementation shape, design decisions, validation
   obligations, deferrals, or revisit triggers before design approval passes.
7. Reopen the functionality-agreement queue only when a design blocker reveals
   a missing upstream behavior decision that cannot be resolved from repository
   evidence.

Decision gate: design decisions are explicitly approved, with no unresolved
high-impact design queue item, no missing specialist review evidence, and no
material design trade-off that has only been recorded as pending. This is the
required explicit design approval point.

Checkpoint: update `planning.md` with a resume note, then compact context or
ask for a fresh-chat continuation if compaction is unavailable.

### 8. Validation, Phase Shaping, And Plan Quality Gate

Spawn `roadmap_stage_validation_planner`.

The subagent must:

1. Review the confirmed functionality, resolved agreement queues, design
   decisions, future-roadmap/reuse safety findings, audit findings, examples,
   risks, and failure modes.
2. Define tests and checks for behavior, edge cases, failure modes,
   integration boundaries, examples, docs/templates/workflows, and
   scientific/workflow contracts.
3. Define optional tests/checks only when they would materially reduce risk.
4. Propose implementation phase order, phase boundaries, dependencies, review
   boundaries, acceptance criteria, test expectations, design impact, future
   compatibility, interface/adapter/protocol reuse implications, and phase
   risks.
5. Keep phases reviewable and coherent; split broad phases before they can
   become implementation-plan work.
6. Reopen only the relevant agreement queue when validation scope, plan
   quality, or reviewable phase design cannot be defined from the accepted
   planning state.
7. Run the plan quality gate inside the same pass: traceability from roadmap to
   requirements, design, examples, validation, and phase shaping; specialist
   evidence freshness; unresolved ambiguity; reopened queues; future-roadmap
   compatibility; interface/adapter/protocol reuse; scientific/workflow
   contract clarity; and phase reviewability.
8. Update `planning.md` with required and optional validation coverage, phase
   sketch, and plan-quality pass/block evidence.

The managing agent reconciles validation coverage, phase shaping, and plan
quality. Raise individual choices only when coverage scope,
scientific/workflow contract, cost, ordering, boundaries, acceptance criteria,
reviewability, specialist evidence, or readiness remain ambiguous or blocked.

Decision gate: validation strategy, phase shaping, and plan quality have no
unresolved maintainer decisions or blockers, and no agreement queue had to be
reopened.

### 9. Implementation Plan

Spawn `roadmap_stage_implementation_planner`.

The subagent must:

1. Read the approved `planning.md` and implementation-plan template.
2. Create or update `implementation-plan.md`.
3. Refuse to create phases if the validation and phase-shaping decision gate is
   unresolved, the plan quality gate has not passed, any required specialist
   evidence is missing or stale, either agreement queue is unresolved or
   reopened, any design decision is `blocked`, any `needs maintainer
   discussion` decision is unresolved, any approval-worthy decision was
   recorded but not raised to the maintainer, or any auto-approved decision
   lacks traceability and adversarial review evidence.
4. Convert functionality, design decisions, examples, and validation into
   sequential phases.
5. Identify likely file/module ownership, dependencies, tests/checks, risks,
   assumptions, and stop conditions.
6. Keep phases small and implementation-ready.

The managing agent reviews the implementation plan automatically, fixes clear
planning issues, records remaining concerns in the plan, and presents only
material questions or blockers to the maintainer.

Gate: implementation plan approved.

## Exit Criteria

- `planning.md` records roadmap extraction, source evidence, stage gates, stage
  readbacks, capability triage, module behavior, functionality-agreement queue,
  confirmed behavior, design-agreement queue, design decisions, implication
  review, audit findings, examples, validation strategy, phase shaping, plan
  quality gate, assumptions, and deferrals.
- `implementation-plan.md` records phased implementation work with clear
  ownership, validation, examples, risks, and stop conditions.
- No unresolved blocker remains unless explicitly accepted as deferred.
