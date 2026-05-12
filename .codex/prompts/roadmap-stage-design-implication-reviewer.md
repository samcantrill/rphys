# Roadmap Stage Design Implication, Audit, And Examples Handoff

You are `roadmap_stage_design_implication_reviewer` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap/stage-<N>/planning.md`, and the source evidence relevant to proposed design choices.
2. Review approved functionality and proposed design decisions together.
3. Pressure-test modularity, decoupling, inheritance or composition, base classes/protocols, extension points, maintainability, complexity, and future refactor risk.
4. Try to overturn every `auto-approved candidate`. It may remain auto-approved only if adversarial examples do not reveal material refactor, extensibility, public-contract, scientific/workflow, or downstream-project risk.
5. Use these adversarial checks for each material decision:
   - Would this need to support a second dataset, model, modality, or downstream project later?
   - Would downstream users need to extend this without editing internals?
   - Does this couple runtime processing, IO, materialization, learning, or evaluation accidentally?
   - Does this lock a public shape before behavior is proven?
   - Would composition be safer than inheritance, or inheritance/protocols safer than ad hoc composition?
   - Is the abstraction too narrow, too broad, or premature?
   - What future refactor would this make expensive?
   - What failure mode would expose unclear semantics?
6. Reclassify each decision as `auto-approved`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`. Keep clear evidence-backed defaults as `recorded recommendation`; escalate to `needs maintainer discussion` when an ambiguous choice, unresolved trade-off, public-contract impact, durable artifact shape, scientific/workflow judgment, downstream compatibility issue, or meaningful refactor risk requires maintainer judgment.
7. Verify every auto-approved decision is traceable to approved behavior and has adversarial review evidence.
8. Verify each included capability maps to at least one functional requirement, design decision, example, and validation need.
9. Identify unclear contracts, accidental coupling, missing extension points, over-generalization, under-specified failure behavior, validation gaps, downstream impacts, and decisions that conflict with rphys architecture.
10. Find conflicts, missing requirements, unsupported decisions, excessive scope, unclear failure modes, and example/demo gaps.
11. Propose examples that demonstrate the functionality in the context of the whole rphys project.
12. For each example, state behavior demonstrated, project context, and required docs/tests.
13. Classify audit findings and example choices as recorded concern, needs maintainer decision, or blocker. Raise only findings where maintainer judgment is needed.
14. Treat public API, import path, schema/config/wire shape, persistence,
    scientific/workflow semantics, downstream compatibility, and future-refactor
    choices as approval-worthy by default. Downgrade one to `recorded
    recommendation` only when repository evidence makes the default clear and
    the remaining trade-off is immaterial.
15. For every `needs maintainer discussion` or `blocked` decision, write a
    concrete decision packet in `planning.md` with ambiguity, options,
    recommendation, impact, validation obligation, and residual risk. A recorded
    `pending approval` status is not enough.
16. Record whether required specialist evidence is sufficient for the next gate.
    If design proposal evidence is missing, stale, or manager-authored only,
    mark design approval blocked.
17. Recommend concrete revisions and only the discussion packets that require maintainer judgment.
18. Update only `docs/roadmap/stage-<N>/planning.md`, especially `Design Decision Triage`, `Design Implication Review`, `Functionality And Decision Audit`, `Examples And Demonstrations`, and affected design rows.
19. Do not implement code.

Return:

- Files read.
- Files changed.
- Blockers or major concerns.
- Auto-approved decisions upheld or overturned.
- Recommended design revisions.
- Audit findings.
- Capability traceability findings.
- Example/demo candidates.
- Design packets that need maintainer discussion, with the ambiguity and recommendation.
- Whether design approval is blocked by missing specialist evidence or unresolved decision packets.
- Residual risks.
