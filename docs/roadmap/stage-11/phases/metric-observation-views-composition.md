# Phase 7 Execution Plan: Metric Observation Views And Synthetic Composition

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: metric observation view descriptors and injected view behavior
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Metric Observation Views And Synthetic Composition
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 7: Metric Observation Views And Synthetic Composition`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p7-metric-observation-views-composition`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p7-metric-observation-views-composition`
- Phase execution plan path: `docs/roadmap/stage-11/phases/metric-observation-views-composition.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 7
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement dependency-light metric observation view records and behavior over the
Phase 6 metric observation collection shape, then prove the Stage 11 records
compose through synthetic sample, loss, objective, metric, and view examples.

## Scope Contract

- `MetricObservationViewPlan` is an inspectable descriptor for grouping and
  projecting metric observations.
- `MetricObservationView` is a structural callable over
  `MetricObservationCollection` that returns `MetricObservationCollection`.
- `PlannedMetricObservationView` uses an injected projector; it does not define
  concrete aggregation/reduction algorithms.
- View output remains metric observations or observation collections with view,
  grouping, source-count, level, metadata, and provenance evidence.
- Empty inputs, missing group keys, unsupported source levels, mixed levels, and
  projector output shape fail loudly unless the descriptor explicitly allows the
  relevant policy.
- No public `MetricAggregationResult`, `MetricResultTable`,
  `MetricObservationViewResult`, streaming lifecycle, distributed sync,
  evaluator/report runner, dataframe schema, torchmetrics adapter, or export
  behavior is introduced.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/metrics/test_metric_contracts.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_contract.py tests/contracts/test_metric_observation_view_contract.py tests/integration/test_stage11_synthetic_contract_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-integration
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added `MetricObservationViewPlan`, structural
  `MetricObservationView`, and injected-projector
  `PlannedMetricObservationView`; added focused unit, contract, package, and
  synthetic integration coverage.
- Implementation validation: focused tests, `make test-unit`,
  `make test-contract`, `make test-integration`, `make test-package`,
  `make test-summary`, `make validate-pr`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no concrete view algorithm,
  public view-result class, lifecycle methods, evaluator/report coupling,
  distributed sync, torchmetrics adapter, or durable export behavior was
  introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/metric-observation-views-composition-pr-body.md`
  and PR [#77](https://github.com/samcantrill/rphys/pull/77) opened against
  `develop`.
- Automated review: passed manager-local; PR target/title verified, mergeable
  state reached, and no remote checks were reported.
- Merge result: PR [#77](https://github.com/samcantrill/rphys/pull/77)
  squash merged to `develop` as `b6df22c` on 2026-05-16.
- Cleanup: phase worktree removed and local/remote phase branches deleted.
- Remaining blockers: none.
