# Stage 11 Loss, Objective, And Metric Contracts - Phase 3: Loss Contracts And Patch Results

## Summary

- Added loss specs, contracts, contexts, terms, results, and structural
  `Loss` protocol exports.
- Added central typed loss validation errors.
- Added focused unit and contract tests for locator normalization, missing
  fields, metadata checks, empty masks, raw scalar handles, immutable patches,
  declared writes, and no input mutation.

## Scientific And Design Contract

- Losses consume declared field containers and fail loudly on missing required
  fields, metadata mismatches, invalid reductions, invalid patch fields, and
  empty masks where the contract can detect them.
- `LossTerm.value` preserves the raw backend-native handle; metadata records
  backend, differentiability, gradient path, reduction, unit, diagnostics, and
  provenance without claiming backend autograd proof.
- `LossResult.fields` is a patch-only immutable mapping; input containers are
  not mutated by default.
- No concrete loss catalogs, objectives, metrics, trainer behavior, backend
  imports, or Stage 10 method-output coupling were added.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/losses/test_loss_contracts.py tests/contracts/test_loss_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Backend-neutral scalar metadata remains descriptive until Stage 12 adapter
  work proves stricter autograd/backward behavior.
