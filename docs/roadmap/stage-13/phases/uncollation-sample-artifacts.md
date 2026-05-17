# Phase 3 Execution Plan: Uncollation And Sample Artifact Export/Reload

## Metadata

- Status: pr_open
- Roadmap stage: `v13`
- Feature focus: Stage 13 explicit uncollation and sample artifact handoff
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Uncollation And Sample Artifact Export/Reload
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 3: Uncollation And Sample Artifact Export/Reload`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
- Phase execution plan path: `docs/roadmap/stage-13/phases/uncollation-sample-artifacts.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 3, `uncollation-sample-artifacts`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Blockers: none

## Objective

Convert returned prediction/evaluation-ready `Batch` fields into one `Sample`
per item with explicit field policy, then prove those samples can be exported
and reloaded through existing export/save and derived datasource descriptors.

## Scope Contract

`UncollatePlan` controls all batch-to-sample splitting. Export request helpers
require a source `RecordRef` plus declared `FieldRef` evidence for any derived
field absent from the source descriptor. Persistence remains existing
`RecordExportRequest` -> `CodecSelectionOperation` -> `SaveOperation` ->
`ExportResult` -> `DerivedDataSourceBuilder`. This phase does not add
prediction storage, prediction export records, output-directory conventions,
new codecs, a batch collection, a collector, or datasource scanning.

## In-Scope Work

- Add explicit `UncollatePolicy`, `UncollateFieldSpec`, `UncollatePlan`, and
  `uncollate_batch_fields` under `rphys.data`.
- Support list/tuple splitting, sequence-like batch-axis splitting, broadcast,
  drop, error, and adapter-owned custom splitters.
- Validate sample count, duplicate locators, payload lengths, metadata
  alignment, unsupported fields, and invalid custom splitter configuration.
- Add descriptor-backed sample artifact helpers in `rphys.ops.export`.
- Add a narrow `export_record_requests` helper that iterates existing
  codec-selection/save operations for already assembled record requests.
- Add unit, contract, package, and integration tests for uncollation,
  descriptor-backed export requests, and derived datasource reload.
- Update glossary and implementation-plan evidence.

## Out-of-Scope Work

- Prediction-specific materializers, export plans/results, manifests, stores,
  storage classes, output directory schemas, or datasource families.
- Implicit tensor-axis guesses, temporal reconstruction, stitching, masking,
  sampling-rate interpretation, or physiological transformations.
- New real codecs or report/visualization writers.
- Public `BatchCollection`, `BatchCollector`, or collection operation behavior.

## Scientific Contract Notes

- Uncollation is explicit and field-locator based; it never infers sample count
  from payloads or treats an entire batch as one durable record.
- Metadata lists/tuples must match `sample_count`; scalar metadata is broadcast.
- Derived prediction fields require descriptor evidence before export, so
  durable reload keeps source record identity and exported field provenance
  inspectable.
- Export helpers do not inspect filesystems beyond existing save operations and
  do not scan output directories to reconstruct datasets.

## Implementation Summary

- `src/rphys/data/uncollation.py` implements explicit field policies and
  `uncollate_batch_fields`.
- `src/rphys/ops/export.py` adds `build_sample_artifact_record`,
  `sample_artifact_export_request`, and `export_record_requests`.
- Package exports and import-boundary tests include the new data/export helpers.
- `tests/integration/test_stage13_sample_artifact_flow.py` proves returned
  `Batch` fields uncollate to samples, export through existing save operations,
  assemble into a derived datasource, and reload through `SampleBuilder`.

## Validation Commands

Targeted development commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_uncollation.py tests/unit/rphys/ops/test_export_sample_artifacts.py tests/contracts/test_stage13_sample_artifact_contract.py tests/integration/test_stage13_sample_artifact_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
```

Final PR-preparation commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-integration
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
git diff --check
```

## Validation Evidence

- Targeted uncollation/export/integration/package tests: 74 passed.
- Stage 13 sample artifact contract tests: 3 passed.
- Unit suite: 746 passed.
- Contract suite: 156 passed.
- Package suite: 68 passed.
- Integration suite: 25 passed.
- `make test-summary`: passed; package 68, unit 746, contract 156, and
  integration 25 passed; e2e and acceptance suites are not present.
- `make validate-pr`: passed, including `uv lock --check`, aggregate test
  summary, `uv build`, and `git diff --check`.

## Reviewability

- Main behavioral review points: `src/rphys/data/uncollation.py`, the sample
  artifact helpers in `src/rphys/ops/export.py`, and the synthetic integration
  reload path.
- Scope-control checks: no prediction-specific export/storage family, no batch
  collection/collector, no new datasource scanner, no real codecs, and no report
  writer.

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: complete.
- Implementation validation: complete.
- PR preparation: complete in `docs/roadmap/stage-13/phases/uncollation-sample-artifacts-pr-body.md`.
- PR: [#87](https://github.com/samcantrill/rphys/pull/87), opened against
  `develop` with required title.
- Merge result: pending.
- Cleanup: pending after merge and metadata commit.
