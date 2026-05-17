# Roadmap Stage 13 Planning

Status: draft; functionality agreement, behavior confirmation, design
implication review, future-roadmap/reuse safety review, functionality/decision
audit, examples/demonstrations, validation strategy, phase shaping, and plan
quality gate complete. Stop point: implementation plan is drafted and revised;
no code implementation has started.
Roadmap version: `v13`
Stage directory: `docs/roadmap/stage-13/`
Implementation plan: `docs/roadmap/stage-13/implementation-plan.md`

## Latest Maintainer Revision

This revision supersedes earlier Stage 13 wording that planned public
`EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`, `ComparisonSpec`, or
compatibility adapters for `MethodOutput`/`StepOutput`.

Locked direction:

- Remove `MethodOutput` and `StepOutput` immediately rather than extending their
  compatibility lifetime. `Method.predict` should return `Batch`; `Learner.step`
  should return `Batch`; `NativeTrainingEngine` should validate and consume
  declared objective/loss/metric/diagnostic fields through a structured
  `TrainingOutputSpec` or equivalent protocol.
- Remove public `MethodOutputSpec`, `MethodOutputAdapter`, and
  `apply_method_output` with `MethodOutput`. Returned-batch conformance should
  be expressed through a generic `BatchOutputSpec` or equivalent validator over
  ordinary `Batch` fields, not method-specific patch specs.
- Make `TrainingOutputSpec` plan-owned. `TrainingPlan` is the source of truth
  for objective, loss, metric, diagnostic, and mode-required field locators.
  NativeTrainingEngine should preflight the plan spec and validate every
  returned learner `Batch` before backward/optimizer steps, failing loudly for
  missing specs, missing required fields, invalid objective payloads,
  unsupported field roles, duplicate locators, or mode/spec mismatches.
- Focus Stage 13 on reusable Sample/Batch/Collection operations:
  `Iterable[Sample] -> Iterable[SampleCollection]`, `SampleCollection ->
  SampleCollection`, `SampleCollection -> Sample`, `Sample -> Sample`, and
  `Batch -> Batch`.
- Add runtime sample-collection grouping, sorting, filtering, projection,
  stitching/concatenation, and metric/comparison operations as generic pipeline
  components. Datasource grouping remains descriptor/index-time behavior for
  split/index construction; it does not replace runtime grouping over loaded
  samples.
- Treat evaluation, inference, reporting, analysis, and dataset formatting as
  recipes composed from generic operations unless repeated code-backed semantics
  prove that a shared engine/protocol is needed. Do not add `EvaluationEngine`,
  `InferenceEngine`, a pipeline registry, or a public generic job/runtime API in
  Stage 13.
- Keep metrics in `rphys.metrics` as detached metric contracts that write
  declared `metrics/<key>` fields onto `Sample`, `Batch`, or
  `SampleCollection` outputs through explicit operations/adapters. Grouping,
  combining, reducing, viewing, exporting, and reporting metric values should
  use generic sample and `SampleCollection` operations, not
  `MetricObservationCollection` or metric-specific observation views.
- Remove or de-publicize the `MetricObservation`, `MetricObservationCollection`,
  `MetricObservationView`, and `MetricResult` family during Stage 13. Public
  metric behavior should expose `MetricValue`, metric output specs if needed,
  and field-writing metric operations over `Sample`, `Batch`, or
  `SampleCollection`.
- Do not add a public `AnalysisOp`, `AnalysisContext`, or `AnalysisResult`
  family by default. Analysis summaries are generic pipeline compositions over
  samples, collections, metric fields, group/reduce operations, and report-row
  construction.
- Keep visualization and reporting as explicit operation-compatible behavior
  only where useful. `VisualizationOperation` may attach ordinary visualization
  fields such as `visualizations/<key>`, `figures/<key>`, or `videos/<key>` with
  provenance and codec/export hints. `ReportOperation` may assemble
  `Report`/`ReportTable` objects or report fields from sample, collection,
  metric, summary, and visualization fields. Any markdown, figure, video, or
  rich-media materialization must use explicit codec/export/save behavior.
- Stage 13 may define codec hint fields, codec-key descriptors, render
  descriptors, and dependency-light fake test codecs. Real matplotlib, video,
  markdown, image, and rich-media render/save adapters are deferred optional
  import-gated work.
- Reconsider collection placement before implementation. Preferred direction is
  to consolidate sample-specific collection records, collectors, views, and
  operations under `rphys.data.collections`; `rphys.collections` should remain
  only as a transitional or truly generic home if moving it is disruptive. Do
  not add `rphys.ops.collections`.

Historical queue, decision, validation, and phase-shaping rows below are retained
as planning evidence. Where they mention evaluation protocols/plans/results or
legacy method/learner output compatibility, or where they route metrics through
`MetricObservationCollection`, public analysis operation/result records, or
fixed `rphys.collections` ownership, this latest revision is the controlling
design.

## Source Evidence

| Source | Relevant content | Used for | Notes |
| --- | --- | --- | --- |
| `AGENTS.md` | `rphys` is a reusable research library; base imports stay lightweight; public behavior needs code, tests, and docs; scientific operations must expose provenance, failure behavior, sampling/alignment assumptions, split/group handling, and edge cases. | Repository constraints and write scope. | Latest refinement updates this planning artifact, the Stage 13 implementation plan, and targeted Stage 13 roadmap text without changing implementation code. |
| `.codex/workflows/roadmap-version-planning.md` | Planning passes record evidence, agreement gates, design proposals, reviews, validation, phase shaping, and handoff state in `planning.md`. | Workflow gate and stop point. | Current pass completes validation, phase shaping, and plan quality, then stops before implementation-plan drafting. |
| `.codex/prompts/roadmap-stage-context-planner.md` | Requires source evidence, exploration coverage, roadmap extraction, overview, capability triage, module behavior, functional requirements, and dependency-ordered functionality queue. | Current specialist pass instructions. | Queue states use `repo-resolved`, `needs maintainer discussion`, `blocked`, `pending`, or later `locked`/`deferred`. |
| `.codex/templates/roadmap-stage-planning.md` | Required planning artifact sections and queue/readback shape. | Document structure. | Planning sections are now populated through plan quality; implementation-plan handoff remains pending. |
| `docs/roadmap.md` sections 1-7 | Field-centric design, export-as-operation rule, thin semantic objects, package ownership, lightweight import policy, fail-loud scientific behavior, and no generic workflow/artifact runtime. | Architecture constraints. | Stage 13 must keep prediction/evaluation/analysis helpers thin, explicit, and provenance-aware. |
| `docs/roadmap.md` Milestone 8 | Durable predictions and processed outputs are normal fields exported through `SaveOp` and derived `DataSourceRef`; Method/Learner/Trainer/Loss/Objective/Metric must not write artifacts implicitly. | Prediction export boundary. | Stage 13 should reuse existing export/save and derived datasource behavior, not create prediction-specific storage. |
| `docs/roadmap.md` Milestones 10-12 | Stage 10 supplies `Method`, `PredictionContext`, patch-like `MethodOutput`, and explicit `apply_method_output`; Stage 11 supplies sample collections, metric observations, and metric observation views; Stage 12 supplies `StepOutput`, `Learner`, `Trainer`, and primitive `TrainingResult` while keeping predictions opaque to trainers. | Upstream contracts and compatibility. | Stage 13 now treats `MethodOutput`/`StepOutput.predictions` as compatibility pressure and refactors the preferred flow toward native `Batch -> Batch` prediction without moving payload capture into trainers. |
| `docs/roadmap.md` Milestone 13 | Direct target: treat predictions, processed outputs, diagnostics, metric observations, and analysis inputs as normal field containers and structured result objects. Earlier roadmap wording listed runner names, but maintainer-approved Stage 13 planning now reframes execution as Sample/Batch-native pipelines plus operation-compatible adapters. | Direct roadmap extraction. | Roadmap explicitly rejects a prediction-specific storage path, alternate scoring runtime, hidden plotting system, dataframe dependency, waveform-only prediction object, and public `Prediction*` record family. |
| `docs/roadmap.md` Milestones 14-15 and critical path | Stage 14 hardens synthetic smoke coverage; Stage 15 deepens training profiling and data-path optimization; root smoke flow now targets method prediction, sample-granular artifact export, reload, metric observation view, analysis op, and report. | Future compatibility. | Stage 13 should create contracts that Stage 14 can smoke-test and Stage 15 can profile around without adding workflow/runtime ownership. |
| `docs/GLOSSARY.md` | Defines `MethodOutput` as patch-like, `StepOutput` predictions as opaque, `TrainingResult` as summary-only, `Analysis` as work over predictions/metrics/provenance, and `Export` as explicit field writing through codecs. | Vocabulary and naming. | Confirms prediction/evaluation/report behavior should stay distinct from training, checkpointing, and datasource crawling. |
| `docs/findings.md` | Prior PURE findings reinforce datasource, formatting/materialization, prepared data, and training iteration as separate layers. | Boundary pressure. | Supports keeping evaluation/report helpers out of raw datasource scanning and training loaders. |
| `docs/roadmap/stage-10/planning.md`; `src/rphys/methods/**`; `tests/integration/test_synthetic_method_prediction_flow.py` | Stage 10 locked patch-like `MethodOutput`; `apply_method_output` explicitly applies fields to a `Batch` with copy/conflict policy; methods do not export, train, score, or mutate input by default. | Prediction input and compatibility baseline. | Stage 13 should plan a Batch-native refactor and keep any `MethodOutput` bridge explicit and transitional. |
| `docs/roadmap/stage-11/planning.md`; `src/rphys/collections.py`; `src/rphys/data/collections.py`; `src/rphys/metrics/**` | Stage 11 implemented collection/view/collector contracts, `SampleCollection`, `SampleCollectionViewPlan`, `MetricObservationCollection`, `MetricObservationViewPlan`, and detached metric value/result behavior. | Evaluation protocol and report input baseline. | Stage 13 can bind these into protocols/results without defining concrete metrics, dataframe adapters, or hidden metric state. |
| `docs/roadmap/stage-12/planning.md`; `docs/roadmap/stage-12/examples.md`; `src/rphys/learning/**`; `src/rphys/training/**`; `tests/integration/test_stage12_synthetic_training_flow.py` | Stage 12 keeps trainers from materializing predictions; `StepOutput.predictions` may be `MethodOutput`, `Sample`, `Batch`, or `None`; `TrainingResult` is primitive summary evidence and does not contain prediction payloads. | Learner/trainer compatibility. | Batch-native compatibility adapters may call method or learner prediction entrypoints directly, but must not mine `TrainingResult` for predictions. |
| `src/rphys/prediction/__init__.py`; `src/rphys/evaluation/__init__.py`; `src/rphys/analysis/__init__.py` | Package homes exist with empty public exports. | Current Stage 13 implementation state. | Stage 13 will introduce first code-backed public names in these packages if approved. |
| `src/rphys/ops/export.py`; `src/rphys/datasources/derived.py`; `src/rphys/datasources/refs.py` | Export specs/results and derived datasource assembly already exist; derived assembly builds descriptor-only derived refs from successful export evidence without prediction, evaluation, or report semantics. | Durable output/export boundary. | Stage 13 should rely on these surfaces for durable prediction, evaluation, and structured report fields and avoid a second storage family. |
| `src/rphys/datasources/adapters.py`; `src/rphys/datasources/filters.py`; `src/rphys/datasources/indexes.py`; `src/rphys/datasources/splits.py`; `src/rphys/datasources/sources.py`; `src/rphys/datasources/prepared.py` | Datasource code is descriptor-first: scan/view/filter/group/split/index/source layers prepare payload-free descriptors; sample sources and prepared readers materialize later from explicit request/context evidence. | Datasource pattern comparison requested by maintainer. | Stage 13 should copy the explicit descriptor/evidence/delayed-materialization pattern, not the datasource scan/filter/split/index ownership. |
| `src/rphys/errors.py`; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; `pyproject.toml` | Broad evaluation and analysis errors exist; no broad prediction error exists; package/import tests enforce exact exports and no heavy optional imports. | Error and import-boundary posture. | Revised recommendation is to add no broad prediction error unless implementation adds code-backed public prediction-operation behavior needing a distinct catch point. |
| `src/rphys/ops/core.py`; `src/rphys/ops/context.py`; `src/rphys/ops/contracts.py`; `src/rphys/ops/pipelines.py` | `OperationStep`, `Operation`, `OperationContext`, `OperationResult`, `OperationContract`, and operation pipelines already provide dependency-light execution, ordered composition, type compatibility checks, metadata/provenance, failure-mode declarations, and side-effect evidence. | Design implication and reuse safety review. | These surfaces are sufficient for evaluation/report/dataset-formatting-style composition; Stage 13 should not add a public generic `PipelineJob`. |
| `src/rphys/collections.py`; `src/rphys/data/collections.py`; `src/rphys/metrics/results.py` | `CollectorResult` is deliberately distinct from `OperationResult`; `CollectionItem` carries item metadata/provenance; `SampleCollectionView` and `MetricObservationCollection` provide reusable pre-metric and post-metric view contracts. | Design implication and reuse safety review. | Supports operation adapters plus collection/view reuse without an evaluator-owned lifecycle. |

## Exploration Coverage

| Area | Files or patterns checked | Findings | Gaps |
| --- | --- | --- | --- |
| Working tree state | `git status --short` | `docs/roadmap.md` was already modified before this pass; current refinement also updates the Stage 13 roadmap text. | Treat current working tree content as source evidence and preserve unrelated local changes. |
| Roadmap and workflow docs | `AGENTS.md`, `.codex/workflows/roadmap-version-planning.md`, `.codex/prompts/roadmap-stage-context-planner.md`, `.codex/templates/roadmap-stage-planning.md`, `docs/roadmap.md` sections 1-7, Milestones 8, 10-15, critical path, vertical slice, release gates, anti-patterns, final strategy | Stage 13 is the prediction/evaluation/analysis/report contract layer after methods, metrics, learners, trainers, and export exist. | Later passes should reread `docs/roadmap.md` because it is locally modified. |
| Feature docs | `find docs/features -maxdepth 3 -type f` | No `docs/features` directory exists. | `docs/roadmap.md` and adjacent stage artifacts are canonical for this pass. |
| Prior stage artifacts | `docs/roadmap/stage-10/planning.md`, `stage-10/implementation-plan.md`, `docs/roadmap/stage-11/planning.md`, `stage-11/implementation-plan.md`, `docs/roadmap/stage-12/planning.md`, `stage-12/implementation-plan.md`, `stage-12/examples.md` | Stages 10-12 are now implemented/approved enough to answer most Stage 13 compatibility questions: patch outputs, metric observation collections, sample collections/views, opaque trainer predictions, and summary-only training results. | This pass did not read every phase merge record; adjacent planning/implementation summaries and current code were sufficient. |
| Prediction/evaluation/analysis package homes | `src/rphys/prediction/__init__.py`, `src/rphys/evaluation/__init__.py`, `src/rphys/analysis/__init__.py` | Empty public exports with package docstrings. | No code-backed Stage 13 names, tests, examples, or docs exist yet. |
| Methods and prediction outputs | `src/rphys/methods/core.py`, `src/rphys/methods/output.py`, `src/rphys/methods/__init__.py`, `tests/integration/test_synthetic_method_prediction_flow.py` | `Method.predict` returns patch-like `MethodOutput`; explicit `apply_method_output` handles copy/conflict behavior; method contracts forbid trainer/export/metric behavior. | Stage 13 should revise toward `Batch -> Batch` prediction and document/test compatibility rather than adding prediction collection records. |
| Learning/training outputs | `src/rphys/learning/output.py`, `src/rphys/learning/supervised.py`, `src/rphys/training/core.py`, `src/rphys/training/backend.py`, `src/rphys/training/results.py`, `docs/roadmap/stage-12/examples.md`, `tests/integration/test_stage12_synthetic_training_flow.py` | Learner outputs can carry opaque predictions; native trainer summarizes metrics/steps but does not expose prediction payloads; prediction mode still returns only `TrainingResult`. | Stage 13 producer/adapters may call `Learner.step(..., LoopMode.PREDICT)` directly or wrap `Method.predict`; they must not use `TrainingResult` as a payload source. |
| Metric and sample collection surfaces | `src/rphys/collections.py`, `src/rphys/data/collections.py`, `src/rphys/metrics/core.py`, `src/rphys/metrics/specs.py`, `src/rphys/metrics/results.py` | Collection items preserve metadata/provenance; `SampleCollection` and `MetricObservationCollection` are immutable snapshots; metric observation views are explicit and dependency-light. | Stage 13 needs protocol/result records that compose these collections without adding concrete metrics or dataframe/report adapters. |
| Export and derived datasource behavior | `src/rphys/ops/export.py`, `src/rphys/datasources/derived.py`, `src/rphys/datasources/refs.py` | Export/save and derived datasource assembly are established and descriptor-only. | Stage 13 should define bridge/result semantics, not new low-level storage writers. |
| Package/import/error tests | `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `src/rphys/errors.py`, `pyproject.toml` | Empty dependencies; core import tests already include prediction/evaluation/analysis as lightweight imports. Evaluation/analysis broad errors exist; prediction-specific broad error does not. | Stage 13 import/export expectations and prediction error taxonomy need planning decisions. |
| Archive/discussions | `.codex/prompts/roadmap-stage-*.md`, `.codex/workflows/**`, adjacent stage planning and examples, `docs/findings.md` | Workflow assets and adjacent stage artifacts are the durable discussion record relevant here. | No separate archive/discussion directory was needed. |

## Roadmap Extraction

- Baseline roadmap outcome: define dependency-light prediction, evaluation,
  analysis, and report contracts that treat predictions, processed outputs,
  diagnostics, metric observations, and report inputs as field-addressed
  containers or structured result records.
- Prerequisites: Stage 8 export/save and derived datasource assembly; Stage 10
  `Method`, `PredictionContext`, patch-like `MethodOutput`, and explicit
  apply/merge helper; Stage 11 `SampleCollection`,
  `SampleCollectionViewPlan`, `MetricObservationCollection`, and
  `MetricObservationViewPlan`; Stage 12 `Learner`, `LoopMode`,
  `StepOutput`, and summary-only `TrainingResult`.
- Prior or adjacent roadmap links: Stage 10 provides raw prediction patches;
  Stage 11 provides detached metric observations and collection/view
  vocabulary; Stage 12 provides learner prediction step semantics but keeps
  trainers from materializing predictions; Stage 14 will harden the synthetic
  smoke path; Stage 15 later profiles/optimizes training and data paths without
  changing Stage 13 contract boundaries.
- Primary feature docs: none found under `docs/features`; `docs/roadmap.md` is
  canonical.
- Deferred or out-of-scope roadmap work: concrete prediction algorithms,
  concrete physiological metrics, real plotting/rendering backends,
  dataframe/pandas integration, dashboarding, alternate scoring runtimes,
  trainer-owned prediction capture, checkpoint selection, ad hoc log crawling,
  datasource scanning/split/index construction, codec/save implementation
  details, report file conventions, workflow runtime, artifact store, concrete
  resampling/reconstruction algorithms unless supplied as explicit adapters or
  views, and heavy optional dependencies in core imports.
- Compatibility obligations: predictions stay field-addressed on `Batch` and
  `Sample`; preferred prediction output becomes Batch-native; existing patch-like
  `MethodOutput` behavior is handled through explicit compatibility adapters if
  still present; durable prediction, evaluation, and structured report fields use
  existing export/save and datasource behavior after batch outputs have been
  uncollated into samples; `TrainingResult` is not a prediction payload source;
  evaluation protocols name selectors, references, grouping, sample/batch field
  projection, sample views, metrics, metric observation views, report
  requirements, and failure behavior; analysis and visualization return
  structured results by default and do not write arbitrary files.
- Public surfaces or durable artifacts likely affected: public names under
  `rphys.data` for uncollation policy/evidence, under `rphys.datasources` for
  generic sample artifact adapters/layouts, under `rphys.evaluation` for
  protocols, plans, operation adapters, results, and evaluation failure records,
  and under `rphys.analysis` for analysis/visualization operations, contexts,
  results, reports, report tables, and diagnostic renderers. Durable artifacts,
  when produced, should be ordinary exported sample fields and datasource refs
  through existing export/save behavior, not prediction-specific storage.

## Overview

- What this stage covers: Batch-native prediction flow over already assembled
  `Batch` iterables or `SampleCollection` inputs, target-free inference field
  projection, explicit pass-through policy for evaluation-ready target/reference
  fields, public batch-field uncollation policy/evidence, sample-granular
  artifact export/reload through datasource adapters, evaluation protocol, plan,
  operation-compatible adapters, and result records over existing sample, metric,
  and report surfaces; analysis and visualization operation contracts that
  return structured results; dependency-light report/table and diagnostic-renderer
  records; package exports, docs, examples, and import-boundary tests.
- Why it exists: the library needs a reusable post-training/post-method layer
  that can transform batches, persist sample artifacts, score, analyze, and
  report prediction fields without
  moving those responsibilities into methods, learners, trainers, metrics,
  datasource adapters, export ops, plotting libraries, or workflow systems.
- Primary outcomes: users can run methods/ops over batches and receive batches
  with `predictions/<key>` fields; keep target/reference fields out of inference
  inputs while optionally carrying them as artifact pass-through fields; uncollate
  batch outputs into individual samples; export one sample per artifact record;
  reload those samples in separate evaluation flows; bind prediction and reference
  fields into evaluation protocols; run multiple metric or report workflows over
  the same sample artifact datasource; and compose analysis/report objects without
  dataframe or plotting dependencies.
- Non-goals: training, checkpoint selection, project config, datasource
  discovery, split construction, index building, raw sample loading,
  concrete rPPG algorithms, concrete metric catalogs, automatic trainer
  prediction capture, prediction-specific storage, ad hoc file writers,
  plotting/rendering backends, dataframe dependencies, dashboards, or workflow
  orchestration.
- Related feature docs: none found.
- Impacted repo areas: `src/rphys/data` collation/uncollation,
  `src/rphys/datasources` artifact adapters, `src/rphys/evaluation`,
  `src/rphys/analysis`, package import tests, unit tests under
  `tests/unit/rphys/{data,datasources,evaluation,analysis}/`, contract tests for
  public behavior, synthetic integration tests for batch prediction to sample
  artifact to metric/report composition, and docs/examples.
- Current state: prediction/evaluation/analysis package homes exist but export
  no public names; upstream method, metric, collection, learning, training,
  export, and derived datasource contracts are code-backed; no Stage 13 code,
  package exports, tests, examples, or docs exist yet.
- Key uncertainty: how much reusable pipeline/job structure Stage 13 should
  expose for evaluation, reports, dataset-formatting-like jobs, and future
  post-processing without creating a second execution runtime beside existing
  operations, pipelines, collections, and downstream workflow tools.
- User clarification questions and resolved answers: maintainer feedback now
  locks the Sample/Batch-native direction, rejects a public prediction record
  family, and requires sample-granular artifact export/reload.
- Planning priority or optimization target: maximize contract composability for
  the synthetic vertical slice while preserving explicit uncollation/export,
  lightweight imports, field/provenance semantics, and future Stage 14 smoke
  hardening.

## Stage Gates

| Gate | Required inputs | Current blockers or queue items | Status | Date/round | Notes |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements | Roadmap extraction, overview, capability triage, module behavior map, functional requirements, initial functionality queue | FQ-13-5 has been reframed by maintainer feedback from standalone runner inclusion to reusable pipeline/job structure review; FQ-13-8 and FQ-13-9 were manager-resolved from repository evidence. | passed for context-planner pass | 2026-05-17 / context planner + manager review | First specialist pass complete; manager review and maintainer feedback reject an evaluation-specific runner by default and ask design to consider reusable structure over existing pipeline primitives. |
| Functionality-agreement review | Functionality Agreement Queue | None. | passed | 2026-05-17 / manager review + maintainer agreement | FQ-13-5 is locked: no standalone `EvaluationRunner`; evaluation must reuse existing pipeline/collection mechanics, and the design pass must consider reusable base/protocol structures before evaluation-specific instantiation. |
| Behavior confirmation | Resolved functionality-agreement queue | None. | passed | 2026-05-17 / manager behavior confirmation | Included/default/failure/unsupported behavior is locked for design input. |
| Context checkpoint if applicable | Resume checkpoint, refreshed context if needed | Not needed. | not needed | 2026-05-17 / validation planner | Refresh if roadmap or Stage 10-12 public contracts change before implementation-plan drafting. |
| Design-agreement review | Proposed implementation shape, design decisions, design-agreement queue, design implication review, future-roadmap/reuse safety review | No blockers. No maintainer-decision packet is required. Public generic `PipelineJob` remains rejected; evaluation uses records plus operation-compatible adapters over existing ops/collections. | passed for design review | 2026-05-17 / design implication review | Proceed to validation planning. Do not add standalone `EvaluationRunner` or public generic `PipelineJob` in Stage 13. |
| Validation, phase shaping, and plan quality gate | Validation strategy, phase shaping, traceability review, specialist evidence check | None. | passed | 2026-05-17 / validation planner | Implementation-plan drafting proceeded after this gate passed. |
| Implementation plan approved | implementation-plan review and approval | None. | passed | 2026-05-17 / implementation planner + manager review | Created `docs/roadmap/stage-13/implementation-plan.md`; ready for the roadmap-version-implementation workflow. No code was implemented. |
| Final design-review approval | Latest maintainer revision, roadmap Stage 13 text, implementation plan, design-review follow-up decisions | None. | passed and approved | 2026-05-17 / final design review | Approved for implementation workflow. The controlling plan removes public method-output patch specs/adapters, `StepOutput`, public metric observation/result surfaces, prediction/evaluation runners, public evaluation protocols/results by default, analysis operation/result records, real visualization/report codecs, and generic job/runtime APIs. |

## Stage Readbacks

| Stage | Gate result | Locked decisions | Defaults and recommendations | Open questions or blockers | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements | first-pass complete | None locked by the specialist pass. | Default to thin, explicit, dependency-light contracts; keep prediction field projection, uncollation, and export explicit; reuse Stage 8/10/11/12 surfaces. | Need to settle how evaluation reuses existing pipeline logic without duplicating a runner. | Functionality-agreement review by managing agent. |
| Functionality-agreement review | passed | FQ-13-1 through FQ-13-10 are resolved. FQ-13-5 locks no standalone `EvaluationRunner`; FQ-13-8 now avoids `RemotePhysPredictionError` unless code-backed public prediction-operation behavior proves need; FQ-13-9 keeps reports in-memory by default, permits ordinary field-export handoff for structured report datasets, and defers report file writers. | Evaluation should instantiate existing `OperationStep`/`OperationPipeline`, `SampleOperationPipeline`/`BatchOperationPipeline`, `Collection`, `Collector`, and `CollectionView` patterns. Design should consider a small reusable job descriptor/protocol only if repeated evaluation/report/dataset-formatting structure cannot be expressed cleanly with existing primitives. | None. | Behavior confirmation. |
| Behavior confirmation | passed | Stage 13 includes Batch-native prediction, explicit uncollation policy, sample-granular artifact export/reload, evaluation protocols/plans/results, pipeline-friendly evaluation composition, analysis/report structures, public errors/imports/docs, and synthetic composition coverage. | Keep execution pipeline-based and Sample/Batch-native; add reusable job structures only if design evidence justifies them; defer concrete algorithms, report writers, plotting/dataframe adapters, checkpoint selection, workflow runtime, and Stage 14 full smoke hardening. | None. | Design proposal. |
| Context checkpoint if applicable | not needed |  |  |  |  |
| Design-agreement review | passed for design review | Locked: no standalone `EvaluationRunner`; no public generic `PipelineJob`; no public `Prediction*` record/export family; no `BatchCollection`/`BatchCollector`; prediction stays as fields on `Sample`/`Batch`. | Reuse existing ops/collections/export/datasource surfaces as the execution, snapshot, and durable handoff substrate. Keep shared diagnostic/job records package-local/private until repeated public semantics justify extraction. | None. No maintainer discussion packet is open. | Validation planning. |
| Validation, phase shaping, and plan quality gate | passed | Validation must prove Sample/Batch-native prediction, explicit uncollation, sample artifact export/reload, and evaluation/report layers over existing `ops`, collection/view/collector, method-output compatibility, learner-output compatibility, export/save, and report records without adding standalone `EvaluationRunner` or public generic job APIs. Six reviewable phases are ready for implementation-plan drafting. | Keep diagnostics/job helper extraction private/package-local unless repeated public semantics justify a later design revisit. Final validation should include package, unit, contract, integration, docs, diff, lock, and PR validation checks where practical. | None. | Implementation-plan drafting and revision; do not implement code from this artifact directly. |
| Implementation-plan handoff | passed | Six reviewable implementation phases are recorded in `docs/roadmap/stage-13/implementation-plan.md`, with no public standalone `EvaluationRunner`, no public generic job runtime, no public prediction record/export family, and Stage 13 behavior native to `Sample` and `Batch`. | Execute phases sequentially through `.codex/workflows/roadmap-version-implementation.md`; maintain package-local/private shared helpers unless implementation proves a public extraction is necessary and reopens design. | None. | Implementation workflow phase execution; no code was implemented in this planning pass. |
| Final design-review approval | passed and approved | Latest revision locks Sample/Batch-native prediction, generic `BatchOutputSpec`-style returned-batch validation, plan-owned `TrainingOutputSpec`, sample-granular artifact handoff, field-native metrics, no public metric observation/result family, analysis-as-pipeline composition, visualization/report fields and records with fake-codec-only Stage 13 validation, and collection placement review toward `rphys.data.collections`. | Proceed to roadmap-version-implementation preflight. Treat historical rows below as evidence only when they conflict with the latest revision. | None. | Phase 1 implementation workflow preflight. |

## Capability Triage

| Capability | Decision | Rationale | Requirements produced | Notes |
| --- | --- | --- | --- | --- |
| Sample/Batch-native prediction flow | include | Maintainer clarified that `Sample` and `Batch` should remain the common data objects and prediction should be field meaning, not a new record family. | FR-13-1 | Preferred runtime shape is `Batch -> Batch` through methods/ops; existing `MethodOutput`/`StepOutput.predictions` are compatibility pressure, not the preferred new Stage 13 surface. |
| Sample-granular durable artifacts | include | Durable test/evaluation artifacts should serialize individual sample entries, not batch records or prediction wrappers. | FR-13-2 | Every exportable batch output must uncollate into `Sample` entries before export; each exported sample becomes one datasource record. |
| Collate/uncollate policy expansion | include | Current LIST-only uncollation cannot safely split arbitrary post-model batch fields; Stage 13 must make per-field uncollation explicit. | FR-13-3 | Add public uncollation evidence/policies for serializable batch fields, including fail-loud behavior when split policy is absent or invalid. |
| Generic sample artifact datasource layouts | include | Test artifacts, evaluation artifacts, and later analysis artifacts share the same layout pattern: sample directories/records with field resources and descriptors. | FR-13-4 | Add generic sample-artifact layout/datasource adapter behavior, not `PredictionDataSource`/`EvaluationDataSource` families. |
| Evaluation protocol and plan contracts | include | Direct Milestone 13 target and core scientific comparison contract. | FR-13-5 | Protocol names selectors, references, grouping, projection/pass-through, sample views, metrics, observation views, report requirements, and failure behavior. |
| Pipeline-based evaluation execution shape | include | Maintainer feedback notes evaluation should reuse the same generic process as iterable datasource/collection -> operations/pipeline -> export/report, avoiding a duplicate runner. | FR-13-6 | Design must test whether existing operation/collection primitives are enough, and only propose shared job descriptors/protocols if they remove duplication across evaluation, reports, dataset formatting, and similar pipeline jobs. |
| AnalysisOp and VisualizationOp structural operations | include | Direct Milestone 13 target and needed for structured analysis outputs. | FR-13-7 | No plotting backend or file writes in core. |
| Structured Report, ReportTable, and DiagnosticRenderer records | include | Direct Milestone 13 target; reports are dependency-light structured objects by default. | FR-13-8 | Minimum shape needs agreement to avoid freezing dataframe/report conventions too early. |
| Package exports, broad errors, docs, examples, and import-boundary tests | include | First public surfaces require code-backed exports and no heavy optional imports. | FR-13-9 | Prediction broad error is unresolved public API question. |
| Dataframe, pandas, plotting, rich media, dashboard, and notebook adapters | defer | Roadmap says these are optional import-gated adapters, not Stage 13 core dependencies. | None | Later adapter stages may consume report/table objects. |
| Concrete rPPG analysis algorithms, physiological metric catalogs, signal reconstruction algorithms | defer | Roadmap and prior stages intentionally define contracts before concrete research components. | None | Use synthetic fakes in tests only. |
| Checkpoint selection, trainer-owned prediction capture, and training-loop scoring runtime | out of scope | Roadmap says analysis does not select checkpoints and Stage 12 trainers keep predictions opaque. | None | Downstream projects or later optional adapters may orchestrate this. |
| Datasource scanning, split construction, index building, and sample loading | out of scope | Owned by datasource/lazy IO/sample source stages. | None | Stage 13 may consume prepared inputs and existing collections only. |
| Prediction-specific record/collection/export/datasource family | out of scope | Maintainer prefers native `Sample`/`Batch` flow and generic sample artifact datasources. | None | Do not add `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, `PredictionExportPlan`, `PredictionDataSource`, `BatchCollection`, or `BatchCollector` in Stage 13. |
| Generic workflow runtime, artifact store, or report file convention | out of scope | Repository boundary assigns orchestration/artifacts to downstream projects or `loom`. | None | Stage 13 returns structured records and explicit export/save evidence. |

## Module Behavior Map

| Module or area | Intended behavior | Why it matters | Codebase capability enabled | Requirements produced | Status |
| --- | --- | --- | --- | --- | --- |
| `rphys.data` / `rphys.collections` | Own the common `Sample`, `Batch`, `FieldValue`, `FieldLocator`, `SampleCollection`, `SampleCollector`, and collection view behavior. Stage 13 should extend this layer only where uncollation/export of batch fields needs generic support. | Keeps prediction, evaluation, dataset formatting, and artifact export compatible through the same field-container objects. | Sample/Batch-native prediction, evaluation, and artifact pipelines. | FR-13-1, FR-13-2, FR-13-3 | revised direction |
| `rphys.methods` / `rphys.learning` | Upstream providers of prediction computation should move toward `Batch -> Batch` output. Existing `MethodOutput` and opaque `StepOutput.predictions` remain compatibility surfaces until refactored. | Avoids an extra prediction container layer while preserving the trainer boundary. | Method/learner prediction as ordinary batch operations. | FR-13-1, FR-13-9 | revised direction |
| `rphys.datasources` / artifact adapters | Own generic sample-artifact layout descriptors and datasource adapters for test, evaluation, and analysis artifacts. | Exported predictions/evaluation outputs should reload as ordinary `Sample`s through existing datasource machinery. | Reusable sample artifact layout for downstream scripts. | FR-13-2, FR-13-4 | revised direction |
| `rphys.evaluation` | Own evaluation protocols/plans/results and pipeline-friendly operation or descriptor adapters that compose sample/batch prediction fields, reference fields, sample collection views, metrics, metric observation views, and report requirements through existing execution primitives. | Evaluation is the scientific comparison contract and should not collapse into metrics, analysis, training, datasource code, or a second pipeline runtime. | Reusable scoring/evaluation layer over existing field, collection, operation, and metric contracts. | FR-13-5, FR-13-6, FR-13-9 | design reviewed; no standalone runner |
| `rphys.ops` / `rphys.collections` / `rphys.ops.export` | Existing generic execution, collection, and export surfaces should be the default substrate for evaluation/report/dataset-formatting-style jobs. Add public shared job structures only if design evidence shows repeated semantics that current `OperationStep`, `OperationPipeline`, `Collector`, `CollectionView`, and existing export/save request/result contracts cannot express cleanly. | Avoids a one-off `EvaluationRunner` while keeping collections passive and export behavior with existing export ownership. | Common composition style for Stage 13 and later dataset formatting/report jobs. | FR-13-6 | design reviewed; no public job API or `rphys.ops.collections` |
| `rphys.analysis` | Own analysis and visualization operation contracts, analysis contexts/results, structured report/report-table records, and diagnostic renderer outputs. | Analysis/reporting need structured outputs without arbitrary plotting/file side effects. | Dependency-light post-evaluation analysis and report objects. | FR-13-7, FR-13-8, FR-13-9 | draft |
| `rphys.metrics` | Provide detached metric values, observations, observation collections, grouping specs, and metric observation view plans. | Evaluation results and reports should reuse existing metric observation semantics. | Structured metric evidence in evaluation/report flows. | FR-13-5, FR-13-6, FR-13-8 | dependency |
| `rphys.ops.export` / `rphys.datasources.derived` | Existing explicit field save/export and derived datasource assembly surfaces. | Durable prediction/evaluation/report fields must be ordinary exported sample fields and derived datasource refs. | Sample artifact export/reload path for synthetic smoke flow. | FR-13-4 | dependency |
| `rphys.errors` | Broad evaluation/analysis errors exist; prediction-specific public errors are no longer a default requirement if no public prediction package surface is added. | Public error names shape downstream exception handling and package boundaries. | Typed failure reporting only where code-backed public behavior needs it. | FR-13-9 | revised direction |
| Package/import tests | Assert public exports are code-backed and imports stay lightweight. | Prevents hidden pandas/plotting/torch/video/datasource/workflow dependencies in new surfaces. | Developer-alpha import-boundary confidence. | FR-13-9 | draft |

## Functionality Agreement Queue

| Queue ID | Related requirement IDs | Depends on | Impact | What is being locked | Why it matters | Recommended answer | Trade-offs or rejected branches | Repo evidence or direct resolution | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FQ-13-1 | FR-13-1, FR-13-2 |  | high | Sample/Batch-native prediction flow. | This prevents Stage 13 from adding a prediction record hierarchy that makes the API harder to compose with existing pipelines. | Treat prediction as field meaning on `Batch`/`Sample`, not as a public `PredictionRecord` family. Preferred prediction execution is `Batch -> Batch`; existing `MethodOutput` and `StepOutput.predictions` are compatibility inputs during the refactor. `TrainingResult` is not a prediction payload source. | Rejected: public `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, public prediction runner lifecycle, trainer-owned prediction capture, `TrainingResult.predictions`, waveform-only prediction rows, datasource scanning, dataloader construction, implicit export. | Maintainer explicitly requested native `Sample`/`Batch` flow and deprecation of `Prediction*` interfaces. | None. | maintainer-revised |
| FQ-13-2 | FR-13-2, FR-13-3 | FQ-13-1 | high | Sample-granular serialization and uncollation. | Durable artifacts need one entry per sample, while model execution often works in batches. | Serialize prediction/test/evaluation artifacts only after converting batch outputs to `Sample` entries. Stage 13 adds public uncollation policy/evidence so every serializable batch field can be split, broadcast, dropped, or rejected explicitly. | Rejected: batch-as-one-record prediction export, hidden sample uncollation, implicit tensor-axis guesses, export from loaded `FieldValue` mappings without descriptors, broad prediction materializer records. | Current `uncollate_batch` is LIST-only and cannot split arbitrary fields added after model execution without new policy evidence. | None. Exact policy class names can be implementation-plan work. | maintainer-revised |
| FQ-13-3 | FR-13-4 | FQ-13-2 | high | Generic sample artifact datasource path. | A second storage path would conflict with Stage 8 export and derived datasource contracts, but downstream scripts need reloadable test/evaluation artifacts. | Define generic sample-artifact layout/datasource adapter behavior for exported sample records. Prediction, evaluation, metric, and structured report fields are ordinary fields in those sample records. | Rejected: prediction-specific manifests, `PredictionDataSource`, `EvaluationDataSource`, ad hoc report/prediction directories without descriptor semantics, trainer artifact writes, datasource adapter export side effects. | Direct Milestone 13 and Milestone 8 text; current `ops.export`, `datasources.derived`, and datasource descriptor code. | None. | maintainer-revised |
| FQ-13-4 | FR-13-5 | FQ-13-1, FQ-13-2 | high | `EvaluationProtocol` minimum scientific comparison contract. | Evaluation protocols are where selectors, references, grouping, views, metrics, and failure behavior become reproducible. | Define `EvaluationProtocol` to name prediction field selectors, reference selectors, grouping metadata, sample/batch field projection and pass-through policy, pre-metric `SampleCollection` views or reconstruction adapters, metrics, metric observation views, report requirements, and failure behavior. `EvaluationPlan` binds this protocol to concrete samples, batches, collections, or sample-artifact datasource inputs. | Rejected: metric-only evaluation with hidden selectors; evaluator-owned datasource scanning/split building; report-only scoring; hidden reconstruction in metric internals. | Direct Milestone 13 text, Stage 11 sample/metric collection contracts, and maintainer revised native dataflow. | None. Exact field names and plan record shape can be design-gate work. | maintainer-revised |
| FQ-13-5 | FR-13-6 | FQ-13-4 | high | Shared pipeline/job structure versus an evaluation-specific runner. | Evaluation, reports, dataset formatting, and future post-processing all follow the same broad pattern: caller-supplied iterable or collection input, operation/view pipeline, typed result, and optional explicit export. A one-off `EvaluationRunner` would duplicate execution semantics already owned by `rphys.ops` and risk creating a second runtime. | Do not add a standalone `EvaluationRunner` as the default Stage 13 abstraction. Reuse existing `OperationStep`/`OperationPipeline`, `SampleOperationPipeline`/`BatchOperationPipeline`, `Collector`, and `CollectionView` mechanics. Stage 13 should define evaluation semantics (`EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`) and pipeline-friendly operation/adaptor shapes. The design pass must explicitly evaluate whether a small shared job descriptor/protocol is justified for reuse across evaluation, reports, dataset formatting, and similar jobs; add one only if it remains narrower than a workflow runtime. | Rejected: evaluation-specific executor lifecycle, hidden iteration semantics, evaluator-owned datasource construction, and a duplicate runner beside pipelines. Avoid prematurely adding a broad generic workflow/job API that belongs in downstream orchestration or `loom`. | Maintainer challenged the runner framing, identified the reusable pipeline/job pattern as the real design question, and agreed to this baseline. Existing code already provides `OperationStep`, `OperationPipeline`, sample/batch pipelines, `Collector`, and `CollectionView`. | None. | locked |
| FQ-13-6 | FR-13-7 | FQ-13-4 | medium | Analysis and visualization operation scope. | Analysis can easily become checkpoint selection, plotting, log crawling, or report file writing unless bounded. | Define `AnalysisOp` and `VisualizationOp` as structural, dependency-light operations over samples, batches, metric observation collections, evaluation results, analysis results, or reports. They return structured `AnalysisResult` or report-compatible objects and do not write files by default. | Rejected: training/checkpoint selection; ad hoc log crawling; mutation of predictions; hidden plotting backend; mandatory matplotlib/pandas dependency; arbitrary file writes. | Direct Milestone 13 analysis/reporting rules and import-boundary policy. | None. Concrete visualization adapters stay deferred. | repo-resolved |
| FQ-13-7 | FR-13-8 | FQ-13-4, FQ-13-6 | medium | Report and report table baseline behavior. | Reports become downstream-facing evidence, so the first shape must be useful without becoming a dataframe or file-format contract. | Define dependency-light in-memory `Report`, `ReportTable`, and `DiagnosticRenderer` outputs. `ReportTable` is a lightweight row/column view over primitive values, metric observations, and provenance. Durable files are written only through explicit save/export/report-save behavior or user code; no pandas or plotting dependency in core. | Rejected: dataframe as core type, HTML/PDF writer as default, plot files from renderers, one-off report file conventions, rich media dependency. | Direct Milestone 13 text. | None for basic in-memory records; report-save behavior should remain deferred unless design pass finds a minimal explicit contract. | repo-resolved |
| FQ-13-8 | FR-13-9 |  | medium | Prediction-specific public error taxonomy. | Public broad errors are durable API, and the revised plan may not add a public prediction package surface. | Do not add a code-backed `RemotePhysPredictionError` by default. Use data/collation/export/method/evaluation errors according to behavior ownership; add a broad prediction base only if implementation introduces public prediction-operation behavior that needs a distinct catch point. | Rejected: adding a broad untested subclass tree; adding prediction-specific errors without public prediction APIs; reusing evaluation errors for data/uncollation failures. | `src/rphys.errors.py` already has broad evaluation and analysis errors; revised Stage 13 moves prediction behavior into `Sample`/`Batch` dataflow. | None. | maintainer-revised |
| FQ-13-9 | FR-13-8, FR-13-9 | FQ-13-7 | medium | Minimal report/table scope and report save behavior. | A too-rich report API risks freezing dataframe, plotting, or file-format conventions; a too-thin API may not support Stage 14 smoke reports. | Stage 13 includes structured in-memory `Report`/`ReportTable` records, primitive and metric-observation rows, provenance, diagnostics, and renderer outputs as data. Defer report file writers and format adapters. If a durable structured report dataset is needed, use item-to-export adapters plus existing field export/save and derived datasource assembly. | Rejected for Stage 13: HTML/PDF/CSV/Markdown report writers, implicit plot/image file writes, report output directories, dataframe-backed tables, format-specific save conventions, and report-specific storage families. | Roadmap says durable files are explicit export/report save behavior or user code; existing export/save behavior is field-oriented, not report-format-oriented. In-memory records plus ordinary field export are enough for Stage 14 smoke handoff. | None. Manager-resolved as in-memory plus field-export handoff, with report file writers deferred. | repo-resolved / deferred |
| FQ-13-10 | FR-13-9, FR-13-10 | FQ-13-1 through FQ-13-9 | medium | Public import and validation posture. | New package surfaces must remain code-backed, lightweight, and testable through synthetic flows. | Add scoped public exports only when code-backed under owning packages such as `rphys.data`, `rphys.datasources`, `rphys.evaluation`, and `rphys.analysis`; keep root `rphys.__all__` empty; no hard torch/numpy/pandas/scipy/matplotlib/video/dataset-SDK imports. Include unit, contract, package, and synthetic integration coverage. | Rejected: placeholder exports, root re-exports, optional backend imports in package import paths, examples requiring external data or GPUs. | Existing package/import-boundary tests and roadmap dependency policy. | None. | repo-resolved |

## Functional Requirements

| ID | Requirement | Depends on | Agreement queue | What | Why | Scope | User-visible behavior | Agent/system behavior | Codebase capability enabled | Impact | Out of scope | Validation | Recommendation | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-13-1 | Refactor prediction flow to native `Sample`/`Batch` data objects. | Stage 10/12 outputs; Stage 11 collections | FQ-13-1 | Prefer `Batch -> Batch` method/operation prediction behavior; treat prediction as fields such as `predictions/<key>` on ordinary `Batch`/`Sample` containers. Existing `MethodOutput` and `StepOutput.predictions` are compatibility surfaces during migration. | Simplifies the API and keeps all pipeline components interoperating through the same field-container model. | `rphys.data`, `rphys.methods`, `rphys.learning`, and operation adapters; no new prediction record package by default. | Users pass `Sample`s and `Batch`es through pipelines and inspect prediction fields by locator. | Validation checks field roles/selectors, model-input projection, target-field exclusion during inference, and no implicit trainer payload capture. | Native prediction handoff from methods/learners to evaluation/export. | high | Public `PredictionRecord`, `PredictionCollection`, prediction runner lifecycle, datasource scanning, concrete algorithms, dataframe rows. | Unit/contract tests for `Batch -> Batch` fake methods/ops, compatibility adapters for existing `MethodOutput` if retained, and no target leakage into inference inputs. | Maintainer-revised default: Sample/Batch native, no new `Prediction*` record family. | maintainer-revised |
| FR-13-2 | Serialize prediction/test/evaluation artifacts as sample-granular records. | FR-13-1; Stage 8 export/derived datasource | FQ-13-2 | Add explicit flow from batched outputs plus allowed pass-through fields to per-sample `Sample`s, then one export record per sample. | Downstream evaluation and analysis scripts should reload artifacts using normal datasource/sample machinery. | Sample export adapters over existing export/save; no prediction-specific storage. | Users get artifact directories/datasources where each sample contains prediction fields and, when requested, target/reference fields. | Export fails unless every field has descriptor-backed identity and valid uncollation/export policy. | Durable test/evaluation artifact handoff. | high | Batch-as-one-record export, hidden uncollation, prediction-specific manifests/storage, raw loaded-field export without descriptors. | Integration/docs tests for batch -> samples -> export -> datasource reload. | Export one sample per record; targets are passthrough for evaluation-ready artifacts, not inference inputs. | maintainer-revised |
| FR-13-3 | Define public batch-field uncollation policy/evidence. | FR-13-1; data collation | FQ-13-2 | Extend collation/uncollation beyond current LIST-only evidence so fields added after batch prediction can declare how they split to samples. | Without explicit policy, batch prediction payloads cannot be serialized safely per sample. | `rphys.data` uncollation policy records/functions and tests; optional adapter hook for custom payload splitters. | Users can mark batch fields as list, batch-axis split, broadcast, drop/error, or adapter-split before sample export. | Missing, incompatible, or lossy policies fail loudly with field locator context. | Reversible or explicit batch-to-sample artifact conversion. | high | Implicit tensor-axis guessing, silent broadcast, hidden scientific reconstruction, backend-specific hard imports. | Unit/contract tests for each policy, invalid sample counts, metadata alignment, and field-level failure behavior. | Implement in Stage 13 before durable artifact export is treated as complete. | maintainer-revised |
| FR-13-4 | Define generic sample artifact layout/datasource adapters. | FR-13-2; Stage 8 export/derived datasource; datasource refs/indexes | FQ-13-3 | Provide generic layout descriptors/adapters for test, evaluation, and analysis artifacts as sample records with fields. | Separate scripts need to load exported artifacts as ordinary samples for later pipelines. | Datasource/sample-source adapter behavior over sample artifact layouts; possibly layout-specific interface names if they improve modularity. | Users can point a datasource adapter at a test/evaluation artifact layout and receive `Sample`s with prediction/reference/derived fields. | Adapters produce descriptors, indexes, and sample loading behavior without learning prediction/evaluation semantics. | Reusable artifact datasource path. | high | `PredictionDataSource`, `EvaluationDataSource`, report-specific storage families, codec logic hidden in evaluation. | Contract/integration tests for two artifact layouts that share the same generic adapter mechanics. | Keep layout-specific interfaces thin and modular, but not domain-specific datasource families. | maintainer-revised |
| FR-13-5 | Define `EvaluationProtocol`, `EvaluationPlan`, and `EvaluationResult`. | FR-13-1 through FR-13-4; Stage 11 metrics/sample collections | FQ-13-4 | Protocol records prediction selectors, references, grouping metadata, sample/batch projection and pass-through policy, pre-metric sample collection views, metrics, metric observation views, report requirements, and failure behavior; plan binds concrete inputs; result carries metric observations, reports, diagnostics, metadata, and provenance. | Makes scientific comparison explicit and reproducible. | `rphys.evaluation` records and structural protocol behavior. | Users can inspect exactly how prediction fields and reference fields are compared and grouped. | Construction validates locator selectors, policy names, metric/view requirements, failure policy, and provenance fields; no datasource/trainer/export ownership. | Evaluation contract layer. | high | Concrete metrics, concrete resampling/reconstruction, trainer loops, datasource scans, report file writing. | Unit/contract tests for protocol validation, selector parsing, missing selectors, grouping metadata, failure policy, and result records. | Revised around Sample/Batch-native inputs and artifact datasources. | maintainer-revised |
| FR-13-6 | Define pipeline-friendly evaluation composition and assess reusable job structures. | FR-13-5 | FQ-13-5 | Make evaluation protocols/plans/results usable as inputs and outputs of existing operations, pipelines, collectors, and collection views. Design must assess whether a narrow shared job descriptor/protocol is needed for repeated evaluation/report/dataset-formatting patterns. | The root smoke flow benefits from standard composition, but a standalone evaluator lifecycle would duplicate existing pipeline execution. | Evaluation-specific operation/adaptor records, pipeline-friendly plan/result shapes, and optional shared descriptor/protocol only if design evidence justifies it. | Users can compose evaluation through existing pipelines and receive structured `EvaluationResult` evidence without learning a second runner model. | Missing references, missing group metadata, invalid projection/pass-through policy, metric failures, or report-builder failures surface through operation/result diagnostics and domain errors. | End-to-end prediction scoring composition without a duplicate execution runtime. | high | Datasource scanning, split/index construction, training, checkpoint selection, arbitrary log crawling, report file conventions, broad workflow/job runtime. | Contract/integration tests proving evaluation can be expressed through existing pipeline/collection primitives; design review must justify any new shared public job structure. | Locked: no standalone `EvaluationRunner`; require shared-structure design review. | locked |
| FR-13-7 | Define analysis and visualization operation contracts. | FR-13-1, FR-13-5 | FQ-13-6 | Add `AnalysisOp`, `VisualizationOp`, `AnalysisContext`, and `AnalysisResult` as dependency-light structured operations over approved input object families. | Analysis and visualization should be reusable but not side-effectful plotting systems. | Structural protocols/records, context metadata/provenance, input type validation, result diagnostics. | Users can run analysis/visualization adapters that return structured data or report-compatible outputs. | Operations do not mutate predictions, train models, select checkpoints, crawl logs, or write files by default. | Post-evaluation analysis extension surface. | medium | Concrete plots, image/video renderers, dashboard frameworks, dataframe adapters, checkpoint selection. | Unit/contract tests with fake analysis ops and visualization outputs; import-boundary tests. | Repo-resolved behavior from roadmap. | functionality agreed; design proposed |
| FR-13-8 | Define structured report, report table, and diagnostic renderer records. | FR-13-5, FR-13-7 | FQ-13-7, FQ-13-9 | Add in-memory `Report`, `ReportTable`, and `DiagnosticRenderer`/renderer-output records over primitive values, metric observations, analysis results, and provenance. | Reports need a lightweight structured output that downstream projects can persist or render. | Row/column table records, report sections/items, diagnostic renderer output data, metadata/provenance, and optional field-export-compatible structured report handoff. | Users can inspect report content without pandas, plotting, or file writers; if they need a durable report dataset, report items can be adapted to ordinary export/save requests. | Records validate primitive/table values and provenance; renderer outputs are data, not implicit files. | Report handoff for Stage 14 smoke and downstream tooling. | medium | HTML/PDF/plot writers, dataframe dependency, rich media rendering backend, artifact store, report file save adapters, report-specific storage. | Unit tests for table construction, invalid rows/columns, metric observation rows, renderer output, optional field-export adapter behavior if implemented, and no heavy imports. | Include in-memory records and field-export handoff compatibility; defer report-save/file adapters. | functionality agreed; design proposed |
| FR-13-9 | Establish Stage 13 public errors, exports, docs, and import boundaries. | FR-13-1 through FR-13-8 | FQ-13-8, FQ-13-10 | Add code-backed scoped exports and broad/specific errors only where approved by implemented behavior; update package/import tests and docs/docstrings for public behavior. | New public surfaces must be intentional, lightweight, and documented. | `rphys.data`, `rphys.datasources`, `rphys.evaluation`, `rphys.analysis`, `rphys.errors`, package tests, docs/examples. | Users import only implemented names from owning packages; root exports remain empty. | Tests fail if heavy optional modules or unrelated package stacks load at import time. | Public API readiness for Stage 13. | medium | Placeholder exports, root re-exports, optional dependency imports, broad untested error taxonomy, public prediction record package. | `make test-package`, import-boundary tests, public `__all__` assertions, docs examples. | Do not add a broad prediction error unless code-backed public prediction behavior proves need; otherwise keep lightweight import posture. | maintainer-revised |
| FR-13-10 | Provide synthetic composition examples and focused smoke coverage. | FR-13-1 through FR-13-9 | FQ-13-10 | Add synthetic tests/docs that show batch-native prediction, target-free inference projection, optional target/reference pass-through for evaluation-ready artifacts, uncollation to samples, sample artifact export/reload, metric observation evaluation, analysis result, and report object composition without real data. | Stage 14 will harden this root smoke path, but Stage 13 should prove its new contracts compose. | Synthetic unit/contract/integration coverage only, tiny license-safe fixtures. | Users and maintainers can see the intended flow without external data or GPUs. | Agents validate no hidden trainer/export/datasource/report side effects. | Confidence before smoke hardening. | medium | Full Stage 14 smoke suite, real datasource, concrete algorithms, performance profiling. | Focused integration tests and docs/examples after implementation; no tests run in this planning pass. | Maintainer-revised validation direction; details belong to validation planner. | maintainer-revised |

## Behavior Confirmation

- Included behavior: Stage 13 defines Sample/Batch-native prediction flow,
  batch-field uncollation policy/evidence, sample-granular artifact export and
  reload, generic sample artifact layout/datasource adapters,
  evaluation protocols/plans/results, pipeline-friendly evaluation composition
  over existing operations/collections/views, analysis and visualization
  operation contracts, in-memory reports/report tables/diagnostic renderer
  outputs, scoped package exports, docs, examples, import-boundary tests, and
  focused synthetic composition coverage.
- Default behavior: predictions are ordinary fields on `Batch`/`Sample`
  containers, addressed by `FieldLocator` roles such as `predictions`.
  Methods/ops should move toward `Batch -> Batch`; existing `MethodOutput` and
  `StepOutput.predictions` remain compatibility surfaces only where needed.
  Durable artifacts are exported only after batch outputs are uncollated into
  individual `Sample` records; evaluation execution is composed through existing
  operation and collection pipelines rather than a standalone `EvaluationRunner`;
  reports are in-memory structured records by default.
- Failure behavior: invalid field selectors, target leakage into inference
  inputs, missing or incompatible uncollation policy, invalid sample counts,
  descriptor/export mismatches, missing references, missing grouping metadata,
  metric/view/report-builder failures, invalid report rows, invalid primitive
  metadata/provenance, and unsupported operation inputs fail loudly with
  package-appropriate typed errors and inspectable diagnostics where result
  records carry partial evidence.
- Unsupported behavior: public `PredictionRecord`/`PredictionCollection`/
  `PredictionCollector`/`PredictionExport*` surfaces, `BatchCollection`/
  `BatchCollector`, prediction-specific storage, trainer-owned prediction
  capture, `TrainingResult` prediction payload mining, automatic datasource
  scanning, dataloader construction, split/index construction, training or
  checkpoint selection, hidden plotting, dataframe dependency, report file
  writers/adapters, broad workflow/job runtime, artifact store, and concrete
  physiological algorithms are out of scope.
- Resume/interruption behavior: no runtime resume behavior is proposed for
  Stage 13 core; downstream workflow systems own orchestration/resume.
- Downstream implications: downstream projects and `loom` can orchestrate jobs,
  persist artifacts, choose checkpoints, or render reports around native
  `Sample`/`Batch` pipelines; Stage 14 can harden the synthetic smoke path
  without inventing prediction/evaluation runners; later dataset-formatting and
  report jobs can reuse the same sample artifact layout and uncollation/export
  policy.
- Explicit deferrals: concrete algorithms, real plotting/dataframe adapters,
  dashboard/report writers, report file writers/adapters, concrete
  reconstruction algorithms, and Stage 14 smoke hardening are recommended
  deferrals.
- Why this behavior is locked: FQ-13-1 through FQ-13-10 are revised from the
  current roadmap, Stage 8/10/11/12 code-backed contracts, import-boundary
  policy, and maintainer agreement that the API should stay native to
  `Sample`/`Batch` dataflow and avoid standalone prediction/evaluation runners.

## Proposed Implementation Shape

Design proposal date: 2026-05-17

The likely Stage 13 implementation should introduce dependency-light public
records and operation-compatible adapters, not a second execution runtime.
Evaluation must reuse the already code-backed execution and collection
surfaces:

- `OperationStep`, `Operation`, `OperationPipeline`, `OperationContext`, and
  `OperationResult` own generic execution, ordered composition, execution
  metadata, and side-effect evidence.
- `SampleOperationPipeline` and `BatchOperationPipeline` own sample/batch
  runtime transforms where concrete `Sample` or `Batch` containers are the
  payload.
- `Collector`, `CollectorResult`, `Collection`, `CollectionItem`, and
  `CollectionView` own iterable materialization, accepted/skipped/rejected
  diagnostics, item metadata/provenance, and collection-to-collection views.
- `SaveOperation`, export result records, and `DerivedDataSourceBuilder` own
  field persistence and derived datasource descriptor assembly.

Stage 13 should define typed post-prediction semantics over those primitives.
It should not add `EvaluationRunner`, a generic `PipelineJob`, an artifact
runtime, report file writers, dataframe adapters, plotting backends, or hidden
datasource/trainer loops.

| Area | Likely public classes/functions/protocols | Internal helpers | Data flow and dependency direction | Related FRs | Extension and validation pressure |
| --- | --- | --- | --- | --- | --- |
| Batch-native prediction execution | `Batch`-returning fake methods/ops, compatibility adapters for existing `MethodOutput` only where needed, and operation-compatible batch prediction steps. | Private field projection, target-exclusion checks, merge/pass-through policy, primitive metadata/provenance validation, and compatibility shims. | Caller provides `Iterable[Batch]`, `SampleCollection` converted to batches by existing data machinery, or another already materialized iterable. Prediction computation returns `Batch` values with `predictions/<key>` fields and must not read `TrainingResult`, build dataloaders, scan datasources, or choose checkpoints. | FR-13-1, FR-13-9 | No public `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, `PredictionPlan`, `PredictionResult`, or `PredictionRunner`. |
| Batch-to-sample uncollation | `UncollatePolicy`, `UncollatePlan`, `uncollate_batch` extensions, or equivalent names selected during implementation. | Private splitters for list, batch-axis, broadcast, drop/error, and adapter-owned custom behavior; metadata alignment checks; sample-count validation. | Batch fields intended for durable export must declare how to produce one `FieldValue` per output `Sample`. Existing LIST evidence remains supported but is not sufficient for post-model prediction fields. | FR-13-2, FR-13-3 | Missing or invalid uncollation policy fails before export; no implicit tensor-axis guessing or hidden scientific reconstruction. |
| Sample artifact export/reload | `SampleArtifactLayout`, `SampleArtifactDataSourceAdapter`, or equivalent generic layout/descriptors if implementation proves these names fit existing datasource code. | Private field-to-export request mapping, source `RecordRef`/augmented export descriptor recovery, artifact path/resource normalization, and descriptor/index helpers. | Per-sample fields -> existing export/save pipeline -> existing export result -> existing derived/sample-artifact datasource descriptors -> later sample-source loading. Dependency points toward existing export/datasource ownership; evaluation code does not own storage. | FR-13-2, FR-13-4 | Add no prediction-specific codec, manifest, writer, datasource family, or output directory convention beyond a generic sample artifact layout. |
| Evaluation protocol and plan | `EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`, `EvaluationFailure` or package-local failure/diagnostic records if tests need partial evidence. | Private selector validation, metric/view requirement validation, primitive mapping helpers, and result-combine helpers. | `rphys.evaluation` consumes `Sample`, `Batch`, `SampleCollection`, reloaded sample artifact datasources, `SampleCollectionView`, metrics, `MetricObservationCollection`, metric observation views, and report builders. It does not execute a loop itself except through operation-compatible adapters supplied by callers. | FR-13-5, FR-13-6, FR-13-9 | Protocol records prediction/reference selectors, grouping keys, sample/batch projection policy, sample views, metrics, observation views, report requirements, and failure policy. |
| Evaluation operation adapters | `EvaluationOperation` or callable-first operation wrappers around protocol/plan functions; no `EvaluationRunner`. | Private operation factory helpers if repeated setup is needed. | `EvaluationPlan` -> `OperationStep.run(...)` -> `OperationResult.output == EvaluationResult`; operation output can be composed with report/analysis operations in `OperationPipeline`. | FR-13-5, FR-13-6 | This is where the reusable pattern lands: evaluation is an operation payload and output, while ordered execution remains in `OperationPipeline`. |
| Analysis and visualization | Structural `AnalysisOp`, `VisualizationOp`, `AnalysisContext`, `AnalysisResult`, and operation-compatible wrappers. | Private accepted-input validation and primitive diagnostic mapping helpers. | Consumes `Sample`, `Batch`, `SampleCollection`, `MetricObservationCollection`, `EvaluationResult`, `AnalysisResult`, or `Report`; returns structured data or report-compatible output. | FR-13-7 | No checkpoint selection, trainer hooks, log crawling, mutation of predictions, plot files, or backend imports. Concrete visualization backends stay optional adapters. |
| Reports and diagnostics | `Report`, `ReportSection`, `ReportTable`, `ReportCell` if needed, `DiagnosticRenderer`, `DiagnosticRenderResult`. | Private row/column validation, primitive value coercion, metric-observation row adapters, and section ordering helpers. | Analysis/evaluation/metric outputs -> report records. Reports may be operation outputs and may be consumed by downstream save/render adapters outside Stage 13 core. | FR-13-8, FR-13-9 | In-memory only. No `to_html`, `to_pdf`, `to_csv`, pandas dataframe, plot/image file writer, output directory schema, or artifact store. |
| Public errors and imports | Use code-backed errors only where implemented behavior needs them; `RemotePhysPredictionError` is optional if no public prediction package surface is added. Existing evaluation/analysis broad errors remain. | Package-local private validation helpers; no public utility module. | `rphys.data`, `rphys.datasources`, `rphys.evaluation`, and `rphys.analysis` re-export only implemented names. Root `rphys.__all__` remains empty. | FR-13-9 | Import tests must prove no torch/numpy/scipy/pandas/matplotlib/video/dataset-SDK/workflow imports through package homes. |

Proposed dependency direction:

```text
rphys.data + rphys.collections + rphys.ops + rphys.methods + rphys.learning
  -> Batch-native prediction operations/adapters

rphys.data + rphys.datasources + rphys.metrics + rphys.data.collections + rphys.ops
  -> rphys.evaluation

rphys.data + rphys.evaluation + rphys.metrics + rphys.collections
  -> rphys.analysis

rphys.ops.export + rphys.datasources.derived + generic sample artifact adapters
  own durable field export and reload behavior.
```

`rphys.training` remains upstream only as the owner of summary-oriented
training loops and results. Stage 13 prediction examples may use
`Learner.step` with `LoopMode.PREDICT` only through Batch-native compatibility
adapters; they must not depend on `Trainer`, `TrainingEngine`, or
`TrainingResult` to recover prediction payloads.

### Reusable Pattern Boundary

The design conclusion is concrete:

- The canonical reusable flow is Sample/Batch-first:

  ```text
  Samples
    -> optional SampleCollection / SampleCollectionView
    -> collated Batches for method or batch-operation execution
    -> Batches with predictions/<key> or derived fields
    -> explicit merge/pass-through policy for allowed fields
    -> public uncollation policy/evidence
    -> Samples
    -> SampleCollection / CollectionView when grouping/projection is needed
    -> item-to-export adapter when durable fields are needed
    -> existing export/save operations
    -> sample-artifact datasource descriptors for downstream reload
  ```

  Prediction, evaluation, reporting, and future dataset-formatting jobs should
  instantiate this shape rather than each defining a separate runtime lifecycle
  or domain-specific data container.
- Belongs in existing `ops`: ordered execution, operation contracts, context,
  execution result wrapping, mutation/side-effect declarations, operation
  pipeline compatibility, and save/export side effects.
- Belongs in existing `collections`: iterable-to-snapshot materialization,
  value iteration, item metadata/provenance, collection views, skip/reject
  diagnostics, and grouping/sorting/reconstruction descriptors.
- Collectors must stay payload-agnostic. A `SampleCollector` may enforce
  collection membership and item metadata/provenance shape, but it should not
  know whether a sample contains prediction, target, metric, report, or formatted
  dataset fields. Field meaning comes from `FieldLocator` roles and schemas.
- Generic collection records, items, collectors, and views stay in
  `rphys.collections`. Stage 13 should not create or duplicate a
  `rphys.ops.collections` namespace and should not add `BatchCollection` or
  `BatchCollector` without reopening design. Collections stay payload/storage
  agnostic; data/artifact adapters provide uncollation and item-to-export
  behavior.
- A narrow shared multi-record export helper is valid only if Phase 3 proves it
  is code-backed and smaller than a job runtime. It belongs with the existing
  export/save surface, not in `rphys.collections`: caller/domain adapters produce
  `RecordExportRequest`s from collection items, export code runs existing
  codec-selection/save operations, and `DerivedDataSourceBuilder` assembles
  descriptors. It must not own scheduling, resume state, artifact refs,
  datasource scans, collection semantics, output directories, writer formats, or
  a workflow lifecycle.
- May belong as small shared records/protocols only after implementation
  proves identical semantics in at least two packages: a tiny diagnostic issue
  record with code/severity/message/metadata/provenance, a structural
  report/table input protocol, or the narrow export request iteration helper
  described above. These are not broad job APIs; keep equivalent fields
  package-local first unless the implementation demonstrates a concrete shared
  need.
- Remains prediction-specific: field-role validation, method/learner
  compatibility adapters where existing outputs require them, target-free
  inference projection, allowed pass-through declarations, prediction field
  handles over `FieldLocator`/`FieldValue`, and source-record/export descriptor
  preservation before durable sample artifact export.
- Remains evaluation-specific: selector/reference pairing, comparison grouping,
  required reference behavior, metric execution requirements, observation view
  order, evaluation failure policy, and evaluation result shape.
- Remains report/analysis-specific: table/section structure, diagnostic
  renderer output records, analysis context/result records, and downstream
  renderer/save adapter handoff.

This preserves the abstract patterns introduced in Stages 10-12: structural
protocols for executable semantic roles, frozen records for inspectable
contexts/results/specs, patch-like field update compatibility where needed,
collection/view/collector contracts for cross-item behavior, learner prediction
payloads as opaque to trainers, and operation pipelines as the only in-library
ordered execution composition.

Maintainer refinement: the abstract flow is valid within the current framework
because `Collection[T]`, `CollectionItem[T]`, `Collector[T, C]`, and
`OperationStep` are structural and payload-generic, while `FieldLocator`,
`FieldValue`, `RecordExportRequest`, `CodecSelectionOperation`,
`SaveOperation`, and `DerivedDataSourceBuilder` already provide the field-handle
and export-save substrate. Stage 13 should therefore prefer prediction-specific
producer/assertion/adaptor code over prediction-specific collection or export
loops. Evaluation and report behavior should follow the same pattern by adding
metric/report operations into the pipeline, collecting typed result collections,
and using item-to-export adapters only when a separate script needs a durable
dataset handoff.

Datasource pattern review: datasource code follows the same architectural
spirit but not the same exact execution substrate. It is descriptor-first:
`DataSourceAdapter.scan` returns `DataSourceScanResult` records without loading
payloads; `build_view` and `FilterChain` create non-mutating descriptor views;
`build_index_candidates`, `GroupBuilder`, `SplitBuilder`, and `IndexBuilder`
turn descriptors into `DataSourceIndex` entries with sidecar identity, split,
group, source, window, and fingerprint evidence; `SampleBuilder` later
materializes lazy runtime samples from `IndexItem` descriptors. Stage 13 should
reuse this pattern of explicit plan/result records, immutable descriptors,
sidecar provenance, and delayed materialization, but it should not import
datasource scan/filter/split/index construction into prediction or evaluation.
For durable output export, the relevant datasource lesson is narrower:
exportable prediction, evaluation, and structured report items need source
`RecordRef` or augmented export-record descriptor evidence in addition to
loaded `FieldValue` payloads, because existing export/save validates field
values against descriptors. This makes separate launch scripts viable without a
new runner: one script can export predictions as a derived datasource, several
evaluation scripts can reload the same prediction fields and export different
metric/evaluation datasets, and a report script can consume those evaluation
datasets or structured in-memory results.

### Sample Artifact Datasource Reuse

Stage 13 should reuse the datasource layer for serialized predictions,
evaluation outputs, metric observations, and structured report datasets by
normalizing all durable outputs to per-sample artifact records. The reuse target
is the durable field/datasource boundary, not a domain-specific in-memory
prediction object:

```text
Batch with predictions/<key> and derived fields
  -> explicit allowed field projection/pass-through
  -> public uncollation policy/evidence
  -> Samples
  -> SampleCollection when a snapshot is useful
  -> sample item-to-export adapter
  -> RecordExportRequest with descriptor-backed FieldValue payloads
  -> CodecSelectionOperation / SaveOperation
  -> ExportResult
  -> DataSourceRef / RecordRef / FieldRef descriptors for later datasource use
```

This means a later script should interact with serialized outputs through normal
datasource descriptors, indexes, sample sources, field locators, and codecs. A
prediction output that has been exported is not a `PredictionDataSource`; it is a
sample artifact datasource whose records contain `predictions/<key>` fields. An
evaluation output that has been exported is not an `EvaluationDataSource`; it is
a sample artifact datasource whose records contain derived `outputs/<key>`,
`metrics/<key>`, or diagnostic fields. Structured report datasets follow the
same rule when a durable handoff is required.

Ownership under the revised design:

- `rphys.data` owns `Sample`, `Batch`, `FieldValue`, `FieldLocator`, and
  collate/uncollate policy/evidence.
- `rphys.collections` owns `SampleCollection`/collection behavior when a
  snapshot or view is needed. Stage 13 should not add `BatchCollection` or
  `BatchCollector` by default; use `Iterable[Batch]` for transient batch streams.
- `rphys.datasources` owns generic sample artifact layout descriptors,
  indexing, prepared/sample loading, and reload mechanics.
- `rphys.evaluation` owns selector/reference/grouping/metric semantics over
  fields in samples/batches.
- `rphys.analysis` owns report/table/analysis records and optional structured
  report item-to-export adapters.
- `rphys.ops.export` owns field save/export request/result behavior and any
  narrow shared multi-record export iteration helper, if implementation proves
  one is needed.

Descriptor-backed export is mandatory for this reuse. Loaded `FieldValue`
mappings alone are not enough, because existing export/save validates
`RecordExportRequest.field_values` against a `RecordRef` whose declared fields
match the exported keys. For prediction/test/evaluation artifacts, the
sample-to-export adapter must therefore provide either a source `RecordRef` or
an augmented export-record descriptor for the output fields.

Separate script examples:

```text
prediction/test artifact script:
  test datasource -> samples -> batches without target leakage
  -> Batch prediction operation
  -> merge predictions plus allowed pass-through targets/references
  -> uncollate to Samples
  -> sample artifact datasource

evaluation script A:
  sample artifact datasource with predictions + references
  -> EvaluationPlan / EvaluationResult
  -> Samples with metric/evaluation fields
  -> evaluation A sample artifact datasource

evaluation script B:
  same prediction sample artifact datasource
  -> different EvaluationPlan / EvaluationResult
  -> evaluation B sample artifact datasource

report script:
  evaluation A/B sample artifact datasources -> Report / ReportTable
  -> optional structured report fields in a sample artifact datasource
```

The missing implementation detail to keep explicit is cross-process descriptor
recovery. Separate launch scripts need a generic way to recover sample artifact
descriptors later, either through existing datasource/index manifest behavior or
a generic derived-output scan/reader adapter. That recovery must stay generic to
sample artifact fields and must not become prediction-, evaluation-, or
report-specific storage.

## Design Agreement Queue

| Queue ID | Related decisions | Depends on | Impact | Ambiguity | Options | Recommendation | Classification | Validation/documentation obligation | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-13-1 | DD-13-1, DD-13-8 | Functionality agreement | high | Public module/import split for data/artifact/evaluation/analysis behavior. | Package-root-only exports; scoped modules plus package re-exports; root-level convenience exports; public `rphys.prediction` record family. | Use scoped modules and package re-exports only for code-backed names; root exports stay empty; avoid a public prediction record package in Stage 13. | recorded recommendation | Package/import-boundary tests and docstrings identify provisional public paths. | None. | maintainer-revised |
| DQ-13-2 | DD-13-2, DD-13-3 | DQ-13-1 | high | Whether prediction execution should expose new prediction records or stay native to `Sample`/`Batch`. | Full runner lifecycle; thin prediction producer/collector helper; operation-only wrapper; native `Batch -> Batch` flow. | Do not add public `Prediction*` records in Stage 13; keep prediction as fields on `Sample`/`Batch` and use operation-compatible batch prediction examples. | recorded recommendation | Contract tests with fake methods/ops, invalid field policies, no trainer/dataloader/datasource access, no public prediction runner/export/collection names. | None. Maintainer revised Stage 13 toward native `Sample`/`Batch` flow. | maintainer-revised |
| DQ-13-3 | DD-13-3, DD-13-4 | DQ-13-2 | high | Uncollation and sample artifact export public shape. | Public uncollation policy records; function-only helper; direct LIST-only uncollation; new storage family. | Add explicit public uncollation policy/evidence for serializable batch fields; export sample artifacts through existing export/save and generic datasource adapters. | recorded recommendation | Tests/docs for uncollation policies, sample counts, descriptor-backed export, and generic artifact reload. | None. | maintainer-revised |
| DQ-13-4 | DD-13-5, DD-13-6 | DQ-13-1 through DQ-13-3 | high | Evaluation composition without `EvaluationRunner` and without a generic job runtime. | Standalone `EvaluationRunner`; generic public `PipelineJob`; operation adapters over `EvaluationPlan`; downstream-only execution. | No standalone `EvaluationRunner` and no public generic job descriptor in Stage 13. Define evaluation records plus operation-compatible adapters over native samples/batches/artifact datasources. | recorded recommendation; maintainer constraint applied | Contract tests should later express evaluation as `OperationStep`/`OperationPipeline` composition. | None. No blocker-level reason for public `PipelineJob` was found. | reviewed; proceed |
| DQ-13-5 | DD-13-8 | DQ-13-4 | medium | Report and diagnostic public shape. | Minimal report/table records; dataframe-backed table; file writer methods; renderer output records. | Add in-memory report/table/diagnostic-renderer records; defer writers and backend adapters. | recorded recommendation | Unit docs/tests for primitive values, metric-observation rows, provenance, and no pandas/plot imports. | None. | reviewed; proceed |
| DQ-13-6 | DD-13-9 | DQ-13-1 | medium | Shared reusable records/protocols beyond existing ops/collections. | Public `PipelineJob`; public shared diagnostic issue record now; private/package-local repeated shapes first; no shared shape ever. | Do not add a public shared job or diagnostic record in Stage 13. Keep diagnostic fields package-local and reopen only if identical public behavior repeats across packages. | recorded recommendation | Document revisit trigger and keep helper modules private. | None. | reviewed; proceed |
| DQ-13-7 | DD-13-10 | DQ-13-1 through DQ-13-6 | medium | Public error taxonomy. | Add broad prediction base only; add many specific subclasses; reuse method/data/evaluation errors. | Do not add `RemotePhysPredictionError` by default if Stage 13 has no public prediction package surface; add code-backed errors only where implemented behavior needs distinct handling. | recorded recommendation | Error tests and package `__all__` tests. | None. | maintainer-revised |

## Design Decisions

| ID | Decision | Depends on | Agreement queue | Classification | What | Why | Proposed implementation shape | Impact | Options | Recommendation | Pros/cons | Limitation or trade-off | Validation/documentation obligation | Future-roadmap interaction considered | Adversarial assumptions considered | Residual risk | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DD-13-1 | Scoped Stage 13 module ownership and import posture. | Functionality agreement | DQ-13-1 | recorded recommendation | Establish public homes for data/artifact/evaluation/analysis behavior without creating a prediction record package by default. | New public imports must be intentional and dependency-light. | Use scoped modules under existing owners such as `data.uncollation`, `datasources` sample artifact adapters, `evaluation.protocols`, `evaluation.results`, `evaluation.ops`, `analysis.core`, and `analysis.reports`. Root exports remain empty. | Public API/import path. | Monolithic packages, package-root-only, root re-exports, placeholder modules, public `rphys.prediction` record family. | Scoped modules with package re-exports only when code-backed. | Pro: mirrors prior stages and keeps dependency direction inspectable. Con: the Stage 10/12 compatibility path may need temporary adapters. | Exact module names become public once implemented/tested. | Package import tests, `__all__` tests, no-heavy-import checks, docstrings with stability posture. | Stage 14 smoke imports these names; optional adapters later must remain additive. | Second dataset/model/report adapter should not require editing core modules; avoid accidental trainer/export/datasource coupling. | Public path churn if implementation chooses too many tiny modules. | maintainer-revised |
| DD-13-2 | Prediction is field meaning on `Sample`/`Batch`, not a public record family. | DD-13-1 | DQ-13-2 | maintainer decision | Define prediction handoff shape. | Evaluation/export/reporting need inspectable prediction fields without extra wrappers. | Methods/ops return `Batch` values carrying `predictions/<key>` fields. `SampleCollection` is used when a sample snapshot is needed. No public `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, `PredictionPlan`, or `PredictionResult` in Stage 13. | Public schema/scientific provenance. | Plain `Batch`/`Sample`; dataframe rows; waveform-only record; prediction-specific datasource; prediction record family. | Native `Sample`/`Batch` flow. | Pro: simpler, compatible pipeline surface. Con: Stage 10 `MethodOutput` needs compatibility/refactor planning. | Does not define durable storage or sample reconstruction by itself. | Tests for field roles/selectors, batch outputs, no target leakage, and compatibility adapters where existing code still emits `MethodOutput`. | Stage 14 can smoke-test native field flow; downstream can add modalities by locators/metadata. | Missing first-class subject/record fields should be handled by sample metadata/provenance and descriptors. | Stage 10/12 refactor may be broader than the original Stage 13 implementation. | maintainer-revised |
| DD-13-3 | Durable artifacts are sample-granular and require explicit batch uncollation policy. | DD-13-2 | DQ-13-2 | maintainer decision | Define how batch prediction outputs become reloadable data. | Batches are transient execution containers; artifacts need per-sample identity. | Add public uncollation policy/evidence to split batch fields into per-sample `FieldValue`s before export. Supported policies should include LIST, batch-axis split, broadcast, drop/error, and adapter-owned custom split if needed. | Data/export boundary. | Batch-as-record export; implicit tensor-axis guessing; automatic scientific reconstruction; no uncollation support. | Explicit uncollation policy plus fail-loud export gating. | Pro: deterministic artifacts and fewer domain wrappers. Con: more requirements on batch-producing methods/ops. | Custom backend payloads may need adapters. | Unit/contract tests for valid/invalid policies, sample counts, metadata alignment, and failure context. | Enables sample-artifact datasources for Stage 14 and later evaluation workflows. | Broadcast/drop policies could hide mistakes if not named and tested clearly. | Policy naming and custom adapter API need careful implementation review. | maintainer-revised |
| DD-13-4 | Generic sample artifact layouts replace prediction-specific export bridges. | DD-13-3 | DQ-13-3 | maintainer decision | Define how prediction/evaluation/report fields become durable. | A second storage path would conflict with roadmap and Stage 8. | Samples plus source `RecordRef` or augmented export-record descriptor plus field values become existing `RecordExportRequest`s; existing export/save returns `ExportResult`; generic sample artifact layout/datasource adapters describe reloadable records. | Public persistence boundary. | New prediction manifest/writer; direct ad hoc directories; `PredictionDataSource`; `EvaluationDataSource`; thin prediction export wrappers. | Generic sample artifact layout and existing export/save. | Pro: keeps storage policy centralized and preserves source descriptor evidence. Con: layout descriptors must be generic enough for test/eval/report artifacts. | Does not define codecs, report files, or datasource scanning outside the artifact adapter. | Integration coverage must prove synthetic sample artifact export/reload without new domain storage. | Stage 14 smoke reloads artifacts through normal datasource/index/sample path. | Export failures or partial writes must surface through existing export evidence. | Existing export APIs may need minor generic adapter glue. | maintainer-revised |
| DD-13-5 | Evaluation is protocol/plan/result plus operation adapters; no standalone `EvaluationRunner`. | DD-13-1 through DD-13-4 | DQ-13-4 | recorded recommendation; maintainer constraint applied | Define evaluation execution shape. | Maintainer explicitly rejected duplicating existing iterable/operation/pipeline mechanics. | `EvaluationProtocol` records selectors, references, grouping keys, sample/batch projection and pass-through policy, sample collection views, metrics, observation views, report requirements, and failure policy. `EvaluationPlan` binds protocol to concrete samples, batches, sample collections, artifact datasources, metric/report inputs. `EvaluationOperation` or callable wrapper returns `EvaluationResult` through `OperationResult.output`. | Public evaluation API/scientific workflow. | Standalone runner; generic job; operation adapter; downstream-only execution. | Operation adapter over explicit records. | Pro: keeps execution model consistent and makes evaluation compose with reports/dataset formatting. Con: users must understand operations/pipelines for multi-step execution. | Does not own datasource scans, split construction, sample loading, checkpoint selection, metric algorithms, or report files. | Later tests must demonstrate `OperationPipeline([evaluation_op, report_op])`. | Future dataset-formatting jobs can follow the same operation/collection shape without evaluation-specific code. | Missing references, missing grouping metadata, and metric failures must not silently produce partial scores. | Public result shape still needs careful review before implementation. | reviewed; proceed |
| DD-13-6 | Reusable job structure stays in existing ops/collections/export surfaces; no public `PipelineJob` in Stage 13. | DD-13-5 | DQ-13-4, DQ-13-6 | recorded recommendation | Decide whether to add a generic shared job descriptor/protocol. | Evaluation, reports, dataset formatting, and post-processing share a pattern, but existing primitives already own the reusable parts. | Do not add public `PipelineJob`, `JobPlan`, `JobRunner`, or generic lifecycle protocols. Reuse `OperationStep`/`OperationPipeline` for execution and `SampleCollection`/`CollectionView` for snapshots/views. Passive collection records stay in `rphys.collections`; do not add `rphys.ops.collections`, `BatchCollection`, or `BatchCollector`. If repeated durable handoff needs shared iteration, add only a narrow helper with existing `rphys.ops.export` semantics over adapter-produced `RecordExportRequest`s. | Public API avoidance / reuse posture. | Add broad job API; add small shared diagnostic record; keep existing primitives plus narrow export helper if code-backed. | Keep existing primitives; allow only a narrow export/save iteration helper if implementation proves duplication. | Pro: avoids workflow-runtime creep. Con: small local duplication in evaluation/analysis diagnostics. | Dataset-formatting convenience remains downstream or later-stage work. | Docs must state what belongs in `rphys.collections`, existing `rphys.ops.export`, and artifact adapters. | Later dataset formatting/report save work can reopen a tiny shared record if current local shapes converge. | A future worker may recreate job lifecycle under another package name; tests/docs should guard against that. | Revisit if operation adapters or export adapters cannot express required flows cleanly. | reviewed; proceed |
| DD-13-8 | Analysis, visualization, and reports are structured operation-compatible outputs, not plotting/file systems. | DD-13-1, DD-13-6 | DQ-13-5 | recorded recommendation | Define analysis/report surface. | Reports are downstream-facing evidence and must stay inspectable without heavyweight dependencies. | Structural `AnalysisOp`/`VisualizationOp` protocols or operation-compatible adapters; `AnalysisContext`/`AnalysisResult`; `Report`, `ReportSection`, `ReportTable`, and diagnostic renderer output records. | Public API/report semantics. | Dataframe; file writer; plotting backend; in-memory records. | In-memory records and structured renderer outputs only. | Pro: supports Stage 14 smoke and downstream rendering. Con: no built-in HTML/PDF/CSV. | Durable files and rich media adapters are deferred. | Later tests/docs for primitive table values, metric observation rows, provenance, and no pandas/matplotlib imports. | Future report save adapters can consume records without changing evaluation. | Report tables could overfit metric observations; keep rows primitive and provenance-aware. | Exact section/table schema may need iteration after examples. | reviewed; proceed |
| DD-13-9 | Shared small record/protocol extraction is deferred behind a revisit trigger. | DD-13-2 through DD-13-8 | DQ-13-6 | recorded recommendation | Decide helper reuse posture. | Prior stages prefer private helpers until repeated public semantics exist. | Use package-local private helper functions for primitive mappings, diagnostics, and non-empty strings. If two implemented packages need identical public issue records, reopen design for a tiny `DiagnosticIssue`-style record; do not add it speculatively. | Internal/public-helper boundary. | Shared public helper module; cross-package private imports; local private helpers. | Local private helpers first. | Pro: no public lock-in. Con: some duplication. | Private helper names are not contracts. | Validate through public behavior only. | Future reports/dataset-formatting may justify shared diagnostics once behavior is real. | Accidental cross-package private imports would create hidden API. | Duplication could become annoying before a shared public record is approved. | reviewed; proceed |
| DD-13-10 | Error taxonomy stays code-backed and minimal. | DD-13-1 | DQ-13-7 | recorded recommendation | Establish Stage 13 errors. | The revised plan avoids a public prediction record package, so a broad prediction error is no longer automatically justified. | Use existing data/collation/export/evaluation/analysis errors where they own behavior. Add `RemotePhysPredictionError` only if implementation introduces a public prediction operation surface that needs a distinct catch point, and add specific subclasses only when tests require distinct handling. | Public API/error handling. | Reuse existing data/method/evaluation errors; broad prediction base; full subclass taxonomy. | Existing owners first; optional broad prediction base only if code-backed. | Pro: avoids public error churn. Con: downstream may not get a separate prediction catch point unless implementation proves need. | Error names become public once exported. | Error tests and package import tests. | Downstream can distinguish evaluation/analysis failures; prediction-operation failures can be revisited if a public package appears. | Too many specific errors would churn; too few could hide failure contexts. | Implementation may discover one or two specific classes are justified. | maintainer-revised |

## Design Decision Triage

| Decision ID | Classification | Why this classification fits | Auto-approval eligibility | Maintainer discussion need | Status |
| --- | --- | --- | --- | --- | --- |
| DD-13-1 | recorded recommendation | Public import paths and package exports are durable API, and implementation may discover fewer modules are needed. | Not auto-approved because public import paths are affected. | None. | reviewed; proceed |
| DD-13-2 | maintainer decision | Removing the prediction record/collection schema affects evaluation/export/report contracts and scientific provenance. | Not auto-approved because public schema and provenance semantics are affected. | None. | maintainer-revised |
| DD-13-3 | maintainer decision | Public uncollation behavior affects data correctness, export safety, and scientific interpretation. | Not auto-approved because batch-to-sample semantics need explicit limits and tests. | None; maintainer requested uncollation support in Stage 13. | maintainer-revised |
| DD-13-4 | maintainer decision | Sample artifact layout touches the persistence/reload boundary, even though it delegates to existing export/save and datasource APIs. | Not auto-approved because persistence/export compatibility is affected. | None. | maintainer-revised |
| DD-13-5 | recorded recommendation | Evaluation protocol/plan/result are core public contracts; no-runner constraint is maintainer-supplied and repository evidence supports it. | Not auto-approved because public evaluation workflow semantics are affected. | None; no standalone `EvaluationRunner` is locked by maintainer input. | reviewed; proceed |
| DD-13-6 | recorded recommendation | Omitting a public generic job API is an architectural decision with future-roadmap consequences, but no blocker-level reason for `PipelineJob` was found. | Not auto-approved because future reuse expectations are affected. | None. Reopen only if operation adapters cannot express required flows cleanly or maintainer explicitly asks for a public shared job shape. | reviewed; proceed |
| DD-13-8 | recorded recommendation | Report/table/analysis schema is public and downstream-facing; it can affect future renderer/save adapters. | Not auto-approved because report schema impacts downstream adapters. | None. | reviewed; proceed |
| DD-13-9 | recorded recommendation | The private-helper part is refactorable, but the public omission of shared diagnostics/protocols affects future reuse and should stay recorded. | Not auto-approved after adversarial review because repeated diagnostic semantics may later justify extraction. | None. | reviewed; proceed |
| DD-13-10 | recorded recommendation | Broad error base is public API and shapes downstream exception handling. | Not auto-approved because public error taxonomy is affected. | None. | reviewed; proceed |

## Design Implication Review

Review date: 2026-05-17

The design proposal is coherent after maintainer reusable-pattern input. The
review found no blocker-level reason to add a standalone `EvaluationRunner` or
public generic `PipelineJob`. The reusable behavior needed by evaluation,
reports, dataset formatting, and similar pipeline jobs is already split across
`OperationStep`/`OperationPipeline`, `SampleOperationPipeline`/
`BatchOperationPipeline`, `SampleCollection`, `CollectionView`, explicit
uncollation policy, and export/save mechanics. Stage 13 should add only the
missing native data/artifact/evaluation/report contracts over those surfaces.

| Pressure test | Risk tested | Finding | Required revision or guardrail |
| --- | --- | --- | --- |
| Evaluation as a runner lifecycle | A class named `EvaluationRunner` would recreate iteration, error handling, result wrapping, and lifecycle semantics already owned by operations and collectors. | Blocker avoided by removing `EvaluationRunner` from Stage 13 implementation shape. Evaluation should be an `EvaluationProtocol`/`EvaluationPlan`/`EvaluationResult` plus operation-compatible callable or `OperationStep`. | Implementation phases must not add `EvaluationRunner`, `Evaluator`, evaluator-owned loops, evaluator-owned buffers, datasource scans, dataloader construction, or report output directories. |
| Public generic `PipelineJob` | A generic job API would become a workflow runtime, artifact abstraction, or second operation contract unless it had semantics not covered by existing primitives. | No blocker-level reason found. Current ops, sample collections, uncollation/export policy, and typed evaluation/report records cover the reusable pieces. | Do not add public `PipelineJob`, `JobPlan`, `JobRunner`, job status lifecycle, resume policy, artifact references, or scheduler hooks in Stage 13. Revisit only if validation proves operation adapters cannot express the root smoke flow. |
| Stage 10 method output reuse | The old patch-like `MethodOutput` shape could keep forcing extra prediction wrappers into Stage 13. | Maintainer now prefers native `Batch -> Batch` prediction flow. Existing `MethodOutput` is compatibility pressure, not the preferred Stage 13 surface. | Plan implementation around batch-native methods/ops. If existing `MethodOutput` remains during migration, add explicit compatibility adapters and tests rather than new public prediction records. |
| Stage 11 collection/view reuse | Evaluation could invent custom grouping, collection snapshots, view results, or skip/reject diagnostics. | `SampleCollectionView`, `MetricObservationCollection`, and generic collection contracts already provide reusable sample/metric views. | Use `SampleCollection` when a sample snapshot is needed; avoid `PredictionCollection`, `BatchCollection`, and evaluator-local grouping machinery. |
| Stage 12 learner/trainer boundary | Prediction flow could mine `TrainingResult`, call trainer prediction loops, or add post-model pipeline routing to learners. | Stage 12 keeps `StepOutput.predictions` opaque to trainers and documents future post-prediction batch pipeline compatibility without implementing learner-level hooks. | Batch-native prediction operations or compatibility adapters may call `Method.predict` or direct `Learner.step(..., LoopMode.PREDICT)` over assembled batches. They must not depend on `Trainer`, `TrainingEngine`, or `TrainingResult` for payloads. |
| Report and analysis reuse | Reports could force pandas, plotting, file formats, or artifact conventions into core. | In-memory `Report`/`ReportTable` and operation-compatible analysis/visualization outputs are enough for Stage 13 and Stage 14 smoke. | No dataframe core type, `to_html`/`to_pdf`/`to_csv`, plot file writer, output directory schema, or report artifact store. Renderer outputs are structured data. |
| Dataset-formatting-like jobs | Future formatting/materialization jobs may resemble evaluation/report flows. | The common shape is caller-provided inputs -> operation pipeline and/or collection view -> typed result -> optional explicit export. Existing primitives express that shape. | Use examples and validation to show dataset formatting can follow the same operation/collection/export pattern without a public job base. |

Adversarial outcome: no candidate remains auto-approved. DD-13-9 was downgraded
from an auto-approved private-helper candidate to a recorded recommendation
because the public decision not to extract shared diagnostics/protocols has
future reuse implications. No design decision is blocked and no decision packet
requires maintainer feedback.

## Future Roadmap And Reuse Safety Review

| Future item | Interaction with Stage 13 | Safety finding | Revisit trigger |
| --- | --- | --- | --- |
| Stage 14 synthetic smoke hardening | Root smoke needs method prediction, sample artifact export, reload, metric observation view, analysis op, and report. | Safe if Stage 13 exposes Batch-native operation examples, sample-granular artifact export/reload, and keeps persistence through existing save/datasource mechanics. | Stage 14 cannot express the smoke flow with `OperationPipeline`, `SampleCollection` views, explicit uncollation, and explicit export evidence. |
| Stage 15 profiling and data-path optimization | Profiling may want timing around prediction/evaluation/report operations. | Safe because operation wrappers produce `OperationResult` metadata/provenance and do not add a separate lifecycle. | Profiling requires standardized spans across prediction/evaluation operations beyond existing Stage 12 event/profile vocabulary. |
| Future post-prediction batch pipelines | Stage 12 deferred learner-level `BatchOperationPipeline` composition. | Stage 13 should not implement learner hooks; it should keep materialized `Batch` outputs compatible with `BatchOperationPipeline`. | Multiple downstream flows require mode-specific train/eval/inference pipeline routing, with maintainer approval. |
| Future dataset formatting/materialization jobs | Similar to evaluation/report composition over samples, batches, collections, operations, uncollation, and explicit export. | Safe without `PipelineJob`; formatting can use existing operation/collection/export contracts, sample artifact layouts, and datasource handoff. | Two or more implemented packages need identical public job metadata that cannot be represented by `OperationContext`, `OperationResult`, `CollectorResult`, or typed result records. |
| Future report save/render adapters | They can consume in-memory `Report`/`ReportTable` records or explicit structured report datasets exported through the field export path. | Safe if Stage 13 avoids file-format methods and backend imports. | A maintainer accepts a report-save adapter stage with explicit output contracts and import gates. |
| Future shared diagnostics | Prediction, evaluation, analysis, and reports may all carry issue-like records. | Keep package-local fields now; public extraction would be premature. | Identical code/severity/message/metadata/provenance semantics appear in at least two code-backed public packages and tests duplicate behavior. |
| Downstream project or `loom` orchestration | Downstream tools may schedule, resume, persist artifacts, or wrap rphys records. | Safe if rphys records stay serializable-ish and provenance-aware without owning workflow runtime. | rphys public APIs start needing artifact refs, scheduler state, stage DAGs, or resume tokens; route to downstream/`loom`, not Stage 13 core. |

## Functionality And Decision Audit

Traceability passes. FR-13-1 through FR-13-10 are covered by DD-13-1 through
DD-13-10, and the reviewed design preserves the maintainer constraints.

| Audit item | Result | Evidence |
| --- | --- | --- |
| Functionality coverage | pass | Batch-native prediction maps to DD-13-2; uncollation maps to DD-13-3; sample artifact export/reload maps to DD-13-4; evaluation maps to DD-13-5 and DD-13-6; analysis/report maps to DD-13-8; public errors/imports map to DD-13-1 and DD-13-10; examples/smoke coverage maps across all decisions. |
| No standalone `EvaluationRunner` | pass | DD-13-5 and DQ-13-4 explicitly reject it; implementation shape uses operation adapters and `OperationResult.output == EvaluationResult`. |
| No public generic `PipelineJob` | pass | DD-13-6 and DQ-13-6 explicitly reject it because existing ops/collections/export surfaces cover the reusable mechanics. No blocker-level reason was found. |
| Stage 10 pattern reuse | revised | Existing `MethodOutput` remains a compatibility pressure, but preferred Stage 13 flow is `Batch -> Batch`; compatibility adapters should be explicit and tested if old code still emits patches. |
| Stage 11 pattern reuse | pass | Evaluation/report plans reuse `SampleCollectionView`, `MetricObservationCollection`, and metric observation views rather than new evaluator-local or prediction-local collection contracts. |
| Stage 12 pattern reuse | pass | Learner prediction payloads remain opaque to trainers; trainers and `TrainingResult` stay out of prediction artifact construction. |
| Export/save boundary | pass | Durable prediction/test/evaluation fields go through sample-granular export/save and datasource descriptors; no prediction-specific manifest/writer/storage path is approved. |
| Report/file boundary | pass | Reports stay in-memory; file writers and rich renderers are deferred. |
| Maintainer decision packets | pass | None required. All reviewed decisions are recorded recommendations with no open blocker or exact feedback request. |

Decision classification after audit:

```text
recorded recommendation:
  DD-13-1 through DD-13-10

needs maintainer discussion:
  none

blocked:
  none

auto-approved:
  none
```

## Examples And Demonstrations

Design examples reviewed for pattern reuse and mapped to validation
requirements. These remain planning examples until implementation adds
code-backed tests/docs.

| Example | Behavior demonstrated | Pattern reuse | Status |
| --- | --- | --- | --- |
| Batch-native prediction. | Caller-provided `Batch` iterable -> method or batch operation -> `Batch` with `predictions/<key>` fields. | Stage 10 method contract pressure plus existing `BatchOperationPipeline`; no trainer, datasource scan, or prediction record family. | maintainer-revised |
| Evaluation-ready artifact export. | Test datasource -> samples -> inference-only batches -> prediction batch -> explicit pass-through of target/reference fields -> uncollate -> sample artifact export. | Existing field containers, new uncollation policy, existing export/save, and generic datasource reload. | maintainer-revised |
| Artifact reload for multiple evaluations. | Sample artifact datasource with predictions + references -> evaluation plan A and evaluation plan B. | Existing datasource/sample-source machinery and operation-compatible evaluation; no `PredictionDataSource` or `PredictionCollection`. | maintainer-revised |
| Pipeline-based evaluation. | Sample artifact datasource, `SampleCollection`, or `Batch` input -> `EvaluationPlan` -> evaluation operation wrapper -> `EvaluationResult` -> optional report operation inside `OperationPipeline`. | Existing `OperationStep`/`OperationPipeline`; no `EvaluationRunner` and no public `PipelineJob`; multiple evaluation workflows can consume the same sample artifact datasource. | reviewed |
| Collection-view evaluation. | Materialized `SampleCollection` -> `SampleCollectionView` -> metric -> `MetricObservationCollection` -> observation view. | Existing `CollectionView`, sample collections, and metric observation views; no metric-owned reconstruction. | reviewed |
| Report building. | `EvaluationResult` plus analysis result -> in-memory `Report`/`ReportTable` -> optional structured report field export through the same item-to-export adapter shape. | Structured records; no dataframe, plotting, file writer, or report artifact dependency. | reviewed |
| Dataset formatting analogue. | Prepared `SampleCollection` -> `SampleOperationPipeline` or collection view -> item-to-export adapter -> explicit export/save -> derived datasource assembly. | Same operation/collection/export pattern as evaluation without a shared public job base. | reviewed |
| Analysis operation analogue. | `MetricObservationCollection` or `EvaluationResult` -> `AnalysisOp` wrapper -> `AnalysisResult` -> report table rows. | Existing operation result wrapping with analysis-specific records; no ad hoc log crawl or checkpoint selection. | reviewed |

## Validation Strategy

Validation planner date: 2026-05-17

Required validation must prove that Stage 13 keeps prediction/evaluation/report
work native to `Sample` and `Batch` containers, adds explicit batch-field
uncollation and sample artifact export/reload behavior, and layers evaluation,
analysis, and report semantics over existing operations, sample collections,
views, metrics, export/save, and datasource substrates. Validation must not
bless a standalone public `EvaluationRunner`, public generic `PipelineJob`/
`JobPlan`/`JobRunner`, public `Prediction*` record family, `BatchCollection`/
`BatchCollector`, trainer-owned prediction capture, prediction-specific storage,
dataframe core type, plotting backend, report writer, or workflow runtime.

| Area | Behavior validated | Required coverage | Test/check type | Likely command or location | Related FRs / decisions | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Package imports, public exports, and errors | Implemented data/artifact/evaluation/analysis names are code-backed and lightweight. | Package `__all__` tests for implemented names only; root `rphys.__all__` stays empty; no optional broad prediction error unless public prediction code justifies it; evaluation/analysis use existing broad bases; no torch, numpy, scipy, pandas, matplotlib, video, dataset-SDK, trainer, workflow, or report-writer imports on package import. | package/unit | `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; `tests/unit/rphys/test_errors.py` or package-local error tests; `make test-package`; `make test-unit` | FR-13-9; DD-13-1; DD-13-10 | required |
| Batch-native prediction flow | Prediction computation uses ordinary `Batch` outputs and field locators. | Fake `Method.predict`/batch operation tests returning `Batch` with `predictions/<key>` fields; compatibility tests for existing `MethodOutput` only if retained; target/reference fields are excluded from model-input projection; no `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, `PredictionRunner`, `Trainer`, `TrainingEngine`, `TrainingResult`, dataloader, datasource scan, checkpoint chooser, export writer, logger, or scheduler dependency. | unit/contract/integration | `tests/unit/rphys/data/` or method/ops tests selected during implementation; `tests/contracts/test_stage13_batch_prediction_contract.py`; synthetic integration; `make test-unit`; `make test-contract`; `make test-integration` | FR-13-1; DD-13-2 | required |
| Batch uncollation policies | Every serializable batch field can produce per-sample `FieldValue`s through explicit policy/evidence. | Unit/contract tests for LIST, batch-axis, broadcast, drop/error, and custom-adapter policies if implemented; invalid sample counts; missing policy; mismatched metadata; unsupported payloads; no implicit tensor-axis guessing; field-locator-specific error context. | unit/contract | `tests/unit/rphys/data/test_uncollation*.py`; `tests/contracts/test_stage13_uncollation_contract.py`; `make test-unit`; `make test-contract` | FR-13-2; FR-13-3; DD-13-3 | required |
| Sample artifact export and derived datasource evidence | Durable prediction/test/evaluation fields use per-sample export/save and datasource reload. | Tests or fakes showing batch prediction fields plus allowed pass-through target/reference fields uncollate to Samples, feed existing export/save request/result surfaces with source `RecordRef` or augmented export-record descriptors, retain export evidence, and reload through generic sample artifact datasource descriptors. No prediction-specific manifest, codec, layout, output directory convention, or storage class is introduced. | contract/integration/docs | sample artifact contract tests; synthetic export fakes near `tests/integration/`; `src/rphys/ops/export.py`; datasource adapter tests; `make test-contract`; `make test-integration` | FR-13-2; FR-13-4; DD-13-4 | required |
| Evaluation protocol, plan, and result records | Scientific comparison semantics are explicit and reproducible without owning execution. | Unit/contract tests for prediction field selectors, reference selectors, grouping metadata, sample/batch projection and pass-through policy, pre-metric `SampleCollectionView` requirements, metric requirements, `MetricObservationCollection` view order, report requirements, failure policy, primitive metadata/provenance, missing selectors/references/groups, invalid policies, partial failure evidence, and optional export evidence when metric/evaluation observations are saved as sample artifact fields. | unit/contract | `tests/unit/rphys/evaluation/test_protocols*.py`; `tests/unit/rphys/evaluation/test_results*.py`; `tests/contracts/test_stage13_evaluation_contract.py`; `make test-unit`; `make test-contract` | FR-13-5; DD-13-5 | required |
| Evaluation operation/pipeline composition | Evaluation is expressible through existing operation and collection primitives. | Contract/integration tests where `EvaluationPlan` is consumed by an operation-compatible callable or `OperationStep`, returns `OperationResult.output == EvaluationResult`, and composes with report/analysis operations in `OperationPipeline`; assert no public `EvaluationRunner`, `Evaluator`, public `PipelineJob`, public `JobPlan`, public `JobRunner`, evaluator-owned lifecycle, datasource scan, dataloader construction, output directory, or resume token. | contract/integration/package | `tests/contracts/test_stage13_evaluation_ops_contract.py`; `tests/integration/test_stage13_synthetic_evaluation_pipeline.py`; package export tests; `make test-contract`; `make test-integration`; `make test-package` | FR-13-6; DD-13-7; DQ-13-4; DQ-13-6 | required |
| Analysis and visualization operation contracts | Analysis/visualization consume approved inputs and return structured outputs without side effects. | Tests with fake `AnalysisOp`/`VisualizationOp` over `Sample`, `Batch`, `SampleCollection`, `MetricObservationCollection`, `EvaluationResult`, `AnalysisResult`, and `Report` where supported; invalid input failures; metadata/provenance; no mutation, checkpoint selection, training, ad hoc log crawling, plot file writing, plotting import, or dataframe dependency. | unit/contract/integration | `tests/unit/rphys/analysis/test_core*.py`; `tests/contracts/test_stage13_analysis_contract.py`; `make test-unit`; `make test-contract` | FR-13-7; DD-13-8 | required |
| Reports, tables, sections, and diagnostic renderers | Reports are dependency-light in-memory records and renderer outputs are data. | Unit tests for row/column validation, primitive values, metric-observation rows, analysis/evaluation result rows, section ordering, provenance, invalid row shape/cell values, renderer output records, diagnostics, optional field-export-compatible structured report dataset behavior if implemented, and no pandas/HTML/PDF/CSV/Markdown writer, plot/image file writer, artifact store, or output directory schema. | unit/contract/package | `tests/unit/rphys/analysis/test_reports*.py`; `tests/contracts/test_stage13_report_contract.py`; `make test-unit`; `make test-contract`; `make test-package` | FR-13-8; DD-13-8 | required |
| Serialized output datasource reuse | Persisted predictions, metric/evaluation outputs, and structured report datasets are reloadable through sample artifact datasource descriptors rather than domain-specific datasource families. | Tests/docs show exported prediction/test artifact samples become a datasource consumed by at least one later evaluation plan; metric/evaluation fields can use the same handoff when persisted; optional structured report datasets use ordinary field export; no `PredictionDataSource`, `EvaluationDataSource`, `ReportDataSource`, runner-owned result cache, or domain-specific storage API appears. Cross-process descriptor recovery is either covered by existing datasource/index manifest behavior or reopened as a generic derived-output scan/reader adapter. | contract/integration/docs | Stage 13 integration examples; sample artifact contract tests if added; final docs/example review; `make test-contract`; `make test-integration` | FR-13-4; FR-13-6; FR-13-8; DD-13-4; DD-13-6 | required |
| Package-local diagnostics and helper reuse | Repeated issue/job-like fields do not become premature public generic APIs. | Review/tests confirm any shared diagnostic issue helpers, job-record helpers, coercion helpers, selector validators, or operation factories are private/package-local; no public generic diagnostic record, job record, scheduler state, artifact reference, or workflow lifecycle is exported. | package/review | Package export tests; code review; `git diff --check`; `make test-package` | FR-13-6; FR-13-9; DD-13-7; DD-13-9 | required review check |
| Scientific and workflow failure behavior | Stage 13 preserves physiological interpretation boundaries and exposes provenance/failure modes. | Tests/docs for missing prediction/reference fields, missing labels, missing group metadata, empty masks/groups where descriptors support them, invalid sampling-rate/window metadata when declared, unsupported temporal slices/selectors, short/flat/NaN inputs where contract-level checks can detect them, dtype/device/backend mismatch metadata, subject/split leakage-sensitive grouping warnings or failure metadata, and per-sample/per-window/per-record/per-subject/per-dataset scope clarity. Do not invent concrete numerical algorithms or reconstruction behavior. | unit/contract/docs | Public docstrings; `tests/unit/rphys/{prediction,evaluation,analysis}/`; `tests/contracts/`; `git diff --check` | Behavior Confirmation; FR-13-5; FR-13-7; FR-13-8 | required |
| Examples, docs, and workflow handoff | Accepted examples map to implemented tests/docs and show substrate reuse without generic runners. | Docs/docstrings/examples for Batch-native prediction, target-free inference projection, evaluation-ready pass-through fields, uncollation to samples, sample artifact export/reload, pipeline-based evaluation, collection-view evaluation, report building, dataset-formatting analogue, and analysis operation analogue; examples use synthetic/tiny license-safe data only and avoid external datasets/GPUs. | docs/integration/review | Public module docstrings; possible docs example under `docs/`; `tests/integration/test_stage13_*`; `git diff --check`; `make test-integration` when added | FR-13-10; Examples And Demonstrations | required |
| Final validation commands | Implementation evidence is reproducible and broad enough for public contracts. | Run focused package/unit/contract/integration checks per phase, then broaden before final handoff. | command | Recommended closeout: `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`; `make validate-pr` | FR-13-1 through FR-13-10 | required before implementation closeout when practical |

### Optional Validation Coverage

| Area | Risk reduced | Optional coverage | Trigger | Likely command or location | Status |
| --- | --- | --- | --- | --- | --- |
| Serialization/primitive persistence smoke | Confirms downstream workflow tools can persist summaries without raw framework objects. | JSON-like or primitive-mapping smoke tests for plans/results/reports/diagnostics where records claim primitive metadata/provenance. | Add if implemented records expose serialization helpers or document primitive-only persistence expectations. | Unit tests near package result/report tests; `make test-unit` | optional |
| Type/protocol conformance probes | Catches drift in structural protocols and operation adapters. | Runtime-checkable fake probes or static snippets for fake batch prediction, evaluation, analysis, report, and operation adapter objects. | Add if implementation uses runtime-checkable protocols, overload-heavy call signatures, or a type-check target appears. | Contract tests or future type-check command | optional |
| Selector/uncollation matrix tests | Reduces missed combinations in selector, locator, grouping, and uncollation policy validation. | Parametrized tests over valid/invalid locators, missing references, duplicate groups, uncollation policies, sample counts, and unsupported payload combinations. | Add when validation helpers have enough branches that example-only tests leave obvious gaps. | `tests/unit/rphys/{data,evaluation}/` | optional |
| Import subprocess diagnostics | Makes heavy-import regressions easier to diagnose. | Isolated subprocess import tests that assert forbidden optional modules are absent from `sys.modules`. | Add if existing package import-boundary tests are insufficient or failures are hard to attribute. | `tests/package/test_import_boundaries.py`; `make test-package` | optional |

### Validation And Examples Mapping

| Example | Required validation mapping | Docs/example expectation |
| --- | --- | --- |
| Batch-native method prediction | Batch-operation tests plus fake `Method.predict` tests returning `Batch` outputs. | Show caller-provided batches -> prediction operation -> batch with `predictions/<key>` fields; no trainer, datasource, or export side effects. |
| Learner compatibility | Fake `Learner.step(..., LoopMode.PREDICT)` tests and no `TrainingResult` payload mining assertions if learner compatibility remains in scope. | Show direct learner prediction step over assembled batches with compatibility adaptation to native `Batch` output. |
| Sample artifact export | Uncollation policy tests plus export/datasource evidence tests or docs review. | Show prediction batch + allowed target/reference pass-through -> uncollated Samples plus source `RecordRef` or export descriptor -> existing export/save -> sample artifact datasource evidence, then a later evaluation flow reusing that datasource. |
| Pipeline-based evaluation | Evaluation operation/pipeline contract/integration test. | Show `EvaluationPlan` as operation input and `EvaluationResult` as operation output inside existing `OperationPipeline`; no public `EvaluationRunner` or generic job. |
| Collection-view evaluation | Evaluation protocol tests using `SampleCollectionView` and `MetricObservationCollection`/views. | Show collection/view/metric order and grouping/provenance without evaluator-owned reconstruction. |
| Report building | Report/table/diagnostic renderer tests. | Show in-memory `Report`/`ReportTable` from evaluation and analysis outputs; if durable handoff is demonstrated, use ordinary field export; no dataframe, plot, or file writer. |
| Dataset formatting analogue | Operation/collection/export example review. | Document prepared `SampleCollection` -> sample operation/view -> explicit export/save -> derived datasource assembly as the same substrate pattern, without a shared public job base. |
| Analysis operation analogue | Fake `AnalysisOp` operation tests and report row tests. | Show `MetricObservationCollection` or `EvaluationResult` -> `AnalysisResult` -> report table rows; no log crawl or checkpoint selection. |

## Phase Shaping

Phase shaping result: revised. The implementation should be split into
reviewable phases with bounded public API, non-overlapping phase ownership, and
acceptance criteria that preserve the Sample/Batch-native dataflow,
sample-granular artifact export, no-standalone-`EvaluationRunner`, and
no-public-generic-job decisions. No phase may add a public `Prediction*` record
family, `BatchCollection`, `BatchCollector`, `PipelineJob`, `JobPlan`,
`JobRunner`, scheduler/resume/artifact lifecycle, evaluator-owned datasource
scan, trainer-owned prediction capture, prediction-specific storage, report file
writer, dataframe core type, plotting backend, or broad workflow runtime.

| Phase | Goal | Scope | Out of scope | Dependencies | Acceptance criteria | Test expectations | Design impact | Future compatibility | Interface/reuse implications | Reviewability | Risks | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Establish package scaffold, errors, and import boundaries. | Add code-backed scoped module/package exports for implemented names, optional code-backed error additions only where needed, package-local validation/diagnostic helper boundaries if needed, and package/import-boundary tests. | Public prediction record behavior, root re-exports, placeholder exports, public generic diagnostic/job records, heavy optional imports, trainer/export/datasource/report-writer imports. | Functionality/design agreement; DD-13-1; DD-13-9; DD-13-10. | Package homes import cleanly; root exports remain empty; evaluation/analysis broad errors remain existing bases; helper modules stay private; no forbidden optional/backend/workflow imports appear. | `make test-package`; focused error unit tests if added; `git diff --check`. | Locks import posture before public data/artifact/evaluation/report behavior depends on it. | Stage 14 smoke and downstream projects get stable provisional import homes without root API churn. | Keeps reusable helper extraction private until two code-backed packages prove identical public semantics. | Small scaffold review; no semantic runners or report APIs included. | Risk of exporting placeholder names early; mitigate with code-backed export tests. | revised |
| 2 | Implement Batch-native prediction and compatibility adapters. | `Batch -> Batch` fake method/operation behavior, field projection, target-exclusion checks, explicit merge/pass-through policy, compatibility adapters for existing `MethodOutput` or `StepOutput.predictions` only where needed, and docs/tests. | Public prediction runner lifecycle, `PredictionRecord`, `PredictionCollection`, `PredictionCollector`, dataloader building, datasource scans, trainer prediction loops, `TrainingResult` payload mining, checkpoint selection, export side effects, operation pipeline runtime ownership. | Phase 1; Stage 10 method contracts; Stage 12 `Learner`/`StepOutput` only for compatibility. | Prediction computation returns/uses ordinary `Batch` containers with `predictions/<key>` fields; invalid field roles or target leakage fail clearly; no public `Prediction*` family is exported. | Unit/contract tests for batch outputs, field projection, target exclusion, and compatibility adapters if retained. | Locks the simplified prediction handoff before uncollation/export and evaluation depend on it. | Stage 14 can smoke-test batch-native prediction without wrapper records. | Reuses existing `BatchOperationPipeline` and field locators rather than custom row tables. | Review can focus on dataflow and trainer/datasource exclusions. | Refactoring `MethodOutput` may be wider than the old plan; keep compatibility adapters explicit. | revised |
| 3 | Implement uncollation policy and sample artifact export/reload. | Public batch-field uncollation policy/evidence, per-sample artifact export helpers/adapters over existing export/save, source `RecordRef` or augmented export-record descriptor requirements, generic sample artifact layout/datasource adapter behavior, and tests/examples. | New codecs, prediction manifests, prediction storage path, domain-specific datasource family, batch-as-one-record export, implicit tensor-axis guesses, implicit mutation, report save adapters, `rphys.ops.collections`, `BatchCollection`, `BatchCollector`. | Phases 1-2; Stage 8 export/save and derived datasource behavior; existing data collation. | Every durable artifact is one record per `Sample`; export delegates persistence to existing export/save and datasource surfaces; no new prediction storage family appears; durable export never proceeds from loaded field values alone. | Unit/contract uncollation tests; integration or fake export/reload tests; docs/example review for artifact layout use. | Locks the batch-to-sample and IO risk boundary needed before evaluation protocols consume artifacts. | Stage 14 can export/reload sample artifacts through normal datasource machinery. | Uses existing export/save operation contracts and descriptor evidence; avoids making prediction own IO. | Review isolates uncollation and artifact descriptor semantics. | Existing export/datasource APIs may need generic adapter glue; if a phase proposes domain storage, reopen FQ-13-3/DD-13-4. | revised |
| 4 | Implement evaluation protocol, result records, and operation adapters. | `EvaluationProtocol`, `EvaluationPlan`, `EvaluationResult`, failure/diagnostic records as private or package-local unless tests require public shape, selector/reference/group/projection/report requirements, and operation-compatible adapter/wrapper over existing `OperationStep`/`OperationPipeline`. | Public `EvaluationRunner`, public generic `PipelineJob`, evaluator-owned lifecycle, datasource scans, split/index construction, dataloader construction, metric catalogs, concrete reconstruction algorithms, report output directories, workflow resume/artifact state. | Phases 1-3; Stage 11 sample and metric observation collections/views; existing ops primitives. | Protocol records scientific comparison semantics over sample/batch fields; plan binds concrete inputs or sample artifact datasources; result carries metric observations/reports/diagnostics/provenance; evaluation can run as operation output; package exports contain no `EvaluationRunner` or generic job API. | Unit/contract protocol/result tests; evaluation operation/pipeline integration; no-runner package export assertions. | Locks scientific evaluation semantics while leaving execution to ops and collections. | Stage 14 smoke and Stage 15 profiling can wrap operation metadata without a second runtime. | Reuses `OperationStep`, `OperationResult`, `OperationPipeline`, `SampleCollectionView`, and `MetricObservationCollection` instead of evaluator-local abstractions. | Review boundary is evaluation package plus operation adapter tests. | Selector/grouping semantics could grow broad; keep concrete reconstruction and datasource policy deferred. | revised |
| 5 | Implement analysis, visualization, reports, tables, and renderer outputs. | Structural `AnalysisOp`/`VisualizationOp`, `AnalysisContext`, `AnalysisResult`, in-memory `Report`, report sections/tables/cells if needed, `DiagnosticRenderer`/render result records, and operation-compatible wrappers where useful. | Checkpoint selection, training, log crawling, prediction mutation, plotting backend, pandas/dataframe core type, HTML/PDF/CSV/Markdown writers, plot/image file writes, dashboard/artifact store, report save conventions. | Phases 1, 2, and 4 where report inputs include evaluation results. | Analysis/report records are dependency-light, structured, primitive/provenance-aware, and side-effect free by default; renderer outputs are data; invalid report rows/cells fail loudly; no heavy imports. | Unit/contract tests for analysis ops and report records; package import checks; docs/example review. | Locks Stage 13's downstream-facing evidence/report object shape without freezing file formats. | Future report render/save adapters can consume records additively behind import gates. | Report/analysis operations may compose through existing `OperationPipeline` but do not define new execution machinery. | Review can focus on data records and side-effect exclusions. | Too-rich report APIs could freeze format conventions; keep save/render adapters deferred. | ready for implementation planning |
| 6 | Complete synthetic composition examples, docs, and final validation. | End-to-end synthetic tests/docs for batch-native prediction, uncollation, sample artifact export/reload, evaluation operation pipeline, collection-view metrics, analysis/report rows, dataset-formatting analogue, public docstrings, package export review, and final validation evidence. | New public product behavior, concrete algorithms, real datasets, GPU checks, performance profiling, implementation-plan creation inside this phase, docs-only PRs outside workflow. | Phases 1-5. | Examples in this planning artifact have tests/docs; no agreement queue reopens; no forbidden prediction record/runner/job/storage/report-writer/import behavior appears; final validation is run or residual risk is recorded. | `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test-summary`; `uv lock --check`; `git diff --check`; `make validate-pr` when practical. | Confirms the public Stage 13 surface is coherent before Stage 14 smoke hardening. | Gives Stage 14 a clear smoke target and keeps Stage 15 profiling/additive adapters unblocked. | Demonstrates the shared substrate pattern across evaluation, reports, dataset formatting analogues, and analysis without public generic job APIs. | Final review boundary for API coherence, examples, docs, and validation evidence. | Cross-package inconsistencies may appear late; mitigate with synthetic composition and import-boundary review before closeout. | revised |

Phase dependencies and review boundaries:

- Phase 1 is the root scaffold for all later package exports and error tests.
- Phase 2 should land before uncollation/artifact export and evaluation because
  it defines the Batch-native prediction field shape consumed by those phases.
- Phase 3 depends on Phase 2 and should be reviewed separately because
  uncollation/export is the main data-shape and IO risk boundary.
- Phase 4 depends on Phases 2-3 and must preserve the operation/collection
  substrate decision; any pressure toward `EvaluationRunner`, public generic
  jobs, or a public `Prediction*` record family reopens DQ-13-2/DQ-13-4/DQ-13-6.
- Phase 5 can begin after Phase 1 for record scaffolding, but report examples
  that consume `EvaluationResult` should wait for Phase 4.
- Phase 6 closes only after Phases 1-5 and should not introduce new public
  decisions except test-driven error/docs refinements that preserve accepted
  semantics.

Implementation-plan acceptance criteria should explicitly include:

- no unresolved functionality or design queue items;
- no public standalone `EvaluationRunner`;
- no public `PipelineJob`, `JobPlan`, `JobRunner`, scheduler, artifact, or
  resume lifecycle;
- no trainer-owned prediction capture or `TrainingResult` payload mining;
- no datasource scans, dataloader construction, checkpoint selection,
  prediction-specific storage, report file writers, plotting/dataframe hard
  dependencies, or workflow runtime ownership;
- public behavior backed by package, unit, contract, integration, and docs
  evidence before downstream use.

## Plan Quality Gate

Gate result: passed. Implementation-plan drafting may proceed in a later pass.
This pass deliberately did not create or edit `implementation-plan.md`.

| Check | Evidence reviewed | Result | Notes |
| --- | --- | --- | --- |
| Required specialist evidence | Source evidence, exploration coverage, roadmap extraction, capability triage, module behavior map, functional requirements, functionality agreement, behavior confirmation, design proposal, design implication review, future-roadmap/reuse safety review, functionality/decision audit, examples, validation strategy, and phase shaping are recorded in this artifact. | pass | Context/functionality/design gates can be treated as passed from the current artifact. No required evidence is manager-only relative to the accepted maintainer constraints. |
| Agreement queues | FQ-13-1 through FQ-13-10 are resolved; DQ-13-1 through DQ-13-7 are reviewed with no blocker or maintainer discussion packet. | pass | No queue item is `needs maintainer discussion`, `blocked`, `pending approval`, or `ready for approval`; no queue reopen is required. |
| Roadmap-to-requirement traceability | Milestone 13 maps to FR-13-1 through FR-13-10, with Stage 8/10/11/12 prerequisites and Stage 14/15 compatibility recorded. | pass | Roadmap Stage 13 text is now aligned to Sample/Batch-native prediction, sample artifact export/reload, evaluation records plus operation adapters, and explicitly rejects public prediction/evaluation runner lifecycles. |
| Requirement-to-design traceability | FR-13-1 through FR-13-10 map to DD-13-1 through DD-13-10 and are audited in `Functionality And Decision Audit`. | pass | No included capability lacks a design decision, validation row, or phase home. |
| Design-to-future/reuse traceability | Future roadmap and reuse safety findings cover Stage 14 smoke, Stage 15 profiling, post-prediction batch pipelines, dataset-formatting-like jobs, report adapters, shared diagnostics, and downstream/`loom` orchestration. | pass | Revisit triggers are carried into validation and phase risks. |
| Stage 10 reusable pattern compatibility | `MethodOutput` remains an existing compatibility surface, but Stage 13 preferred behavior is Batch-native prediction. | revised | Validation covers compatibility adapters if needed, target-free model inputs, and no waveform-only prediction object. |
| Stage 11 reusable pattern compatibility | Evaluation/report behavior reuses `SampleCollectionView`, `MetricObservationCollection`, and metric observation views. | pass | No evaluator-local or prediction-local collection/view lifecycle is approved. |
| Stage 12 reusable pattern compatibility | Batch-native compatibility may call direct learner prediction steps, while trainers and `TrainingResult` remain summary-only and opaque to artifact construction. | pass | Tests must assert no trainer dependency and no `TrainingResult` payload mining. |
| Operation/export substrate compatibility | Evaluation/report/analysis composition is expressed through `OperationStep`, `OperationResult`, `OperationPipeline`, sample/batch pipelines where relevant, explicit uncollation policy, and explicit export/save/datasource behavior. | pass | No public generic job abstraction or second runtime is needed for implementation-plan drafting. |
| Validation readiness | Required validation covers unit behavior, edge cases, failure behavior, integration boundaries, interface/adapter/protocol reuse, examples, docs/templates/workflows, and scientific/workflow contracts. | pass | Optional validation is trigger-based and does not block implementation planning. |
| Phase-shaping readiness | Six phases have dependencies, scope, out-of-scope boundaries, acceptance criteria, test expectations, design impact, future compatibility, interface/reuse implications, review boundaries, and risks. | pass | Implementation planner can convert the phase sketch into `implementation-plan.md` later. |
| Extensibility and maintainability | Public surfaces are scoped; helper extraction remains private/package-local; no registry, global state, placeholder exports, broad workflow/job runtime, or hidden side-effect system is approved. | pass | Shared diagnostics/job semantics may be revisited only after repeated code-backed public behavior exists. |
| Scientific/workflow contract clarity | Failure modes and docs/tests cover selectors, grouping, labels, provenance, uncollation, artifact pass-through, missing data, empty groups/masks, invalid metadata, leakage-sensitive grouping, and scope semantics at the contract level. | pass | Concrete algorithms, reconstruction, plotting, report writers, and real datasets remain deferred. |
| Documentation and example readiness | Examples are mapped to validation and docs expectations, including evaluation/report/dataset-formatting-like jobs reusing existing substrate without a generic runner. | pass | Implementation planning should carry these examples into phase acceptance criteria. |
| Stale evidence or reopened decisions | Current working tree has unrelated modified `docs/roadmap.md`; this artifact uses the current roadmap text and adjacent stage evidence. No stale evidence conflicts with accepted decisions. | pass | Recheck only if `docs/roadmap.md` or Stage 10-12 public contracts change before implementation planning. |
| Implementation-plan boundary | User requested no code implementation and no `implementation-plan.md` creation in this pass. | pass | Stop after this planning artifact update. |

Blocking findings: none.

Unresolved/open questions: none.

Queue reopen required: no.

Accepted risks:

- Exact module and record names may adjust during implementation if accepted
  semantics, import boundaries, and validation obligations remain intact.
- Package-local diagnostic/helper duplication is accepted to avoid premature
  public generic APIs; extraction requires a future revisit trigger.
- In-memory reports may be less convenient than file writers, but this avoids
  freezing dataframe, plotting, and report-format conventions in Stage 13 core.
- Existing export/save APIs may make a dedicated prediction export bridge
  unnecessary; implementation may document direct use instead of adding a thin
  wrapper if tests/examples still prove the prediction-as-derived-datasource
  flow.

Revisit triggers:

- Implementation cannot express evaluation/report/analysis examples through
  existing operations, pipelines, collections, views, collectors, and explicit
  export/save evidence.
- Implementation proposes a standalone public `EvaluationRunner`, public
  generic `PipelineJob`/`JobPlan`/`JobRunner`, scheduler/resume/artifact
  lifecycle, evaluator-owned datasource scan, or output directory convention.
- Prediction collection depends on `Trainer`, `TrainingEngine`, or
  `TrainingResult` to recover prediction payloads.
- Batch prediction or artifact export hides target leakage, guesses uncollation
  policy, serializes batches as single records, creates prediction-specific
  storage, or bypasses existing export/save and datasource behavior.
- Reports require pandas, plotting, rich media, file writers, or report output
  directories in core imports.
- Required tests cannot express accepted behavior, or Stage 10-12 public
  contracts change before implementation planning.

No implementation code should be written until an implementation plan is
created and approved.

## Accepted Assumptions And Deferrals

| Item | Type | Rationale | Revisit trigger |
| --- | --- | --- | --- |
| No `docs/features` directory exists. | assumption | Feature docs search failed; roadmap and adjacent stage artifacts are canonical. | Feature docs are added or maintainer points to external feature material. |
| Current modified `docs/roadmap.md` is the source read and aligned roadmap target for this pass. | assumption | Working tree shows `docs/roadmap.md` modified before this pass; latest refinement makes targeted Stage 13 wording updates to remove runner language and describe durable derived-dataset handoff. | Maintainer updates/reverts roadmap before agreement or design. |
| Concrete algorithms and report/rendering adapters are deferred. | deferral | Roadmap says Stage 13 core is structured/dependency-light and optional adapters are import-gated. | Maintainer explicitly includes a concrete algorithm/adapter, or Stage 14 smoke cannot prove the flow without one. |
| Sample artifact export uses existing export/save and datasource behavior. | deferral/assumption | Stage 8 already owns save/export and datasource refs; Stage 13 should not invent storage. Sample-to-export adapters must provide a source `RecordRef` or augmented export-record descriptor declaring the fields being exported, because existing export/save validates loaded `FieldValue`s against record descriptors. | Existing export APIs cannot support sample artifact fields without widening, or implementation attempts durable export from loaded field values alone; reopen FQ-13-3. |
| Serialized output interaction reuses the datasource layer. | assumption/conditional inclusion | Once persisted, predictions, metric/evaluation outputs, and structured report datasets are ordinary fields in sample artifact datasource records. Domain packages own interpretation; datasource code owns descriptor reload/index/sample-source behavior. | Implementation needs a domain-specific datasource family, runner-owned result cache, or a non-generic persistence reader; instead reopen the relevant queue for a generic sample artifact descriptor recovery path. |
| No public generic `PipelineJob` is added in Stage 13. | deferral/rejection | Existing operations, pipelines, collectors, collection views, and export/save mechanics cover the reusable behavior needed by evaluation, reports, dataset formatting, and similar jobs. | Validation proves the root examples cannot be expressed with existing primitives, or two public packages need identical job metadata that cannot be represented by existing operation/collection/result records. |
| No standalone public `EvaluationRunner` is added in Stage 13. | deferral/rejection | Maintainer-approved design review found evaluation execution belongs in existing operation/pipeline/collection primitives, with Stage 13 owning semantic protocol/plan/result records and operation adapters. | Implementation pressure shows evaluation cannot be expressed as operation-compatible records without duplicating substantial logic. |
| No `rphys.ops.collections`, `BatchCollection`, or `BatchCollector` package/API is added for Stage 13. | assumption/conditional inclusion | The current framework already has generic collections, operation steps, field handles, export requests, codec selection, save operations, and datasource assembly. Passive collection records, items, collectors, and views remain in `rphys.collections`; transient batches can use `Iterable[Batch]`; durable handoff is expressed by sample artifact adapters plus existing export behavior. | Implementation cannot keep repeated export loops narrow without duplicating behavior across evaluation/report, or it starts owning scheduling, resume state, artifact refs, datasource scans, collection semantics, output directories, or writer formats. |
| Shared diagnostics/job-record helpers stay private/package-local. | assumption/deferral | Similar issue-like fields may appear across prediction/evaluation/analysis/report results, but public extraction is premature before duplicated code-backed behavior exists. | Identical public code/severity/message/metadata/provenance semantics appear in at least two packages and cannot remain private without inconsistent behavior. |
| Exact module names may be adjusted during implementation. | assumption | Planning locks semantics and validation obligations, not every file name. | Implementation changes dependency direction, public API scope, or accepted behavior rather than only local module layout. |
| Validation commands are planned, not run, in this pass. | assumption | This pass updates planning documentation only and does not implement code. | Implementation-plan or phase execution begins. |

## Resume Checkpoints

### After Functionality Agreement

- Queue state: FQ-13-1 through FQ-13-10 resolved; FQ-13-5, FQ-13-8, and
  FQ-13-9 are locked or deferred as recorded.
- Behavior confirmation status: passed.
- Open questions: none for functionality.
- Next step: design proposal.

### After Design Agreement

- Queue state: DQ-13-1 through DQ-13-7 reviewed; no item is blocked and no
  maintainer discussion packet is open.
- Implementation shape locked for validation planning: reuses
  `OperationStep`/`OperationPipeline`, sample/batch pipelines, `Collector`,
  `CollectionView`, export/save, and derived datasource assembly; no
  standalone `EvaluationRunner` or public generic `PipelineJob` is approved.
- Open questions: none.
- Next step: validation planning.

### After Validation, Phase Shaping, And Plan Quality Gate

- Validation baseline locked: required package/import, unit, contract,
  integration, docs/review, scientific/workflow contract, example-mapping, and
  final validation checks are recorded. Optional checks are trigger-based.
- Phase sketch revised: six reviewable phases cover scaffold/imports/errors;
  Batch-native prediction; uncollation and sample artifact export/reload;
  evaluation protocol/results/operation adapters; analysis/report records; and
  synthetic composition/docs/final validation.
- Gate result: passed on 2026-05-17. No blocker, missing or stale specialist
  evidence, unresolved packet, or queue-reopen need remains.
- Open questions: none. Implementation must reopen the relevant queue if it
  cannot satisfy no public `EvaluationRunner`, no public generic job API,
  explicit uncollation/sample artifact export, trainer-free batch prediction,
  lightweight imports, in-memory reports, or operation/collection substrate
  reuse.
- Next step: implementation-plan drafting by the appropriate workflow role;
  this pass deliberately did not create `implementation-plan.md`.

### After Implementation Plan Handoff

- Implementation plan status: passed on 2026-05-17 after implementation planner
  drafting and managing-agent review.
- Artifact created:
  `docs/roadmap/stage-13/implementation-plan.md`.
- Phase plan revised for execution workflow: six sequential phases covering
  scaffold/imports/errors; Batch-native prediction; uncollation and sample
  artifact export/reload; evaluation protocols/results/operation adapters;
  analysis/report records; and docs/examples/final validation.
- Open questions: none. The implementation workflow must reopen the relevant
  queue before adding a standalone public `EvaluationRunner`, public
  `Prediction*` record family, public generic job/runtime API, trainer-owned
  prediction capture, prediction-specific storage, report file writers,
  plotting/dataframe core dependencies, or workflow lifecycle ownership.
- Next step: execute the roadmap-version-implementation workflow when code
  implementation is requested.

## Workflow Feedback Routing

| Feedback | Routing | Action | Status |
| --- | --- | --- | --- |
| User requested stopping after context scaffold / initial functionality queue and not asking maintainer questions. | prior-session preference | Earlier pass stopped before functionality-agreement discussion, design proposal, validation, and implementation planning. | superseded by current continuation |
| Maintainer agreed that reusable pipeline/job patterns are preferable to an evaluation-specific runner and asked to consider abstract/generic design patterns from Stages 10-12. | product/design requirement | Route to Stage 13 design proposal and implication review; require proposed design decisions to evaluate reusable protocols/adapters/records before evaluation-specific instantiation. | recorded |
| User requested continuing Stage 13 after functionality agreement and behavior confirmation, writing only `planning.md`, treating no standalone `EvaluationRunner` as critical design input, and stopping after design proposal. | prior-session preference | Drafted proposed implementation shape, design queue, design decisions, triage, and design examples only. Did not run implication review, validation planning, phase shaping, or implementation planning. | superseded by current continuation |
| User requested continuing Stage 13 design review after maintainer reusable-pattern input, with no standalone `EvaluationRunner`, no public generic `PipelineJob` unless blocker-level reason, and explicit pressure tests against Stages 10-12 reusable patterns. | current-session preference | Completed design implication review, future-roadmap/reuse safety review, functionality/decision audit, examples/demonstrations, and design queue/decision reclassification. No maintainer discussion packet was opened. | applied |
| User requested continuing Stage 13 validation/quality planning, writing only `docs/roadmap/stage-13/planning.md`, treating context/functionality/design gates as passed if supported, and stopping before code or `implementation-plan.md`. | current-session preference | Completed validation strategy, validation/examples mapping, phase shaping, plan quality gate, accepted assumptions/deferrals, resume checkpoint, and gate/readback updates. | applied |
| User approved continuing the Stage 13 planning workflow through implementation-plan drafting after the planning gates passed. | current-session preference | Created `docs/roadmap/stage-13/implementation-plan.md` from the approved planning artifact and recorded implementation-plan handoff. | applied |
| Maintainer refined the reusable pattern toward payload-agnostic collection and explicit durable handoff. | prior-session design requirement | Superseded by the Sample/Batch-native revision: keep collectors payload-agnostic, use `SampleCollection` only when a sample snapshot/view is useful, avoid public prediction or batch collection families, and allow only a narrow code-backed export/save helper over existing export/save primitives if implementation proves duplication. | superseded/refined |
| Maintainer approved the design-review findings and requested four refinements: require source `RecordRef` or augmented export descriptors for prediction export, place generic collection operation helpers under `rphys.ops.collections`, remove prediction runner language for now, and compare the pattern against datasource design. | prior-session design requirement | Updated planning and implementation-plan artifacts to remove public prediction runner implementation shape, require descriptor-backed export adapters, and add datasource pattern alignment guidance. The `rphys.ops.collections` placement was superseded by the later maintainer refinement to keep collection mechanics in `rphys.collections` and shared export behavior under existing export ownership. | superseded |
| Maintainer refined collection placement and durable handoff: keep collection APIs under `rphys.collections`, do not create `rphys.ops.collections`, and treat prediction/evaluation/report launches as separate scripts over derived datasets when needed. | current-session design requirement | Updated planning and implementation-plan artifacts to describe prediction, evaluation, and structured report outputs as the same sample artifact -> item-to-export adapter -> existing export/save -> datasource handoff, with multiple evaluation workflows able to consume the same sample artifact datasource. | applied |
| Maintainer agreed that serialized predictions, evaluation results, and report datasets should be interacted with through the datasource layer where possible. | current-session design requirement | Added explicit serialized-output datasource reuse documentation, including descriptor-backed export requirements, domain/datasource ownership split, separate-script examples, and a generic cross-process descriptor recovery revisit trigger. | applied |
| Maintainer revised Stage 13 to keep prediction/evaluation/report flows native to `Sample` and `Batch`, avoid public `Prediction*` record families and `BatchCollection`/`BatchCollector`, serialize artifacts as individual samples, add explicit uncollation policy support, and load test/evaluation artifacts through generic datasource adapters. | current-session design requirement | Updated roadmap, planning, and implementation-plan direction to prioritize Batch-native prediction, sample-granular artifact export/reload, generic sample artifact layouts, and evaluation over reloaded samples rather than prediction-specific records/datasources. | applied |
| Maintainer refined analysis, visualization, reporting, and collection placement. | current-session design requirement | Updated controlling Stage 13 direction so analysis is generic group/reduce/metric pipeline composition rather than a public `AnalysisOp` family; visualization/report behavior attaches ordinary fields or returns report objects with explicit codec/export/save handling; and Phase 4 must reconsider consolidating sample collection APIs under `rphys.data.collections` with `rphys.collections` only transitional or truly generic if needed. | applied |
| Maintainer accepted design-review recommendations for stale public surfaces and spec ownership. | current-session design requirement | Updated controlling direction and implementation plan to remove public `MetricObservation*`/`MetricResult`, remove `MethodOutputSpec`/`MethodOutputAdapter` with `MethodOutput`, replace method-output specs with generic returned-batch validation, make `TrainingOutputSpec` plan-owned with preflight/per-step guardrails, and restrict Stage 13 visualization/report codec work to hints/descriptors/fake test codecs. | applied |
| Maintainer requested final design review and approval if aligned. | current-session design approval | Ran final alignment review against `docs/roadmap.md`, `planning.md`, and `implementation-plan.md`; found no blockers in the controlling revision; approved the Stage 13 plan for implementation workflow preflight. | applied |

## Change Log

| Round | Update |
| --- | --- |
| 2026-05-17 / context planner | Created Stage 13 planning scaffold and populated source evidence, exploration coverage, roadmap extraction, overview, capability triage, module behavior map, functional requirements, and initial functionality-agreement queue. |
| 2026-05-17 / manager functionality review | Initially resolved FQ-13-8 toward a code-backed `RemotePhysPredictionError`, resolved FQ-13-9 to in-memory reports with report file writers deferred, and narrowed maintainer functionality decision to FQ-13-5 `EvaluationRunner` inclusion. Later Sample/Batch-native revision supersedes the prediction-error default. |
| 2026-05-17 / maintainer runner challenge | Maintainer challenged the `EvaluationRunner` framing as potentially duplicative of existing iterable/operation/pipeline/export patterns and requested consideration of reusable base/protocol structures that could also serve reports, dataset formatting, and similar pipeline jobs. FQ-13-5 and FR-13-6 were reframed around shared pipeline/job structure versus an evaluation-specific runner. |
| 2026-05-17 / FQ-13-5 agreement | Maintainer agreed to the no-standalone-runner baseline and asked for explanation/examples of the reusable pipeline/job structure. FQ-13-5 and FR-13-6 were locked; behavior confirmation was populated and marked passed. |
| 2026-05-17 / reusable-pattern design input | Maintainer agreed this is a better pattern and requested explicit consideration of abstract/generic design patterns introduced in Stages 10, 11, and 12 for better reuse across evaluation, reports, dataset formatting, and similar pipeline jobs. |
| 2026-05-17 / design proposal | Drafted proposed implementation shape, public/private interface direction, dependency direction, extension points, reusable-pattern boundary, DQ-13-1 through DQ-13-7, DD-13-1 through DD-13-10, design triage, and proposed examples. Stopped before implication review, validation planning, phase shaping, and implementation planning. |
| 2026-05-17 / design implication review | Pressure-tested the design against existing operation, collection/view/collector, method output, learner output, export/save, evaluation, report, dataset-formatting, and future-roadmap patterns. Rejected standalone `EvaluationRunner` and public generic `PipelineJob`; reclassified DD-13-1 through DD-13-10 as recorded recommendations with no blockers and no maintainer discussion packets. |
| 2026-05-17 / validation, phase shaping, and plan quality | Completed validation strategy, examples-to-validation mapping, six-phase implementation shape, plan quality gate, accepted assumptions/deferrals, resume checkpoint, and gate/readback updates. No code was implemented and `implementation-plan.md` was not created. |
| 2026-05-17 / implementation-plan handoff | Created `docs/roadmap/stage-13/implementation-plan.md` with six sequential phases, ownership, validation, examples, risks, stop conditions, and no-runner/no-public-generic-job guardrails. Marked implementation-plan handoff passed; no code was implemented. |
| 2026-05-17 / collection-first refinement | Validated that the current framework supports reuse through generic collections, operation pipelines, field handles, export requests, codec selection, save operations, and derived datasource assembly. Later Sample/Batch-native revision refined this away from `PredictionCollector` and collection materializer language toward `Batch` fields, explicit uncollation, and sample artifact adapters. |
| 2026-05-17 / descriptor-backed export and datasource alignment | Updated Stage 13 planning after maintainer review: no public `PredictionRunner` implementation shape, prediction export requires source `RecordRef` or augmented export-record descriptor evidence, and datasource design is recorded as a descriptor-first analogue rather than a Stage 13 ownership expansion. |
| 2026-05-17 / collection placement and durable handoff refinement | Updated Stage 13 planning to keep collection mechanics in `rphys.collections`, avoid `rphys.ops.collections`, route any shared export iteration through existing export/save ownership, and document prediction/evaluation/report as separate launchable derived-dataset handoff stages. |
| 2026-05-17 / serialized output datasource reuse | Documented that persisted predictions, metric/evaluation outputs, and structured report datasets should be ordinary derived datasource fields with domain-owned item-to-export adapters and datasource-owned reload/index/sample-source behavior. |
| 2026-05-17 / Sample-Batch native revision | Revised Stage 13 away from public `PredictionRecord`/`PredictionCollection`/`PredictionExport*` surfaces and toward native `Sample`/`Batch` pipeline flow, explicit batch uncollation policy, sample-granular artifact export, and generic sample artifact datasource reload. |
| 2026-05-17 / analysis-visualization-report refinement | Revised Stage 13 to avoid public analysis operation/result records by default, model analysis as generic pipeline composition, keep visualization/reporting operation-compatible with ordinary fields and explicit codec/export/save handoff, and reopen collection placement toward `rphys.data.collections` consolidation before Phase 4 implementation. |
| 2026-05-17 / design-review follow-up | Locked removal/de-publicization of metric observation/result surfaces, removal of method-output specs/adapters, generic `BatchOutputSpec`-style returned-batch validation, plan-owned `TrainingOutputSpec` guardrails, and fake-codec-only Stage 13 visualization/report validation. |
| 2026-05-17 / final design-review approval | Reviewed the controlling Stage 13 plan after the stale-surface/spec-ownership refinements and approved it for roadmap-version-implementation preflight. |
