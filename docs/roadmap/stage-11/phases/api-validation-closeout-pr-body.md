# Stage 11 Loss, Objective, And Metric Contracts - Phase 8: API, Docs, Import Review, And Validation Closeout

## Summary

- Closed Stage 11 with scoped API/docstring review for collections, sample
  collections, losses, objectives, metrics, and metric observation views.
- Extended import-boundary tests so `rphys.data` and `rphys.data.collections`
  are directly included in Stage 11 dependency-light import checks.
- Added a package test that rejects cross-package private `_validation` helper
  imports across Stage 11 modules.
- Refined metric error and observation docstrings to cover view descriptors,
  grouped observations, view provenance, and fail-loud missing-group behavior.

## Scientific And Design Contract

- Public names remain code-backed and package-scoped; root `rphys` re-exports
  remain empty for Stage 11.
- Rejected metric row/table/aggregation/view-result/view-state public names
  remain absent.
- Stage 11 imports remain free of hard backend/report/trainer/evaluator/export
  dependencies, including `torch` and `torchmetrics`.
- No concrete algorithms, trainer/evaluator lifecycle, distributed sync,
  report/dataframe schema, export behavior, or Stage 10 method-output coupling
  was added.
- Examples 1-8 remain covered by synthetic unit, contract, integration, and
  package/import-boundary tests, including the direct sample-to-metric-view and
  loss-to-objective-total integration flow.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/package/test_import.py tests/package/test_import_boundaries.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_observation_view_contract.py tests/integration/test_stage11_synthetic_contract_flow.py` passed: 63 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed: 57 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed: 710 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed: 136 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-integration` passed: 21 tests.
- `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed: 924 tests overall.
- `uv lock --check` passed.
- `git diff --check` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` passed, including
  `uv lock --check`, test summary, `uv build`, and `git diff --check`.

## Residual Risk

- Stage 12 still owns stricter scalar/backward/distributed policy and trainer
  integration.
- Stage 13 still owns evaluator/report/dataframe schemas, concrete observation
  view lifecycle, first-class identity fields, and concrete aggregation
  algorithms.
- Package-local helper duplication remains an accepted short-term tradeoff to
  avoid hidden public API; repeated inconsistency should trigger later
  extraction review.
