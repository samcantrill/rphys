# Phase 1 Execution Plan: Scaffold, Imports, And Errors

## Metadata

- Status: implemented
- Roadmap stage: `v13`
- Feature focus: Stage 13 package import and error posture
- Stage descriptor: Prediction, Evaluation, Analysis, And Reports
- Phase descriptor: Scaffold, Imports, And Errors
- PR title: `Stage 13 Prediction, Evaluation, Analysis, And Reports - Phase 1: Scaffold, Imports, And Errors`
- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p1-scaffold-imports-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p1-scaffold-imports-errors`
- Phase execution plan path: `docs/roadmap/stage-13/phases/scaffold-imports-errors.md`
- Full plan: `docs/roadmap/stage-13/implementation-plan.md`
- Planning document: `docs/roadmap/stage-13/planning.md`
- Source phase: Phase 1, `scaffold-imports-errors`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed in implementation plan review
- Draft pass: manager-local fast-path plan
- Refine pass: not needed
- Setup limitations: Stage 13 planning and implementation-plan artifacts were present only in the control checkout and were copied into this phase branch as source metadata.
- Blockers: none

## Objective

Establish the Stage 13 package homes as lightweight, code-backed scaffolds and
lock the initial error posture before later phases add public behavior.

## Full-Plan Context

This phase does not add prediction, evaluation, analysis, visualization, report,
or artifact behavior. It prepares the import surface and broad error categories
used by later Batch-native, uncollation, collection, metric, and report phases.

## Source Phase Summary

- Goal: keep package homes importable and minimal.
- Required scope: `rphys.prediction`, `rphys.evaluation`, `rphys.analysis`, central error docstrings, package/import tests, and import-boundary tests.
- Required checkpoints: no placeholder public exports, no broad prediction error, no optional/backend/workflow imports.
- Acceptance criteria: package homes import with empty `__all__`, evaluation/analysis broad errors remain available, and forbidden Stage 13 public names are absent.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: empty Stage 13 package homes already exist; `RemotePhysEvaluationError` and `RemotePhysAnalysisError` already exist in `src/rphys/errors.py`.
- Existing tests or harness behavior: package tests centralize public `__all__` checks; import-boundary tests run subprocess checks for forbidden imports.
- Import-boundary or dependency constraints: Stage 13 package imports must not load datasources, methods, export codecs, training, workflow, plotting/dataframe, tensor, video, or test-support modules.

## Phase Isolation State

- Control checkout dirty-state review: dirty only in roadmap/stage planning files; no Phase 1 code or test files were modified in the control checkout.
- Dedicated branch/worktree status: created for Phase 1.
- Current `develop` base: `be3256e`.
- Earlier phase dependency status: no earlier Stage 13 phases.
- Push/PR infrastructure status: GitHub auth verified with network access and git credential setup completed.
- Stop condition if isolation cannot be maintained: do not implement in the control checkout.

## In-Scope Work

- Clarify Stage 13 package-home docstrings without adding exports.
- Clarify broad evaluation and analysis error docstrings.
- Add package tests for Stage 13 scaffold package surfaces and broad-error posture.
- Add import-boundary tests for forbidden backend/workflow/export dependencies.

## Out-of-Scope Work

- Public prediction records, runners, collectors, output specs, materializers, datasources, or storage helpers.
- Public evaluation runners, engines, protocols, plans, results, comparison specs, or job/runtime APIs.
- Public analysis operation/result/context records, report records, visualization descriptors, or report writers.
- Any Method, Learner, TrainingPlan, uncollation, collection, metric, export, or report behavior.

## Assumptions

- Existing broad evaluation and analysis error bases are the right Stage 13 catch points until code-backed subclasses are needed.
- A broad prediction error remains absent until a public prediction-operation surface needs a distinct catch point.
- Empty package homes are acceptable when guarded by import and export tests.

## Scope Contract

No public behavior beyond package importability and broad error availability is
introduced. Root `rphys.__all__` remains empty. Stage 13 package `__all__`
values remain empty and must not expose placeholder names.

## Scientific Contract Notes

- Sampling and temporal alignment: not affected.
- Field roles, locators, schemas, and provenance: no field behavior is added.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: not affected.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not affected.

## Design Impact

- Maintainability: package homes can grow only when later phases add code-backed behavior.
- Extensibility: forbidden placeholder names prevent accidental commitment to runner or storage APIs.
- Lightweight import policy: guarded by subprocess import-boundary tests.
- Source-tree boundaries: no cross-package dependencies are added.

## Future Compatibility

Later phases can add Batch-native output specs, uncollation policies, collection
operations, metric adapters, visualization descriptors, and report records under
their package homes without changing the root import posture.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add placeholder public runner/result/report classes now | The Stage 13 plan requires code-backed exports only and rejects runner/job/storage families by default. |
| Add `RemotePhysPredictionError` immediately | No Phase 1 code-backed prediction behavior needs a distinct broad catch point. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Stage 13 package homes remain empty | Later phases own the concrete public contracts. | A later phase adds implemented public behavior. |

## Reviewability

- Expected PR size and shape: small scaffold/test/doc metadata PR.
- Files and areas to inspect: Stage 13 package `__init__` files, central error docstrings, package tests, import-boundary tests, and this phase artifact.
- Scope-control checks: no public Stage 13 behavior classes, no root exports, and no new dependencies.

## Implementation Steps

1. Clarify package docstrings and broad error docstrings.
2. Add package export/absence tests for Stage 13 scaffolds.
3. Add import-boundary tests for Stage 13 package homes.
4. Run Phase 1 validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: Stage 13 package homes are empty, code-backed, dependency-light, and do not expose forbidden names.

### Unit Suite

- Status: not required
- Expected paths: existing `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: no new errors were added; broad error posture is covered in package tests.

### Contract Suite

- Status: deferred
- Expected paths: none for Phase 1
- Required assertions or deferral reason: later phases introduce public contracts.

### Integration Suite

- Status: deferred
- Expected paths: none for Phase 1
- Required assertions or deferral reason: no behavior pipeline exists yet.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: not in scope.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no acceptance behavior added.

## Risks

- Empty packages can be mistaken for stable public APIs without guardrails.
- Future phases may accidentally add placeholder exports without tests.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: docstrings, package tests, import-boundary tests.
- Tests to run with each slice: targeted package pytest, then `make test-package`.
- Decisions the executor must not revisit: no public prediction/evaluation/analysis runner or record family; no broad prediction error in Phase 1.
- Conditions that require stopping for the manager: any need for code-backed behavior beyond import/error posture.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: manager-local fast path.
- Final phase execution plan: this document.
- Implementation summary: Stage 13 package/error/import scaffold tests and docstrings were added.
- Implementation validation: `uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py` passed with 64 tests; `make test-package` passed with 67 tests; `make test-summary` passed across package, unit, contract, and integration suites; `make validate-pr` passed; `git diff --check` passed.
- Refinement summary: not needed.
- Pre-submit blocker gate: passed; no placeholder exports, broad prediction error, forbidden Stage 13 public names, backend/workflow/export imports, or root re-exports were introduced.
- PR preparation: complete in `docs/roadmap/stage-13/phases/scaffold-imports-errors-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
