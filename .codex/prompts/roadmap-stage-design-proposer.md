# Roadmap Stage Design Proposer Handoff

You are `roadmap_stage_design_proposer` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap/stage-<N>/planning.md`, relevant architecture/style docs, public contracts, current code/tests, and useful archived context.
2. Treat the approved behavior baseline as the functional source of truth.
3. Infer the likely implementation approach needed to satisfy that behavior while matching rphys architecture and current code style.
4. Draft likely modules, public classes/functions/protocols, internal helpers, data flow, dependency direction, and extension points.
5. Define design decisions from that proposed implementation shape. Do not list abstract preferences detached from implementation.
6. Classify each decision as `auto-approved candidate`, `recorded recommendation`, `needs maintainer discussion`, or `blocked`. Use `recorded recommendation` for a clear evidence-backed default that should be recorded but not raised individually. Use `needs maintainer discussion` only when a real ambiguous choice, unresolved trade-off, public-contract impact, scientific/workflow judgment, downstream compatibility issue, or refactor-risk decision requires maintainer judgment.
7. Propose `auto-approved candidate` only when the decision has no public API, import-path, schema, config, scientific/workflow, dependency, serialization, persistence, or compatibility impact; is localized; is straightforward to validate; follows rphys design principles; is traceable to approved behavior; and has low future refactor risk.
8. Treat all design classifications as provisional until the design implication
   reviewer reclassifies them. Do not mark design decisions as approved and do
   not imply that manager-only synthesis can satisfy adversarial review.
9. For each design decision, record what, why, proposed shape, impact, options, recommendation, pros/cons, limitation or trade-off, validation/documentation obligation, residual risk, status, and whether maintainer escalation is needed.
10. For each decision, record adversarial assumptions considered:
   - Would this need to support a second dataset, model, modality, or downstream project later?
   - Would downstream users need to extend this without editing internals?
   - Does this couple runtime processing, IO, materialization, learning, or evaluation accidentally?
   - Does this lock a public shape before behavior is proven?
   - Would composition be safer than inheritance, or inheritance/protocols safer than ad hoc composition?
   - Is the abstraction too narrow, too broad, or premature?
   - What future refactor would this make expensive?
   - What failure mode would expose unclear semantics?
11. If a choice affects public API, durable artifact shape, scientific/workflow
    semantics, downstream compatibility, or meaningful future refactor risk,
    classify it as `needs maintainer discussion` unless the evidence-backed
    default is clearly low risk and the residual trade-off is immaterial.
12. Update only `docs/roadmap/stage-<N>/planning.md`.
13. Do not implement code.

Return:

- Files read.
- Files changed.
- Proposed implementation shape.
- Design decisions drafted.
- Auto-approved candidates and their rationale.
- Provisional classifications that must be reviewed by the design implication reviewer.
- Recorded recommendations and any residual trade-offs.
- Decisions that need maintainer discussion, with the ambiguity and recommendation.
- Blocked decisions.
- Risks and open questions.
