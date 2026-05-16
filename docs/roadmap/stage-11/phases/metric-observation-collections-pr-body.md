# Stage 11 Loss, Objective, And Metric Contracts - Phase 6: Metric Values, Observations, Collections, And Grouping

## Summary

- Added metric specs, contexts, protocol, detached values, observations,
  observation collections, grouping specs, and metric result patches.
- Added central typed metric validation errors.
- Added unit and contract tests for detachment, grouping metadata, collection
  immutability, grouping, patch validation, and rejected row/table names.

## Scientific And Design Contract

- Metric values are detached and non-differentiable; invalid differentiability
  claims fail loudly.
- Observations carry level, grouping identity, window metadata, diagnostics,
  metadata, and provenance.
- Identity remains in `groups`/metadata and is caller-supplied; datasource-owned
  grouping and report/dataframe schema work stays deferred.
- No public `MetricResultRow`, `MetricResultTable`, or
  `MetricAggregationResult` was added.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/metrics/test_metric_contracts.py tests/contracts/test_metric_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Stage 13 still owns evaluator/report/dataframe schemas, first-class identity
  fields, and any concrete metric algorithm catalog.
