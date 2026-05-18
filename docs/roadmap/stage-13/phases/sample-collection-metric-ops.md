# Phase 4 Execution Plan: Runtime Sample-Collection And Metric Operations

## Metadata

- Status: merged
- Roadmap stage: `v13`
- Feature focus: Stage 13 runtime sample-collection grouping, collection operations, and metric adapters
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Runtime Sample-Collection And Metric Operations
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 4: Runtime Sample-Collection And Metric Operations`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
- Phase execution plan path: `docs/roadmap/stage-13/phases/sample-collection-metric-ops.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 4, `sample-collection-metric-ops`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Blockers: none

## Objective

Make evaluation-like and dataset-formatting-like recipes expressible through
existing operation, collection, and metric substrates: sample streams group into
`SampleCollection` snapshots; collection operations sort, project, filter, and
stitch fields; metrics bind directly to ordinary `metrics/*` fields on returned
containers.

## Scope Contract

Metrics now expose detached `MetricValue` payloads and declared metric fields
instead of public metric observation/result records. Collection grouping and
stitching stay runtime-only and explicit: no datasource scan, no evaluator
lifecycle, no prediction-specific storage, no metric table/result family, and
no public generic job API are added.

## In-Scope Work

- Add `SampleCollectionGroupPlan`, `SampleCollectionSortPlan`, and
  `SampleCollectionConcatPlan`.
- Add runtime helpers for grouping `Iterable[Sample | CollectionItem[Sample]]`
  into grouped `SampleCollection` values, sorting by metadata or fields,
  projecting fields, filtering with skip diagnostics, and concatenating member
  sample fields into a revised `Sample`.
- Add operation adapters under `rphys.ops.sample` for grouping, existing
  `SampleCollectionView` execution, and collection-field concatenation without
  creating `rphys.ops.collections`.
- Refactor public metrics to keep `MetricValue`, `Metric`, `MetricContext`,
  `MetricContract`, and `MetricInputSpec`, while removing public
  `MetricObservation*`, `MetricObservationView*`, and `MetricResult` surfaces.
- Add `collect_metric_fields`, `MetricSampleOperation`, and
  `MetricCollectionOperation` as lazy metric operation exports.
- Update supervised learning to consume field-native metric outputs.
- Add unit, contract, package, and integration coverage for sample-collection
  operations, metric adapters, removed metric observation/result exports, and
  evaluation-like operation composition.
- Update glossary vocabulary for field-native metric operations and sample
  collections.

## Out-of-Scope Work

- Public `EvaluationRunner`, evaluator lifecycle, evaluation protocols/plans,
  inference engines, comparison specs, pipeline jobs, schedulers, registries,
  report writers, concrete visualization/report codecs, or output-directory
  conventions.
- Public `BatchCollection`, `BatchCollector`, `rphys.ops.collections`, metric
  observation collections/views, metric result rows/tables, or prediction
  storage classes.
- Concrete physiological stitching, filtering, resampling, masking, alignment,
  or metric catalogs.

## Scientific Contract Notes

- Grouping by item metadata and field payload values is explicit and fails on
  missing keys unless the plan allows missing values.
- Sorting by metadata or fields fails when required keys are missing or when key
  values cannot be ordered.
- Concatenation gathers member payloads in collection order and uses an
  injected joiner; the default tuple joiner makes no sampling-rate, axis,
  reconstruction, or alignment claim.
- Collection-level metric fields are written back onto copied samples with
  explicit replication metadata so downstream reductions can inspect scope.
- Metric callables must produce all declared writes and cannot emit undeclared
  metric fields.

## Implementation Summary

- `src/rphys/data/collections.py` implements runtime grouping, sorting,
  projection, filtering, and field concatenation descriptors/helpers.
- `src/rphys/ops/sample.py` adds `SampleCollectionGroupOperation`,
  `SampleCollectionViewOperation`, and `SampleCollectionConcatOperation`.
- `src/rphys/metrics/operations.py` adds field binding and sample/collection
  metric operation adapters; package-level metric operation exports are lazy to
  preserve import boundaries.
- `src/rphys/metrics/results.py`, `src/rphys/metrics/core.py`, and
  `src/rphys/metrics/specs.py` remove public observation/result/view records
  from metric contracts.
- `src/rphys/learning/supervised.py` now writes metric fields from
  `collect_metric_fields`.
- Package tests assert removed metric observation/result surfaces stay absent.

## Validation Commands

Targeted development commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_collections.py tests/unit/rphys/metrics/test_metric_contracts.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_contract.py tests/contracts/test_metric_observation_view_contract.py tests/contracts/test_stage13_sample_collection_ops_contract.py tests/contracts/test_stage13_metric_operation_contract.py tests/package/test_import.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/learning/test_supervised.py tests/integration/test_stage11_synthetic_contract_flow.py tests/integration/test_stage12_synthetic_training_flow.py tests/integration/test_stage13_synthetic_sample_collection_pipeline.py tests/unit/rphys/training/test_backend.py
```

Final PR-preparation commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-integration
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
git diff --check
```

## Validation Evidence

- Targeted collection/metric/package tests: 71 passed.
- Targeted learner/training/integration tests: 15 passed.
- Unit suite: 744 passed.
- Contract suite: 158 passed.
- Integration suite: 26 passed.
- Package suite: 68 passed.
- `make test-summary`: passed; package 68, unit 744, contract 158, and
  integration 26 passed; e2e and acceptance suites are not present.
- `make validate-pr`: passed, including `uv lock --check`, aggregate test
  summary, `uv build`, and `git diff --check`.
- `git diff --check`: passed.

## Reviewability

- Main behavioral review points: `src/rphys/data/collections.py`,
  `src/rphys/ops/sample.py`, and `src/rphys/metrics/operations.py`.
- Scope-control checks: no public evaluator, evaluation plan/result/runner,
  inference engine, generic job, registry, prediction storage, batch
  collection/collector, metric observation/result family, or `rphys.ops.collections`.

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: complete.
- Implementation validation: complete.
- PR preparation: complete in `docs/roadmap/stage-13/phases/sample-collection-metric-ops-pr-body.md`.
- PR: [#88](https://github.com/samcantrill/rphys/pull/88), opened against
  `develop` with required title.
- Merge result: PR [#88](https://github.com/samcantrill/rphys/pull/88) merged
  to `develop` at `2026-05-17T14:05:50Z`; merge commit
  `150f947587463aecde6950f325b8be7a44d374c3`.
- Cleanup: pending after merge and metadata commit.
