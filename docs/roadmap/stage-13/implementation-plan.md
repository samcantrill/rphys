# Roadmap Stage 13 Implementation Plan

Status: ready for implementation workflow
Roadmap version: `v13`
Planning document: `docs/roadmap/stage-13/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 1 - `scaffold-imports-errors`
Blockers: none

## Summary

- Goal: implement Stage 13 as a Sample/Batch-native prediction, runtime
  sample-collection operation, metric-adapter, analysis, and report layer over
  existing operation, collection/view, uncollation, export/save, and datasource
  substrates.
- Source functionality-agreement gate: passed on 2026-05-17; FQ-13-1 through FQ-13-10 are resolved, with FQ-13-5 locked against a standalone public `EvaluationRunner`.
- Approved behavior: prediction is field meaning on ordinary `Batch` and
  `Sample` containers, not a new public record family. `Method.predict` and
  `Learner.step` return `Batch` values directly; `MethodOutput`,
  `MethodOutputSpec`, `MethodOutputAdapter`, `apply_method_output`, and
  `StepOutput` are removed rather than preserved as compatibility surfaces.
  Generic returned-batch validation replaces method-output specs. Training
  engines consume returned learner batches through a `TrainingPlan`-owned
  `TrainingOutputSpec` or an equivalent field-output protocol. Durable
  prediction/test/evaluation artifacts are
  normalized to one `Sample` per record through explicit uncollation policy and
  exported through existing export/save plus datasource reload behavior.
  Evaluation, inference, reporting, analysis, and dataset formatting are recipes
  over generic operations unless repeated code-backed semantics justify a later
  shared engine/protocol. Analysis/report outputs are structured, in-memory, and
  side-effect free by default.
- Source behavior confirmation: passed on 2026-05-17 after maintainer agreement that evaluation/report/dataset-formatting-like flows should reuse existing pipelines, collections, views, collectors, export/save behavior, and derived datasource refs instead of adding a new runner/runtime.
- Key design constraints: no standalone public `EvaluationRunner`,
  `EvaluationEngine`, `InferenceEngine`, `EvaluationProtocol`, `EvaluationPlan`,
  `EvaluationResult`, or `ComparisonSpec` by default; no public
  `PredictionRecord`, `PredictionCollection`, `PredictionCollector`,
  `PredictionExport*`, `BatchCollection`, or `BatchCollector`; no public
  `MethodOutput`, `MethodOutputSpec`, `MethodOutputAdapter`,
  `apply_method_output`, `StepOutput`, `MetricObservation`,
  `MetricObservationCollection`, `MetricObservationView`, `MetricResult`,
  `AnalysisOp`, `AnalysisContext`, `AnalysisResult`, generic `PipelineJob`,
  `JobPlan`, `JobRunner`, scheduler, artifact, resume, registry, or workflow
  lifecycle abstraction; keep shared diagnostic/job helpers package-local/private
  unless future repeated public behavior justifies extraction.
- Source design-agreement gate: passed on 2026-05-17; DQ-13-1 through DQ-13-7 are reviewed with no blocker, reopened queue, or maintainer discussion packet.
- Source functionality-agreement queue: FQ-13-1 through FQ-13-10 revised;
  FQ-13-5 locked; FQ-13-8 no longer adds `RemotePhysPredictionError` by default
  unless code-backed public prediction behavior justifies it; FQ-13-9 defers
  report writers, keeps reports in-memory by default, and allows structured
  report dataset handoff through ordinary field export.
- Source design-agreement queue: DQ-13-1 through DQ-13-7 reviewed; none are `needs maintainer discussion`, `blocked`, `pending approval`, or reopened.
- Source future-roadmap/reuse safety review: passed with revisit triggers for Stage 14 smoke, Stage 15 profiling, future post-prediction batch pipelines, dataset-formatting-like jobs, report save/render adapters, shared diagnostics, and downstream/`loom` orchestration.
- Examples covered: Batch-native prediction, learner `Batch` output with
  structured training-output fields, target-free inference projection,
  evaluation-ready pass-through fields, explicit uncollation to samples, sample
  artifact export/reload for multiple downstream workflows, runtime
  `Iterable[Sample] -> Iterable[SampleCollection] -> Iterable[Sample]`
  grouping/sorting/stitching, metric-as-sample-operation adapters, visualization
  fields, report building, dataset-formatting analogue, and analysis-as-pipeline
  analogue.
- Source phase shaping: revised with six reviewable phases:
  scaffold/imports/errors; Batch-native method/learner/training-output refactor;
  uncollation and sample artifact export/reload; runtime sample-collection and
  metric operations; visualization/report records and recipe examples; synthetic
  composition/docs/final validation.
- Source plan quality gate: passed; required specialist evidence is present, no agreement queue is unresolved, no design decision is blocked, and no auto-approved decision needs missing traceability evidence.
- Out of scope: standalone public `EvaluationRunner`, `EvaluationEngine`,
  `InferenceEngine`, `EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`,
  or `ComparisonSpec` by default; public `Prediction*` record/export family;
  public `MethodOutput*`/`StepOutput`; public `MetricObservation*`/`MetricResult`;
  `BatchCollection`; `BatchCollector`; public generic job/runtime or registry
  APIs; trainer-owned prediction capture; `TrainingResult` payload mining;
  datasource scans; dataloader construction; checkpoint selection;
  prediction-specific storage; report file writers; real visualization/report
  codecs; plotting/dataframe hard dependencies; concrete algorithms; real
  datasets; GPU/performance profiling; workflow runtime ownership.

## Implementation Workflow State

- Implementation-plan quality gate: passed by drafting review on 2026-05-17
- Review pass: completed during plan drafting against `docs/roadmap/stage-13/planning.md`
- Refinement pass: not required; no readiness blockers found
- Confirmation review: completed by managing agent on 2026-05-17; no material blockers or maintainer questions remain before implementation workflow execution
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `scaffold-imports-errors` | pr_open | `agent/stage-13-prediction-evaluation-analysis-reports-p1-scaffold-imports-errors` | [#85](https://github.com/samcantrill/rphys/pull/85) | Package homes, central errors, package/import tests | Establish scoped package scaffold, optional code-backed errors, and lightweight import boundaries. | `make test-package`; focused error tests if added; `git diff --check` | Import/API posture |
| 2 | `batch-native-method-learner-output` | pending | `agent/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output` | pending | `src/rphys/methods/**`, `src/rphys/learning/**`, `src/rphys/training/**`, batch-operation fakes | Remove `MethodOutput`/method-output adapters and `StepOutput`; make methods/learners return `Batch`; add generic returned-batch output spec/validation, plan-owned training-output spec/validation, field projection, target exclusion, and pass-through policy. | `make test-unit`; `make test-contract`; `make test-package`; focused integration if added | Batch-native prediction; learner Batch output; plan-owned training spec; target-free inference |
| 3 | `uncollation-sample-artifacts` | pending | `agent/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts` | pending | Data uncollation policy, sample artifact datasource/export adapters, tests | Implement explicit batch-field uncollation policy/evidence and sample-granular artifact export/reload over existing export/save/datasource APIs. | `make test-unit`; `make test-contract`; `make test-integration`; `git diff --check` | Uncollate to samples; sample artifact export/reload |
| 4 | `sample-collection-metric-ops` | pending | `agent/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops` | pending | `src/rphys/data/collections.py`, transitional `src/rphys/collections.py` only if still needed, `src/rphys/ops/**`, `src/rphys/metrics/**` adapters | Implement runtime grouping/collation of `Iterable[Sample]` into `Iterable[SampleCollection]`, collection sort/project/stitch/concat operations, and sample/collection metric operation adapters. | `make test-unit`; `make test-contract`; `make test-integration`; `make test-package` | Runtime grouping; stitched samples; metric-as-sample-operation |
| 5 | `visualization-reports-recipes` | pending | `agent/stage-13-prediction-evaluation-analysis-reports-p5-visualization-reports-recipes` | pending | `src/rphys/analysis/**`, visualization/report tests, recipe docs/examples | Implement visualization/report operation-compatible builders, in-memory report/table/diagnostic renderer records, and importable recipe examples without a registry or engine. Analysis remains generic group/reduce/metric pipeline composition. | `make test-unit`; `make test-contract`; `make test-package`; docs review | Visualization fields; report building; structured report dataset handoff; recipe examples |
| 6 | `docs-examples-final-validation` | pending | `agent/stage-13-prediction-evaluation-analysis-reports-p6-docs-examples-final-validation` | pending | Stage 13 docs/docstrings/examples, synthetic integration tests, final validation evidence | Complete synthetic composition examples, docs, package export review, and final validation. | `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`; `make validate-pr` | Full synthetic Stage 13 composition; sample-artifact handoff; dataset-formatting/evaluation recipe analogue |

## Implementation Readiness Blockers

No readiness blockers are present.

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Readiness passed: validation and phase-shaping gate passed; plan quality gate passed; future-roadmap/reuse findings are resolved or explicitly deferred with revisit triggers; no design decision is blocked; no `needs maintainer discussion` packet is unresolved; no auto-approved decisions remain. | `docs/roadmap/stage-13/planning.md` Stage Gates, Stage Readbacks, Design Implication Review, Future Roadmap And Reuse Safety Review, Functionality And Decision Audit, Validation Strategy, Phase Shaping, and Plan Quality Gate | No action before phase execution except normal implementation-plan preflight. | resolved |

## Phase Ordering And Parallelization

- Execute implementation PRs sequentially under `.codex/workflows/roadmap-version-implementation.md`: one phase branch/worktree/PR at a time, merged to `develop` before the next phase starts unless a phase is explicitly marked `blocked`.
- Phase 1 is the root dependency for all later public exports and error/import checks.
- Phase 2 depends on Phase 1 and must land before Phases 3 and 4 because it removes the old method/learner output records and defines the returned-`Batch` field shape consumed by later phases.
- Phase 3 depends on Phases 1-2 because uncollation/export policy depends on final batch field semantics.
- Phase 4 depends on Phases 1-3 and is the main guardrail for runtime grouping/stitching/metric composition without public evaluation engines or generic job APIs.
- Phase 5 may be designed after Phase 1 for visualization/report records, but
  recipe examples should wait until Phase 4 when collection and metric
  operations exist.
- Phase 6 must never parallelize with earlier phases. It closes docs, examples, import review, integration coverage, and final validation after Phases 1-5.

## Global Ownership Boundaries

- Stage 13 should not add a public `rphys.prediction` record family by default.
  Prediction behavior is expressed as fields on `Sample`/`Batch`.
- Stage 13 removes public `MethodOutput`, `MethodOutputSpec`,
  `MethodOutputAdapter`, `apply_method_output`, and `StepOutput`. Method
  prediction and learner steps return `Batch` values. Generic returned-batch
  conformance is expressed through `BatchOutputSpec` or an equivalent
  field-locator validator over ordinary `Batch` fields. Training consumes
  objective/loss/metric fields through a `TrainingPlan`-owned
  `TrainingOutputSpec` or an equivalent declared field-output protocol.
- Batch-native prediction code must not import datasource scanners, dataloader
  builders, checkpoint selectors, plotting/dataframe stacks, or workflow modules.
  Training integration may touch `rphys.training` only to replace the old
  `StepOutput` engine contract with returned-`Batch` validation and plan-owned
  training-output spec preflight.
- `rphys.evaluation` should not gain a public module surface in Stage 13 by
  default. Do not export `EvaluationProtocol`, `EvaluationPlan`,
  `EvaluationResult`, `ComparisonSpec`, `EvaluationEngine`, `InferenceEngine`,
  `EvaluationRunner`, `Evaluator`, public generic job records, scheduler state,
  artifact refs, resume tokens, datasource scans, dataloader construction, metric
  catalogs, or report output directories. Evaluation is demonstrated as a recipe
  composed from generic sample/collection/metric/report/export operations.
- `rphys.analysis` owns visualization/report operation-compatible builders and
  in-memory reports/tables/diagnostic renderer outputs. It does not own a public
  `AnalysisOp`, `AnalysisContext`, or `AnalysisResult` family by default:
  analysis summaries are ordinary generic pipeline compositions over samples,
  collections, and metric fields. It must not add pandas/dataframe core types,
  eager plotting imports, implicit HTML/PDF/CSV/Markdown writers, ad hoc
  plot/image file writes, dashboard adapters, artifact stores, checkpoint
  selection, log crawling, or training behavior.
- Existing `rphys.ops`, `rphys.data.collections`, optional transitional
  `rphys.collections`,
  `rphys.metrics`, `rphys.ops.export`, and `rphys.datasources` remain the generic
  substrate. Stage 13 adds uncollation, runtime sample-collection operations,
  metric adapters, artifact, visualization, and report contracts over them
  rather than replacing them.
- Collectors remain payload-agnostic. Prediction, evaluation, analysis, report,
  and future dataset-formatting packages may provide value validators,
  selectors, field-handle adapters, or item-to-export-request adapters, but
  collection mechanics stay in the generic collection substrate.
- Datasource scan/view/filter/group/split/index construction remains outside
  Stage 13. Stage 13 may consume already assembled inputs, `RecordRef` evidence,
  derived datasource export evidence, and prepared collections, but it must not
  rebuild datasource planning as a prediction/evaluation lifecycle.
- Reconsider collection placement before Phase 4 implementation. Preferred
  direction is to consolidate sample-specific collection records, collectors,
  views, and collection operations under `rphys.data.collections` where they sit
  beside `Sample`/`Batch` field-container behavior. Existing `rphys.collections`
  may remain as a thin transitional home for truly generic collection records or
  compatibility imports only if moving it would be disruptive. Do not add
  `rphys.ops.collections`, `BatchCollection`, or `BatchCollector` in Stage 13.
  Use `Iterable[Batch]` for transient batch streams and `SampleCollection` for
  durable/sample snapshots. Artifact adapters provide uncollation and
  item-to-export behavior; if repeated durable handoff needs a shared helper,
  place only a narrow multi-record export/save iteration helper with existing
  `rphys.ops.export` ownership.
- A narrow export iteration helper is allowed only if it remains adapter-produced
  `RecordExportRequest` -> existing codec-selection/save operations -> export
  evidence -> derived datasource assembly. It must not become a public
  `PipelineJob`, scheduler, artifact store, resume lifecycle, datasource
  scanner, collection abstraction, output directory convention, or
  format-specific writer.
- Separate prediction, evaluation, and report launch scripts are an orchestration
  concern for downstream projects or examples. Stage 13 should make those
  scripts easy by exposing native sample/batch field policies, runtime grouping
  and collection operations, metric operation adapters, and report records, and
  by ensuring predictions, metric/evaluation observations, and structured report
  datasets can use the same sample-granular export/save and datasource handoff
  when durable reload is needed.
- Package-local validation/coercion/diagnostic helpers stay private. Reopen design before exporting a shared diagnostic/job helper or importing another package's private helper.
- Public exports must be code-backed, tested, documented, and scoped to package homes. Root `rphys.__all__` remains empty.

## Sample Artifact Datasource Reuse Contract

Stage 13 should implement serialized output handoff as ordinary sample artifact
datasource interaction. In memory, predictions and derived values are fields on
ordinary `Batch` and `Sample` objects. Once persisted, prediction, target,
metric/evaluation, diagnostic, and structured report fields are fields on
per-sample artifact records that can be reloaded through normal datasource,
index, and sample-source machinery.

Implementation obligations:

- Batch prediction output must be explicitly projected and uncollated to
  `Sample` entries before durable export. Do not export a whole batch as one
  prediction artifact.
- Domain packages provide field selectors, validators, and item-to-export
  adapters from `Sample` or collection/result items to descriptor-backed
  `RecordExportRequest`s. The adapters carry domain meaning; datasource code
  does not learn prediction, evaluation, or report semantics.
- Every durable sample artifact item must provide a source `RecordRef` or an
  augmented export-record descriptor whose declared fields match the
  `FieldValue` payloads being exported.
- Existing `CodecSelectionOperation`, `SaveOperation`, `ExportResult`, and
  `DerivedDataSourceBuilder` remain the persistence path. Do not add
  prediction-, evaluation-, or report-specific datasource families.
- If implementation discovers repeated export-loop code, extract only a narrow
  multi-record export/save iteration helper under existing export ownership.
  Do not create `rphys.ops.collections`.
- Separate script examples should reload serialized prediction/test/evaluation
  outputs through normal datasource/index/sample-source behavior, not through a
  domain runner or private result-cache object.
- Cross-process descriptor recovery must be generic. Use existing
  datasource/index manifest behavior if it is sufficient; otherwise reopen the
  relevant queue for a generic derived-output scan/reader adapter rather than a
  prediction/evaluation/report storage API.

Accepted durable handoff examples:

```text
test datasource + trained method/model artifact
  -> Samples -> Batches without target leakage
  -> Batch prediction operation
  -> Batches with predictions/<key> plus allowed pass-through fields
  -> explicit uncollation policy
  -> Samples
  -> export/save
  -> sample artifact datasource

sample artifact datasource with predictions + references
  -> generic sample/collection/metric operation recipe
  -> Samples or SampleCollections with metric/summary/visualization fields, or Report
  -> item-to-export adapter when durable handoff is needed
  -> sample artifact datasource

sample artifact datasource(s)
  -> Report / ReportTable
  -> optional structured report item-to-export adapter
  -> sample artifact datasource
```

## Phase 1: Scaffold, Imports, And Errors

Status: pr_open
Slug: `scaffold-imports-errors`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p1-scaffold-imports-errors`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p1-scaffold-imports-errors`
PR: [#85](https://github.com/samcantrill/rphys/pull/85)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish code-backed Stage 13 package homes, import-boundary tests, and
  minimal error posture before semantic records depend on them.
- Files/modules owned: `src/rphys/errors.py` only if a code-backed error is
  needed; `src/rphys/evaluation/__init__.py`; `src/rphys/analysis/__init__.py`;
  data/datasource package exports only if Phase 1 adds code-backed names; private
  package-local validation modules if immediately needed;
  `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`;
  focused package-local error tests only if errors are added.
- Behavior implemented: existing `RemotePhysEvaluationError` and
  `RemotePhysAnalysisError` remain the broad bases for evaluation/report and
  visualization/report-rendering failures; no broad prediction error is added unless
  implementation adds code-backed public prediction-operation behavior requiring
  a distinct catch point; package homes import without heavy optional
  dependencies and export only implemented names.
- Decisions applied: DD-13-1, DD-13-9, DD-13-10; FQ-13-8; FQ-13-10; DQ-13-1; DQ-13-6; DQ-13-7.
- Future-roadmap/reuse constraints: no public shared diagnostic/job record; no root exports; no placeholder modules/classes just to reserve names; no hard dependency on torch, numpy, scipy, pandas, matplotlib, video stacks, dataset SDKs, trainer modules, workflow modules, report writers, or export codecs through package imports.
- Examples or demos covered: import/API posture only.
- Out of scope: public prediction records, prediction producer helpers,
  materializers, export bridge behavior, evaluation records, visualization/report
  records, operation adapters, docs examples beyond import/error docstrings.
- Dependencies: approved Stage 13 planning artifact; current central error pattern.

### Tasks

- Keep package `__init__.py` files lightweight and export only names implemented in this phase.
- Add or update package tests for `rphys.prediction`, `rphys.evaluation`, and `rphys.analysis` importability and root export posture.
- Extend import-boundary tests to guard against forbidden optional/backend/workflow imports from Stage 13 package homes.
- Add focused error tests only for code-backed errors present after this phase.
- Assert that a broad prediction error is absent unless the implementation has
  introduced a public prediction-operation surface that needs it.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify Stage 13 package homes and root exports stay lightweight and code-backed. | yes |
| focused error unit tests if errors are added | Verify code-backed broad errors and absence/presence expectations. | yes, if errors are changed |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: package homes import cleanly; evaluation/analysis broad
  bases remain available; no broad prediction error is exported unless
  code-backed public prediction-operation behavior exists.
- Design-decision evidence: no placeholder exports, no root re-exports, no public generic diagnostic/job record.
- Future-roadmap/reuse evidence: Stage 14 smoke can import package homes without depending on optional adapters; future shared diagnostics still have a recorded revisit trigger.
- Example/demo evidence: import/API posture covered by package tests.
- Documentation evidence: module docstrings or error docstrings state broad
  catch-point intent where public errors exist.
- Scientific contract evidence: error/import boundaries are ready for later phases to expose provenance and failure modes without hiding backend or workflow state.

### Phase Workflow State

- Phase execution plan: complete; `docs/roadmap/stage-13/phases/scaffold-imports-errors.md`
- Planning/refinement budget: small; one refinement pass if import/export naming becomes ambiguous.
- Implementation/refinement budget: small.
- PR review budget: small; focus on public import posture and minimal error taxonomy.
- Blocker-resolution budget: stop if implementing a broad error requires a
  specific subclass tree, root exports, or new shared public helper.
- Pre-submit blocker gate: no placeholder exports; no forbidden imports; no public generic job/diagnostic APIs.
- Merge record: pending

### Risks And Stop Conditions

- Risks: exporting future names early; missing a forbidden optional import; broad
  error taxonomy expanding without test-driven need.
- Stop conditions: a change requires root-level convenience exports, public generic diagnostics/jobs, or any concrete Stage 13 behavior record before Phase 2.
- Assumptions: current empty package homes can remain lightweight while later phases add code-backed names.

### Completion Summary

- Implementation: complete; package-home docstrings, broad error docstrings, Stage 13 scaffold package tests, and import-boundary tests.
- Validation: `uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py`; `make test-package`; `make test-summary`; `make validate-pr`; `git diff --check`.
- PR: [#85](https://github.com/samcantrill/rphys/pull/85), opened against `develop` with required title.
- Merge: pending
- Follow-up: Phase 2 replaces legacy method/learner output records with
  returned-`Batch` contracts; it should not add a public prediction record family.

## Phase 2: Batch-Native Method, Learner, And Training Output

Status: pending
Slug: `batch-native-method-learner-output`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: remove `MethodOutput`, method-output specs/adapters, and `StepOutput`
  and make prediction/training step execution ordinary `Batch -> Batch` field
  transformation over caller-provided assembled inputs.
- Files/modules owned: `src/rphys/methods/**`, `src/rphys/learning/**`,
  `src/rphys/training/**`, `src/rphys/data/**` for field projection helpers only
  if needed, operation adapter modules if the implementation already has a
  suitable home, package-local validation helpers, source-mirrored tests for
  methods/learning/training, `tests/contracts/test_stage13_batch_prediction_contract.py`,
  focused synthetic integration tests only if a useful assembled-input flow fits
  this phase, and test support fakes for fake method/learner behavior.
- Behavior implemented: fake method/operation prediction returns a `Batch` with
  `predictions/<key>` fields; `Learner.step` returns a `Batch`; generic
  `BatchOutputSpec` or equivalent validation can assert that returned batches
  contain declared fields with expected locators, roles, schemas, payload types,
  metadata/provenance, and conflict/pass-through behavior; training output fields
  are declared by a `TrainingPlan`-owned `TrainingOutputSpec` or an equivalent
  protocol; native training validates required fields by mode and
  backpropagates only the declared objective field; inference input projection
  excludes target and reference fields; optional pass-through policy marks fields
  that may be carried alongside outputs for later evaluation-ready artifact
  export. Do not export public `MethodOutput`, `MethodOutputSpec`,
  `MethodOutputAdapter`, `apply_method_output`, `StepOutput`,
  `PredictionRecord`, `PredictionCollection`, `PredictionCollector`,
  `PredictionPlan`, `PredictionResult`, or `PredictionRunner` names in Stage 13.
- Decisions applied: DD-13-1, DD-13-2, DD-13-3, DD-13-9, DD-13-10; FQ-13-1; FQ-13-2; FQ-13-8; FQ-13-10; DQ-13-2.
- Future-roadmap/reuse constraints: prediction field identity remains flexible but
  inspectable through `FieldLocator`/`FieldValue` roles and sample metadata; keep
  batch-output specs generic enough for methods, learners, and batch operations
  without recreating method-output patch records; keep `SampleCollection` for
  durable/sample snapshots and `Iterable[Batch]` for transient batch streams; do
  not introduce waveform-only rows, prediction-specific datasources, or a public
  prediction collection family; preserve the trainer boundary by making training
  engines read only fields declared in the plan-owned output spec.
- Examples or demos covered: batch-native method prediction, batch operation
  prediction, learner returned-batch output, training objective-field validation,
  and target-free inference projection.
- Out of scope: durable export, uncollation implementation, evaluation,
  visualization/report records, report writers, operation pipeline runtime ownership,
  generic jobs, trainer prediction loops, `TrainingResult` payload mining,
  datasource scans, dataloader construction, checkpoint selection, logger
  integration, public prediction package APIs.
- Dependencies: Phase 1; Stage 10 `Method` and `PredictionContext`; Stage 11
  collection/collector contracts; Stage 12 `Learner`, `LoopMode`,
  `LoopContext`, `TrainingPlan`, and `NativeTrainingEngine`.

### Tasks

- Define or refine field projection helpers for model inputs so prediction code
  receives only approved input fields and fails loudly if target/reference fields
  would be consumed during inference.
- Define a `Batch -> Batch` fake method or operation path that adds
  `predictions/<key>` fields without mutating input batches by default.
- Refactor `Method.predict` to return `Batch` and remove public
  `MethodOutput`, `MethodOutputSpec`, `MethodOutputAdapter`, and
  `apply_method_output` exports.
- Replace method-output specs/adapters with a generic `BatchOutputSpec` or
  equivalent returned-batch validator. If implementation needs a helper for
  raw backend outputs, it should write fields directly onto a `Batch` using the
  generic spec and must not recreate a method-specific patch object.
- Refactor `Learner.step` to return `Batch` and remove public `StepOutput`
  exports.
- Define a `TrainingOutputSpec` or equivalent protocol owned by `TrainingPlan`
  that declares objective, loss, metric, diagnostic, and mode-required fields on
  returned learner batches.
- Update `TrainingPlan` construction/preflight so train mode requires an
  objective locator, mode-required locators are unique and role-valid, and
  missing/invalid specs fail before the loop starts.
- Update `NativeTrainingEngine` to validate returned learner batches through the
  plan-owned spec before recording summaries, backward, or optimizer/scheduler
  steps, and to backpropagate only the declared objective field in train mode.
- Add direct fake `Method.predict` tests and fake `Learner.step` tests returning
  `Batch` values.
- Assert no dependency on `Trainer`, `TrainingEngine`, or `TrainingResult` for payload recovery.
- Assert package exports do not add public `MethodOutput*`, `StepOutput`,
  prediction record, collection, collector, plan, result, runner, datasource, or
  export names.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Cover batch prediction field addition, generic returned-batch output spec validation, learner returned-batch output, plan-owned training-output spec validation, input projection, pass-through policy, diagnostics, metadata, and provenance. | yes |
| `make test-contract` | Cover public batch prediction/training-output contracts, method-output removal, no target leakage, and datasource/workflow exclusions. | yes |
| `make test-package` | Verify code-backed exports and lightweight imports. | yes |
| focused integration test if added | Prove method/learner/batch-operation prediction and native training objective-field consumption over synthetic assembled inputs. | yes, if integration coverage is added in this phase |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: valid method/learner/operation flows produce `Batch` outputs
  with declared fields; invalid selectors, missing train objectives, invalid
  objective payloads, duplicate locators, role/schema/type mismatches, plan/spec
  omissions, or target leakage fail loudly with field-locator and mode context.
- Training guardrail evidence: `TrainingPlan` owns the output spec used by
  NativeTrainingEngine; train-mode runs without a plan-owned objective locator
  fail before the loop starts; per-step validation happens before backward,
  optimizer, scheduler, metric summary, or event completion side effects.
- Design-decision evidence: prediction behavior is assembled-input-only and
  Batch-native; no lifecycle, dataloaders, datasources, checkpoints, export,
  logging, workflow state, or public prediction record family is introduced.
- Future-roadmap/reuse evidence: Stage 14 smoke can use the same `Batch` field
  shape before Phase 3 uncollation/export; future modalities can add fields by
  locator/metadata without wrapper records.
- Example/demo evidence: tests demonstrate caller-provided batches -> batch
  prediction method/op -> `Batch` with prediction fields, plus learner step ->
  returned `Batch` -> training engine consumes declared objective field.
- Documentation evidence: docstrings document field roles, input projection,
  target-free inference, pass-through policy, training-output fields, and the
  trainer-free artifact boundary.
- Scientific contract evidence: prediction fields preserve locator/provenance
  context without interpreting sampling, alignment, masks, labels, or
  physiological meaning.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium; refine if field-role projection or
  training-output spec scope becomes ambiguous.
- Implementation/refinement budget: medium.
- PR review budget: medium; focus on field-role schema, import direction, and
  trainer/datasource exclusions.
- Blocker-resolution budget: reopen DQ-13-2 if prediction production cannot
  stay Batch-native over assembled inputs.
- Pre-submit blocker gate: no trainer dependency; no `TrainingResult` payload
  mining; no datasource/dataloader/checkpoint behavior; no uncollation/export
  side effects; no public prediction record family.
- Merge record: pending

### Risks And Stop Conditions

- Risks: field-role semantics overfit early examples; removing old output records
  touches more Stage 10/12 tests than expected; learner context adaptation becomes
  too broad.
- Stop conditions: implementation needs trainer-owned prediction loops,
  datasource scans, dataloader construction, checkpoint selection, public generic
  job state, public prediction records, or mutation/export behavior.
- Assumptions: Stage 10/11/12 tests can be updated in the same phase to the
  returned-`Batch` contract without preserving public output shims.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: Phase 3 consumes `Batch` prediction fields for explicit uncollation
  and sample artifact export/reload behavior.

## Phase 3: Uncollation And Sample Artifact Export/Reload

Status: pending
Slug: `uncollation-sample-artifacts`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement explicit batch-field uncollation policy/evidence and prove
  durable prediction/test/evaluation artifacts are exported and reloaded as one
  sample artifact record per `Sample` over existing export/save and datasource
  behavior.
- Files/modules owned: `src/rphys/data/**` collation/uncollation policy records
  and functions; `src/rphys/datasources/**` generic sample artifact layout or
  adapter modules if needed; `src/rphys/ops/export.py` only for a narrow
  multi-record helper if duplication proves it is needed; source-mirrored unit
  tests under `tests/unit/rphys/{data,datasources}/`; contract tests for
  uncollation/export boundaries; integration tests for synthetic sample artifact
  export/reload; test support synthetic codecs/export fakes only where existing
  support is insufficient.
- Behavior implemented: explicit `UncollatePolicy`/`UncollatePlan` or
  equivalent names; split policies for list-like values, batch-axis values,
  broadcast values, drop/error behavior, and adapter-owned custom splitters if
  needed; sample-count and metadata alignment validation; item-to-export adapters
  from uncollated `Sample` entries to descriptor-backed `RecordExportRequest`s;
  generic sample artifact layout/datasource reload behavior. Do not implement
  `PredictionMaterializer`, `PredictionMaterializationPlan`,
  `PredictionMaterializationResult`, `PredictionExportPlan`, or
  `PredictionExportResult`.
- Decisions applied: DD-13-4, DD-13-5, DD-13-7, DD-13-9; FQ-13-2; FQ-13-3; DQ-13-3; DQ-13-6.
- Future-roadmap/reuse constraints: preserve Stage 8 export/save ownership;
  keep collection mechanics storage-agnostic and preferably consolidated under
  `rphys.data.collections`; make any shared durable-handoff helper generic over
  adapter-produced export requests rather than collection internals; require the
  sample item-to-export adapter to provide a source `RecordRef` or augmented
  export-record descriptor whose declared fields match exported field values;
  the uncollation/artifact phase must not define visualization codecs,
  prediction manifests, output directory conventions, prediction storage
  classes, `rphys.ops.collections`, or datasource scanning. Phase 5 may define
  lightweight codec identities, codec hints, render descriptors, or fake
  dependency-light test codecs only; real visualization/report codecs remain
  deferred optional import-gated work.
- Examples or demos covered: batch with prediction fields -> explicit
  uncollation -> per-sample artifact export -> generic sample artifact datasource
  reload; evaluation-ready artifact export with allowed target/reference
  pass-through fields.
- Out of scope: implicit sample uncollation, temporal stitching, scientific
  reconstruction, backend tensor conversion without an adapter, implicit
  mutation, implicit export, report save adapters, prediction-specific storage
  path, concrete codecs or manifest writers, `BatchCollection`, `BatchCollector`.
- Dependencies: Phases 1-2; Stage 8 export/save and derived datasource
  contracts; current data container collate/uncollate behavior.

### Tasks

- Define explicit uncollation policy/evidence naming consistent with existing
  data collation code.
- Implement field-level split behavior for all approved policy cases and fail
  loudly when sample count, metadata alignment, or field policy is invalid.
- Define projection/pass-through behavior that lets evaluation-ready artifacts
  carry target/reference fields without letting inference computation consume
  those fields.
- Convert `Batch` outputs to individual `Sample` entries before export.
- Define sample artifact item-to-export adapters that provide source `RecordRef`
  or augmented export-record descriptors for every exported field.
- Add generic sample artifact layout/datasource reload behavior if existing
  datasource/index/sample-source surfaces do not already provide it directly.
- Decide whether a narrow export/save iteration helper is necessary; if existing export APIs are sufficient, document direct composition and add tests/examples without a redundant public wrapper.
- If a generic helper is added, place it with existing export/save ownership and keep it as adapter-produced `RecordExportRequest` -> codec selection -> save -> export evidence mapping over existing export/save and `DerivedDataSourceBuilder`, not a new collection namespace, writer, or storage family.
- Require every exportable sample item to resolve to a `RecordExportRequest` with
  a source `RecordRef` or equivalent descriptor declaring the exported fields.
  Loaded `FieldValue` mappings alone are insufficient for durable export because
  existing export/save validates fields against the source record descriptor.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Cover uncollation policies, sample-count validation, field projection/pass-through, and unsupported payload failures. | yes |
| `make test-contract` | Cover public uncollation/sample artifact contracts and storage-boundary exclusions. | yes |
| `make test-integration` | Prove synthetic prediction fields can uncollate to samples, export through existing export/save, and reload through datasource/sample-source behavior. | yes |
| `make test-package` | Verify new exports remain code-backed and lightweight. | yes |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: batch outputs are uncollated to one `Sample` per entry;
  fields use explicit uncollation policy; target/reference fields are carried
  only through approved pass-through; durable export walks sample items through
  existing export/save operations with a source `RecordRef` or augmented export
  record descriptor for each exported item.
- Design-decision evidence: export evidence delegates to existing export/save
  and datasource APIs; no prediction manifest, writer, codec, output directory
  schema, storage class, public prediction export wrapper, `BatchCollection`, or
  `BatchCollector` appears.
- Future-roadmap/reuse evidence: Stage 14 can reload sample artifact prediction
  fields through normal datasource/index/sample behavior; future reconstruction
  algorithms can plug in through explicit views/policies.
- Example/demo evidence: tests or docs show `Batch(predictions/<key>)` ->
  uncollated `Sample`s -> existing export/save -> sample artifact datasource
  reload.
- Documentation evidence: docstrings document uncollation policy, pass-through
  policy, unsupported payloads, source-record/export-descriptor requirements,
  and export delegation.
- Scientific contract evidence: uncollation records provenance and does not
  infer alignment, sampling, temporal stitching, NaN handling, or physiological
  interpretation beyond explicit field splitting/broadcast/drop policy.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium; refine if sample artifact reload requires
  generic datasource adapter decisions or export APIs need widening.
- Implementation/refinement budget: medium.
- PR review budget: medium; focus on uncollation semantics and IO boundary.
- Blocker-resolution budget: reopen FQ-13-3/DD-13-5 if export cannot be expressed through existing export/save and derived datasource behavior.
- Pre-submit blocker gate: no implicit mutation/export; no prediction-specific
  storage; no domain-specific datasource family; no new codec/manifest/output
  directory convention.
- Merge record: pending

### Risks And Stop Conditions

- Risks: uncollation policy is too backend-specific; sample artifact adapters
  duplicate datasource behavior; pass-through policy is confused with model
  inputs.
- Stop conditions: implementation requires implicit reconstruction,
  prediction-specific persistence, export API widening beyond evidence mapping,
  durable export without source `RecordRef` or equivalent field descriptor
  evidence, `BatchCollection`, `BatchCollector`, or hidden conflict replacement.
- Assumptions: existing export/save APIs can handle uncollated sample fields as
  ordinary fields when the item-to-export adapter supplies matching source record
  descriptors and loaded field values.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: Phase 4 consumes sample/batch field projection and sample artifact
  reload policy in runtime sample-collection and metric operation recipes.

## Phase 4: Runtime Sample-Collection And Metric Operations

Status: pending
Slug: `sample-collection-metric-ops`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement reusable runtime operations for grouping loaded samples into
  sample collections, sorting/projecting/stitching collections, emitting revised
  samples, and binding existing metrics as sample or collection operations.
- Files/modules owned: `src/rphys/data/collections.py`,
  `src/rphys/collections.py` only for migration or transitional compatibility if
  implementation proves it is still needed, `src/rphys/ops/**`,
  `src/rphys/metrics/**` adapter modules if needed, source-mirrored unit tests,
  `tests/contracts/test_stage13_sample_collection_ops_contract.py`,
  `tests/contracts/test_stage13_metric_operation_contract.py`,
  `tests/integration/test_stage13_synthetic_sample_collection_pipeline.py`, and
  package export/import tests.
- Behavior implemented: a generic grouping/collation operation from
  `Iterable[Sample]` to `Iterable[SampleCollection]`; collection operations for
  metadata/field-key grouping, sorting, filtering, projection, and
  stitching/concatenation into `SampleCollection` or `Sample`; metric operation
  adapters that run existing `Metric` contracts against `Sample` or
  `SampleCollection` inputs and write declared metric fields onto returned
  `Sample`, `Batch`, or `SampleCollection` outputs; public metric observation
  collection/view/result surfaces are removed or made private migration details.
- Decisions applied: DD-13-1, DD-13-6, DD-13-7, DD-13-9, DD-13-10; FQ-13-4; FQ-13-5; FQ-13-10; DQ-13-4; DQ-13-6; DQ-13-7.
- Future-roadmap/reuse constraints: evaluation, inference, reporting, dataset
  formatting, and analysis recipes must reuse `OperationStep`, `Operation`,
  `OperationContext`, `OperationResult`, `OperationPipeline`,
  `SampleCollectionView`, metric-field-bearing samples, `Collector`, and
  `CollectionView`; durable metric/evaluation outputs, when requested, use
  item-to-export adapters plus existing export/save and datasource assembly;
  dataset-formatting-like examples must use the same substrate without public
  generic job APIs. Metric grouping/reduction must stay field-native and must
  not reintroduce `MetricObservationCollection` or metric-specific observation
  views under another name.
- Examples or demos covered: runtime grouping, collection sorting, stitching
  window samples into record samples, metric-as-sample-operation, and
  collection-level metric field aggregation flow.
- Out of scope: public `EvaluationRunner`, public `Evaluator`,
  `EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`, `ComparisonSpec`,
  `EvaluationEngine`, `InferenceEngine`, public `PipelineJob`, public `JobPlan`,
  public `JobRunner`, evaluator-owned lifecycle/buffers, datasource scans,
  split/index construction, dataloader construction, metric catalogs, concrete
  reconstruction algorithms, checkpoint selection, report output directories,
  scheduler/resume/artifact state, workflow runtime, and a pipeline registry.
- Dependencies: Phases 1-3; Stage 11 sample collections/views and metric
  contracts; existing operation primitives.

### Tasks

- Define runtime grouping/collation behavior that accepts `Iterable[Sample]` and
  emits `Iterable[SampleCollection]` with item metadata/provenance preserved.
- Define collection operations for sorting by fields or `CollectionItem`
  metadata, selecting fields, filtering/skipping with diagnostics, and
  concatenating/stitching member sample fields into one revised `Sample`.
- Define metric field bindings that adapt existing `Metric`, `MetricContext`,
  `MetricValue`, and field binding behavior to `SampleOperation` or collection
  operation outputs.
- Refactor metric public exports and contracts so `MetricObservation`,
  `MetricObservationCollection`, `MetricObservationView`, and `MetricResult` are
  removed from public APIs or made private migration details. Public metric
  operations should expose `MetricValue`, metric output specs if needed, and
  ordinary `metrics/<key>` fields on returned containers.
- Structure evaluation examples as sample artifact datasource -> samples ->
  grouping operation -> collection sort/stitch operation -> sample metric
  operation(s) -> optional field grouping/reduction -> optional
  item-to-export adapter/export/save -> optional report operation.
- Add package export assertions that no public metric observation/result family,
  evaluation engine/protocol/result, generic job names, scheduler/resume/artifact
  names, registry, or output-directory APIs are exported.
- Add integration coverage showing generic operations express an evaluation-like
  pipeline without `EvaluationPlan`, `EvaluationResult`, `EvaluationRunner`, or a
  public generic job.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Cover grouping/collation, collection sorting/projection/stitching, field-native metric operation bindings, metric-observation removal/private migration behavior, failure policies, metadata, and provenance. | yes |
| `make test-contract` | Cover sample-collection operation and metric-operation public contracts, including absence of public metric observation/result surfaces. | yes |
| `make test-integration` | Prove evaluation-like and dataset-formatting-like recipes compose through existing operation/pipeline and collection/view primitives. | yes |
| `make test-package` | Assert exports are code-backed and forbidden evaluation engine/protocol/result/runner/job/registry names are absent. | yes |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: generic operations transform samples into grouped
  collections, sorted/stitched collections, revised samples, or metric fields
  with explicit diagnostics and provenance.
- Design-decision evidence: evaluation-like recipes execute through generic
  operations; package exports contain no `MetricObservation`,
  `MetricObservationCollection`, `MetricObservationView`, `MetricResult`,
  `EvaluationRunner`, `Evaluator`, `EvaluationProtocol`, `EvaluationPlan`,
  `EvaluationResult`, `EvaluationEngine`, `InferenceEngine`, public
  `PipelineJob`, `JobPlan`, `JobRunner`, or registry.
- Future-roadmap/reuse evidence: Stage 14 smoke can compose evaluation/report
  examples with operation metadata without a second lifecycle.
- Example/demo evidence: tests demonstrate sample artifact datasource -> runtime
  grouping -> collection sorting/stitching -> metric-as-sample-operation ->
  summary/reduction -> report operation style composition, and at least one
  example where two recipes consume the same sample artifact datasource or
  `SampleCollection`.
- Documentation evidence: docstrings state grouping/sorting/stitching,
  metric-binding, field-projection, and explicit execution substrate semantics.
- Scientific contract evidence: missing prediction/reference fields, missing
  grouping metadata, invalid selectors/projection policy, metric failures, empty
  groups/masks where descriptors support them, and leakage-sensitive grouping
  warnings/failures are explicit and inspectable.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium-high; refine if grouping/stitching or metric
  operation adapter naming becomes ambiguous.
- Implementation/refinement budget: medium-high.
- PR review budget: high; focus on no-engine/no-generic-job constraints,
  collection provenance, and scientific metric/stitching semantics.
- Blocker-resolution budget: reopen DQ-13-4/DQ-13-6 if evaluation-like recipes
  cannot be expressed with existing operations, pipelines, collections, views,
  collectors, metrics, and report records.
- Pre-submit blocker gate: no public evaluation/inference engine, protocol, plan,
  result, comparison spec, registry, or public generic job/runtime names; no
  evaluator-owned datasource/dataloader/output-directory behavior.
- Merge record: pending

### Risks And Stop Conditions

- Risks: grouping/stitching schemas grow too broad; operation adapters drift into
  a runner lifecycle; metric/report failures are masked as successful partial
  scores.
- Stop conditions: implementation requires public evaluator lifecycle, public
  generic job metadata, datasource scans, dataloader construction, checkpoint
  selection, report output directory conventions, or a registry.
- Assumptions: Stage 11 metric and view contracts are sufficient for
  contract-level metric examples without concrete physiological metrics.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: Phase 5 consumes samples, sample collections, metric fields,
  visualization fields, and report records in operation-compatible outputs.

## Phase 5: Visualization, Reports, And Diagnostics

Status: pending
Slug: `visualization-reports-recipes`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p5-visualization-reports-recipes`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p5-visualization-reports-recipes`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement dependency-light visualization/report operation-compatible
  builders and structured in-memory report/table/diagnostic renderer records.
  Analysis remains generic sample/collection grouping, reduction, projection,
  metric-field computation, and report-row construction through existing
  pipeline components.
- Files/modules owned: `src/rphys/analysis/**`; analysis package exports;
  package-local visualization/report validators;
  `tests/unit/rphys/analysis/test_visualization*.py`;
  `tests/unit/rphys/analysis/test_reports*.py`;
  `tests/contracts/test_stage13_visualization_contract.py`;
  `tests/contracts/test_stage13_report_contract.py`; package import/export
  tests; docs/docstrings for visualization and report surfaces.
- Behavior implemented: structural `VisualizationOperation` and
  `ReportOperation` where useful as ordinary operation-compatible adapters,
  `VisualizationOutput` or equivalent field-ready render descriptors if needed,
  `Report`, `ReportSection`, `ReportTable`, report cell/row helpers if needed,
  `DiagnosticRenderer`, and renderer output records as data. No public
  `AnalysisOp`, `AnalysisContext`, or `AnalysisResult` family is added by
  default.
- Decisions applied: DD-13-1, DD-13-8, DD-13-9, DD-13-10; FQ-13-6; FQ-13-7; FQ-13-9; FQ-13-10; DQ-13-5; DQ-13-6; DQ-13-7.
- Future-roadmap/reuse constraints: Stage 13 may define codec keys/hints,
  field-ready render descriptors, and dependency-light fake test codecs only.
  Real visualization render/save codecs, report materializers, markdown writers,
  figure/video writers, and rich-media adapters remain deferred optional
  import-gated work. Structured report records should be consumable by future
  adapters without changing generic sample/metric operation recipes; structured
  report datasets, markdown report fields, figure/video fields, and rich-media
  outputs use item-to-export adapters plus existing field export/save rather
  than report-format writers or ad hoc file writes; operation compatibility
  should reuse existing operations instead of adding new execution machinery.
- Examples or demos covered: visualization field attachment, report building,
  markdown/report-field handoff, and analysis-as-generic-pipeline analogue.
- Out of scope: checkpoint selection, training, log crawling, mutation of
  predictions, eager plotting backend imports, pandas/dataframe core type,
  implicit HTML/PDF/CSV/Markdown writers, implicit plot/image/video file writes,
  dashboard adapters, artifact store, report output directory schema, report
  save conventions, rich media backend imports in core.
- Dependencies: Phases 1-2; Phase 4 where reports consume samples,
  `SampleCollection`, metric fields, summary fields, or visualization fields;
  Stage 11 sample collections/views and metrics contracts.

### Tasks

- Document analysis-as-composition examples using Phase 4 grouping/reduction,
  metric-field operations, and report-row construction. Do not add public
  analysis operation/result records by default.
- Define visualization operation protocols or adapters that attach fields such
  as `visualizations/<key>`, `figures/<key>`, or `videos/<key>` to `Sample`,
  `Batch`, or `SampleCollection` outputs with primitive provenance and explicit
  codec keys/hints for later export.
- Define lightweight visualization output/render descriptor records if field
  payloads need a structured value that can be exported without importing a
  plotting or video backend in core.
- Define report operation-compatible builders that consume sample, collection,
  metric, summary, visualization, and primitive fields to produce `Report` or
  `ReportTable` objects, or report fields such as `reports/<key>`.
- Define report/section/table records with primitive cells, visualization
  references, row/column validation, ordering, provenance, and diagnostics.
- Define diagnostic renderer output records as data, not files or backend render
  calls.
- Add fake visualization/report tests over approved inputs, including
  `SampleCollection`, `Batch`, metric-field-bearing samples or collections,
  visualization-field-bearing samples or collections, and `Report` where
  supported.
- Add report tests for metric-field rows, sample/collection/summary rows,
  visualization references, invalid cells/rows, provenance, optional
  structured-report item-to-export adapter behavior if implemented, explicit
  codec keys/hints or fake test codecs, and no implicit file-writer/dataframe
  behavior.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Cover visualization outputs, report/table validation, renderer output records, and invalid inputs. | yes |
| `make test-contract` | Cover visualization/report public contracts and side-effect exclusions. | yes |
| `make test-package` | Verify code-backed exports and no pandas/plotting/report-writer imports. | yes |
| docs/example review | Ensure docstrings/examples describe analysis-as-pipeline composition, visualization fields, in-memory report behavior, and operation compatibility. | yes |
| `git diff --check` | Catch whitespace and formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: visualization/report operations return structured data or
  attach ordinary visualization/report fields; reports/tables are in-memory
  primitive/provenance-aware records; invalid rows/cells fail loudly.
- Design-decision evidence: no `AnalysisOp`, `AnalysisContext`,
  `AnalysisResult`, dataframe core type, eager plotting backend import, file
  writer methods, output directories, artifact store, checkpoint selection, log
  crawling, or mutation side effects appear.
- Future-roadmap/reuse evidence: future visualization codecs and report
  save/render adapters can consume descriptor fields or records additively;
  structured report dataset handoff can use the same field-export path;
  dataset-formatting-like examples remain operation/collection/export based.
- Example/demo evidence: tests show `SampleCollection`, metric-field-bearing
  samples, summary fields, or visualization fields -> `ReportTable` rows.
- Documentation evidence: docstrings state accepted inputs, provenance,
  side-effect-free behavior, explicit codec-key/export handling, fake-codec-only
  Stage 13 validation, and writer/backend deferrals.
- Scientific contract evidence: report rows preserve metric/sample scope and
  provenance so per-sample/per-window/per-record/per-subject/per-dataset
  interpretation is inspectable.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium; refine if report/table schema becomes too broad.
- Implementation/refinement budget: medium.
- PR review budget: medium-high; focus on report schema and dependency-light side-effect boundaries.
- Blocker-resolution budget: reopen DQ-13-5 if report records require file writers or dataframe/plotting behavior.
- Pre-submit blocker gate: no writer/render backend imports; no report output directory schema; no checkpoint/log/training behavior.
- Merge record: pending

### Risks And Stop Conditions

- Risks: report API freezes file-format assumptions; diagnostic renderer drifts into backend rendering; analysis inputs become too permissive.
- Stop conditions: implementation requires real pandas, plotting, rich media,
  file writers, dashboard/artifact APIs, or checkpoint/log/training behavior in
  core instead of codec hints/descriptors and fake dependency-light test codecs.
- Assumptions: in-memory report/table records are enough for Stage 14 smoke and downstream adapter handoff.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: Phase 6 completes cross-package examples and final validation.

## Phase 6: Docs, Synthetic Examples, And Final Validation

Status: pending
Slug: `docs-examples-final-validation`
Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p6-docs-examples-final-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p6-docs-examples-final-validation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path unless final validation failures trigger expanded refinement

### Scope

- Goal: complete Stage 13 docs, examples, synthetic composition tests, package export review, and final validation evidence.
- Files/modules owned: public docstrings in Stage 13 packages; possible Stage 13 docs/example file under `docs/` if the implementation workflow accepts it; `tests/integration/test_stage13_*`; package import/export tests; final validation summary evidence in this implementation plan after phase merge.
- Behavior implemented: examples and tests prove Batch-native method/operation
  prediction, learner returned-batch output, explicit uncollation,
  sample-granular artifact export/reload for separate downstream recipes,
  runtime sample-collection grouping/sorting/stitching, metric-as-sample or
  collection operations, summary/report rows, visualization fields,
  dataset-formatting analogue,
  public import posture, and no forbidden runner/job/storage/report-writer/import
  behavior.
- Decisions applied: all DD-13 decisions and FQ/DQ queues; especially DD-13-6, DD-13-7, DD-13-8, DD-13-9, and no-runner/no-generic-job acceptance criteria.
- Future-roadmap/reuse constraints: Stage 14 receives a clear synthetic smoke target; Stage 15 and future adapters can wrap operation metadata and report records without changing Stage 13 core; shared diagnostics/job extraction remains deferred.
- Examples or demos covered: all planning examples.
- Out of scope: new public product behavior beyond documentation/test-driven polish; concrete algorithms; real datasets; GPU checks; performance profiling; public report save/render adapters; docs-only PRs outside the phase workflow.
- Dependencies: Phases 1-5.

### Tasks

- Add or complete synthetic integration coverage for Batch-native method or
  operation prediction, learner returned-batch output, uncollation/export, sample
  artifact datasource reload into more than one operation recipe, runtime
  sample-collection grouping/sorting/stitching, metric-as-sample or collection
  operations, visualization/report records, summary/report rows, and
  dataset-formatting analogue.
- Update public docstrings and any Stage 13 docs/example page to show substrate reuse without a generic runner.
- Review package exports and import-boundary tests for all implemented names and forbidden names.
- Assert no public `PredictionRunner`, no standalone public `EvaluationRunner`,
  no `EvaluationEngine`, no `InferenceEngine`, no public
  `EvaluationProtocol`/`EvaluationPlan`/`EvaluationResult` by default, no public
  `PipelineJob`/`JobPlan`/`JobRunner`, no registry, no scheduler/resume/artifact
  lifecycle, no trainer-owned prediction capture, no prediction-specific storage,
  no report writers, and no hard dataframe/plotting dependencies.
- Run final validation commands or record exact residual risks and unavailable checks.
- Update this implementation plan with phase completion/merge evidence after PR merge according to the implementation workflow.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify final public exports and import boundaries. | yes |
| `make test-unit` | Verify all Stage 13 unit coverage remains passing. | yes |
| `make test-contract` | Verify public contracts and no-runner/no-generic-job guardrails. | yes |
| `make test-integration` | Verify synthetic Stage 13 composition examples. | yes |
| `make test-summary` | Produce standard test summary evidence. | yes |
| `uv lock --check` | Verify lockfile consistency. | yes |
| `git diff --check` | Catch whitespace and formatting issues. | yes |
| `make validate-pr` | Run broad PR validation before closeout when practical. | yes |

### Acceptance Evidence

- Behavior evidence: synthetic examples exercise the accepted end-to-end Stage 13 flow without external datasets, GPUs, concrete algorithms, or workflow runtime.
- Design-decision evidence: final package/export review proves forbidden runner/job/storage/report-writer/import names and behaviors were not introduced.
- Future-roadmap/reuse evidence: docs/tests explicitly show
  prediction/evaluation-like/report/dataset-formatting-like reuse of existing
  operation, collection/view/collector, metric, export/save, and derived
  datasource substrates, including separate launchable handoffs through derived
  datasets.
- Example/demo evidence: Batch-native method/operation prediction, learner
  returned-batch output, uncollation/export, sample artifact datasource reload
  into multiple operation recipes, runtime grouping/sorting/stitching,
  metric-as-operation, visualization fields, report building,
  dataset-formatting analogue, and analysis-as-pipeline analogue are all
  represented in tests/docs.
- Documentation evidence: public docstrings and docs examples explain shapes,
  units where relevant, provenance, failure behavior, grouping/reference scope,
  uncollation/export order, and dependency deferrals.
- Serialized-output evidence: docs/tests show persisted predictions, persisted
  metric/evaluation outputs, and any persisted structured report datasets are
  reloaded through datasource descriptors/index/sample-source behavior rather
  than domain-specific datasource families or runner-owned result caches.
- Scientific contract evidence: examples preserve selector/reference/grouping,
  label availability, split/leakage-sensitive grouping, per-scope
  interpretation, missing data/failure reporting, and explicit uncollation
  semantics at the contract level.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: medium; refine if final examples reveal cross-package inconsistencies.
- Implementation/refinement budget: medium-high due final validation surface.
- PR review budget: high; focus on cross-package API coherence, docs, examples, and validation evidence.
- Blocker-resolution budget: stop and reopen the relevant queue if final examples require any forbidden runner/job/storage/report-writer/workflow behavior.
- Pre-submit blocker gate: all final validation commands run or residual risks recorded; no forbidden public APIs; no docs/examples implying out-of-scope behavior.
- Merge record: pending

### Risks And Stop Conditions

- Risks: cross-package inconsistencies appear late; final examples pressure APIs to add convenience beyond accepted scope; broad validation is slow or exposes unrelated failures.
- Stop conditions: final composition cannot be expressed through existing operations, collections, views, collectors, explicit export/save, and typed result records; Stage 13 requires any forbidden public runner/job/runtime/storage/report-writer dependency.
- Assumptions: Phases 1-5 merge cleanly and their public names remain compatible with the accepted examples.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: Stage 14 should harden the synthetic smoke path rather than expand Stage 13 core behavior.

## Cross-Phase Validation

- Full relevant test command: `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`; `make validate-pr`.
- Docs/template checks: public docstrings and any Stage 13 docs/examples must match implemented names and avoid implying public method-output patch specs/adapters, public metric observation/result collections, prediction/evaluation runners, evaluation/inference engines, evaluation protocols/plans/results by default, public generic jobs, prediction-specific storage, report writers, real visualization/report codecs, plotting/dataframe dependencies, trainer-owned prediction capture, registries, or workflow/runtime ownership.
- Scientific/workflow contract checks: preserve Stage 10/12 returned-`Batch`
  semantics, Stage 11 collection/view/collector semantics, the learner-vs-engine/trainer
  boundary, explicit selectors/references/grouping/uncollation/report
  requirements, provenance, failure behavior, and per-scope interpretation.
- Example/demo checks: Batch-native method/operation prediction; learner
  returned-batch output; explicit uncollation/export; sample artifact datasource
  reload into multiple operation recipes; runtime grouping/sorting/stitching;
  metric-as-sample/collection operation; report building; dataset-formatting
  analogue; analysis-as-pipeline analogue.
- Manual review focus: import dependency direction, public exports, forbidden
  name absence, private helper boundaries, uncollation/pass-through semantics,
  export delegation, operation adapter shape, report side-effect boundaries, and
  final residual-risk reporting.

## Reuse Examples Required Across Phases

- Canonical Sample/Batch flow: samples -> optional `SampleCollection` or view ->
  collated batches -> operation pipeline when needed -> `Batch` outputs with
  prediction or derived fields -> explicit projection/pass-through ->
  uncollation to samples -> optional `SampleCollection` -> item-to-export
  adapter -> existing export/save operations -> sample artifact datasource
  assembly when durable reload is required. Domain packages provide validators,
  selectors, field-handle adapters, and item-to-export-request adapters; they do
  not redefine collection mechanics.
- Prediction reuse: caller-provided batches or samples flow through method,
  learner, or operation prediction code and return ordinary `Batch` values with
  `predictions/<key>` fields. `SampleCollection` is used only when a durable
  sample snapshot or runtime grouped view is useful. There is no public
  prediction collection or batch collection family.
- Evaluation-like reuse: a reloaded sample artifact datasource flows through
  generic sample/collection operations, metric operation adapters, metric-field
  grouping/reduction, optional visualization/report operations, and optional
  export/save.
  Ordered execution remains in `OperationPipeline` or explicit Python
  composition. No public evaluation protocol/result/engine is introduced by
  default.
- Report reuse: metric-field-bearing samples, `SampleCollection` values, summary
  fields, or visualization fields feed a report operation; output is an
  in-memory `Report`/`ReportTable` or ordinary `reports/<key>` field. If a
  structured report dataset is needed, report items use the same
  item-to-export-request mapping and existing export/save path. No implicit
  writer, dataframe, plotting backend, output directory, or artifact store
  appears.
- Dataset-formatting-like reuse: a prepared `SampleCollection` flows through `SampleOperationPipeline` or a collection view, then item-to-export adapter, explicit export/save, and derived datasource assembly. This demonstrates the shared substrate pattern without adding public `PipelineJob`, `JobPlan`, `JobRunner`, scheduler, artifact, resume, or workflow lifecycle APIs.
- Prediction/evaluation/report export reuse: uncollated prediction fields,
  metric/evaluation fields, and structured report records are ordinary sample
  fields passed to existing export/save behavior and datasource refs; durable
  handoff uses item-to-export-request mapping plus existing codec
  selection/save operations; domain code records bridge evidence but does not
  own storage.
- Serialized output datasource reuse: once durable, prediction/metric/report
  outputs are interacted with as ordinary derived datasources. Domain packages
  may provide adapters that explain how to export or interpret fields, but they
  must not introduce `PredictionDataSource`, `EvaluationDataSource`, or
  `ReportDataSource` families.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No readiness blocker found. The source planning artifact records passed functionality, behavior, design, validation/phase-shaping, and plan quality gates; queues are resolved; required future-roadmap/reuse findings have revisit triggers. | note | Convert the six accepted phases into implementation-ready phase guidance and carry all locked constraints into phase acceptance gates. | resolved |
| Final design review found the controlling Stage 13 plan aligned with maintainer decisions after the latest stale-surface/spec-ownership refinements. | note | Keep the latest maintainer revision authoritative over historical planning rows; execute phases with package-export checks for removed public method-output, step-output, metric-observation/result, evaluation runner/protocol/result, and analysis operation/result surfaces. | approved |

Gate result:

- Status: passed and approved
- Review evidence: read `AGENTS.md`, `.codex/workflows/roadmap-version-planning.md`, `.codex/workflows/roadmap-version-implementation.md`, `.codex/templates/roadmap-stage-implementation-plan.md`, `docs/roadmap.md` Stage 13 and vertical-slice context, and `docs/roadmap/stage-13/planning.md`; checked Stage Gates, Stage Readbacks, Functionality Agreement Queue, Design Agreement Queue, Design Decisions, Design Implication Review, Future Roadmap And Reuse Safety Review, Functionality And Decision Audit, Examples And Demonstrations, Validation Strategy, Phase Shaping, Plan Quality Gate, Accepted Assumptions And Deferrals, and Resume Checkpoints.
- Accepted risks: exact module and record names may adjust during
  implementation if accepted semantics, import boundaries, and validation
  obligations remain intact; package-local diagnostic/helper duplication is
  accepted until repeated public semantics justify extraction; existing
  export/save APIs may make a dedicated sample artifact helper unnecessary if
  direct composition is tested and documented.
- Revisit triggers: implementation cannot express accepted examples through existing operations/pipelines/collections/views/collectors/metrics/export/save evidence; any phase proposes standalone public `EvaluationRunner`, evaluation/inference engines, evaluation protocols/plans/results by default, public generic job/runtime APIs, trainer-owned prediction capture, prediction-specific storage, public `MethodOutput*`/`StepOutput`, public `MetricObservation*`/`MetricResult`, report writers, real visualization/report codecs in core, plotting/dataframe core dependencies, registry behavior, or workflow ownership; Stage 10-12 public contracts change before execution.

## Final Approval

- Approval status: approved for roadmap-version-implementation preflight and phase execution.
- Approved scope: six sequential phases covering scaffold/imports/errors;
  Batch-native method/learner/training-output refactor; uncollation and sample
  artifact export/reload; runtime sample-collection and metric operations;
  visualization/report records and recipe examples; docs/examples/final
  validation.
- Accepted risks: exact module names may adjust; package-local diagnostic
  duplication may remain; sample artifact export/reload may be docs/direct
  composition instead of a public wrapper if existing APIs are sufficient.
- Deferred items: concrete algorithms; real datasets; GPU/performance profiling; real report save/render adapters; real visualization/report codecs; dataframe/plotting/rich media adapters; public generic job/diagnostic extraction; workflow/scheduler/artifact/resume lifecycle; Stage 14 smoke hardening beyond focused Stage 13 synthetic examples.
