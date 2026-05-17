# Phase 6 Execution Plan: Docs, Synthetic Examples, And Final Validation

## Metadata

- Status: ready for PR
- Roadmap stage: `v13`
- Feature focus: Stage 13 final synthetic composition examples, documentation, package posture, and validation evidence
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Docs, Synthetic Examples, And Final Validation
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 6: Docs, Synthetic Examples, And Final Validation`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p6-docs-examples-final-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p6-docs-examples-final-validation`
- Phase execution plan path: `docs/roadmap/stage-13/phases/docs-examples-final-validation.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 6, `docs-examples-final-validation`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Blockers: none

## Objective

Close Stage 13 by proving the accepted behavior with synthetic tests and docs:
Batch-native prediction, learner returned-batch output, explicit uncollation,
sample-artifact export/reload, grouped sample-collection recipes, metric
operations, visualization fields, reports, dataset-formatting-like handoff, and
final public import posture all compose without introducing forbidden runner,
job, storage, writer, or backend dependencies.

## Scope Contract

This phase is documentation, examples, validation, and guardrail coverage only.
It does not add new public product behavior beyond tests/docs, does not create a
public evaluation/report/analysis engine, and does not introduce real datasets,
concrete physiological algorithms, report writers, visualization backends, or
workflow runtime abstractions.

## In-Scope Work

- Add a Stage 13-named synthetic integration test for Batch-native method
  prediction, `SupervisedLearner.step(...) -> Batch`, target pass-through, and
  explicit uncollation to per-sample prediction fields.
- Extend the sample-artifact integration flow so reloaded derived datasource
  samples feed two separate recipes: metric/visualization/report construction
  and dataset-formatting-like collection concatenation.
- Add a Stage 13 example doc that maps executable tests to the accepted reuse
  pattern and explicitly records forbidden public surfaces.
- Add final package/import guardrails for forbidden Stage 13 runner, job,
  storage, analysis-result, output, metric-observation, and report-writer names.
- Run the required final validation commands and record evidence.

## Out-of-Scope Work

- Public `PredictionRunner`, `EvaluationRunner`, `EvaluationEngine`,
  `InferenceEngine`, `EvaluationProtocol`, `EvaluationPlan`,
  `EvaluationResult`, `PipelineJob`, `JobPlan`, `JobRunner`, `AnalysisOp`,
  `AnalysisContext`, `AnalysisResult`, prediction storage, report writers,
  dashboards, artifact stores, scheduler/resume APIs, or registries.
- Real plotting/dataframe/video/image dependencies, report materializers,
  markdown/HTML/PDF/CSV writers, real datasets, concrete algorithms, GPU or
  performance profiling, checkpoint selection, and training-log crawling.

## Scientific Contract Notes

- Returned batches remain ordinary `Batch` values; uncollation is explicit and
  includes every field retained for durable handoff.
- Derived sample artifacts reload through datasource/index/sample-builder
  behavior before evaluation-like, report-like, or dataset-formatting-like
  recipes run.
- Metric, visualization, and report examples preserve sample IDs, subject IDs,
  record IDs, split labels, field locators, metadata, and provenance in
  inspectable records.
- Dataset-formatting-like output is expressed through collection sorting and
  field concatenation, not a generic job or workflow engine.

## Implementation Summary

- `tests/integration/test_stage13_synthetic_composition_flow.py` proves
  Batch-native method and learner output plus explicit uncollation.
- `tests/integration/test_stage13_sample_artifact_flow.py` now carries reloaded
  sample artifacts into metric/visualization/report and formatted-record
  recipes.
- `tests/package/test_import.py` adds final forbidden-surface checks across
  root, prediction, evaluation, analysis, learning, methods, and metrics
  packages.
- `docs/roadmap/stage-13/examples.md` documents the executable Stage 13
  composition pattern and deferrals.

## Validation Commands

Focused development command:

```sh
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_stage13_synthetic_composition_flow.py tests/integration/test_stage13_sample_artifact_flow.py tests/integration/test_stage13_synthetic_sample_collection_pipeline.py tests/package/test_import.py tests/package/test_import_boundaries.py
```

Final PR-preparation commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-integration
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache uv lock --check
git diff --check
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
```

## Validation Evidence

- Focused Stage 13 integration/package tests: 71 passed.
- Package suite: 71 passed.
- Unit suite: 752 passed.
- Contract suite: 161 passed.
- Integration suite: 27 passed.
- `make test-summary`: passed; package 71, unit 752, contract 161, and
  integration 27 passed; e2e and acceptance suites are not present.
- `uv lock --check`: passed.
- `git diff --check`: passed.
- `make validate-pr`: passed, including `uv lock --check`, aggregate test
  summary, `uv build`, and `git diff --check`.

## Reviewability

- Main behavioral review points: `tests/integration/test_stage13_synthetic_composition_flow.py`,
  `tests/integration/test_stage13_sample_artifact_flow.py`, and
  `docs/roadmap/stage-13/examples.md`.
- Scope-control checks: no new public runtime APIs, no forbidden runner/job
  names, no prediction storage, no report writer/backend, and no hard
  dataframe/plotting dependency.

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: complete.
- Implementation validation: complete.
- PR preparation: complete in `docs/roadmap/stage-13/phases/docs-examples-final-validation-pr-body.md`.
- PR: pending.
- Merge result: pending.
- Cleanup: pending after merge and metadata commit.
