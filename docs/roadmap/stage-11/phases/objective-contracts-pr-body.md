# Stage 11 Loss, Objective, And Metric Contracts - Phase 4: Objective Contracts And Optimizer Scalar Results

## Summary

- Added objective specs, contracts, contexts, terms, results, and structural
  `Objective` protocol exports.
- Added central typed objective validation errors.
- Added unit and contract tests for aggregation descriptors, public loss-term
  passthrough, required `.total`, immutable patches, declared writes, and fake
  objective composition.

## Scientific And Design Contract

- `ObjectiveResult.total` is required and carries the raw backend-native scalar
  handle that Stage 12 can use as an optimizer target.
- Objective terms record backend, weights, reductions, differentiability,
  source terms, gradient path, diagnostics, metadata, and provenance without
  owning backward or optimizer mechanics.
- Public loss records are consumed through `rphys.losses`; no loss private
  helpers or trainer/evaluator/backends are imported.
- Field updates remain patch-only through immutable `fields`.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/objectives/test_objective_contracts.py tests/contracts/test_objective_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Stage 12 still owns stricter scalar/backward/distributed contracts,
  optimizers, schedulers, checkpoints, and trainer orchestration.
