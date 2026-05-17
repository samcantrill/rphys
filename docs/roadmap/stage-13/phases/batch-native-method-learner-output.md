# Phase 2 Execution Plan: Batch-Native Method, Learner, And Training Output

## Metadata

- Status: implemented
- Roadmap stage: `v13`
- Feature focus: Stage 13 Batch-native prediction and training output contracts
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Batch-Native Method, Learner, And Training Output
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 2: Batch-Native Method, Learner, And Training Output`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
- Phase execution plan path: `docs/roadmap/stage-13/phases/batch-native-method-learner-output.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 2, `batch-native-method-learner-output`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Draft pass: manager-local fast-path plan
- Refine pass: not needed
- Setup limitations: Phase 2 was based on `origin/develop` after Phase 1 metadata because the control checkout retained unrelated local roadmap edits.
- Blockers: none

## Objective

Replace the Stage 10/12 patch-style method and learner output records with
ordinary returned `Batch` values. Make output conformance generic and
field-locator based so later Stage 13 phases can uncollate, export, evaluate,
and report over the same runtime containers without prediction-specific wrapper
records.

## Scope Contract

Methods expose `Batch -> Batch` prediction behavior. Learners return a `Batch`
for every loop mode. Training engines read only fields declared by the
`TrainingPlan`-owned `TrainingOutputSpec`; train mode backpropagates only the
declared objective field. Inference input projection excludes target fields.
This phase does not add prediction runners, record families, collectors,
datasources, dataloaders, checkpoint selectors, export side effects, or
uncollation/materialization behavior.

## In-Scope Work

- Add `BatchOutputFieldSpec`, `BatchOutputSpec`, and `project_batch_fields` under
  `rphys.data` and re-export the generic output helpers from `rphys.methods`.
- Refactor `Method.predict` to return `Batch`.
- Remove public `MethodOutput`, `MethodOutputSpec`, `MethodOutputAdapter`, and
  `apply_method_output` names.
- Refactor `Learner.step` and `SupervisedLearner.step` to return `Batch`.
- Remove public `StepOutput` and `StepPrediction` names.
- Add `TrainingOutputSpec` and wire it into `TrainingPlan` and
  `NativeTrainingEngine`.
- Update unit, contract, integration, and package tests to the returned-`Batch`
  contract.
- Update glossary vocabulary for Batch-native method, learner, and training
  output behavior.

## Out-of-Scope Work

- Public `PredictionRecord`, `PredictionCollection`, `PredictionCollector`,
  `PredictionPlan`, `PredictionResult`, `PredictionRunner`, prediction
  datasource, prediction storage, or prediction export APIs.
- Durable sample artifact export/reload and explicit uncollation policy.
- Public evaluation protocols, engines, runners, comparison specs, or generic
  job/runtime records.
- Visualization/report records or report writers.
- Public metric-observation/result surface removal; that is left for the later
  metric/collection phase.

## Scientific Contract Notes

- Field meaning is carried by `FieldLocator`, role, schema, field metadata, and
  provenance on ordinary `Batch` fields.
- Projection helpers fail if target fields would be consumed by inference input
  projection.
- Returned-batch validation checks declared locators, roles, payload types,
  schemas, required fields, pass-through locators, and extra-field policy but
  does not infer sample rate, temporal alignment, masking, normalization, or
  physiological interpretation.
- Training validation raises mode and locator-aware errors for missing or
  non-backwardable train objectives.
- Training summaries remain primitive and do not materialize prediction
  payloads or mine `TrainingResult` for fields.

## Implementation Summary

- `src/rphys/data/output.py` implements generic returned-`Batch` output
  validation and construction.
- `src/rphys/methods/**` now keeps only method input adapters and re-exports the
  generic data output spec; method prediction returns `Batch`.
- `src/rphys/learning/**` now keeps `BackwardableScalar` validation and returns
  `Batch` from learners; `SupervisedLearner` writes loss/objective/metric fields
  onto returned batches.
- `src/rphys/training/plan.py` adds `TrainingOutputSpec`; `TrainingPlan`
  preflights train batches with a required objective locator.
- `src/rphys/training/backend.py` validates learner-returned batches through the
  plan-owned output spec before native train mechanics and summary recording.
- Tests update Stage 10/12 contracts and add Stage 13 returned-batch training
  output coverage.

## Validation Commands

Targeted development commands:

```sh
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/unit/rphys/data/test_batch_output.py tests/unit/rphys/learning/test_supervised.py tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_plan.py
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

- Targeted package/data/learning/training tests: 68 passed.
- Unit suite: 738 passed.
- Contract suite: 153 passed.
- Package suite: 68 passed.
- Integration suite: 24 passed.
- Test summary: package 68 passed; unit 738 passed; contract 153 passed;
  integration 24 passed; e2e and acceptance suites not present.
- `make validate-pr`: passed, including `uv lock --check`, aggregate test
  summary, `uv build`, and `git diff --check`.

## Reviewability

- Main behavioral review points: returned-`Batch` validation in
  `src/rphys/data/output.py`, trainer output declaration in
  `src/rphys/training/plan.py`, native engine validation order in
  `src/rphys/training/backend.py`, and `SupervisedLearner` field naming.
- Scope-control checks: no method-output or step-output compatibility shim
  remains public; no prediction runner/record/storage/export family is added;
  no datasource, dataloader, checkpoint, logger, plotting, or workflow import is
  introduced.

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: complete.
- Implementation validation: complete.
- Pre-submit blocker gate: passed; target leakage, public output-shim exports,
  trainer-owned prediction capture, `TrainingResult` payload mining, datasource
  scans, dataloader construction, checkpoint selection, and prediction
  storage/runner APIs are absent.
- PR preparation: complete in
  `docs/roadmap/stage-13/phases/batch-native-method-learner-output-pr-body.md`.
- Automated review: pending after PR creation.
- Merge result: pending.
- Cleanup: pending after merge and metadata commit.

