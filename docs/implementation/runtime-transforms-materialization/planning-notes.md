# Stage 1 Planning Notes: Runtime Transforms And Materialization

## Metadata

- Roadmap slug: `runtime-transforms-materialization`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: draft
- Current discussion stage: roadmap framing
- Related roadmap row: `Runtime transforms and materialization`
- Blockers:
  - Split boundaries have not been confirmed by the maintainer.
  - Dependency on accepted runtime and IO contracts is unresolved.
  - Design-decision review has not started.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | draft | Broad architecture is split; this package owns runtime pipelines, augmentation, checks, ops, exporters, and materialization | Dataset formatting belongs here, not in datasets | Should ops be implemented here or in a separate package? | Confirm scope |
| Intent discovery | draft | None yet | Serve preprocessing, augmentation, extraction, checks, and offline formatting workflows | Which materialization path must work first? | Clarify workflows |
| Capability brainstorming | draft | None yet | Include core transform contracts and synthetic exporters | Full transform/export library deferred | Mark include/defer |
| Functionality and behavior confirmation | not started | None yet | `Sample -> Sample`; explicit RNG; no hidden IO in runtime transforms | None yet | Confirm behavior |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None | Record checkpoint |
| Design-decision review | not started | None yet | Review queue below | None yet | Review decisions |
| Phase shaping | not started | None yet | Contract-first, synthetic materialization | None yet | Sketch phases |
| Handoff | not started | None yet | Carry accepted lifecycle rules into Stage 2 | None yet | Prepare Stage 2 inputs |

## Context Extraction

Baseline outcome:

- Implement the runtime operation and offline materialization lifecycle around Samples.

Constraints:

- Runtime transforms are `Sample -> Sample`.
- Augmentations are stochastic transforms with reproducible parameter sampling.
- Checks validate, annotate, or warn; they are not the normal filtering mechanism.
- Formatting is materialization/export, not a dataset package component.
- Ops are pure or mostly pure computation without IO or Sample plumbing.

Deferred or out-of-scope ideas:

- Full transform library.
- Heavy landmark/mask/mesh extraction algorithms.
- Production video/signal exporters.
- Full materialization backend catalog.
- Training and evaluation scaffolds.

Scientific workflow obligations:

- Transform contracts must declare required inputs/outputs, mutation behavior, coordinate-frame assumptions, temporal alignment assumptions, and failure behavior.
- Augmentation must be reproducible across workers, epochs, items, and transform steps.
- Materialized outputs must declare whether field keys are replaced or added.

## User Intent

Target audience:

- Users composing preprocessing and augmentation pipelines.
- Maintainers implementing offline formatting and precomputed field generation.

User-visible outcome:

- A standard way to modify Samples at runtime and materialize/export derived fields offline.

Success criteria:

- Runtime transforms validate input/output contracts.
- Augmentations produce reproducible sampled parameters under fixed context.
- Materialization pipelines load fields, optionally process them, export fields, and emit new FieldRefs/DatasetRefs without mutating inputs.

Non-goals:

- Dataset scanning and indexing.
- Training objectives and metrics.
- Full production exporter catalog.

Operational constraints:

- Use synthetic exporters and fixtures first.
- Keep runtime transforms free of hidden file IO.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| Pure ops boundary | include, pending confirmation | Reusable math should not depend on IO/Samples | Exact ops catalog deferred |
| `SampleTransform` | include, pending confirmation | Core runtime operation | `Sample -> Sample` |
| Transform roles | include, pending confirmation | Clarifies lifecycle | Deterministic, augmentation, extraction, check, export |
| `SamplePipeline` | include, pending confirmation | Standard transform composition | Provides per-step context |
| `SampleAugmentation` | include, pending confirmation | Reproducible stochastic operations | Params sampled separately from application |
| `SampleCheck` | include, pending confirmation | Validation without filtering misuse | Modes: raise/annotate/warn |
| `SampleExporter` | include, pending confirmation | Offline write/symlink field export | Not hot-path transform |
| `MaterializationPipeline` | include, pending confirmation | Formatting/precompute lifecycle | Emits new refs/manifests |
| Concrete materialization stages | maybe | Useful for loom integration | Thin stage skeletons only if dependency ready |
| Full export library | defer | Scope control | Add incrementally later |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed scope includes ops boundary, transform contracts, pipeline contexts, augmentation RNG, checks, exporter contract, materialization pipeline, and synthetic export smoke tests.

User-visible behavior:

- Pending maintainer confirmation. Users compose runtime pipelines for Samples and use materialization pipelines for offline formatting/precomputed fields.

Agent-visible behavior:

- Pending maintainer confirmation. Future agents should not place formatting under `datasets/` or load files inside runtime transforms.

Default behavior:

- Pending maintainer confirmation. Transforms may mutate Samples; augmentation randomness comes from context; checks raise by default for training-critical failures; materialization creates new refs.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Transform contract errors, coordinate-frame errors, temporal-alignment errors, missing fields, exporter failures, and invalid output refs fail loudly.

Explicit deferrals:

- Pending maintainer confirmation. Full transform/export library, real heavy algorithms, spatial/time slicing, and nested multi-view containers are deferred.

Out-of-scope behavior:

- Pending maintainer confirmation. Dataset scanning/indexing internals, learning loops, metrics, and analysis.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/runtime-transforms-materialization/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| Ops package ownership | Prevents hidden IO/Sample coupling | Confirm ops as pure layer in this package or separate package | draft |
| Transform role model | Affects package organization and user expectations | Confirm role-first organization | draft |
| Mutating transform contract | Affects debugging and branching pipelines | Confirm mutation and copy rules from runtime core | draft |
| Augmentation RNG derivation | Affects reproducibility | Confirm seed inputs and provenance needs | draft |
| Check behavior modes | Affects validation and filtering boundaries | Confirm raise/annotate/warn behavior | draft |
| Materialization output semantics | Affects reproducibility and manifests | Confirm replace/add field-key rules | draft |
| Formatting package location | Prevents dataset package side effects | Confirm formatting under materialization/export | draft |
| Stage skeleton inclusion | Affects loom dependency timing | Confirm whether to include thin stages now | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Avoids premature lifecycle lock-in | Keeps transform/materialization extensible | Review required | Revisit after behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Proposed contracts: `TransformRole`, `SampleTransform`, `BaseSampleTransform`, `SampleAugmentation`, `SampleCheck`, `SamplePipeline`, `SampleContext`, `PipelineContext`, `SampleExporter`, and `MaterializationPipeline`.

Workflow and artifact surface:

- Materialization stages consume DatasetRefs/IndexItems and emit new DatasetRefs/manifests.

Failure modes and diagnostics:

- Contract violations, missing fields, RNG misuse, hidden IO, coordinate-frame mismatch, temporal misalignment, and exporter failures.

Extension points and flexibility boundaries:

- Users add transforms/exporters through public protocols and `_target_` paths.

Maintainability assessment:

- Lifecycle separation prevents datasets, transforms, and exporters from becoming one coupled layer.

Extensibility assessment:

- The same operation can be wrapped as ops, transform, method, or materialization step as needed.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Runtime Pipeline And Materialization Contracts

Goal:

- Implement contract-first runtime and offline processing lifecycle.

Scope:

- Ops boundaries, transform base, contexts, pipeline, augmentation, checks, exporter, materialization pipeline, synthetic tests.

Out of scope:

- Full transform/export algorithm catalog.

Acceptance criteria:

- Synthetic runtime and materialization flows work with strict contracts and reproducible augmentation.

Test expectations:

- Package: import checks.
- Unit: transforms, contexts, RNG, checks, exporters.
- Contract: no hidden IO; output refs are explicit.
- Integration: synthetic materialization flow.
- E2E: tiny deterministic transform/export pipeline.
- Opt-in: none initially.

Design impact:

- Locks runtime/offline lifecycle rules.

Future compatibility:

- Enables formatting, precomputed landmarks/masks, augmentations, and preprocessing.

Reviewability:

- Workflow-heavy but can stay synthetic.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should ops be its own roadmap package? | Scope | Keep minimal ops boundary here | open |
| Should any concrete exporter be real or synthetic only? | Validation realism | Synthetic and symlink-like exporter first | open |
| Should materialization stages be included before loom contracts are firm? | Integration risk | Document stages, implement only if loom contract exists | open |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 21-26, 33-35, 39-41.
- Accepted runtime and dataset IO contracts.

Quality-gate risks:

- Scope creep into concrete algorithms.
- Ambiguous materialized field replacement semantics.
- Reproducibility bugs in augmentation context.

Assumptions to carry forward:

- Runtime field core and dataset IO/index core exist or are planned before this package.
