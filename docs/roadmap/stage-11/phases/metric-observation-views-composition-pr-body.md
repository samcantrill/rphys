# Stage 11 Loss, Objective, And Metric Contracts - Phase 7: Metric Observation Views And Synthetic Composition

## Summary

- Added `MetricObservationViewPlan`, the structural `MetricObservationView`
  protocol, and `PlannedMetricObservationView` with injected projector behavior.
- Added fail-loud validation for empty inputs, missing group keys, unsupported
  source levels, mixed-level groups, projector output shape, and output level.
- Added unit, contract, and integration coverage for metric-then-view order and
  synthetic Stage 11 composition across samples, losses, objectives, metrics,
  and observation views.

## Scientific And Design Contract

- View outputs are still `MetricObservation` records inside a
  `MetricObservationCollection`; no view-result or aggregation-result family was
  introduced.
- View provenance records plan name, grouping keys, source counts, source
  levels, and source observation names on output collection entries.
- Projection behavior is injected so Stage 11 avoids concrete reduction
  algorithms, hidden accumulation, streaming lifecycle methods, distributed
  synchronization, report/dataframe schemas, and torchmetrics adapters.
- The synthetic integration flow covers
  `Iterable[Sample] -> CollectorResult[SampleCollection] -> SampleCollectionView
  -> Metric -> MetricObservationCollection -> MetricObservationView` plus an
  independent `LossResult -> ObjectiveResult.total` path.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/metrics/test_metric_contracts.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_contract.py tests/contracts/test_metric_observation_view_contract.py tests/integration/test_stage11_synthetic_contract_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed: 710 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed: 136 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-integration` passed: 21 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed: 56 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed: overall 923 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` passed, including
  `uv lock --check`, test summary, `uv build`, and `git diff --check`.
- `git diff --check` passed.

## Residual Risk

- Stage 13 still owns evaluator-owned observation view lifecycle, report and
  dataframe schemas, distributed synchronization policy, and concrete metric
  aggregation algorithms.
