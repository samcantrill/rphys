# Stage 11 Loss, Objective, And Metric Contracts - Phase 1: Error And Import Scaffold

## Summary

- Added central broad catch points:
  `RemotePhysLossError`, `RemotePhysObjectiveError`, and
  `RemotePhysMetricError`.
- Kept `rphys.losses`, `rphys.objectives`, and `rphys.metrics` as lightweight
  package homes with empty public surfaces until later phases add code-backed
  contracts.
- Extended package/import-boundary tests to include direct Stage 11 package
  imports and `torchmetrics` as a forbidden optional dependency sentinel.

## Scientific And Design Contract

- No numerical loss, objective, metric, backend, trainer, evaluator, report, or
  observation behavior is implemented in this phase.
- Broad errors are centralized in `rphys.errors`; no package-local duplicate
  taxonomy or root re-export was added.
- The new errors preserve the base `RemotePhysError` message/context behavior
  for later contract validation.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Later phases still need package-specific contract records and typed
  validation errors. This phase only establishes the broad catch points and
  import posture.
