# Phase 6 Execution Plan: Metric Values, Observations, Collections, And Grouping

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: detached metric values, observations, collections, grouping, and metric results
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Metric Values, Observations, Collections, And Grouping
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 6: Metric Values, Observations, Collections, And Grouping`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p6-metric-observation-collections`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p6-metric-observation-collections`
- Phase execution plan path: `docs/roadmap/stage-11/phases/metric-observation-collections.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 6
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement detached metric value and observation records, immutable observation
collections, grouping descriptors, metric contexts/contracts/results, and
scoped exports without adding concrete metric algorithms or report/dataframe
schemas.

## Scope Contract

- `MetricValue` must be detached and non-differentiable.
- `MetricObservation` is the row-like public record; no
  `MetricResultRow`, `MetricResultTable`, or `MetricAggregationResult` is
  introduced.
- `MetricObservationCollection` is immutable, iterable over observations,
  preserves entry metadata, combines collections, and groups through
  caller-supplied `GroupBySpec`.
- Identity remains in `groups`/metadata using keys such as `subject_id`,
  `record_id`, `sample_id`, and `split`.
- `MetricResult.fields` is an immutable patch-only mapping validated against
  declared writes.
- No pandas/report/evaluator/datasource/trainer/backend imports are added.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/metrics/test_metric_contracts.py tests/contracts/test_metric_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added metric specs/contracts/context/protocol,
  detached values, observations, observation collections, grouping, results,
  package exports, and typed metric validation errors.
- Implementation validation: focused tests passed; `make test-unit`,
  `make test-contract`, `make test-package`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no report/dataframe/evaluator
  scope, public row/table classes, hidden metric state, or backend imports were
  introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/metric-observation-collections-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
