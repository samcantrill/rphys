# Stage 11 Loss, Objective, And Metric Contracts - Phase 2: Shared Collection, View, And Collector Contracts

## Summary

- Added `rphys.collections` with structural `Collection`, `CollectionView`,
  and `Collector` protocols plus frozen `CollectionItem`,
  `CollectionContext`, `CollectionViewPlan`, and `CollectorResult` records.
- Added central collection validation errors in `rphys.errors`.
- Added unit and contract tests for value iteration, entry metadata access,
  immutable metadata/provenance, collector diagnostics, fail-loud validation,
  and fake collector/view composition.

## Scientific And Design Contract

- Collection iteration yields member values; `entries` preserves item-level
  metadata/provenance for later grouping, ordering, and diagnostics.
- Views return collections directly; no public view-result family was added.
- `CollectorResult` is only a materialization diagnostic record and requires
  explicit skip/reject policies when skipped or rejected items are recorded.
- The shared module depends only on `rphys.errors` and the standard library.

## Validation

- `uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/test_collections.py tests/contracts/test_collection_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-unit` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-contract` passed.
- `UV_CACHE_DIR=/tmp/uv-cache make test-package` passed.
- `git diff --check` passed.

## Residual Risk

- Later sample and metric collection phases still need domain-specific
  collection snapshots and views. This phase intentionally does not provide a
  concrete generic collection implementation or operation pipeline wrapper.
