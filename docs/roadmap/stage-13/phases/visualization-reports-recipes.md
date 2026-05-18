# Phase 5 Execution Plan: Visualization, Reports, And Diagnostics

## Metadata

- Status: merged
- Roadmap stage: `v13`
- Feature focus: Stage 13 dependency-light visualization descriptors, in-memory report records, and diagnostic renderer records
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Visualization, Reports, And Diagnostics
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 5: Visualization, Reports, And Diagnostics`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p5-visualization-reports-recipes`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p5-visualization-reports-recipes`
- Phase execution plan path: `docs/roadmap/stage-13/phases/visualization-reports-recipes.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 5, `visualization-reports-recipes`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Blockers: none

## Objective

Make Stage 13 analysis outputs expressible as ordinary operation-compatible
records and fields: visualization builders attach field-ready descriptors to
runtime containers, report builders return in-memory structured records, and
diagnostic renderers describe their outputs as data without writer or backend
side effects.

## Scope Contract

Analysis remains composition over existing samples, batches, sample
collections, metric fields, and operations. This phase intentionally adds
code-backed visualization/report records and adapters only; it does not add a
public `AnalysisOp`, `AnalysisContext`, `AnalysisResult`, evaluator lifecycle,
plotting backend, dataframe core type, report writer, output directory schema,
dashboard adapter, or artifact store.

## In-Scope Work

- Add dependency-light `VisualizationOutput` descriptors and a
  `VisualizationOperation` that attaches descriptors to copied `Sample`,
  `Batch`, or `SampleCollection` values.
- Add `ReportCell`, `ReportRow`, `ReportTable`, `ReportSection`, and `Report`
  records with primitive, metric, and visualization cell validation.
- Add `ReportOperation` for operation-compatible report/table builders.
- Add `DiagnosticRenderer` and `DiagnosticRenderOutput` as structural data
  contracts, not backend render/save hooks.
- Update package exports and import-boundary tests for the implemented
  analysis names.
- Add unit and contract tests for in-memory behavior, invalid rows/cells,
  operation compatibility, and writer/backend exclusions.
- Update glossary vocabulary for visualization, report, and diagnostic records.

## Out-of-Scope Work

- Public `AnalysisOp`, `AnalysisContext`, `AnalysisResult`, report engines,
  evaluation runners/protocols/results, prediction runners, inference engines,
  pipeline jobs, schedulers, registries, dashboards, artifact stores, output
  directories, report save conventions, and file writers.
- Eager imports of pandas, plotting, image/video, tensor, or rich media
  backends from analysis modules.
- Concrete report materializers, markdown/HTML/PDF/CSV writers, and real
  visualization codecs.
- Checkpoint selection, training-log crawling, mutation of predictions, or
  project-specific workflow behavior.

## Scientific Contract Notes

- Visualization outputs are descriptors with explicit codec keys or hints. They
  make no claim that rendering, plotting, video encoding, or file export has
  happened.
- Visualization operations copy runtime containers before writing descriptor
  fields and fail on field conflicts.
- Report cells accept primitive values, detached `MetricValue` records, and
  `VisualizationOutput` descriptors. Row columns must exactly match table
  columns so report scope remains inspectable.
- Report and diagnostic records preserve metadata, diagnostics, and provenance
  as ordinary primitive mappings; they do not own aggregation, evaluation, or
  export lifecycle semantics.

## Implementation Summary

- `src/rphys/analysis/visualization.py` implements visualization descriptors,
  field attachment, and operation-compatible visualization builders.
- `src/rphys/analysis/reports.py` implements report/table/cell records,
  report-builder operation compatibility, and diagnostic renderer output
  records.
- `src/rphys/analysis/_validation.py` keeps package-local validation helpers
  private.
- `src/rphys/analysis/__init__.py` now exposes only code-backed analysis names.
- Package tests assert analysis exports are scoped and root `rphys` does not
  re-export them.
- Contract and unit tests cover sample, batch, and collection visualization
  attachment, report records, metric-field rows, visualization references,
  invalid cells/rows, and no writer/dataframe/render methods.

## Validation Commands

Targeted development command:

```sh
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/analysis/test_visualization.py tests/unit/rphys/analysis/test_reports.py tests/contracts/test_stage13_visualization_contract.py tests/contracts/test_stage13_report_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py
```

Final PR-preparation commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
git diff --check
```

## Validation Evidence

- Targeted analysis/contract/package tests: 78 passed.
- Unit suite: 752 passed.
- Contract suite: 161 passed.
- Package suite: 70 passed.
- `make test-summary`: passed; package 70, unit 752, contract 161, and
  integration 26 passed; e2e and acceptance suites are not present.
- `make validate-pr`: passed, including `uv lock --check`, aggregate test
  summary, `uv build`, and `git diff --check`.
- `git diff --check`: passed.

## Reviewability

- Main behavioral review points: `src/rphys/analysis/visualization.py` and
  `src/rphys/analysis/reports.py`.
- Scope-control checks: no public analysis operation/result family, no
  dataframe/report-writer/render backend APIs, no output directory schema, no
  dashboard/artifact store, and no evaluator or job runner surfaces.

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: complete.
- Implementation validation: complete.
- PR preparation: complete in `docs/roadmap/stage-13/phases/visualization-reports-recipes-pr-body.md`.
- PR: [#89](https://github.com/samcantrill/rphys/pull/89), opened against
  `develop` with required title.
- Merge result: PR [#89](https://github.com/samcantrill/rphys/pull/89) merged
  to `develop` at `2026-05-17T14:25:38Z`; merge commit
  `8e390b0aae8996c2825e3cf502da4b64e2338f2f`.
- Cleanup: pending after merge and metadata commit.
