# Stage 1 Planning Notes: Field-Centric Architecture Scaffold

## Metadata

- Roadmap slug: `field-centric-architecture-scaffold`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `AGENTS.md`
  - `.codex/workflows/stage-1-roadmap.md`
  - `.codex/prompts/stage-1-planning-notes-facilitate.md`
  - `.codex/templates/stage-1-planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: split into narrower draft work packages
- Current discussion stage: roadmap framing split complete
- Related roadmap rows:
  - `Public architecture contracts`
  - `Field runtime core`
  - `Dataset IO and index core`
  - `Runtime transforms and materialization`
  - `Learning evaluation core`
  - `Extension docs and validation scaffold`
- Blockers:
  - Split package boundaries are confirmed as the working Stage 1 roadmap map; individual package-size risk remains under review.
  - No split package has been accepted for Stage 2.
  - Each split package still needs functionality/behavior confirmation, checkpointing, and design-decision review.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | completed | Maintainer chose to split the broad v3 architecture before acceptance and confirmed the six-package split as the working Stage 1 map | Treat this file as source extraction and use split package notes for acceptance | Revisit package subdivision only if a package's decision queue proves too broad | Move to `Public architecture contracts` intent discovery |
| Intent discovery | draft | Stable public API is the highest project priority; `Public architecture contracts` should be reviewed first | Base library for remote physiological measurement, not downstream experiment repo | Which public contracts must be stable first? | Clarify stable API surface |
| Capability brainstorming | draft | None yet | Include field-centric scaffold, lazy IO, runtime Sample pipeline, materialization, methods, evaluation, docs, and tests as proposed capabilities | Which capabilities are initial scaffold versus deferred library depth? | Mark include/defer boundaries |
| Functionality and behavior confirmation | draft | None yet | Fail loudly by default; use field keys and public contracts; keep loom/rphys boundary explicit | Are proposed defaults acceptable? | Confirm behavior before design review |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None once behavior is confirmed | Record checkpoint |
| Design-decision review | not started | None yet | Use the decision queue below, grouped from v3 plan section 47 | Does the queue miss or over-split any decisions? | Review queued decisions after checkpoint |
| Phase shaping | not started | None yet | Provisional phase sketch only | What implementation path and slice size should Stage 2 plan? | Shape phases after decisions |
| Handoff | not started | None yet | Master-plan inputs remain provisional | Which work package is accepted for Stage 2? | Prepare Stage 2 handoff after acceptance |

## Context Extraction

Baseline outcome:

- Build `rphys` as a domain-specific remote physiological measurement base library layered on top of `loom`.
- Keep `loom` responsible for generic reproducible experiment infrastructure.
- Make `rphys` responsible for domain concepts, field-aware datasets, codecs, transforms, materialization/export, methods, training, evaluation, analysis, recipes, and concrete domain stages.
- Establish a small stable public contract surface before implementation hardens.

Constraints:

- `rphys` depends on `loom`; `loom` must not depend on `rphys`.
- Do not duplicate generic infrastructure already owned by `loom`, including config composition, recipe expansion, pipeline DAG execution, run/artifact stores, generic stage execution, resume logic, executors, sweep runner, and generic artifact/resource infrastructure.
- Dataset adapters should emit serializable references, not loaded tensors, decoded media, open file handles, or runtime objects.
- The index/view/slice system describes lazy IO only.
- Runtime data operations use `Sample -> Sample`.
- Dataset formatting is offline materialization/export, not a `datasets/` side effect.
- Predictions are represented as Samples or Batches with prediction fields.
- Public behavior should be documented in docs, tests, or docstrings before downstream use.
- Scientific contracts must document units, shapes, dtypes, coordinate frames, temporal alignment, sampling rates, leakage risks, and failure behavior.

Deferred or out-of-scope ideas:

- Exact collate policy list.
- Exact codec and export-format library.
- Exact dataset adapter library.
- Exact model architecture library.
- Immediate mesh implementation.
- Nested multi-view Samples.
- Spatial slices.
- Time-based slices.
- Multi-member IndexItems.
- Plugin discovery through Python entry points.
- Full self-supervised learner library.
- Full signal-processing method library.
- Full materialization exporter library.
- Full publication/reporting analysis stack.
- Generic experiment infrastructure that belongs in `loom`.

Scientific workflow obligations:

- Preserve field metadata for schema, layout, axes, units, sample rate, fps, coordinate frame, temporal coordinate frame, selector, codec, collation, and provenance where relevant.
- Fail loudly when required attributes are missing or ambiguous.
- Avoid silent time/index conversion, coordinate-frame conversion, full-load fallback, truncation, padding, or role mismatch.
- Keep filtering out of runtime transforms so invalid windows are excluded during record/view/index construction.
- Ensure reproducible stochastic augmentation through explicit context-derived RNG streams.
- Provide synthetic data fixtures and contract tests for field schemas, index slices, collation, transforms, metrics, recipes, and loom stages.

## User Intent

Target audience:

- `rphys` maintainers rebuilding the package as a clean base library.
- Downstream remote physiological measurement researchers who need reusable domain components without adopting a monolithic experiment repository.
- Extension authors adding datasets, fields, codecs, transforms, exporters, methods, models, learners, losses, metrics, and protocols.
- Automation agents that need durable planning notes, roadmap rows, and handoff artifacts.

User-visible outcome:

- A coherent scaffold roadmap item that can be accepted for Stage 2 master-plan drafting.
- A planning note ledger that captures the v3 architecture plan as work-package scope, proposed behavior, design-decision queue, open questions, and provisional phase shape.

Success criteria:

- The architecture plan is converted into roadmap-level work-package scope rather than tiny implementation tasks.
- The loom/rphys boundary is explicit.
- The public contract surface is named and grouped.
- Runtime, offline materialization, dataset indexing, learning, and evaluation lifecycles are separated.
- Proposed defaults and failure behavior are visible for maintainer confirmation.
- Design decisions are queued for review before implementation planning.
- Stage 2 can start only after explicit work-package acceptance.

Non-goals:

- Implementing code in Stage 1.
- Accepting a roadmap package without maintainer confirmation.
- Replacing `loom` generic infrastructure inside `rphys`.
- Choosing every concrete dataset, codec, model, metric, or exporter now.
- Treating historical project structure as an API contract.

Operational constraints:

- Keep roadmap rows concise.
- Store durable planning under `docs/implementation/<roadmap-slug>/`.
- Do not start Stage 2 until the roadmap work package is accepted.
- Use work-package granularity: package-level scaffold decisions, not individual PR tasks.

## Split Work Packages

The broad `Field-centric architecture scaffold` proposal has been split before acceptance. This file remains the source extraction ledger for the v3 architecture plan. Stage 1 acceptance should now happen on one or more split work packages, not on this umbrella note.

| Split package | Planning notes | Primary scope | Depends on |
| --- | --- | --- | --- |
| Public architecture contracts | `docs/implementation/public-architecture-contracts/planning-notes.md` | `loom`/`rphys` boundary, public contract inventory, package skeleton, error taxonomy, registry policy, dependency policy | None |
| Field runtime core | `docs/implementation/field-runtime-core/planning-notes.md` | `DataKey`, `FieldSpec`, `FieldValue`, data objects, `Sample`, `Batch`, mutability, collation | Public architecture contracts, if planned first |
| Dataset IO and index core | `docs/implementation/dataset-io-index-core/planning-notes.md` | `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, `IndexItem`, `SampleSpec`, `SampleBuilder`, filters, codec contracts | Field runtime core |
| Runtime transforms and materialization | `docs/implementation/runtime-transforms-materialization/planning-notes.md` | Ops boundary, `SampleTransform`, augmentation, checks, pipelines, exporters, materialization lifecycle | Field runtime core; Dataset IO and index core |
| Learning evaluation core | `docs/implementation/learning-evaluation-core/planning-notes.md` | Method/model/learner/trainer boundaries, adapters, losses, predictions, metrics, aggregation, evaluation protocols | Field runtime core |
| Extension docs and validation scaffold | `docs/implementation/extension-docs-validation-scaffold/planning-notes.md` | Extension guides, synthetic fixtures, docs checks, recipe/stage examples, validation strategy | Accepted contracts from the other packages |

Current split recommendation:

- Keep the six-package split as the working dependency map for Stage 1. This split is confirmed by the maintainer.
- Use `Public architecture contracts` first because stable public API design is the main maintainability and extensibility risk.
- Do not split `Field runtime core` yet because `DataKey`, `FieldSpec`, `FieldValue`, `Sample`, `Batch`, and collation are one coherent runtime API surface.
- Do not split `Dataset IO and index core` yet because `FieldRef`, `FieldView`, `TemporalIndexSlice`, `IndexItem`, codecs, and `SampleBuilder` must agree on lazy IO semantics.
- Revisit splitting `Runtime transforms and materialization` into separate runtime-pipeline and materialization/export packages if its design queue grows too broad.
- Revisit splitting `Learning evaluation core` into method/training and prediction/evaluation packages if its design queue grows too broad.
- Treat `Extension docs and validation scaffold` as a cross-cutting follow-up unless a docs-first acceptance is explicitly useful.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| loom/rphys boundary | include, pending confirmation | Prevents duplicate generic experiment infrastructure and keeps `rphys` domain-specific | `loom` runs artifact pipelines; `rphys` defines remote-phys semantics |
| Public contract surface | include, pending confirmation | Gives downstream projects stable extension points | Includes `DataKey`, `FieldSpec`, `DatasetRef`, `FieldRef`, `Sample`, `Batch`, transforms, methods, learners, metrics |
| Field-centric data model | include, pending confirmation | Supports video, BVP, timestamps, landmarks, masks, meshes, labels, predictions, and custom fields uniformly | Video should not be privileged |
| DatasetRef/RecordRef/FieldRef hierarchy | include, pending confirmation | Separates dataset structure from loaded runtime data | Records expose arbitrary logical fields |
| FieldSpec/FieldRef/FieldView/FieldValue separation | include, pending confirmation | Keeps declaration, storage reference, lazy IO request, and loaded value distinct | Avoids mixing schemas with runtime payloads |
| TemporalIndexSlice | include, pending confirmation | Provides initial lazy temporal slicing with bounded semantics | Index-based, half-open, field-native indices only |
| IndexItem as lazy IO request | include, pending confirmation | Keeps indexing out of transform, formatting, and learning semantics | Contrastive views should be runtime augmentation initially |
| Sample and Batch runtime containers | include, pending confirmation | Gives all runtime operations a single field API | Batch should be Sample-like |
| Mutable Samples | include, pending confirmation | Reduces hot-path copying and matches transform behavior | Branching requires explicit copies |
| Field-level collation | include, pending confirmation | Avoids silent shape, padding, and missing-field ambiguity | Exact policy list can evolve |
| Dataset filters and index builders | include, pending confirmation | Excludes invalid records/windows before runtime loading | Filtering is not a SampleTransform |
| Field codecs and IO registry | include, pending confirmation | Loads/saves field views through explicit codec capabilities | No silent full-load fallback |
| Pure ops layer | include, pending confirmation | Reusable math stays independent of IO and Sample plumbing | Ops can back transforms or methods |
| Runtime transforms and pipelines | include, pending confirmation | Standardizes deterministic processing, extraction, checks, and composition | `SampleTransform` is `Sample -> Sample` |
| SampleAugmentation reproducibility | include, pending confirmation | Needed for multi-worker/distributed training and reproducible views | RNG derived from run seed, epoch, worker, item, transform |
| Sample checks | include, pending confirmation | Validates samples without becoming the main filtering mechanism | Default mode should raise for training-critical checks |
| Materialization/export pipeline | include, pending confirmation | Handles formatting, symlinking, conversion, and precomputed fields | Produces new FieldRefs/RecordRefs/DatasetRefs |
| Methods/models/learners/trainers separation | include, pending confirmation | Keeps prediction, neural modules, learning style, and loop orchestration independent | Supports classical, signal-processing, neural, SSL, contrastive |
| Predictions as Samples/Batches | include, pending confirmation | Supports waveform, HR, embeddings, masks, landmarks, and multitask outputs | Metrics consume fields by key |
| Evaluation protocols and aggregation | include, pending confirmation | Supports per-window and record-level metric orders | Separate sample aggregation and metric aggregation |
| Analysis utilities | maybe | Useful but could depend on heavier optional packages | Should consume artifacts/reports, not rerun training |
| Recipes and concrete stages | include, pending confirmation | Exposes reusable domain workflows through `loom` config/stage machinery | Stages are thin wrappers around rphys APIs |
| Extension guides | include, pending confirmation | Keeps downstream extension path documented and testable | Guides should cover datasets, fields, codecs, transforms, methods, learners, losses, metrics |
| Full plugin discovery | defer | Import-path `_target_` extensions are enough initially | Entry points can come later |
| Spatial/time-based slices | defer | The v3 plan recommends index-based temporal slices first | Avoids expanding IO semantics prematurely |
| Full dataset/model/codec catalog | defer | Scaffold should establish contracts before broad libraries | Add concrete implementations incrementally |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed initial scope includes the field-centric data model, public contracts, lazy IO references, Sample/Batch runtime containers, collation policy hooks, dataset filtering/indexing, codecs, ops, transforms, augmentation, checks, materialization/export, method/learner/trainer boundaries, prediction Samples, evaluation aggregation, domain recipes, domain stages, extension guides, and contract tests.

User-visible behavior:

- Pending maintainer confirmation. Proposed behavior is that users interact with stable public contracts and field keys, extend by adding importable objects and configs, and receive explicit errors for missing/ambiguous scientific contracts.

Agent-visible behavior:

- Pending maintainer confirmation. Proposed behavior is that future planning and implementation agents treat this planning note as the Stage 1 decision ledger, keep roadmap rows concise, and avoid implementation until Stage 2 acceptance and quality gates are complete.

Default behavior:

- Pending maintainer confirmation. Proposed defaults are lazy loading, mutable Samples, strict missing-field/schema/slice/collation behavior, index-based temporal slicing only, runtime stochastic augmentation only unless explicitly materialized, and `_target_` import paths for user extensions.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Proposed failures include `MissingFieldError`, `MissingRequiredMetadataError`, `FieldTypeError`, `FieldSchemaError`, `FieldValidationError`, `CodecResolutionError`, `SliceUnsupportedError`, `SliceOutOfBoundsError`, `CollateError`, `TransformContractError`, `CoordinateFrameError`, and `TemporalAlignmentError`.

Explicit deferrals:

- Pending maintainer confirmation. Proposed deferrals include exact catalogs of codecs/datasets/models/metrics/exporters, mesh depth, spatial/time-based slices, nested multi-view Samples, multi-member IndexItems, plugin entry-point discovery, and full analysis/reporting stack.

Out-of-scope behavior:

- Pending maintainer confirmation. Proposed out-of-scope behavior includes generic config composition, recipe expansion machinery, pipeline DAG execution, run/artifact stores, generic stage execution, generic executors, sweep runner, locking, and generic artifact/resource definitions already owned by `loom`.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before beginning design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| loom/rphys boundary | Prevents duplicate infrastructure and unclear ownership | Confirm exact boundary and any exceptions | draft |
| DatasetRef/RecordRef/FieldRef structure | Defines dataset and field reference semantics | Confirm hierarchy and whether generic loom records/manifests are wrapped or reused | draft |
| FieldSpec/FieldRef/FieldView/FieldValue separation | Keeps declaration, reference, lazy IO, and runtime value separate | Confirm separation and naming | draft |
| DataKey grammar and namespaces | Prevents field collisions and stabilizes user extension surface | Confirm grammar, reserved namespaces, and custom namespace rule | draft |
| TemporalIndexSlice semantics | Sets initial IO slice contract | Confirm index-only, half-open, field-native semantics | draft |
| IndexItem semantics | Prevents index from becoming transform/formatting/learning plan | Confirm lazy IO-only scope | draft |
| Arbitrary logical fields in dataset adapters | Determines whether video is privileged | Confirm uniform field model for all modalities | draft |
| Formatting as materialization/export | Places offline conversion outside `datasets/` | Confirm package location and lifecycle | draft |
| Sample as central runtime container | Determines transform/method/evaluation API | Confirm centrality and field API | draft |
| Batch as Sample-like container | Affects downstream method, loss, and metric access patterns | Confirm inheritance versus duplicate API preference | draft |
| Mutable Samples by default | Affects hot-path performance and transform contracts | Confirm mutability and explicit copy rules | draft |
| Explicit field metadata/schema/layout/collate attributes | Controls scientific interpretability and validation | Confirm required metadata depth for initial scaffold | draft |
| Loud default failures | Avoids silent scientific errors | Confirm no silent fallback defaults | draft |
| Filtering during record/view/index construction | Keeps runtime pipelines from wasting IO and hiding exclusions | Confirm filter locations and exception cases | draft |
| SampleTransform as core runtime operation | Sets standard processing interface | Confirm `Sample -> Sample` as universal transform contract | draft |
| Role-first transform organization | Affects package navigation and lifecycle clarity | Confirm role-first versus modality-first organization | draft |
| SampleAugmentation subtype | Separates stochastic runtime operations from deterministic transforms | Confirm parameter sampling and provenance expectations | draft |
| Reproducibility context supplied by SamplePipeline | Determines seed and RNG handling | Confirm seed inputs and debugging needs | draft |
| SamplePipeline composition | Standardizes transform order and context handling | Confirm pipeline responsibilities and branching strategy | draft |
| SampleExporter and MaterializationPipeline | Defines formatting/export/symlink mechanism | Confirm exporter lifecycle and output DatasetRef behavior | draft |
| Pure ops layer | Keeps reusable math decoupled from IO and Samples | Confirm import and dependency boundaries | draft |
| Runtime versus offline stage lifecycle | Determines where precomputed fields and formatting live | Confirm materialized outputs replace/add field keys explicitly | draft |
| Model/Method/Learner/Trainer separation | Supports many learning styles without coupling | Confirm responsibility boundaries | draft |
| Predictions as Samples/Batches | Enables multitask and non-waveform evaluation | Confirm prediction field naming and container behavior | draft |
| Metric aggregation order | Supports window-level and record-level evaluation | Confirm pre-metric sample aggregation and post-metric aggregation components | draft |
| Field-level collation policy | Avoids shape and missing-field ambiguity | Confirm initial strict defaults and padding/mask behavior | draft |
| Stable documented extension contracts | Sets public API and docs burden | Confirm which contracts are stable in first scaffold | draft |
| Registry policy | Prevents excessive registration burden | Confirm symbolic registries versus `_target_` import paths | draft |
| User extensions through `_target_` paths | Controls downstream ergonomics | Confirm import-path extension as the default | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Prevents premature implementation commitments | Keeps v3 plan as proposal until accepted | Review queue must be discussed after checkpoint | Revisit after functionality/behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Proposed stable groups: `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, `rphys.methods`, `rphys.training`, `rphys.losses`, and `rphys.evaluation`.
- Proposed extension guides should explain required protocols/base classes, serialization expectations, field keys, contracts, tests, and explicit anti-patterns.
- Deep modality implementations may be public in practice but should not be the primary stable extension contract.

Workflow and artifact surface:

- `rphys` stages should be thin concrete implementations of `loom` stage protocols.
- Stages should consume and produce artifact references, delegate domain logic to `rphys` APIs, and remain safe to rerun.
- Dataset stages should build/validate references and indexes.
- Materialization stages should create new manifests or DatasetRefs rather than mutating inputs.

Failure modes and diagnostics:

- Missing fields, missing metadata, wrong field types, schema/layout mismatch, unsupported slices, out-of-bounds slices, codec resolution errors, collate ambiguity, transform contract violations, coordinate-frame errors, and temporal-alignment errors should fail explicitly by default.
- Fallbacks may exist only as explicit configuration choices.

Extension points and flexibility boundaries:

- Users add new fields with `DataKey`, `FieldSpec`, `FieldRef`, optional data object, optional codec, and requested SampleSpec/IndexBuilder behavior.
- Users add transforms, augmentations, exporters, methods, models, learners, losses, and metrics through public protocols and `_target_` config paths.
- Registries are reserved for symbolic names such as dataset names, codec keys, field schemas, metrics, and recipes.

Maintainability assessment:

- The proposed separation reduces hidden dependencies among dataset scanning, lazy IO, runtime transforms, offline formatting, learning, and evaluation.
- Role-first transform organization makes lifecycle semantics visible but may create extra package depth.
- Mutable Samples improve runtime efficiency but require clear transform contracts and copy rules.

Extensibility assessment:

- Uniform field keys and arbitrary FieldRefs allow new modalities without changing core containers.
- Prediction-as-Sample keeps evaluation extensible for waveform, scalar, embedding, mask, landmark, quality, and multitask outputs.
- `_target_` extension avoids requiring users to modify registries or internals for experiment-specific components.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 0 - Scaffold Boundary And Public Contract Inventory

Goal:

- Establish repository package/documentation skeleton and the accepted public contract inventory without implementing deep domain algorithms.

Scope:

- Package directories, public API export plan, error taxonomy, dependency boundary notes, doc placeholders, and contract inventory.

Out of scope:

- Concrete dataset adapters, heavy codecs, neural models, full materialization exporters, and full training/evaluation workflows.

Acceptance criteria:

- The scaffold exposes the accepted module boundaries and documented contract names.
- Generic loom-owned concerns remain out of `rphys`.

Test expectations:

- Package: import smoke tests.
- Unit: error and key/type primitives if implemented.
- Contract: public API inventory check.
- Integration: none unless `loom` contract stubs exist.
- E2E: none.
- Opt-in: none.

Design impact:

- Locks package ownership and import boundaries.

Future compatibility:

- Leaves room for optional dependencies and plugin discovery later.

Reviewability:

- Small, mostly structural diff.

### Phase 1 - Field, Sample, Batch, And Collation Core

Goal:

- Implement the field-centric runtime container layer.

Scope:

- `DataKey`, `FieldSpec`, `FieldValue`, typed data object base, `Sample`, `Batch`, `CollatePolicy`, collation contracts, and scientific metadata validation hooks.

Out of scope:

- Dataset scanning, concrete codecs, method/training/evaluation stacks.

Acceptance criteria:

- Samples and Batches support the same field access behavior.
- Strict collation behavior fails on ambiguous shapes or missing fields unless policy permits it.

Test expectations:

- Package: import checks.
- Unit: keys, fields, Sample/Batch mutation/access, collation policies.
- Contract: metadata/schema/collation validation.
- Integration: synthetic multi-field sample collation.
- E2E: none.
- Opt-in: none.

Design impact:

- Establishes the runtime API used by every later package.

Future compatibility:

- Allows new modalities through `FieldValue` and data object subclasses.

Reviewability:

- Focused but API-sensitive.

### Phase 2 - Dataset References, Lazy IO, And Codec Contracts

Goal:

- Implement the reference and lazy IO layer without concrete heavy backends.

Scope:

- `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, `IndexItem`, `SampleSpec`, `SampleBuilder`, `DatasetAdapter` protocol, filters, index builders, codec protocol, registry, and synthetic codec fixtures.

Out of scope:

- Full real dataset adapter catalog and production video/signal codecs unless chosen as thin examples.

Acceptance criteria:

- Dataset adapters can emit records with arbitrary logical fields.
- SampleBuilder loads FieldViews through codecs and fails loudly on missing fields or unsupported slices.

Test expectations:

- Package: import checks.
- Unit: refs, slice validation, index item construction, codec resolution.
- Contract: no loaded data in refs/indexes; unsupported slice errors.
- Integration: synthetic DatasetRef -> IndexItem -> SampleBuilder flow.
- E2E: tiny synthetic scan/build/load pipeline.
- Opt-in: real backend codec tests deferred.

Design impact:

- Locks lazy IO semantics and prevents transform/learning leakage into indexing.

Future compatibility:

- Supports future datasets, codecs, and modalities.

Reviewability:

- Larger contract surface; should be separated from runtime container work.

### Phase 3 - Runtime Pipelines, Augmentation, Checks, And Materialization

Goal:

- Implement runtime `Sample -> Sample` composition and offline export lifecycle.

Scope:

- Transform roles, `BaseSampleTransform`, `SampleContext`, `PipelineContext`, `SamplePipeline`, `SampleAugmentation`, `SampleCheck`, `SampleExporter`, `MaterializationPipeline`, deterministic provenance hooks, and symlink or synthetic exporters.

Out of scope:

- Broad transform library, heavy extraction algorithms, production materialization backends.

Acceptance criteria:

- Transform contracts validate inputs/outputs.
- Augmentations are reproducible under fixed context.
- Materialization exports fields and emits new FieldRefs without mutating input DatasetRefs.

Test expectations:

- Package: import checks.
- Unit: transform contracts, context seed derivation, checks, exporters.
- Contract: filtering not implemented as SampleTransform; no hidden IO in runtime transforms.
- Integration: synthetic materialization flow.
- E2E: synthetic deterministic transform/export pipeline.
- Opt-in: none initially.

Design impact:

- Defines lifecycle split between runtime and offline processing.

Future compatibility:

- Allows landmark extraction, formatting, and precomputed fields to share one materialization pattern.

Reviewability:

- API and workflow heavy; should follow confirmed reference layer.

### Phase 4 - Methods, Training, Evaluation, Recipes, And Docs

Goal:

- Add the minimal learning/evaluation scaffold and user-facing extension documentation.

Scope:

- Method, learner, trainer, adapters, losses, prediction Samples, metrics, aggregators, evaluation protocols, thin domain stage skeletons, recipes, extension guides, and testing strategy docs.

Out of scope:

- Full neural architecture library, full training framework integration, full analysis stack, and production reports.

Acceptance criteria:

- A synthetic method can produce prediction fields consumed by a metric through field keys.
- User extension docs describe how to add datasets, fields, codecs, transforms, augmentations, exporters, methods, models, learners, losses, metrics, and evaluation protocols.

Test expectations:

- Package: import checks.
- Unit: method/loss/metric adapter contracts.
- Contract: predictions as Samples/Batches; metric aggregation order.
- Integration: synthetic predict/evaluate flow.
- E2E: minimal synthetic recipe or stage smoke if loom is available.
- Opt-in: torch-dependent tests behind optional group if needed.

Design impact:

- Extends the field API into learning and evaluation while keeping model/trainer responsibilities separate.

Future compatibility:

- Supports supervised, self-supervised, contrastive, masked, signal-processing, and multitask methods without changing containers.

Reviewability:

- Superseded by the separate `learning-evaluation-core` and `extension-docs-validation-scaffold` work-package notes.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should the v3 architecture become one broad roadmap package or be split into multiple accepted packages before Stage 2? | Roadmap granularity and Stage 2 scope | Split into six draft work packages | answered: split |
| Are the six split work-package boundaries correct? | Roadmap granularity and Stage 2 scope | Use the split table above | open |
| Which split package should go through detailed Stage 1 review first? | Phase priority and acceptance criteria | Public architecture contracts first, then field runtime core | open |
| Should `Batch` subclass `Sample` or duplicate the same public field API? | Runtime API and type clarity | Duplicate API is acceptable if inheritance is undesirable | open |
| How much of the public contract surface should be implemented in the first master plan versus documented as future API? | Stage 2 scope | Implement core contracts first, document broader contracts | open |
| Should role-first transform organization be strict or only used where lifecycle clarity benefits outweigh package depth? | Package structure and navigation | Role-first for transform implementation modules | open |
| Which optional dependencies are acceptable in the initial scaffold? | Packaging and CI | Keep core lightweight; put video/signal/torch/analysis behind extras | open |
| Should any real codec, dataset adapter, or model be included as a thin reference implementation in the relevant package? | Validation realism and scope | Use synthetic fixtures first | open |
| What degree of loom integration should Stage 2 require before code exists in either repo? | Stage tests and artifact contracts | Keep stages thin and integrate when loom contract is available | open |

## Handoff Notes

Master-plan draft inputs:

- Source architecture plan: `docs/rphys_architecture_plan_v3.md`.
- Split package planning notes under `docs/implementation/*/planning-notes.md`.
- Accepted functionality and behavior checkpoint for whichever split package is chosen.
- Design-decision table for the chosen split package, once reviewed.
- Provisional phase sketch in the chosen split package notes, to be refined after accepted decisions.
- Roadmap row in `docs/roadmap/index.md`.

Quality-gate risks:

- A split package may still be too broad if it absorbs concrete implementations that should be deferred.
- Public API names could harden before loom generic record/resource boundaries are known.
- Mutable Sample semantics require careful tests to avoid hidden mutation surprises.
- Field-level scientific metadata requirements could become burdensome if initial minimums are not staged.
- Optional dependency boundaries must be enforced early to avoid a heavy core package.

Assumptions to carry forward:

- The v3 plan is a source proposal, not an accepted implementation contract.
- `rphys` should remain a base library for downstream research projects.
- `loom` owns generic experiment execution and artifact mechanics.
- `rphys` owns remote physiological measurement semantics and domain components.
- Initial implementation should use synthetic fixtures and contract tests before broad real-world integrations.
